#!/usr/bin/env python3
"""Bounded, timestamp-aware Kraken + Uniswap V2 empirical data ingestor.

Only Python's standard library is required. Kraken rows are private research data;
do not commit or publicly redistribute them. The Open Price DEX rows are CC BY 4.0.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import io
import json
import os
import shutil
import statistics
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path
from typing import Any, Iterable


USER_AGENT = "master-thesis-empirical-ingestor/0.1"
KRAKEN_URL = "https://api.kraken.com/0/public/PostTrade"
OPENPRICE_LOGIN_URL = "https://files.deepmining.ch/api/login"
OPENPRICE_CSV_URL = (
    "https://files.deepmining.ch/api/raw/ethereum/prices/"
    "weth_usdt_uniswap_v2_03.csv"
)
OPENPRICE_PAGE_URL = "https://fair.deepmining.ch/ethereum"
OPENPRICE_REPO_URL = "https://github.com/DeepMining-Lab/Open_Price_Infra"
KRAKEN_DOC_URL = "https://docs.kraken.com/api/docs/rest-api/get-post-trade"

DEX_FIELDS = [
    "timestamp",
    "block_timestamp_utc",
    "block_number",
    "block_hash",
    "transaction_index",
    "transaction_hash",
    "log_index",
    "pool_address",
    "pool_fee_tier",
    "chain_id",
    "price_usdt_per_eth",
    "eth_amount",
    "usdt_amount",
    "volume_usdt",
    "reserve0",
    "reserve1",
    "pool_tvl_at_block",
    "slip_1k",
    "slip_10k",
    "quality_flags",
    "receipt_status",
    "gas_used",
    "effective_gas_price_wei",
    "transaction_gas_cost_eth",
    "estimated_transaction_gas_cost_usdt",
    "gas_usdt_price_basis",
]

KRAKEN_FIELDS = [
    "venue",
    "market",
    "trade_id",
    "trade_ts_utc",
    "publication_ts_utc",
    "price_usdt_per_eth",
    "quantity_eth",
    "notional_usdt",
    "aggressor_side",
]

ALIGNED_FIELDS = [
    "minute_utc",
    "cex_trade_count",
    "cex_open_usdt_per_eth",
    "cex_high_usdt_per_eth",
    "cex_low_usdt_per_eth",
    "cex_close_usdt_per_eth",
    "cex_volume_eth",
    "cex_volume_usdt",
    "cex_last_trade_ts_utc",
    "cex_publication_lag_median_ms",
    "dex_swap_count",
    "dex_volume_usdt",
    "dex_last_swap_ts_utc",
    "dex_last_swap_price_usdt_per_eth",
    "dex_last_reserve_price_usdt_per_eth",
    "dex_last_slip_1k_source_value",
    "dex_pool_fee_bps",
    "cex_dex_last_event_gap_ms",
    "cex_minus_dex_last_swap_price_usdt",
    "execution_replay_ready",
]


class IngestError(RuntimeError):
    pass


def parse_utc(value: str) -> dt.datetime:
    text = value.strip()
    if text.endswith("Z"):
        text = text[:-1] + "+00:00"
    parsed = dt.datetime.fromisoformat(text)
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=dt.timezone.utc)
    return parsed.astimezone(dt.timezone.utc)


def iso_utc(value: dt.datetime) -> str:
    return value.astimezone(dt.timezone.utc).isoformat(timespec="microseconds").replace(
        "+00:00", "Z"
    )


def preserve_utc_timestamp(value: str) -> str:
    """Normalize UTC suffix without truncating source sub-microsecond precision."""
    text = value.strip()
    if text.endswith("Z"):
        return text
    if text.endswith("+00:00"):
        return text[:-6] + "Z"
    return iso_utc(parse_utc(text))


def number(value: Any) -> float | None:
    if value is None or value == "":
        return None
    try:
        parsed = float(value)
        return parsed if parsed == parsed and abs(parsed) != float("inf") else None
    except (TypeError, ValueError):
        return None


def request_bytes(
    url: str,
    *,
    headers: dict[str, str] | None = None,
    data: bytes | None = None,
    method: str | None = None,
    timeout: int = 60,
) -> tuple[bytes, Any]:
    request_headers = {"User-Agent": USER_AGENT, **(headers or {})}
    request = urllib.request.Request(
        url, data=data, headers=request_headers, method=method
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            return response.read(), response.headers
    except urllib.error.HTTPError as exc:
        body = exc.read(512).decode("utf-8", "replace").replace("\n", " ")
        host = urllib.parse.urlsplit(url).hostname or "unknown host"
        raise IngestError(f"HTTP {exc.code} from {host}: {body}") from exc
    except urllib.error.URLError as exc:
        host = urllib.parse.urlsplit(url).hostname or "unknown host"
        raise IngestError(f"Network error from {host}: {exc.reason}") from exc


def request_json(url: str, *, timeout: int = 60) -> dict[str, Any]:
    payload, _ = request_bytes(url, headers={"Accept": "application/json"}, timeout=timeout)
    try:
        decoded = json.loads(payload)
    except json.JSONDecodeError as exc:
        raise IngestError("A source returned malformed JSON") from exc
    if not isinstance(decoded, dict):
        raise IngestError("A source returned an unexpected JSON structure")
    return decoded


def rpc_json(url: str, method: str, params: list[Any], request_id: int) -> Any:
    payload = json.dumps({"jsonrpc": "2.0", "id": request_id, "method": method, "params": params}).encode()
    response, _ = request_bytes(
        url,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        data=payload,
        method="POST",
        timeout=30,
    )
    try:
        body = json.loads(response)
    except json.JSONDecodeError as exc:
        raise IngestError("Ethereum RPC returned malformed JSON.") from exc
    if body.get("error"):
        raise IngestError(f"Ethereum RPC {method} failed: {body['error']}")
    return body.get("result")


def fetch_kraken_trades(
    start: dt.datetime,
    end: dt.datetime,
    market: str,
    max_trades: int,
) -> tuple[list[dict[str, Any]], int]:
    cursor = start
    cursor_query = iso_utc(start)
    by_id: dict[str, dict[str, Any]] = {}
    requests = 0
    while cursor < end:
        query = urllib.parse.urlencode(
            {
                "symbol": market,
                "from_ts": cursor_query,
                "to_ts": iso_utc(end),
                "count": 1000,
            }
        )
        response = request_json(f"{KRAKEN_URL}?{query}")
        requests += 1
        errors = response.get("error") or []
        if errors:
            raise IngestError(f"Kraken rejected the request: {errors}")
        result = response.get("result") or {}
        trades = result.get("trades") or []
        if not trades:
            break

        parsed_times: list[dt.datetime] = []
        for trade in trades:
            raw_trade_time = str(trade.get("trade_ts", ""))
            trade_time = parse_utc(raw_trade_time)
            parsed_times.append(trade_time)
            if not (start <= trade_time < end):
                continue
            trade_id = str(trade.get("trade_id") or "")
            price = number(trade.get("price"))
            quantity = number(trade.get("quantity"))
            if not trade_id or price is None or quantity is None:
                continue
            publication = trade.get("publication_ts")
            publication_time = parse_utc(str(publication)) if publication else None
            by_id[trade_id] = {
                "venue": "kraken",
                "market": market,
                "trade_id": trade_id,
                "trade_ts_utc": preserve_utc_timestamp(raw_trade_time),
                "publication_ts_utc": preserve_utc_timestamp(str(publication)) if publication_time else "",
                "price_usdt_per_eth": price,
                "quantity_eth": quantity,
                "notional_usdt": price * quantity,
                "aggressor_side": trade.get("side", ""),
            }
            if len(by_id) > max_trades:
                raise IngestError(
                    f"CEX trade limit ({max_trades}) reached; narrow the window or raise --max-cex-trades."
                )

        last_ts = result.get("last_ts")
        cursor_query = preserve_utc_timestamp(str(last_ts)) if last_ts else iso_utc(max(parsed_times))
        newest = parse_utc(cursor_query)
        if len(trades) < 1000 or newest >= end:
            break
        if newest <= cursor:
            raise IngestError("Kraken pagination stopped advancing; refusing a partial silent result.")
        cursor = newest
        time.sleep(0.15)

    return sorted(by_id.values(), key=lambda row: (row["trade_ts_utc"], row["trade_id"])), requests


def openprice_token() -> str:
    body, _ = request_bytes(
        OPENPRICE_LOGIN_URL,
        headers={"Content-Type": "application/json", "Accept": "application/json"},
        data=b"{}",
        method="POST",
    )
    text = body.decode("utf-8").strip()
    try:
        value = json.loads(text)
        if isinstance(value, dict):
            value = value.get("token") or value.get("auth") or value.get("X-Auth")
        elif isinstance(value, str):
            value = value
    except json.JSONDecodeError:
        value = text
    if not isinstance(value, str) or not value:
        raise IngestError("Open Price did not return an anonymous download token.")
    return value


def openprice_range(token: str, start: int, end: int) -> tuple[bytes, Any]:
    payload, headers = request_bytes(
        OPENPRICE_CSV_URL,
        headers={"X-Auth": token, "Range": f"bytes={start}-{end}"},
        timeout=120,
    )
    if headers.get("Content-Range") is None:
        raise IngestError("Open Price did not honor byte-range reads; refusing a full multi-GB download.")
    return payload, headers


def content_total(headers: Any) -> int:
    value = headers.get("Content-Range", "")
    try:
        return int(value.rsplit("/", 1)[1])
    except (IndexError, ValueError) as exc:
        raise IngestError("Could not determine the Open Price file size from Content-Range.") from exc


def decode_csv_line(line: bytes) -> list[str] | None:
    if not line.strip():
        return None
    try:
        return next(csv.reader([line.decode("utf-8")]))
    except (UnicodeDecodeError, csv.Error):
        return None


def timestamp_from_line(line: bytes) -> dt.datetime | None:
    values = decode_csv_line(line)
    if not values or not values[0]:
        return None
    try:
        return parse_utc(values[0])
    except ValueError:
        return None


def locate_dex_offset(
    token: str,
    total_bytes: int,
    header_line: bytes,
    start: dt.datetime,
    download_budget: int,
) -> tuple[int, int, int]:
    low = len(header_line) + 1
    high = total_bytes - 1
    requests = 0
    bytes_read = 0
    while high - low > 1:
        midpoint = (low + high) // 2
        range_end = min(total_bytes - 1, midpoint + 32_767)
        payload, _ = openprice_range(token, midpoint, range_end)
        requests += 1
        bytes_read += len(payload)
        if bytes_read > download_budget:
            raise IngestError("DEX seek exceeded --max-source-mib; increase the explicit limit to continue.")
        lines = payload.splitlines()
        # The first line may be a partial record, even when the offset lands on a boundary.
        candidates = lines[1:] if len(lines) > 1 else []
        candidate_time = next(
            (stamp for line in candidates if (stamp := timestamp_from_line(line)) is not None),
            None,
        )
        if candidate_time is None or candidate_time >= start:
            high = midpoint
        else:
            low = midpoint + 1
    return max(len(header_line) + 1, low - 65_536), requests, bytes_read


def fetch_openprice_swaps(
    start: dt.datetime,
    end: dt.datetime,
    max_source_bytes: int,
) -> tuple[list[dict[str, str]], int, dict[str, Any]]:
    token = openprice_token()
    header_bytes, range_headers = openprice_range(token, 0, 65_535)
    total = content_total(range_headers)
    header_line = header_bytes.splitlines()[0]
    header = next(csv.reader([header_line.decode("utf-8")]))
    index = {column: position for position, column in enumerate(header)}
    if "timestamp" not in index:
        raise IngestError("Open Price CSV is missing its timestamp column.")

    scan_start, seek_requests, seek_bytes = locate_dex_offset(
        token, total, header_line, start, max_source_bytes
    )
    bytes_read = len(header_bytes) + seek_bytes
    rows: list[dict[str, str]] = []
    position = scan_start
    chunk_size = 1_048_576
    carry = b""
    first_range = True
    finished = False
    range_requests = 1

    while position < total and not finished:
        range_end = min(total - 1, position + chunk_size - 1)
        payload, _ = openprice_range(token, position, range_end)
        range_requests += 1
        bytes_read += len(payload)
        if bytes_read > max_source_bytes:
            raise IngestError(
                "DEX event range exceeded --max-source-mib; narrow the requested interval or raise the explicit limit."
            )
        if first_range:
            # Range starts inside a line; skip the partial row so no malformed data is retained.
            payload = payload.split(b"\n", 1)[1] if b"\n" in payload else b""
            first_range = False
        lines = (carry + payload).split(b"\n")
        carry = lines.pop()
        for line in lines:
            values = decode_csv_line(line)
            if not values:
                continue
            try:
                event_time = parse_utc(values[index["timestamp"]])
            except (ValueError, IndexError):
                continue
            if event_time >= end:
                finished = True
                break
            if event_time < start:
                continue
            row = {
                field: values[index[field]] if field in index and index[field] < len(values) else ""
                for field in DEX_FIELDS
            }
            rows.append(row)
        position += range_end - position + 1

    metadata = {
        "source_file_bytes": total,
        "downloaded_bytes_including_header": bytes_read,
        "seek_range_requests": seek_requests,
        "stream_range_requests": range_requests - 1,
        "source_date_latest": max((row["timestamp"] for row in rows), default=None),
        "source_url": OPENPRICE_CSV_URL,
    }
    return rows, bytes_read, metadata


def enrich_gas_receipts(rows: list[dict[str, str]], max_receipts: int) -> dict[str, Any]:
    rpc_url = os.environ.get("ETHEREUM_RPC_URL", "").strip()
    if not rpc_url:
        raise IngestError("--enrich-gas requires an ETHEREUM_RPC_URL environment variable.")
    transaction_hashes = sorted({row["transaction_hash"] for row in rows if row.get("transaction_hash")})
    if len(transaction_hashes) > max_receipts:
        raise IngestError(
            f"Gas receipt limit ({max_receipts}) exceeded; narrow the window or raise --max-gas-receipts."
        )
    chain_id = rpc_json(rpc_url, "eth_chainId", [], 1)
    if chain_id != "0x1":
        raise IngestError(f"Expected Ethereum mainnet chain ID 0x1, received {chain_id!r}.")
    receipts: dict[str, dict[str, str]] = {}
    for index, transaction_hash in enumerate(transaction_hashes, start=2):
        receipt = rpc_json(rpc_url, "eth_getTransactionReceipt", [transaction_hash], index)
        if receipt is None:
            continue
        try:
            gas_used = int(receipt["gasUsed"], 16)
            effective_price = int(receipt["effectiveGasPrice"], 16)
        except (KeyError, TypeError, ValueError) as exc:
            raise IngestError(f"Ethereum receipt for {transaction_hash} lacks gas fields.") from exc
        cost_eth = Decimal(gas_used) * Decimal(effective_price) / Decimal(10**18)
        receipts[transaction_hash] = {
            "receipt_status": receipt.get("status", ""),
            "gas_used": str(gas_used),
            "effective_gas_price_wei": str(effective_price),
            "transaction_gas_cost_eth": format(cost_eth, ".18g"),
        }
        time.sleep(0.12)

    for row in rows:
        receipt = receipts.get(row.get("transaction_hash", ""), {})
        row.update(receipt)
        if receipt:
            try:
                gas_cost = Decimal(receipt["transaction_gas_cost_eth"])
                pool_price = Decimal(row.get("price_usdt_per_eth", ""))
                row["estimated_transaction_gas_cost_usdt"] = format(gas_cost * pool_price, ".12g")
                row["gas_usdt_price_basis"] = "same-swap effective price proxy"
            except (InvalidOperation, ValueError):
                row["estimated_transaction_gas_cost_usdt"] = ""
                row["gas_usdt_price_basis"] = ""
    return {
        "rpc_chain_id": chain_id,
        "transactions_requested": len(transaction_hashes),
        "receipts_returned": len(receipts),
        "gas_usdt_conversion": "whole-transaction gas multiplied by same-pool swap price; a proxy, not gas attribution to this pool event",
    }


def minute_key(value: str) -> dt.datetime:
    parsed = parse_utc(value)
    return parsed.replace(second=0, microsecond=0)


def decimal_reserve_price(row: dict[str, str]) -> str:
    try:
        reserve_weth = Decimal(row.get("reserve0", ""))
        reserve_usdt = Decimal(row.get("reserve1", ""))
        if reserve_weth <= 0 or reserve_usdt <= 0:
            return ""
        price = (reserve_usdt / Decimal(10**6)) / (reserve_weth / Decimal(10**18))
        return format(price, ".12g")
    except (InvalidOperation, ValueError):
        return ""


def aggregate_and_align(
    start: dt.datetime,
    end: dt.datetime,
    cex_rows: list[dict[str, Any]],
    dex_rows: list[dict[str, str]],
) -> list[dict[str, Any]]:
    cex_by_minute: dict[dt.datetime, list[dict[str, Any]]] = defaultdict(list)
    dex_by_minute: dict[dt.datetime, list[dict[str, str]]] = defaultdict(list)
    for row in cex_rows:
        cex_by_minute[minute_key(row["trade_ts_utc"])].append(row)
    for row in dex_rows:
        dex_by_minute[minute_key(row["timestamp"])].append(row)

    first_minute = minute_key(iso_utc(start))
    last_minute = minute_key(iso_utc(end - dt.timedelta(microseconds=1)))
    result: list[dict[str, Any]] = []
    minute = first_minute
    while minute <= last_minute:
        cex = sorted(
            cex_by_minute.get(minute, []),
            key=lambda row: (row["trade_ts_utc"], row["trade_id"]),
        )
        dex = sorted(
            dex_by_minute.get(minute, []),
            key=lambda row: (
                row.get("timestamp", ""),
                row.get("block_number", ""),
                row.get("transaction_index", ""),
                row.get("log_index", ""),
            ),
        )
        cex_prices = [row["price_usdt_per_eth"] for row in cex]
        cex_volume_eth = sum(row["quantity_eth"] for row in cex)
        cex_volume_usdt = sum(row["notional_usdt"] for row in cex)
        publication_lags = []
        for row in cex:
            if row["publication_ts_utc"]:
                lag = (parse_utc(row["publication_ts_utc"]) - parse_utc(row["trade_ts_utc"])).total_seconds() * 1000
                publication_lags.append(lag)

        last_dex = dex[-1] if dex else None
        dex_price = number(last_dex.get("price_usdt_per_eth")) if last_dex else None
        cex_close = cex_prices[-1] if cex_prices else None
        cex_last_ts = cex[-1]["trade_ts_utc"] if cex else ""
        event_gap_ms = (
            (parse_utc(cex_last_ts) - parse_utc(last_dex["timestamp"])).total_seconds() * 1000
            if cex and last_dex
            else ""
        )
        try:
            fee_bps = float(Decimal(last_dex.get("pool_fee_tier", "")) / Decimal(100)) if last_dex else None
        except (InvalidOperation, ValueError):
            fee_bps = None
        result.append(
            {
                "minute_utc": iso_utc(minute),
                "cex_trade_count": len(cex),
                "cex_open_usdt_per_eth": cex_prices[0] if cex_prices else "",
                "cex_high_usdt_per_eth": max(cex_prices) if cex_prices else "",
                "cex_low_usdt_per_eth": min(cex_prices) if cex_prices else "",
                "cex_close_usdt_per_eth": cex_close if cex_close is not None else "",
                "cex_volume_eth": cex_volume_eth if cex else "",
                "cex_volume_usdt": cex_volume_usdt if cex else "",
                "cex_last_trade_ts_utc": cex_last_ts,
                "cex_publication_lag_median_ms": statistics.median(publication_lags) if publication_lags else "",
                "dex_swap_count": len(dex),
                "dex_volume_usdt": sum(number(row.get("volume_usdt")) or 0.0 for row in dex) if dex else "",
                "dex_last_swap_ts_utc": last_dex.get("timestamp", "") if last_dex else "",
                "dex_last_swap_price_usdt_per_eth": dex_price if dex_price is not None else "",
                "dex_last_reserve_price_usdt_per_eth": decimal_reserve_price(last_dex) if last_dex else "",
                "dex_last_slip_1k_source_value": last_dex.get("slip_1k", "") if last_dex else "",
                "dex_pool_fee_bps": fee_bps if fee_bps is not None else "",
                "cex_dex_last_event_gap_ms": event_gap_ms,
                "cex_minus_dex_last_swap_price_usdt": cex_close - dex_price if cex_close is not None and dex_price is not None else "",
                "execution_replay_ready": "false",
            }
        )
        minute += dt.timedelta(minutes=1)
    return result


def write_csv(path: Path, fields: list[str], rows: Iterable[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def partition_rows(
    rows: list[dict[str, Any]], time_field: str, root: Path, source: str, fields: list[str]
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        moment = parse_utc(str(row[time_field]))
        grouped[moment.strftime("%Y-%m-%d")].append(row)
    outputs = []
    for day, day_rows in sorted(grouped.items()):
        path = root / f"raw/{source}/date={day}/part.csv"
        write_csv(path, fields, day_rows)
        outputs.append({"path": str(path), "rows": len(day_rows)})
    return outputs


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for block in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def azure_upload(root: Path, account: str, container: str, prefix: str) -> list[str]:
    if not shutil.which("az"):
        raise IngestError("Azure upload requested, but the Azure CLI is not installed.")
    check = subprocess.run(
        ["az", "account", "show", "--query", "name", "-o", "tsv"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=False,
    )
    if check.returncode:
        raise IngestError("Azure upload requested, but `az login` has no active account in this shell.")
    uploaded: list[str] = []
    for path in sorted(root.rglob("*")):
        if not path.is_file():
            continue
        blob_name = "/".join(part.strip("/") for part in [prefix, path.relative_to(root).as_posix()] if part)
        command = [
            "az", "storage", "blob", "upload",
            "--account-name", account,
            "--container-name", container,
            "--name", blob_name,
            "--file", str(path),
            "--auth-mode", "login",
            "--overwrite", "true",
            "--only-show-errors",
        ]
        completed = subprocess.run(command, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, check=False)
        if completed.returncode:
            error = completed.stderr.decode("utf-8", "replace")[-400:]
            raise IngestError(f"Azure upload failed for {path.name}: {error}")
        uploaded.append(blob_name)
    return uploaded


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--start", required=True, help="Inclusive UTC start timestamp (ISO-8601).")
    parser.add_argument("--end", required=True, help="Exclusive UTC end timestamp (ISO-8601).")
    parser.add_argument("--market", default="ETH/USDT", help="Kraken spot market symbol, default ETH/USDT.")
    parser.add_argument("--raw-output", type=Path, default=Path("data/raw/empirical-private"))
    parser.add_argument("--processed-output", type=Path, default=Path("data/processed/empirical-private"))
    parser.add_argument("--max-cex-trades", type=int, default=100_000)
    parser.add_argument("--enrich-gas", action="store_true", help="Fetch mainnet transaction receipts via ETHEREUM_RPC_URL.")
    parser.add_argument("--max-gas-receipts", type=int, default=500)
    parser.add_argument("--max-source-mib", type=int, default=512)
    parser.add_argument("--public-dex-sample", type=Path, help="Optionally save only CC BY 4.0 DEX rows to a tracked sample path.")
    parser.add_argument("--upload", action="store_true", help="Upload private capture via Azure CLI OAuth/RBAC.")
    parser.add_argument("--azure-account", default=os.environ.get("AZURE_STORAGE_ACCOUNT"))
    parser.add_argument("--azure-container", default=os.environ.get("AZURE_STORAGE_CONTAINER", "empirical-market"))
    parser.add_argument("--azure-prefix", default="microworld")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    start, end = parse_utc(args.start), parse_utc(args.end)
    if start >= end:
        raise IngestError("--start must be earlier than --end.")
    if args.max_cex_trades <= 0 or args.max_source_mib <= 0:
        raise IngestError("Download limits must be positive.")
    max_source_bytes = args.max_source_mib * 1024 * 1024

    print(f"Fetching Kraken {args.market} public trades for [{iso_utc(start)}, {iso_utc(end)})", flush=True)
    cex_rows, cex_requests = fetch_kraken_trades(start, end, args.market, args.max_cex_trades)
    print(f"Fetching the matching Uniswap V2 WETH/USDT event window ({args.max_source_mib} MiB cap)", flush=True)
    dex_rows, dex_bytes, dex_metadata = fetch_openprice_swaps(start, end, max_source_bytes)
    if args.enrich_gas:
        dex_metadata["gas_receipts"] = enrich_gas_receipts(dex_rows, args.max_gas_receipts)

    run_id = f"{start.strftime('%Y%m%dT%H%M%SZ')}_{end.strftime('%Y%m%dT%H%M%SZ')}"
    raw_root = args.raw_output / run_id
    processed_root = args.processed_output / run_id
    cex_partitions = partition_rows(cex_rows, "trade_ts_utc", raw_root, "cex-kraken-eth-usdt", KRAKEN_FIELDS)
    dex_partitions = partition_rows(dex_rows, "timestamp", raw_root, "dex-uniswap-v2-weth-usdt", DEX_FIELDS)
    aligned = aggregate_and_align(start, end, cex_rows, dex_rows)
    aligned_path = processed_root / "aligned_1m.csv"
    write_csv(aligned_path, ALIGNED_FIELDS, aligned)

    if args.public_dex_sample:
        write_csv(args.public_dex_sample, DEX_FIELDS, dex_rows)

    manifest: dict[str, Any] = {
        "schema_version": "real_cex_dex_ingest_v1",
        "run_id": run_id,
        "collection_timestamp_utc": iso_utc(dt.datetime.now(dt.timezone.utc)),
        "requested_window_start_utc_inclusive": iso_utc(start),
        "requested_window_end_utc_exclusive": iso_utc(end),
        "alignment_unit": "UTC minute; CEX executions and DEX block-time events are aggregated separately",
        "no_silent_forward_fill": True,
        "sources": {
            "cex": {
                "provider": "Kraken public Post-Trade API",
                "market": args.market,
                "url": KRAKEN_DOC_URL,
                "license_status": "public API data; no open redistribution license identified; keep source rows private",
                "redistribution": "not permitted by this project; exclude CEX raw and CEX-derived values from public Git",
                "records": len(cex_rows),
                "requests": cex_requests,
                "fields": ["trade_ts", "publication_ts", "price", "quantity", "trade side"],
            },
            "dex": {
                "provider": "Open Price / FairOnChain, DeepMining Lab",
                "pool": "Ethereum mainnet Uniswap V2 WETH/USDT, 0.30% pool fee",
                "url": OPENPRICE_PAGE_URL,
                "repository": OPENPRICE_REPO_URL,
                "license": "CC BY 4.0",
                "records": len(dex_rows),
                **dex_metadata,
            },
        },
        "outputs": {
            "cex_partitions_private": cex_partitions,
            "dex_partitions": dex_partitions,
            "aligned_1m_private": str(aligned_path),
            "aligned_1m_rows": len(aligned),
            "files": [],
        },
        "execution_replay_readiness": {
            "ready": False,
            "available": ["observed CEX trades", "exchange publication-to-execution timestamp difference where supplied", "DEX swaps", "reserves", "pool fee tier", "source slippage proxies", "transaction receipt gas when --enrich-gas is enabled"],
            "missing_or_external": ["CEX account-specific fee tier", "historical CEX order-book depth", "agent-specific network and decision latency", "agent capital and inventory", "transaction receipt gas unless separately enriched through an Ethereum RPC"],
            "interpretation": "This pilot validates acquisition and alignment only; it is not a finding, calibration, or executable backtest.",
        },
        "source_csv_downloaded_bytes": dex_bytes,
        "storage": {"mode": "local-private", "azure_upload_requested": args.upload},
        "ingestor_sha256": sha256_file(Path(__file__)),
    }
    all_outputs = [
        path
        for root in (raw_root, processed_root)
        for path in sorted(root.rglob("*"))
        if path.is_file()
    ]
    manifest["outputs"]["files"] = [
        {
            "path": str(path),
            "bytes": path.stat().st_size,
            "sha256": sha256_file(path),
        }
        for path in all_outputs
    ]
    manifest_path = raw_root / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    checksum_path = raw_root / "SHA256SUMS"
    checksum_targets = [*all_outputs, manifest_path]
    checksum_path.write_text(
        "".join(
            f"{sha256_file(path)}  {path.relative_to(raw_root).as_posix() if path.is_relative_to(raw_root) else 'processed/' + path.name}\n"
            for path in checksum_targets
        ),
        encoding="utf-8",
    )

    if args.upload:
        if not args.azure_account:
            raise IngestError("Set AZURE_STORAGE_ACCOUNT or provide --azure-account before requesting Azure upload.")
        uploaded = azure_upload(raw_root, args.azure_account, args.azure_container, args.azure_prefix + "/runs/" + run_id)
        uploaded.extend(azure_upload(processed_root, args.azure_account, args.azure_container, args.azure_prefix + "/runs/" + run_id + "/processed"))
        print(f"Uploaded {len(uploaded)} private objects to {args.azure_container}/{args.azure_prefix}/{run_id}")
    else:
        print("Azure upload skipped; pass --upload after provisioning the private Blob container and az login.")

    print(json.dumps({
        "run_id": run_id,
        "cex_trade_count": len(cex_rows),
        "dex_swap_count": len(dex_rows),
        "aligned_minutes": len(aligned),
        "private_manifest": str(manifest_path),
        "public_dex_sample": str(args.public_dex_sample) if args.public_dex_sample else None,
        "source_file_size_bytes": dex_metadata["source_file_bytes"],
        "downloaded_dex_bytes": dex_bytes,
    }, indent=2))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except IngestError as exc:
        print(f"INGEST FAILED: {exc}", file=sys.stderr)
        raise SystemExit(2)

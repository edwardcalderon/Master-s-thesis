#!/usr/bin/env python3
"""Summarize the checked-in, openly licensed DEX pilot excerpt.

This deliberately excludes the private CEX capture and reports descriptive
pipeline-readiness metrics only. It uses the Python standard library and makes no
network requests.
"""

from __future__ import annotations

import argparse
import csv
from decimal import Decimal
from pathlib import Path


DEFAULT_INPUT = Path("data/samples/empirical-pilot/uniswap_v2_weth_usdt_swaps.csv")
DEFAULT_OUTPUT = Path("thesis/figures/data/empirical_dex_pilot_summary.csv")


def summarize(source: Path) -> list[dict[str, str]]:
    with source.open(newline="", encoding="utf-8") as stream:
        rows = list(csv.DictReader(stream))
    if not rows:
        raise ValueError("The DEX pilot sample contains no observations.")
    if any(row["quality_flags"] != "ok" for row in rows):
        raise ValueError("The sample contains a row with a non-ok quality flag.")
    if len({row["pool_address"] for row in rows}) != 1:
        raise ValueError("The sample combines multiple pools.")
    if len({row["pool_fee_tier"] for row in rows}) != 1:
        raise ValueError("The sample combines fee tiers.")

    def values(column: str) -> list[Decimal]:
        return [Decimal(row[column]) for row in rows]

    prices = values("price_usdt_per_eth")
    slip_1k_percent = [value * 100 for value in values("slip_1k")]
    slip_10k_percent = [value * 100 for value in values("slip_10k")]
    fee_tier = Decimal(rows[0]["pool_fee_tier"])
    start = min(row["block_timestamp_utc"] for row in rows)
    end = max(row["block_timestamp_utc"] for row in rows)

    metrics = [
        ("Observed swaps", str(len(rows)), "events"),
        ("Observed event span", f"{start} to {end}", "UTC"),
        (
            "Sample quote volume",
            f"{sum(values('volume_usdt')):.6f}",
            "USDT across the three excerpted swaps; not venue-wide volume",
        ),
        (
            "Effective swap price range",
            f"{min(prices):.8f}--{max(prices):.8f}",
            "USDT/ETH; event trade prices, not reserve-implied marginal prices",
        ),
        (
            "Source-estimated slippage at 1,000 USDT",
            f"{min(slip_1k_percent):.8f}--{max(slip_1k_percent):.8f}",
            "percent; source estimate for a hypothetical trade size",
        ),
        (
            "Source-estimated slippage at 10,000 USDT",
            f"{min(slip_10k_percent):.8f}--{max(slip_10k_percent):.8f}",
            "percent; source estimate for a hypothetical trade size",
        ),
        (
            "Pool fee tier",
            f"{fee_tier / Decimal(10000):.4f}",
            "percent; nominal pool tier, not total execution cost",
        ),
    ]
    return [
        {"metric": metric, "value": value, "definition": definition}
        for metric, value, definition in metrics
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=DEFAULT_INPUT)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()

    summary = summarize(args.input)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", newline="", encoding="utf-8") as stream:
        writer = csv.DictWriter(stream, fieldnames=["metric", "value", "definition"])
        writer.writeheader()
        writer.writerows(summary)
    print(f"Wrote {len(summary)} DEX-only summary rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

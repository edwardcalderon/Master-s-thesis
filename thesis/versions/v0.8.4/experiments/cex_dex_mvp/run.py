#!/usr/bin/env python3
"""Deterministic CPMM mechanism checks for the CEX/DEX thesis MVP.

This is a synthetic mechanism model, not an empirically calibrated market simulator.
It uses only the Python standard library and writes a CSV trajectory plus JSON
summary/metadata into a run-specific output directory.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
DEFAULT_CONFIG = HERE / "config.json"
DEFAULT_OUTPUT = HERE / "output"
NUMERIC_TOLERANCE = 1e-12
TIME_SERIES_FIELDS = [
    "experiment",
    "scenario",
    "tick",
    "event",
    "cex_price",
    "dex_price",
    "reserve_x",
    "reserve_y",
    "log_error",
    "excess_error",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git_context() -> dict[str, Any]:
    try:
        head = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=HERE,
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        dirty = bool(
            subprocess.run(
                ["git", "status", "--porcelain"],
                cwd=HERE,
                check=True,
                capture_output=True,
                text=True,
            ).stdout.strip()
        )
        return {"git_head": head, "git_working_tree_dirty": dirty}
    except (OSError, subprocess.CalledProcessError):
        return {"git_head": None, "git_working_tree_dirty": None}


def price(reserve_x: float, reserve_y: float) -> float:
    return reserve_y / reserve_x


def log_error(reserve_x: float, reserve_y: float, cex_price: float) -> float:
    return math.log(price(reserve_x, reserve_y) / cex_price)


def excess_error(error: float, band: float) -> float:
    return math.copysign(max(abs(error) - band, 0.0), error)


def sell_x(reserve_x: float, reserve_y: float, amount_x: float) -> tuple[float, float]:
    """Swap x into a zero-fee CPMM and return updated reserves."""
    amount_out_y = reserve_y * amount_x / (reserve_x + amount_x)
    return reserve_x + amount_x, reserve_y - amount_out_y


def buy_x(reserve_x: float, reserve_y: float, amount_y: float) -> tuple[float, float]:
    """Swap y into a zero-fee CPMM and return updated reserves."""
    amount_out_x = reserve_x * amount_y / (reserve_y + amount_y)
    return reserve_x - amount_out_x, reserve_y + amount_y


def arbitrage_order(
    reserve_x: float,
    reserve_y: float,
    reference_price: float,
    band: float,
    capacity_fraction: float,
) -> tuple[str, float, str] | None:
    """Calculate a zero-fee trade toward the band edge without executing it."""
    error = log_error(reserve_x, reserve_y, reference_price)
    if abs(error) <= band + NUMERIC_TOLERANCE or capacity_fraction <= 0.0:
        return None

    invariant = reserve_x * reserve_y
    if error > band:
        target_price = reference_price * math.exp(band)
        needed_x = max(math.sqrt(invariant / target_price) - reserve_x, 0.0)
        amount_x = min(needed_x, capacity_fraction * reserve_x)
        if amount_x <= 0.0:
            return None
        return "sell-x", amount_x, "arbitrage-sell-x"

    target_price = reference_price * math.exp(-band)
    needed_y = max(math.sqrt(invariant * target_price) - reserve_y, 0.0)
    amount_y = min(needed_y, capacity_fraction * reserve_y)
    if amount_y <= 0.0:
        return None
    return "buy-x", amount_y, "arbitrage-buy-x"


def execute_arbitrage_order(
    reserve_x: float, reserve_y: float, order: tuple[str, float, str]
) -> tuple[float, float, str]:
    side, amount, event = order
    if side == "sell-x":
        next_x, next_y = sell_x(reserve_x, reserve_y, amount)
    elif side == "buy-x":
        next_x, next_y = buy_x(reserve_x, reserve_y, amount)
    else:
        raise ValueError(f"unknown arbitrage order side: {side}")
    return next_x, next_y, event


def arbitrage_step(
    reserve_x: float,
    reserve_y: float,
    reference_price: float,
    band: float,
    capacity_fraction: float,
) -> tuple[float, float, str]:
    """Execute one immediate arbitrage trade toward the nearest band edge."""
    order = arbitrage_order(reserve_x, reserve_y, reference_price, band, capacity_fraction)
    if order is None:
        return reserve_x, reserve_y, "arbitrage-none"
    return execute_arbitrage_order(reserve_x, reserve_y, order)


def snapshot(
    experiment: str,
    scenario: str,
    tick: int,
    event: str,
    reference_price: float,
    reserve_x: float,
    reserve_y: float,
    band: float,
) -> dict[str, Any]:
    error = log_error(reserve_x, reserve_y, reference_price)
    return {
        "experiment": experiment,
        "scenario": scenario,
        "tick": tick,
        "event": event,
        "cex_price": reference_price,
        "dex_price": price(reserve_x, reserve_y),
        "reserve_x": reserve_x,
        "reserve_y": reserve_y,
        "log_error": error,
        "excess_error": excess_error(error, band),
    }


def tracking_case(
    config: dict[str, Any],
    scenario: str,
    capacity_fraction: float,
    execution_delay_ticks: int = 0,
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    if execution_delay_ticks < 0:
        raise ValueError("execution_delay_ticks must be nonnegative")
    reserve_x = float(config["initial_reserve_x"])
    reserve_y = float(config["initial_reserve_y"])
    reference = float(config["initial_cex_price"])
    band = float(config["no_arbitrage_band_log"])
    shock_tick = int(config["shock_tick"])
    horizon = int(config["horizon_ticks"])
    shock = float(config["shock_log_return"])
    sustained_ticks = int(config["sustained_band_ticks"])
    rows = [snapshot("E0-E1", scenario, 0, "initial", reference, reserve_x, reserve_y, band)]
    errors: list[float] = [abs(log_error(reserve_x, reserve_y, reference))]
    in_band_streak = 0
    return_tick: int | None = None
    pending_order: tuple[str, float, str] | None = None
    pending_execute_tick: int | None = None

    for tick in range(1, horizon + 1):
        events: list[str] = []
        if tick == shock_tick:
            reference *= math.exp(shock)
            events.append("cex-shock")

        executed_delayed_order = False
        if pending_order is not None and pending_execute_tick is not None and tick >= pending_execute_tick:
            reserve_x, reserve_y, arb_event = execute_arbitrage_order(
                reserve_x, reserve_y, pending_order
            )
            events.append(f"delayed-{arb_event}")
            pending_order = None
            pending_execute_tick = None
            executed_delayed_order = True

        if pending_order is not None and not executed_delayed_order:
            events.append("arbitrage-order-waiting")
        elif not executed_delayed_order:
            order = arbitrage_order(
                reserve_x,
                reserve_y,
                reference,
                band,
                capacity_fraction,
            )
            if order is None:
                events.append("arbitrage-pending" if pending_order is not None else "arbitrage-none")
            elif execution_delay_ticks == 0:
                reserve_x, reserve_y, arb_event = execute_arbitrage_order(
                    reserve_x, reserve_y, order
                )
                events.append(arb_event)
            else:
                pending_order = order
                pending_execute_tick = tick + execution_delay_ticks
                events.append("arbitrage-order-submitted")

        row = snapshot(
            "E0-E1",
            scenario,
            tick,
            "+".join(events),
            reference,
            reserve_x,
            reserve_y,
            band,
        )
        rows.append(row)
        errors.append(abs(float(row["log_error"])))

        if abs(float(row["log_error"])) <= band + NUMERIC_TOLERANCE:
            in_band_streak += 1
            if return_tick is None and in_band_streak >= sustained_ticks:
                return_tick = tick - sustained_ticks + 1
        else:
            in_band_streak = 0

    return rows, {
        "experiment": "E0-E1",
        "scenario": scenario,
        "capacity_fraction_per_tick": capacity_fraction,
        "max_absolute_log_error": max(errors),
        "max_excess_error": max(max(value - band, 0.0) for value in errors),
        "sustained_return_tick": return_tick,
        "sustained_return_rule_ticks": sustained_ticks,
        "horizon_ticks": horizon,
        "execution_delay_ticks": execution_delay_ticks,
        "pending_order_at_horizon": pending_order is not None,
    }


def fixed_sale_case(
    config: dict[str, Any], scenario: str, remaining_fraction: float
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    reserve_x = float(config["initial_reserve_x"])
    reserve_y = float(config["initial_reserve_y"])
    reference = float(config["initial_cex_price"])
    band = float(config["no_arbitrage_band_log"])
    sale = float(config["fixed_sale_x"])
    rows = [snapshot("E2", scenario, 0, "initial", reference, reserve_x, reserve_y, band)]

    if remaining_fraction < 1.0:
        reserve_x *= remaining_fraction
        reserve_y *= remaining_fraction
    rows.append(snapshot("E2", scenario, 1, "proportional-lp-withdrawal", reference, reserve_x, reserve_y, band))
    price_before = price(reserve_x, reserve_y)
    reserve_x, reserve_y = sell_x(reserve_x, reserve_y, sale)
    rows.append(snapshot("E2", scenario, 2, "fixed-x-sale", reference, reserve_x, reserve_y, band))
    price_after = price(reserve_x, reserve_y)

    return rows, {
        "experiment": "E2",
        "scenario": scenario,
        "remaining_reserve_fraction": remaining_fraction,
        "fixed_sale_x": sale,
        "reserve_x_before_sale": reserve_x - sale,
        "reserve_x_after_sale": reserve_x,
        "absolute_log_price_impact": abs(math.log(price_after / price_before)),
        "percentage_price_change": price_after / price_before - 1.0,
        "arbitrage_disabled": True,
    }


def adaptive_liquidity_case(
    config: dict[str, Any], scenario: str, adaptive: bool
) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    """Compare static LP depth with a one-shot threshold withdrawal under shared flow."""
    e3 = config["e3"]
    reserve_x = float(config["initial_reserve_x"])
    reserve_y = float(config["initial_reserve_y"])
    reference = float(config["initial_cex_price"])
    band = float(config["no_arbitrage_band_log"])
    shock_tick = int(e3["shock_tick"])
    horizon = int(e3["horizon_ticks"])
    shock = float(e3["shock_log_return"])
    sale_x = float(e3["fixed_x_sale_per_tick"])
    trigger = float(e3["adaptive_lp_trigger_log_error"])
    remaining_fraction = float(e3["lp_remaining_reserve_fraction"])
    capacity = float(e3["arbitrage_capacity_fraction"])

    rows = [snapshot("E3", scenario, 0, "initial", reference, reserve_x, reserve_y, band)]
    errors: list[float] = [abs(log_error(reserve_x, reserve_y, reference))]
    withdrawal_applied = False
    in_band_streak = 0
    return_tick: int | None = None

    for tick in range(1, horizon + 1):
        events: list[str] = []
        if tick == shock_tick:
            reference *= math.exp(shock)
            events.append("cex-shock")

        reserve_x, reserve_y = sell_x_into_pool(reserve_x, reserve_y, sale_x)
        events.append("exogenous-x-sale")

        if adaptive and not withdrawal_applied:
            observed_error = abs(log_error(reserve_x, reserve_y, reference))
            if observed_error > trigger:
                reserve_x *= remaining_fraction
                reserve_y *= remaining_fraction
                withdrawal_applied = True
                events.append("adaptive-lp-proportional-withdrawal")

        reserve_x, reserve_y, arb_event = arbitrage_step(
            reserve_x,
            reserve_y,
            reference,
            band,
            capacity,
        )
        events.append(arb_event)
        row = snapshot(
            "E3",
            scenario,
            tick,
            "+".join(events),
            reference,
            reserve_x,
            reserve_y,
            band,
        )
        rows.append(row)
        error = abs(float(row["log_error"]))
        errors.append(error)
        if error <= band + NUMERIC_TOLERANCE:
            in_band_streak += 1
            if return_tick is None and in_band_streak >= int(config["sustained_band_ticks"]):
                return_tick = tick - int(config["sustained_band_ticks"]) + 1
        else:
            in_band_streak = 0

    return rows, {
        "experiment": "E3",
        "scenario": scenario,
        "lp_policy": "one-shot-threshold-withdrawal" if adaptive else "static",
        "shock_log_return": shock,
        "shock_tick": shock_tick,
        "fixed_x_sale_per_tick": sale_x,
        "total_exogenous_x_sales": sale_x * horizon,
        "adaptive_lp_trigger_log_error": trigger if adaptive else None,
        "lp_remaining_reserve_fraction": remaining_fraction if withdrawal_applied else 1.0,
        "adaptive_lp_withdrawal_applied": withdrawal_applied,
        "arbitrage_capacity_fraction": capacity,
        "arbitrage_execution_delay_ticks": 0,
        "max_absolute_log_error": max(errors),
        "max_excess_error": max(max(value - band, 0.0) for value in errors),
        "sustained_return_tick": return_tick,
        "minimum_geometric_depth": min(
            math.sqrt(float(row["reserve_x"]) * float(row["reserve_y"])) for row in rows
        ),
        "horizon_ticks": horizon,
    }


def sell_x_into_pool(reserve_x: float, reserve_y: float, amount_x: float) -> tuple[float, float]:
    """Apply an exogenous trader sale through the zero-fee CPMM swap formula."""
    return sell_x(reserve_x, reserve_y, amount_x)


def validate(config: dict[str, Any]) -> None:
    positive = (
        "initial_reserve_x",
        "initial_reserve_y",
        "initial_cex_price",
        "horizon_ticks",
        "sustained_band_ticks",
    )
    for key in positive:
        if float(config[key]) <= 0.0:
            raise ValueError(f"{key} must be positive")
    initial_pool_price = float(config["initial_reserve_y"]) / float(config["initial_reserve_x"])
    if not math.isclose(initial_pool_price, float(config["initial_cex_price"]), rel_tol=1e-12):
        raise ValueError("initial CPMM and CEX prices must match")
    if not 1 <= int(config["shock_tick"]) <= int(config["horizon_ticks"]):
        raise ValueError("shock_tick must fall inside the simulation horizon")
    delay = float(config["execution_delay_ticks"])
    if not delay.is_integer() or delay < 0:
        raise ValueError("execution_delay_ticks must be a nonnegative integer")
    if float(config["no_arbitrage_band_log"]) < 0.0:
        raise ValueError("no_arbitrage_band_log must be nonnegative")
    if float(config["fixed_sale_x"]) <= 0.0:
        raise ValueError("fixed_sale_x must be positive")
    remaining = float(config["lp_remaining_reserve_fraction"])
    if not 0.0 < remaining <= 1.0:
        raise ValueError("lp_remaining_reserve_fraction must be in (0, 1]")
    for name, fraction in config["capacity_fractions"].items():
        if not 0.0 <= float(fraction) <= 1.0:
            raise ValueError(f"capacity fraction {name!r} must be in [0, 1]")
    e3 = config["e3"]
    e3_horizon = int(e3["horizon_ticks"])
    if e3_horizon <= 0 or not 1 <= int(e3["shock_tick"]) <= e3_horizon:
        raise ValueError("E3 shock_tick must fall inside a positive horizon")
    if float(e3["fixed_x_sale_per_tick"]) <= 0.0:
        raise ValueError("E3 fixed_x_sale_per_tick must be positive")
    if float(e3["adaptive_lp_trigger_log_error"]) < 0.0:
        raise ValueError("E3 adaptive_lp_trigger_log_error must be nonnegative")
    if not 0.0 < float(e3["lp_remaining_reserve_fraction"]) <= 1.0:
        raise ValueError("E3 lp_remaining_reserve_fraction must be in (0, 1]")
    if not 0.0 <= float(e3["arbitrage_capacity_fraction"]) <= 1.0:
        raise ValueError("E3 arbitrage_capacity_fraction must be in [0, 1]")
    if int(e3["arbitrage_execution_delay_ticks"]) != 0:
        raise ValueError("E3 currently requires zero arbitrage execution delay")


def run(config_path: Path, output_root: Path) -> Path:
    raw_config = config_path.read_bytes()
    config = json.loads(raw_config)
    validate(config)
    source = Path(__file__).read_bytes()
    run_hash = sha256_bytes(raw_config + source)[:12]
    run_id = f"cex-dex-mvp-{run_hash}"
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    rows: list[dict[str, Any]] = []
    summaries: list[dict[str, Any]] = []
    capacities = config["capacity_fractions"]
    for scenario, capacity_name in (
        ("E0-arbitrage-off", "off"),
        ("E0-arbitrage-on", "high"),
        ("E1-low-capacity", "low"),
        ("E1-high-capacity", "high"),
    ):
        case_rows, summary = tracking_case(
            config,
            scenario,
            float(capacities[capacity_name]),
            int(config["execution_delay_ticks"]),
        )
        rows.extend(case_rows)
        summaries.append(summary)

    for scenario, remaining_fraction in (
        ("E2-static-liquidity", 1.0),
        ("E2-withdrawn-liquidity", float(config["lp_remaining_reserve_fraction"])),
    ):
        case_rows, summary = fixed_sale_case(config, scenario, remaining_fraction)
        rows.extend(case_rows)
        summaries.append(summary)

    for scenario, adaptive in (
        ("E3-static-lp", False),
        ("E3-threshold-adaptive-lp", True),
    ):
        case_rows, summary = adaptive_liquidity_case(config, scenario, adaptive)
        rows.extend(case_rows)
        summaries.append(summary)

    with (run_dir / "timeseries.csv").open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TIME_SERIES_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    (run_dir / "summary.json").write_text(
        json.dumps({"run_id": run_id, "model_version": config["model_version"], "scenarios": summaries}, indent=2) + "\n",
        encoding="utf-8",
    )
    (run_dir / "config.json").write_bytes(raw_config)
    artifact_paths = ("timeseries.csv", "summary.json", "config.json")
    metadata = {
        "run_id": run_id,
        "model_version": config["model_version"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "config_sha256": sha256_bytes(raw_config),
        "runner_sha256": sha256_bytes(source),
        **git_context(),
        "randomness": "none; all configured contrasts are deterministic",
        "scope": "synthetic CPMM mechanism checks; not calibrated or externally validated",
        "artifact_sha256": {
            artifact: sha256_bytes((run_dir / artifact).read_bytes()) for artifact in artifact_paths
        },
    }
    (run_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return run_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run_dir = run(args.config.resolve(), args.output.resolve())
    print(f"Wrote deterministic CEX/DEX mechanism run to {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Run deterministic selection grids for E0/E1/E2/E3 CPMM mechanisms."""

from __future__ import annotations

import argparse
import csv
import json
import math
import platform
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from run import (
    DEFAULT_CONFIG,
    DEFAULT_OUTPUT,
    adaptive_liquidity_case,
    fixed_sale_case,
    git_context,
    sha256_bytes,
    tracking_case,
    validate,
)


HERE = Path(__file__).resolve().parent
DEFAULT_GRID = HERE / "sweep.json"
SUMMARY_FIELDS = [
    "experiment",
    "scenario",
    "shock_log_return",
    "capacity_fraction",
    "no_arbitrage_band_log",
    "execution_delay_ticks",
    "remaining_reserve_fraction",
    "max_absolute_log_error",
    "max_excess_error",
    "sustained_return_tick",
    "fixed_sale_x",
    "total_exogenous_x_sales",
    "absolute_log_price_impact",
    "percentage_price_change",
    "lp_policy",
    "adaptive_lp_trigger_log_error",
    "adaptive_lp_withdrawal_applied",
    "minimum_geometric_depth",
    "paired_peak_error_delta",
    "paired_excess_error_delta",
    "paired_return_tick_delta",
]
TIME_SERIES_FIELDS = [
    "experiment",
    "scenario",
    "shock_log_return",
    "capacity_fraction",
    "no_arbitrage_band_log",
    "execution_delay_ticks",
    "remaining_reserve_fraction",
    "tick",
    "event",
    "cex_price",
    "dex_price",
    "reserve_x",
    "reserve_y",
    "log_error",
    "excess_error",
    "lp_policy",
    "adaptive_lp_trigger_log_error",
    "adaptive_lp_remaining_reserve_fraction",
]


def run_sweep(config_path: Path, grid_path: Path, output_root: Path) -> Path:
    config_bytes = config_path.read_bytes()
    grid_bytes = grid_path.read_bytes()
    config = json.loads(config_bytes)
    grid = json.loads(grid_bytes)
    validate(config)

    shocks = [float(value) for value in grid["shock_log_returns"]]
    capacities = [float(value) for value in grid["arbitrage_capacity_fractions"]]
    bands = [float(value) for value in grid["no_arbitrage_band_logs"]]
    delay_values = [float(value) for value in grid["execution_delay_ticks"]]
    liquidity_levels = [float(value) for value in grid["liquidity_remaining_fractions"]]
    e3_grid = grid["e3_policy_selection"]
    e3_triggers = [float(value) for value in e3_grid["trigger_log_errors"]]
    e3_remaining = [float(value) for value in e3_grid["remaining_reserve_fractions"]]
    if (
        not shocks
        or not capacities
        or not bands
        or not delay_values
        or not liquidity_levels
        or not e3_triggers
        or not e3_remaining
    ):
        raise ValueError("sweep dimensions must not be empty")
    all_values = shocks + capacities + bands + delay_values + liquidity_levels + e3_triggers + e3_remaining
    if any(not math.isfinite(value) for value in all_values):
        raise ValueError("sweep values must be finite numbers")
    if any(value < 0.0 or value > 1.0 for value in capacities):
        raise ValueError("arbitrage capacity fractions must be in [0, 1]")
    if any(value < 0.0 for value in bands):
        raise ValueError("no-arbitrage bands must be nonnegative")
    if any(not value.is_integer() or value < 0.0 for value in delay_values):
        raise ValueError("execution delays must be nonnegative integer ticks")
    delays = [int(value) for value in delay_values]
    if any(value <= 0.0 or value > 1.0 for value in liquidity_levels):
        raise ValueError("liquidity remaining fractions must be in (0, 1]")
    if any(value < 0.0 for value in e3_triggers):
        raise ValueError("E3 trigger thresholds must be nonnegative")
    if any(value <= 0.0 or value > 1.0 for value in e3_remaining):
        raise ValueError("E3 remaining reserve fractions must be in (0, 1]")

    summary_rows: list[dict[str, Any]] = []
    time_series_rows: list[dict[str, Any]] = []

    for shock in shocks:
        for band in bands:
            case_config = {
                **config,
                "shock_log_return": shock,
                "no_arbitrage_band_log": band,
            }
            validate(case_config)
            for delay in delays:
                for capacity in capacities:
                    scenario = (
                        f"E0-E1-shock-{shock:+.3f}-band-{band:.3f}-"
                        f"delay-{delay}-capacity-{capacity:.3f}"
                    )
                    rows, summary = tracking_case(case_config, scenario, capacity, delay)
                    summary_rows.append(
                        {
                            "experiment": summary["experiment"],
                            "scenario": scenario,
                            "shock_log_return": shock,
                            "capacity_fraction": capacity,
                            "no_arbitrage_band_log": band,
                            "execution_delay_ticks": delay,
                            "remaining_reserve_fraction": None,
                            "max_absolute_log_error": summary["max_absolute_log_error"],
                            "max_excess_error": summary["max_excess_error"],
                            "sustained_return_tick": summary["sustained_return_tick"],
                            "fixed_sale_x": None,
                            "total_exogenous_x_sales": None,
                            "absolute_log_price_impact": None,
                            "percentage_price_change": None,
                            "lp_policy": None,
                            "adaptive_lp_trigger_log_error": None,
                            "adaptive_lp_withdrawal_applied": None,
                            "minimum_geometric_depth": None,
                            "paired_peak_error_delta": None,
                            "paired_excess_error_delta": None,
                            "paired_return_tick_delta": None,
                        }
                    )
                    time_series_rows.extend(
                        {
                            **row,
                            "shock_log_return": shock,
                            "capacity_fraction": capacity,
                            "no_arbitrage_band_log": band,
                            "execution_delay_ticks": delay,
                            "remaining_reserve_fraction": None,
                            "lp_policy": None,
                            "adaptive_lp_trigger_log_error": None,
                            "adaptive_lp_remaining_reserve_fraction": None,
                        }
                        for row in rows
                    )

    for fraction in liquidity_levels:
        scenario = f"E2-remaining-{fraction:.3f}"
        rows, summary = fixed_sale_case(config, scenario, fraction)
        summary_rows.append(
            {
                "experiment": summary["experiment"],
                "scenario": scenario,
                "shock_log_return": None,
                "capacity_fraction": None,
                "no_arbitrage_band_log": None,
                "execution_delay_ticks": None,
                "remaining_reserve_fraction": fraction,
                "max_absolute_log_error": None,
                "max_excess_error": None,
                "sustained_return_tick": None,
                "fixed_sale_x": summary["fixed_sale_x"],
                "total_exogenous_x_sales": None,
                "absolute_log_price_impact": summary["absolute_log_price_impact"],
                "percentage_price_change": summary["percentage_price_change"],
                "lp_policy": None,
                "adaptive_lp_trigger_log_error": None,
                "adaptive_lp_withdrawal_applied": None,
                "minimum_geometric_depth": None,
                "paired_peak_error_delta": None,
                "paired_excess_error_delta": None,
                "paired_return_tick_delta": None,
            }
        )
        time_series_rows.extend(
            {
                **row,
                "shock_log_return": None,
                "capacity_fraction": None,
                "no_arbitrage_band_log": None,
                "execution_delay_ticks": None,
                "remaining_reserve_fraction": fraction,
                "lp_policy": None,
                "adaptive_lp_trigger_log_error": None,
                "adaptive_lp_remaining_reserve_fraction": None,
            }
            for row in rows
        )

    for trigger in e3_triggers:
        for remaining_fraction in e3_remaining:
            e3_config = {
                **config,
                "e3": {
                    **config["e3"],
                    "adaptive_lp_trigger_log_error": trigger,
                    "lp_remaining_reserve_fraction": remaining_fraction,
                },
            }
            validate(e3_config)
            pair_id = f"E3-trigger-{trigger:.3f}-remaining-{remaining_fraction:.3f}"
            static_scenario = f"{pair_id}-static"
            adaptive_scenario = f"{pair_id}-adaptive"
            static_rows, static_summary = adaptive_liquidity_case(
                e3_config, static_scenario, False
            )
            adaptive_rows, adaptive_summary = adaptive_liquidity_case(
                e3_config, adaptive_scenario, True
            )
            paired_peak_delta = (
                adaptive_summary["max_absolute_log_error"]
                - static_summary["max_absolute_log_error"]
            )
            paired_excess_delta = (
                adaptive_summary["max_excess_error"] - static_summary["max_excess_error"]
            )
            static_return = static_summary["sustained_return_tick"]
            adaptive_return = adaptive_summary["sustained_return_tick"]
            paired_return_delta = (
                adaptive_return - static_return
                if static_return is not None and adaptive_return is not None
                else None
            )
            for policy_summary, policy_rows, policy_name in (
                (static_summary, static_rows, "static"),
                (adaptive_summary, adaptive_rows, "one-shot-threshold-withdrawal"),
            ):
                summary_rows.append(
                    {
                        "experiment": "E3",
                        "scenario": policy_summary["scenario"],
                        "shock_log_return": policy_summary["shock_log_return"],
                        "capacity_fraction": policy_summary["arbitrage_capacity_fraction"],
                        "no_arbitrage_band_log": float(e3_config["no_arbitrage_band_log"]),
                        "execution_delay_ticks": 0,
                        "remaining_reserve_fraction": policy_summary[
                            "lp_remaining_reserve_fraction"
                        ],
                        "max_absolute_log_error": policy_summary[
                            "max_absolute_log_error"
                        ],
                        "max_excess_error": policy_summary["max_excess_error"],
                        "sustained_return_tick": policy_summary[
                            "sustained_return_tick"
                        ],
                        "fixed_sale_x": None,
                        "total_exogenous_x_sales": policy_summary[
                            "total_exogenous_x_sales"
                        ],
                        "absolute_log_price_impact": None,
                        "percentage_price_change": None,
                        "lp_policy": policy_name,
                        "adaptive_lp_trigger_log_error": trigger,
                        "adaptive_lp_withdrawal_applied": policy_summary[
                            "adaptive_lp_withdrawal_applied"
                        ],
                        "minimum_geometric_depth": policy_summary[
                            "minimum_geometric_depth"
                        ],
                        "paired_peak_error_delta": (
                            paired_peak_delta if policy_name != "static" else None
                        ),
                        "paired_excess_error_delta": (
                            paired_excess_delta if policy_name != "static" else None
                        ),
                        "paired_return_tick_delta": (
                            paired_return_delta if policy_name != "static" else None
                        ),
                    }
                )
                time_series_rows.extend(
                    {
                        **row,
                        "shock_log_return": policy_summary["shock_log_return"],
                        "capacity_fraction": policy_summary[
                            "arbitrage_capacity_fraction"
                        ],
                        "no_arbitrage_band_log": float(
                            e3_config["no_arbitrage_band_log"]
                        ),
                        "execution_delay_ticks": 0,
                        "remaining_reserve_fraction": policy_summary[
                            "lp_remaining_reserve_fraction"
                        ],
                        "lp_policy": policy_name,
                        "adaptive_lp_trigger_log_error": trigger,
                        "adaptive_lp_remaining_reserve_fraction": remaining_fraction,
                    }
                    for row in policy_rows
                )

    runner_source = (HERE / "run.py").read_bytes()
    sweep_source = Path(__file__).read_bytes()
    run_hash = sha256_bytes(config_bytes + grid_bytes + runner_source + sweep_source)[:12]
    run_id = f"cex-dex-sweep-{run_hash}"
    run_dir = output_root / "sweeps" / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "config.json").write_bytes(config_bytes)
    (run_dir / "sweep.json").write_bytes(grid_bytes)

    summary_path = run_dir / "summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(summary_rows)

    timeseries_path = run_dir / "timeseries.csv"
    with timeseries_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=TIME_SERIES_FIELDS)
        writer.writeheader()
        writer.writerows(time_series_rows)

    artifacts = ("config.json", "sweep.json", "summary.csv", "timeseries.csv")
    metadata = {
        "run_id": run_id,
        "model_version": config["model_version"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "config_sha256": sha256_bytes(config_bytes),
        "sweep_grid_sha256": sha256_bytes(grid_bytes),
        "runner_sha256": sha256_bytes(runner_source),
        "sweep_script_sha256": sha256_bytes(sweep_source),
        "randomness": "none; parameter and E3 policy-selection grids only, not statistical replications",
        "scenario_count": len(summary_rows),
        "selection_only": True,
        "confirmation_configurations_included": False,
        **git_context(),
        "artifact_sha256": {
            name: sha256_bytes((run_dir / name).read_bytes()) for name in artifacts
        },
    }
    (run_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return run_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--grid", type=Path, default=DEFAULT_GRID)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run_dir = run_sweep(args.config.resolve(), args.grid.resolve(), args.output.resolve())
    print(f"Wrote deterministic E0/E1/E2/E3 selection sweep to {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

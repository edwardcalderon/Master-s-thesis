#!/usr/bin/env python3
"""Run a bounded paired exploratory experiment on the reference ABM.

This is a web exploration path, not a replacement for frozen thesis analyses.
The same exogenous noise schedule is used for the static and adaptive LP cases.
"""
from __future__ import annotations

import argparse
import copy
import json
import math
import re
import statistics
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
EXPERIMENTS = HERE.parents[1] / "experiments" / "cex_dex_mvp"
sys.path.insert(0, str(EXPERIMENTS))
from abm import make_noise_schedule, quantile, run_condition  # noqa: E402

MODEL_VERSION = "0.4.0"
MAX_SEEDS = 100
MAX_HORIZON = 100


def run_experiment(run_id: str, seed_start: int, seed_count: int, horizon: int,
                   shock: float, capacity: float, output: Path) -> dict[str, Any]:
    if not re.fullmatch(r"[a-f0-9-]{16,36}", run_id):
        raise ValueError("run_id must be a UUID-like lowercase identifier")
    if not 2 <= seed_count <= MAX_SEEDS:
        raise ValueError(f"seed_count must be between 2 and {MAX_SEEDS}")
    if not 5 <= horizon <= MAX_HORIZON:
        raise ValueError(f"horizon must be between 5 and {MAX_HORIZON}")
    if isinstance(seed_start, bool) or not 0 <= seed_start <= 1_000_000:
        raise ValueError("seed_start must be between 0 and 1000000")
    if not math.isfinite(shock) or not -0.2 <= shock <= 0.2:
        raise ValueError("shock must be finite and between -0.2 and 0.2")
    if not math.isfinite(capacity) or not 0.0 <= capacity <= 0.1:
        raise ValueError("capacity must be finite and between 0 and 0.1")

    config = json.loads((EXPERIMENTS / "abm_config.json").read_text())
    config["horizon_ticks"] = horizon
    config["shock_tick"] = 1
    scenarios = (("static-lp", False), ("adaptive-lp", True))
    by_scenario: dict[str, list[dict[str, Any]]] = {name: [] for name, _ in scenarios}
    series: dict[str, list[list[dict[str, Any]]]] = {name: [] for name, _ in scenarios}

    for seed in range(seed_start, seed_start + seed_count):
        schedule = make_noise_schedule(config, seed)
        for name, adaptive in scenarios:
            rows, summary = run_condition(
                copy.deepcopy(config), shock, seed, name, capacity, adaptive, schedule
            )
            by_scenario[name].append(summary)
            series[name].append(rows)

    metrics = (
        "maximum_absolute_log_error", "mean_absolute_log_error",
        "maximum_excess_error", "cumulative_excess_error",
        "minimum_geometric_depth", "ending_geometric_depth",
    )
    summaries: dict[str, dict[str, Any]] = {}
    for name, rows in by_scenario.items():
        summaries[name] = {
            "seed_count": seed_count,
            **{
                metric: {
                    "mean": statistics.mean(float(row[metric]) for row in rows),
                    "p05": quantile([float(row[metric]) for row in rows], 0.05),
                    "p95": quantile([float(row[metric]) for row in rows], 0.95),
                }
                for metric in metrics
            },
            "return_to_band_rate": sum(row["sustained_return_tick"] is not None for row in rows) / seed_count,
        }

    trajectory = []
    for tick in range(horizon + 1):
        point: dict[str, Any] = {"tick": tick}
        for name in by_scenario:
            tick_rows = [run[tick] for run in series[name]]
            point[f"{name}_cex"] = statistics.mean(float(row["cex_price"]) for row in tick_rows)
            point[f"{name}_dex"] = statistics.mean(float(row["dex_price"]) for row in tick_rows)
            point[f"{name}_abs_error"] = statistics.mean(abs(float(row["log_error"])) for row in tick_rows)
        trajectory.append(point)

    result = {
        "schema_version": "1.0",
        "run_id": run_id,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "synthetic": True,
        "exploratory": True,
        "model_version": MODEL_VERSION,
        "seed_start": seed_start,
        "seed_count": seed_count,
        "horizon_ticks": horizon,
        "shock_log_return": shock,
        "capacity_fraction": capacity,
        "pairing": "shared exogenous noise schedule within seed",
        "scenarios": summaries,
        "trajectory": trajectory,
        "limitations": "Exploratory web run; not frozen thesis evidence or empirical market validation.",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, sort_keys=True, indent=2) + "\n")
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--seed-start", type=int, default=0)
    parser.add_argument("--seed-count", type=int, default=20)
    parser.add_argument("--horizon", type=int, default=40)
    parser.add_argument("--shock", type=float, default=0.1)
    parser.add_argument("--capacity", type=float, default=0.03)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    run_experiment(args.run_id, args.seed_start, args.seed_count, args.horizon,
                   args.shock, args.capacity, args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

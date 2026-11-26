#!/usr/bin/env python3
"""Compare an affine reduced map with a band-aware hybrid map on held-out ABM cells."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import random
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from abm import make_noise_schedule, run_condition, validate as validate_abm
from confirm import scaled_config, write_csv
from run import git_context, sha256_bytes

HERE = Path(__file__).resolve().parent
MODEL_CONFIG = HERE / "abm_config.json"
ANALYSIS_CONFIG = HERE / "hybrid_config.json"
OUTPUT = HERE / "output" / "hybrid"
CONDITIONS = (
    ("E0-arb-off-static", 0.0, False),
    ("E1-arb-low-static", 0.005, False),
    ("E1-arb-high-static", 0.03, False),
    ("E3-adaptive-lp-high-arb", 0.03, True),
)
def features(error: float, z: float, band: float, hybrid: bool) -> list[float]:
    if not hybrid:
        return [error, z]
    outside = float(abs(error) > band)
    signed_excess = math.copysign(max(abs(error) - band, 0.0), error)
    return [error, z, signed_excess, z * outside]


def fit_regression(rows: list[tuple[float, float, float, float, float]], band: float,
                   hybrid: bool, target_index: int) -> list[float]:
    width = 4 if hybrid else 2
    x_rows = [features(row[0], row[1], band, hybrid) for row in rows]
    targets = [row[target_index] for row in rows]
    if len(rows) < width * 10:
        raise ValueError(f"insufficient transitions for {width}-parameter fit: {len(rows)}")
    matrix = [[sum(x[i] * x[j] for x in x_rows) for j in range(width)] for i in range(width)]
    vector = [sum(x[i] * y for x, y in zip(x_rows, targets)) for i in range(width)]
    # Partial-pivot Gaussian elimination for the small normal-equation system.
    augmented = [matrix[i] + [vector[i]] for i in range(width)]
    for column in range(width):
        pivot = max(range(column, width), key=lambda row: abs(augmented[row][column]))
        if abs(augmented[pivot][column]) <= 1e-18:
            raise ValueError("selection design is rank-deficient")
        augmented[column], augmented[pivot] = augmented[pivot], augmented[column]
        divisor = augmented[column][column]
        augmented[column] = [item / divisor for item in augmented[column]]
        for row in range(width):
            if row == column:
                continue
            factor = augmented[row][column]
            augmented[row] = [a - factor * b for a, b in zip(augmented[row], augmented[column])]
    return [augmented[i][-1] for i in range(width)]


def predict(coefficients: dict[str, list[float]], error: float, z: float,
            cex_return: float, band: float, hybrid: bool) -> tuple[float, float]:
    basis = features(error, z, band, hybrid)
    next_error = error - cex_return + sum(a * b for a, b in zip(coefficients["e"], basis))
    next_z = sum(a * b for a, b in zip(coefficients["z"], basis))
    return next_error, next_z


def fit_candidates(selection: list[dict[str, Any]], band: float) -> tuple[dict[str, dict[str, list[float]]], dict[str, dict[str, int]]]:
    by_condition: dict[str, list[tuple[float, float, float, float, float]]] = defaultdict(list)
    regime_counts: dict[str, dict[str, int]] = defaultdict(lambda: {"in_band": 0, "out_of_band": 0})
    groups: dict[tuple[int, float, str], list[dict[str, Any]]] = defaultdict(list)
    for row in selection:
        groups[(int(row["seed"]), float(row["shock_log_return"]), str(row["scenario"]))].append(row)
    for trajectory in groups.values():
        trajectory.sort(key=lambda item: int(item["tick"]))
        for current, following in zip(trajectory, trajectory[1:]):
            e = float(current["log_error"])
            regime_counts[str(current["scenario"])]["out_of_band" if abs(e) > band else "in_band"] += 1
            z = float(current["normalized_net_buy_pressure_z"])
            cex_return = float(following["cex_log_return"])
            by_condition[str(current["scenario"])].append((
                e, z, float(following["log_error"]) - e + cex_return,
                float(following["normalized_net_buy_pressure_z"]), cex_return,
            ))
    models: dict[str, dict[str, list[float]]] = {}
    for condition, *_ in CONDITIONS:
        values = by_condition[condition]
        models[condition] = {}
        for name, hybrid in (("L0", False), ("Hyb", True)):
            models[condition][name] = {
                "e": fit_regression(values, band, hybrid, 2),
                "z": fit_regression(values, band, hybrid, 3),
            }
    return models, dict(regime_counts)


def trajectory_errors(rows: list[dict[str, Any]], coefficients: dict[str, list[float]],
                      band: float, hybrid: bool) -> dict[str, float]:
    one_e: list[float] = []
    one_z: list[float] = []
    rollout_e: list[float] = []
    rollout_z: list[float] = []
    pred_e = float(rows[0]["log_error"])
    pred_z = float(rows[0]["normalized_net_buy_pressure_z"])
    for tick, (current, following) in enumerate(zip(rows, rows[1:]), start=1):
        actual_e = float(following["log_error"])
        actual_z = float(following["normalized_net_buy_pressure_z"])
        cex_return = float(following["cex_log_return"])
        observed_e, observed_z = predict(coefficients, float(current["log_error"]),
                                         float(current["normalized_net_buy_pressure_z"]), cex_return, band, hybrid)
        one_e.append(abs(observed_e - actual_e))
        one_z.append(abs(observed_z - actual_z))
        pred_e, pred_z = predict(coefficients, pred_e, pred_z, cex_return, band, hybrid)
        rollout_e.append(abs(pred_e - actual_e))
        rollout_z.append(abs(pred_z - actual_z))
    return {"one_e": statistics.mean(one_e), "one_z": statistics.mean(one_z),
            "rollout_e": statistics.mean(rollout_e), "rollout_z": statistics.mean(rollout_z)}


def bootstrap_interval(values: list[float], draws: int, seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(values)
    means = [statistics.mean(values[rng.randrange(n)] for _ in range(n)) for _ in range(draws)]
    means.sort()
    return means[math.floor(0.025 * (draws - 1))], means[math.floor(0.975 * (draws - 1))]


def run(model_path: Path, analysis_path: Path, output_root: Path) -> Path:
    model_bytes = model_path.read_bytes()
    analysis_bytes = analysis_path.read_bytes()
    base = json.loads(model_bytes)
    protocol = json.loads(analysis_bytes)
    validate_abm(base)
    seeds = protocol["seeds"]
    selection_seeds = range(int(seeds["selection_start"]), int(seeds["selection_start"]) + int(seeds["selection_count"]))
    confirmation_seeds = range(int(seeds["confirmation_start"]), int(seeds["confirmation_start"]) + int(seeds["confirmation_count"]))
    if set(selection_seeds) & set(confirmation_seeds):
        raise ValueError("selection and confirmation seed ranges overlap")
    band = float(base["no_arbitrage_band_log"])

    selection_rows: list[dict[str, Any]] = []
    for seed in selection_seeds:
        schedule = make_noise_schedule(base, seed)
        for shock in protocol["selection"]["shock_log_returns"]:
            config = scaled_config(base, 1.0)
            for condition, capacity, adaptive in CONDITIONS:
                rows, _ = run_condition(config, float(shock), seed, condition, capacity, adaptive, schedule)
                selection_rows.extend(rows)
    models, regime_counts = fit_candidates(selection_rows, band)

    records: list[dict[str, Any]] = []
    for seed in confirmation_seeds:
        schedule = make_noise_schedule(base, seed)
        for depth in protocol["confirmation"]["depth_scales"]:
            config = scaled_config(base, float(depth))
            for shock in protocol["confirmation"]["shock_log_returns"]:
                for condition, capacity, adaptive in CONDITIONS:
                    rows, _ = run_condition(config, float(shock), seed, condition, capacity, adaptive, schedule)
                    rows.sort(key=lambda item: int(item["tick"]))
                    record: dict[str, Any] = {
                        "split": "confirmation", "seed": seed, "depth_scale": float(depth),
                        "shock_log_return": float(shock), "condition": condition,
                    }
                    for name, is_hybrid in (("L0", False), ("Hyb", True)):
                        errors = trajectory_errors(rows, models[condition][name], band, is_hybrid)
                        for metric, value in errors.items():
                            record[f"{name}_{metric}_mae"] = value
                    records.append(record)

    seed_metrics: dict[int, dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    seed_model_metrics: dict[int, dict[str, dict[str, list[float]]]] = defaultdict(
        lambda: defaultdict(lambda: {"L0": [], "Hyb": []})
    )
    cell_metrics: dict[tuple[float, float, str], dict[str, list[float]]] = defaultdict(lambda: defaultdict(list))
    for record in records:
        seed = int(record["seed"])
        key = (float(record["depth_scale"]), float(record["shock_log_return"]), str(record["condition"]))
        for metric in ("one_e", "one_z", "rollout_e", "rollout_z"):
            l0 = float(record[f"L0_{metric}_mae"])
            hybrid = float(record[f"Hyb_{metric}_mae"])
            seed_metrics[seed][metric].append(l0 - hybrid)
            seed_model_metrics[seed][metric]["L0"].append(l0)
            seed_model_metrics[seed][metric]["Hyb"].append(hybrid)
            cell_metrics[key][metric].append(l0 - hybrid)
    paired = []
    for seed, metrics in sorted(seed_metrics.items()):
        row: dict[str, Any] = {"seed": seed}
        for metric, values in metrics.items():
            row[f"improvement_{metric}"] = statistics.mean(values)
            row[f"L0_mean_{metric}"] = statistics.mean(seed_model_metrics[seed][metric]["L0"])
            row[f"Hyb_mean_{metric}"] = statistics.mean(seed_model_metrics[seed][metric]["Hyb"])
        paired.append(row)
    primary = [float(row["improvement_rollout_e"]) for row in paired]
    uncertainty = protocol["metrics"]["uncertainty"]
    ci_low, ci_high = bootstrap_interval(primary, int(uncertainty["resamples"]), int(uncertainty["rng_seed"]))
    overall = {
        "primary_metric": "positive value means Hyb has lower rollout MAE of signed log error than L0",
        "seed_count": len(paired), "confirmation_trajectory_count": len(records),
        "mean_improvement_rollout_mae_e": statistics.mean(primary),
        "bootstrap_95pct_ci_low": ci_low, "bootstrap_95pct_ci_high": ci_high,
        "share_seeds_hyb_lower_rollout_mae_e": sum(value > 0.0 for value in primary) / len(primary),
        "metric_summary": {
            metric: {
                "L0_mean_mae": statistics.mean(float(row[f"L0_mean_{metric}"]) for row in paired),
                "Hyb_mean_mae": statistics.mean(float(row[f"Hyb_mean_{metric}"]) for row in paired),
                "mean_improvement_L0_minus_Hyb": statistics.mean(float(row[f"improvement_{metric}"]) for row in paired),
                "share_seeds_improved": sum(float(row[f"improvement_{metric}"]) > 0.0 for row in paired) / len(paired),
            }
            for metric in ("one_e", "one_z", "rollout_e", "rollout_z")
        },
        "selection_transition_count": sum(
            int(protocol["seeds"]["selection_count"])
            * len(protocol["selection"]["shock_log_returns"])
            * int(base["horizon_ticks"])
            for _ in CONDITIONS
        ),
        "cell_summary": [],
        "interpretation_limit": protocol["scope"],
    }
    cell_rows = []
    for key, metrics in sorted(cell_metrics.items()):
        row: dict[str, Any] = {"depth_scale": key[0], "shock_log_return": key[1], "condition": key[2], "seed_count": len(metrics["rollout_e"])}
        for metric, values in metrics.items():
            row[f"mean_improvement_{metric}"] = statistics.mean(values)
        cell_rows.append(row)
    source_names = ("hybrid.py", "hybrid_config.json", "abm.py", "run.py", "h1c.py", "confirm.py")
    source_hashes = {name: sha256_bytes((HERE / name).read_bytes()) for name in source_names}
    run_hash = sha256_bytes(model_bytes + analysis_bytes + json.dumps(source_hashes, sort_keys=True).encode())[:12]
    run_id = f"cex-dex-hybrid-{run_hash}"
    run_dir = output_root / run_id
    if run_dir.exists():
        raise FileExistsError(
            f"refusing to overwrite existing run {run_dir}; use --output with a fresh directory to reproduce it"
        )
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "model_config.json").write_bytes(model_bytes)
    (run_dir / "hybrid_config.json").write_bytes(analysis_bytes)
    (run_dir / "fitted_models.json").write_text(json.dumps(models, indent=2) + "\n", encoding="utf-8")
    (run_dir / "selection_regime_counts.json").write_text(json.dumps(regime_counts, indent=2) + "\n", encoding="utf-8")
    write_csv(run_dir / "seed_metrics.csv", paired, list(paired[0]))
    write_csv(run_dir / "cell_metrics.csv", cell_rows, list(cell_rows[0]))
    write_csv(run_dir / "trajectory_metrics.csv", records, list(records[0]))
    artifacts = ("model_config.json", "hybrid_config.json", "fitted_models.json", "selection_regime_counts.json", "seed_metrics.csv", "cell_metrics.csv", "trajectory_metrics.csv")
    metadata = {
        "run_id": run_id, "model_version": protocol["model_version"], "analysis_version": protocol["analysis_version"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(), "python_version": platform.python_version(),
        "model_config_sha256": sha256_bytes(model_bytes), "hybrid_config_sha256": sha256_bytes(analysis_bytes),
        "source_sha256": source_hashes, "selection_seeds": [min(selection_seeds), max(selection_seeds)],
        "confirmation_seeds": [min(confirmation_seeds), max(confirmation_seeds)],
        "selection_cells": {"depth_scales": protocol["selection"]["depth_scales"], "shock_log_returns": protocol["selection"]["shock_log_returns"]},
        "confirmation_cells": {"depth_scales": protocol["confirmation"]["depth_scales"], "shock_log_returns": protocol["confirmation"]["shock_log_returns"]},
        "independent_unit": "seed; confirmation cells averaged within each seed for primary interval",
        "metrics": protocol["metrics"], "selection_transition_count": overall["selection_transition_count"],
        "confirmation_trajectory_count": len(records), "git": git_context(),
        "artifact_sha256": {name: sha256_bytes((run_dir / name).read_bytes()) for name in artifacts},
    }
    (run_dir / "summary.json").write_text(json.dumps(overall, indent=2) + "\n", encoding="utf-8")
    (run_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2) + "\n", encoding="utf-8")
    return run_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-config", type=Path, default=MODEL_CONFIG)
    parser.add_argument("--analysis-config", type=Path, default=ANALYSIS_CONFIG)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    args = parser.parse_args()
    result = run(args.model_config.resolve(), args.analysis_config.resolve(), args.output.resolve())
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

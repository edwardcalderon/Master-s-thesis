#!/usr/bin/env python3
"""Fit a reduced map on selection data and evaluate it on held-out ABM runs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import platform
import statistics
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from abm import (
    DEFAULT_ABM_OUTPUT,
    make_noise_schedule,
    run_condition,
    validate as validate_abm,
)
from run import git_context, sha256_bytes


HERE = Path(__file__).resolve().parent
DEFAULT_CONFIRMATION_CONFIG = HERE / "h1c_config.json"
DEFAULT_MODEL_CONFIG = HERE / "abm_config.json"
def conditions_from_config(config: dict[str, Any]) -> tuple[tuple[str, float, bool], ...]:
    capacities = config["arbitrage_capacity_fractions"]
    return (
        ("E0-arb-off-static", float(capacities["off"]), False),
        ("E1-arb-low-static", float(capacities["low"]), False),
        ("E1-arb-high-static", float(capacities["high"]), False),
        ("E3-adaptive-lp-high-arb", float(capacities["high"]), True),
    )
FIT_FIELDS = [
    "condition",
    "lp_policy",
    "arbitrage_capacity_fraction",
    "transition_count",
    "a",
    "beta",
    "c",
    "rho",
    "alpha",
    "chi",
    "trace_A",
    "det_A",
    "spectral_radius",
    "schur_1",
    "schur_2",
    "schur_3",
    "schur_contractive",
    "r_squared_d",
    "rmse_d_selection",
    "r_squared_z",
    "rmse_z_selection",
]
CLASSIFICATION_FIELDS = [
    "shock_log_return",
    "condition",
    "schur_prediction",
    "contractive_count",
    "persistent_count",
    "contractive_rate",
    "wilson_95pct_low",
    "wilson_95pct_high",
    "observed_majority_label",
    "map_matches_observed_majority",
]
PREDICTION_FIELDS = [
    "shock_log_return",
    "condition",
    "seed_count",
    "transition_count",
    "rmse_d",
    "mean_signed_error_d",
    "rmse_z",
    "mean_signed_error_z",
]
SUMMARY_FIELDS = [
    "selection_run_id",
    "selection_transition_count",
    "confirmation_seed_start",
    "confirmation_seed_count",
    "confirmation_shocks",
    "condition_count",
    "classification_count",
    "classifications_not_mixed",
    "classification_agreement_count",
    "classification_agreement_rate",
    "mean_d_prediction_rmse",
    "mean_z_prediction_rmse",
    "selection_schur_stable_conditions",
    "interpretation_limit",
]


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, fields: list[str], rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def group_trajectories(
    rows: list[dict[str, str]],
) -> dict[tuple[float, int, str], list[dict[str, str]]]:
    grouped: dict[tuple[float, int, str], list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        key = (
            float(row["shock_log_return"]),
            int(row["seed"]),
            str(row["scenario"]),
        )
        grouped[key].append(row)
    for trajectory in grouped.values():
        trajectory.sort(key=lambda row: int(row["tick"]))
    return grouped


def transitions(
    grouped: dict[tuple[float, int, str], list[dict[str, str]]]
) -> dict[str, list[tuple[float, float, float, float, float]]]:
    result: dict[str, list[tuple[float, float, float, float, float]]] = defaultdict(list)
    for (_shock, _seed, condition), trajectory in grouped.items():
        for current, following in zip(trajectory, trajectory[1:]):
            d = float(current["excess_error"])
            z = float(current["normalized_net_buy_pressure_z"])
            u_next = float(following["cex_log_return"])
            d_next = float(following["excess_error"])
            z_next = float(following["normalized_net_buy_pressure_z"])
            result[condition].append((d, z, u_next, d_next, z_next))
    return result


def fit_two_predictors(
    x: list[float], z: list[float], target: list[float]
) -> dict[str, float | int | None]:
    if not (len(x) == len(z) == len(target)) or len(target) < 3:
        raise ValueError("OLS requires at least three aligned observations")
    sxx = sum(value * value for value in x)
    sxz = sum(a * b for a, b in zip(x, z))
    szz = sum(value * value for value in z)
    sxy = sum(a * b for a, b in zip(x, target))
    szy = sum(a * b for a, b in zip(z, target))
    determinant = sxx * szz - sxz * sxz
    if not math.isfinite(determinant) or abs(determinant) <= 1e-18:
        raise ValueError("reduced-map selection predictors are collinear or degenerate")
    first = (sxy * szz - szy * sxz) / determinant
    second = (szy * sxx - sxy * sxz) / determinant
    residuals = [y - first * a - second * b for a, b, y in zip(x, z, target)]
    rmse = math.sqrt(statistics.mean(value * value for value in residuals))
    target_mean = statistics.mean(target)
    total = sum((value - target_mean) ** 2 for value in target)
    residual_sum = sum(value * value for value in residuals)
    r_squared = 1.0 - residual_sum / total if total > 0.0 else None
    return {
        "first": first,
        "second": second,
        "rmse": rmse,
        "r_squared": r_squared,
        "n": len(target),
    }


def fit_condition(
    condition: str,
    values: list[tuple[float, float, float, float, float]],
    condition_meta: tuple[float, bool],
) -> tuple[dict[str, Any], dict[str, float]]:
    d = [item[0] for item in values]
    z = [item[1] for item in values]
    u_next = [item[2] for item in values]
    d_next_adjusted = [item[3] - item[2] for item in values]
    z_next = [item[4] for item in values]
    fit_d = fit_two_predictors(d, z, d_next_adjusted)
    fit_z = fit_two_predictors(d, z, z_next)
    a = float(fit_d["first"])
    beta = float(fit_d["second"])
    c = float(fit_z["first"])
    rho = float(fit_z["second"])
    trace = a + rho
    determinant = a * rho - beta * c
    schur_1 = 1.0 - determinant
    schur_2 = 1.0 - trace + determinant
    schur_3 = 1.0 + trace + determinant
    discriminant = trace * trace - 4.0 * determinant
    if discriminant >= 0.0:
        root = math.sqrt(discriminant)
        spectral_radius = max(abs((trace + root) / 2.0), abs((trace - root) / 2.0))
    else:
        spectral_radius = math.sqrt(max(determinant, 0.0))
    contractive = schur_1 > 0.0 and schur_2 > 0.0 and schur_3 > 0.0
    capacity, adaptive_lp = condition_meta
    model = {
        "a": a,
        "beta": beta,
        "c": c,
        "rho": rho,
        "trace": trace,
        "determinant": determinant,
        "spectral_radius": spectral_radius,
        "schur_1": schur_1,
        "schur_2": schur_2,
        "schur_3": schur_3,
        "schur_contractive": contractive,
    }
    fit_row = {
        "condition": condition,
        "lp_policy": "one-shot-threshold-withdrawal" if adaptive_lp else "static",
        "arbitrage_capacity_fraction": capacity,
        "transition_count": len(values),
        "a": a,
        "beta": beta,
        "c": c,
        "rho": rho,
        "alpha": 1.0 - a,
        "chi": -c,
        "trace_A": trace,
        "det_A": determinant,
        "spectral_radius": spectral_radius,
        "schur_1": schur_1,
        "schur_2": schur_2,
        "schur_3": schur_3,
        "schur_contractive": contractive,
        "r_squared_d": fit_d["r_squared"],
        "rmse_d_selection": fit_d["rmse"],
        "r_squared_z": fit_z["r_squared"],
        "rmse_z_selection": fit_z["rmse"],
    }
    return fit_row, model


def wilson_interval(successes: int, total: int, z_value: float) -> tuple[float, float]:
    if total <= 0:
        return 0.0, 1.0
    p = successes / total
    z2 = z_value * z_value
    denominator = 1.0 + z2 / total
    center = (p + z2 / (2.0 * total)) / denominator
    half = z_value * math.sqrt(
        p * (1.0 - p) / total + z2 / (4.0 * total * total)
    ) / denominator
    return max(0.0, center - half), min(1.0, center + half)


def analyze(
    selection_run_dir: Path,
    model_config_path: Path,
    analysis_config_path: Path,
    output_root: Path,
) -> Path:
    selection_meta_path = selection_run_dir / "run_metadata.json"
    selection_config_path = selection_run_dir / "config.json"
    selection_timeseries_path = selection_run_dir / "timeseries.csv"
    selection_meta = json.loads(selection_meta_path.read_text(encoding="utf-8"))
    if not all(path.is_file() for path in (selection_config_path, selection_timeseries_path)):
        raise ValueError("selection run directory is missing config or timeseries artifacts")

    abm_source = (HERE / "abm.py").read_bytes()
    mechanics_source = (HERE / "run.py").read_bytes()
    if selection_meta.get("abm_runner_sha256") != sha256_bytes(abm_source):
        raise ValueError("selection run was generated by a different ABM source version")
    if selection_meta.get("mechanics_runner_sha256") != sha256_bytes(mechanics_source):
        raise ValueError("selection run was generated by a different CPMM mechanics source")

    model_config_bytes = model_config_path.read_bytes()
    selection_model_config_bytes = selection_config_path.read_bytes()
    if model_config_bytes != selection_model_config_bytes:
        raise ValueError("current ABM config differs from the config copied into selection run")
    model_config = json.loads(selection_model_config_bytes)
    analysis_config_bytes = analysis_config_path.read_bytes()
    analysis_config = json.loads(analysis_config_bytes)
    validate_abm(model_config)

    selection_rows = read_rows(selection_timeseries_path)
    selection_groups = group_trajectories(selection_rows)
    selection_transitions = transitions(selection_groups)
    conditions = conditions_from_config(model_config)
    condition_metadata = {
        name: (capacity, adaptive) for name, capacity, adaptive in conditions
    }
    fits: list[dict[str, Any]] = []
    models: dict[str, dict[str, float]] = {}
    for condition, meta in condition_metadata.items():
        if condition not in selection_transitions:
            raise ValueError(f"selection data has no trajectories for {condition}")
        fit_row, model = fit_condition(condition, selection_transitions[condition], meta)
        fits.append(fit_row)
        models[condition] = model

    shocks = [float(value) for value in analysis_config["confirmation_shock_log_returns"]]
    seed_start = int(analysis_config["confirmation_seed_start"])
    seed_count = int(analysis_config["confirmation_seed_count"])
    early_start, early_end = [int(value) for value in analysis_config["early_error_window_ticks"]]
    late_start, late_end = [int(value) for value in analysis_config["late_error_window_ticks"]]
    majority_threshold = float(analysis_config["majority_contraction_threshold"])
    stability_threshold = float(analysis_config["map_schur_stability_threshold"])
    z_value = float(analysis_config["normal_approximation_z"])
    if seed_count <= 1 or seed_start < 0:
        raise ValueError("confirmation seed range must be nonnegative and contain at least two seeds")
    selection_seeds = {
        int(row["seed"]) for row in read_rows(selection_run_dir / "replication_seeds.csv")
    }
    confirmation_seeds = set(range(seed_start, seed_start + seed_count))
    if selection_seeds & confirmation_seeds:
        raise ValueError("selection and confirmation seed ranges overlap")
    if max(early_end, late_end) > int(model_config["horizon_ticks"]):
        raise ValueError("classification windows exceed the configured model horizon")

    trajectories: list[dict[str, Any]] = []
    confirmation_rows: list[dict[str, Any]] = []
    rmse_values: dict[tuple[float, str], dict[str, list[float]]] = defaultdict(
        lambda: {"d": [], "z": []}
    )
    actual_labels: dict[tuple[float, str], list[bool]] = defaultdict(list)

    for seed in sorted(confirmation_seeds):
        schedule = make_noise_schedule(model_config, seed)
        for shock in shocks:
            for condition, capacity, adaptive_lp in conditions:
                rows, summary = run_condition(
                    model_config,
                    shock,
                    seed,
                    condition,
                    capacity,
                    adaptive_lp,
                    schedule,
                )
                confirmation_rows.extend(rows)
                absolute_d_by_tick = {
                    int(row["tick"]): abs(float(row["excess_error"]))
                    for row in rows
                }
                early = [
                    absolute_d_by_tick[tick]
                    for tick in range(early_start, early_end + 1)
                ]
                late = [
                    absolute_d_by_tick[tick]
                    for tick in range(late_start, late_end + 1)
                ]
                actual_labels[(shock, condition)].append(
                    statistics.mean(late) < statistics.mean(early)
                )

                model = models[condition]
                for current, following in zip(rows, rows[1:]):
                    d = float(current["excess_error"])
                    z = float(current["normalized_net_buy_pressure_z"])
                    u_next = float(following["cex_log_return"])
                    predicted_d = model["a"] * d + model["beta"] * z + u_next
                    predicted_z = model["c"] * d + model["rho"] * z
                    rmse_values[(shock, condition)]["d"].append(
                        predicted_d - float(following["excess_error"])
                    )
                    rmse_values[(shock, condition)]["z"].append(
                        predicted_z - float(following["normalized_net_buy_pressure_z"])
                    )
                trajectories.append(
                    {
                        "shock_log_return": shock,
                        "condition": condition,
                        "seed": seed,
                        "maximum_absolute_log_error": summary[
                            "maximum_absolute_log_error"
                        ],
                        "mean_absolute_log_error": summary["mean_absolute_log_error"],
                        "early_mean_absolute_excess": statistics.mean(early),
                        "late_mean_absolute_excess": statistics.mean(late),
                        "observed_label": (
                            "contractive"
                            if statistics.mean(late) < statistics.mean(early)
                            else "persistent"
                        ),
                    }
                )

    classification: list[dict[str, Any]] = []
    prediction_rows: list[dict[str, Any]] = []
    z_threshold = stability_threshold
    for shock in shocks:
        for condition, _capacity, _adaptive in conditions:
            model = models[condition]
            labels = actual_labels[(shock, condition)]
            successes = sum(labels)
            rate = successes / len(labels)
            low, high = wilson_interval(successes, len(labels), z_value)
            observed = (
                "contractive"
                if rate > majority_threshold
                else "persistent"
                if rate < majority_threshold
                else "mixed"
            )
            predicted = (
                "contractive"
                if model["spectral_radius"] < z_threshold
                else "persistent"
            )
            classification.append(
                {
                    "shock_log_return": shock,
                    "condition": condition,
                    "schur_prediction": predicted,
                    "contractive_count": successes,
                    "persistent_count": len(labels) - successes,
                    "contractive_rate": rate,
                    "wilson_95pct_low": low,
                    "wilson_95pct_high": high,
                    "observed_majority_label": observed,
                    "map_matches_observed_majority": (
                        predicted == observed if observed != "mixed" else None
                    ),
                }
            )
            residual_d = rmse_values[(shock, condition)]["d"]
            residual_z = rmse_values[(shock, condition)]["z"]
            prediction_rows.append(
                {
                    "shock_log_return": shock,
                    "condition": condition,
                    "seed_count": seed_count,
                    "transition_count": len(residual_d),
                    "rmse_d": math.sqrt(statistics.mean(value * value for value in residual_d)),
                    "mean_signed_error_d": statistics.mean(residual_d),
                    "rmse_z": math.sqrt(statistics.mean(value * value for value in residual_z)),
                    "mean_signed_error_z": statistics.mean(residual_z),
                }
            )

    comparable = [
        row for row in classification if row["map_matches_observed_majority"] is not None
    ]
    agreement_count = sum(bool(row["map_matches_observed_majority"]) for row in comparable)
    agreement_rate = agreement_count / len(comparable) if comparable else None
    scenario_rmse_d = [float(row["rmse_d"]) for row in prediction_rows]
    scenario_rmse_z = [float(row["rmse_z"]) for row in prediction_rows]

    source = Path(__file__).read_bytes()
    run_hash = sha256_bytes(
        selection_timeseries_path.read_bytes()
        + selection_config_path.read_bytes()
        + model_config_bytes
        + analysis_config_bytes
        + source
        + abm_source
        + mechanics_source
    )[:12]
    run_id = f"cex-dex-h1c-{run_hash}"
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)
    (run_dir / "h1c_config.json").write_bytes(analysis_config_bytes)
    (run_dir / "abm_config.json").write_bytes(model_config_bytes)
    write_csv(run_dir / "map_fits.csv", FIT_FIELDS, fits)
    write_csv(run_dir / "classification.csv", CLASSIFICATION_FIELDS, classification)
    write_csv(run_dir / "prediction_errors.csv", PREDICTION_FIELDS, prediction_rows)
    write_csv(run_dir / "confirmation_trajectories.csv", list(trajectories[0]), trajectories)
    confirmation_fields = list(confirmation_rows[0])
    write_csv(run_dir / "confirmation_timeseries.csv", confirmation_fields, confirmation_rows)
    summary = {
        "selection_run_id": selection_meta["run_id"],
        "selection_transition_count": sum(int(row["transition_count"]) for row in fits),
        "confirmation_seed_start": seed_start,
        "confirmation_seed_count": seed_count,
        "confirmation_shocks": shocks,
        "condition_count": len(conditions),
        "classification_count": len(classification),
        "classifications_not_mixed": len(comparable),
        "classification_agreement_count": agreement_count,
        "classification_agreement_rate": agreement_rate,
        "mean_d_prediction_rmse": statistics.mean(scenario_rmse_d),
        "mean_z_prediction_rmse": statistics.mean(scenario_rmse_z),
        "selection_schur_stable_conditions": sum(
            bool(row["schur_contractive"]) for row in fits
        ),
        "interpretation_limit": (
            "held-out shock magnitude and random streams under the same representative-agent rules; "
            "not generalization to new policies, fee regimes, capacity levels, or live markets"
        ),
    }
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")

    artifacts = (
        "h1c_config.json",
        "abm_config.json",
        "map_fits.csv",
        "classification.csv",
        "prediction_errors.csv",
        "confirmation_trajectories.csv",
        "confirmation_timeseries.csv",
        "summary.json",
    )
    metadata = {
        "run_id": run_id,
        "analysis_version": analysis_config["analysis_version"],
        "abm_model_version": model_config["model_version"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "selection_run_id": selection_meta["run_id"],
        "selection_timeseries_sha256": hashlib.sha256(
            selection_timeseries_path.read_bytes()
        ).hexdigest(),
        "selection_config_sha256": sha256_bytes(selection_config_path.read_bytes()),
        "confirmation_config_sha256": sha256_bytes(model_config_bytes),
        "h1c_config_sha256": sha256_bytes(analysis_config_bytes),
        "h1c_runner_sha256": sha256_bytes(source),
        "abm_runner_sha256": sha256_bytes(abm_source),
        "mechanics_runner_sha256": sha256_bytes(mechanics_source),
        "selection_shocks": selection_meta.get("shock_conditions"),
        "confirmation_shocks": shocks,
        "selection_seeds": sorted(selection_seeds),
        "confirmation_seeds": sorted(confirmation_seeds),
        "selection_and_confirmation_disjoint": not bool(selection_seeds & confirmation_seeds),
        "map_state_definition": "signed excess error and normalized quote-valued net trader buy pressure",
        "map_input_definition": "CEX log return; coefficient constrained to 1 in the d equation",
        "classification_rule": "Schur stable iff all 2x2 inequalities hold; ABM contraction iff mean |d| at ticks 16-20 is below ticks 1-5",
        "interval_method": "Wilson interval for held-out contraction share; normal approximation for mean contrasts in the upstream selection run",
        "confirmation_is_held_out": True,
        **git_context(),
        "artifact_sha256": {
            name: sha256_bytes((run_dir / name).read_bytes()) for name in artifacts
        },
    }
    (run_dir / "run_metadata.json").write_text(
        json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
    )
    return run_dir


def find_latest_selection_run(root: Path) -> Path:
    candidates: list[tuple[str, Path]] = []
    for path in root.glob("cex-dex-abm-*"):
        metadata_path = path / "run_metadata.json"
        if not metadata_path.is_file() or not (path / "timeseries.csv").is_file():
            continue
        try:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        candidates.append((str(metadata.get("generated_at_utc", "")), path))
    if not candidates:
        raise FileNotFoundError(f"no stochastic ABM selection run found under {root}")
    return max(candidates, key=lambda item: item[0])[1]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--selection-run-dir", type=Path)
    parser.add_argument("--model-config", type=Path, default=DEFAULT_MODEL_CONFIG)
    parser.add_argument("--analysis-config", type=Path, default=DEFAULT_CONFIRMATION_CONFIG)
    parser.add_argument("--output", type=Path, default=HERE / "output" / "h1c")
    args = parser.parse_args()
    selection_dir = args.selection_run_dir or find_latest_selection_run(DEFAULT_ABM_OUTPUT)
    run_dir = analyze(
        selection_dir.resolve(),
        args.model_config.resolve(),
        args.analysis_config.resolve(),
        args.output.resolve(),
    )
    print(f"Wrote held-out H1c map evaluation to {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

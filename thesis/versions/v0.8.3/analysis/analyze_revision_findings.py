#!/usr/bin/env python3
"""Reproduce H1/H2 summaries and the exploratory nominal flow-capacity check.

This script summarizes archived runs only; it does not rerun the simulator or
turn the post-hoc pressure ratio into a confirmatory hypothesis.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
from collections import defaultdict
from pathlib import Path
from statistics import mean


HERE = Path(__file__).resolve().parent
DEFAULT_CONFIRM = HERE / "output/confirm/cex-dex-confirm-5b06486d695e/run_metrics.csv"
DEFAULT_ENGINEERING = HERE / "output/release-0.1.9/engineering/cex-dex-engineering-9438e194aa7e/run_metrics.csv"
DEFAULT_MODEL = HERE / "output/confirm/cex-dex-confirm-5b06486d695e/model_config.json"
DEFAULT_ENGINEERING_CONFIG = HERE / "output/release-0.1.9/engineering/cex-dex-engineering-9438e194aa7e/abm_config.json"
DEFAULT_OUTPUT = HERE.parents[1] / "thesis/figures/data"
REPOSITORY_ROOT = HERE.parents[1]


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def portable_path(path: Path) -> str:
    """Keep manifests reproducible without recording workstation-specific paths."""
    try:
        return path.resolve().relative_to(REPOSITORY_ROOT).as_posix()
    except ValueError:
        return "<external-input>/" + path.name


def as_bool(value: str) -> bool:
    return value.strip().casefold() in {"1", "true", "yes"}


def write_csv(path: Path, rows: list[dict[str, object]]) -> None:
    if not rows:
        raise ValueError(f"No rows to write to {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def quantile(sorted_values: list[float], probability: float) -> float:
    position = (len(sorted_values) - 1) * probability
    lower = math.floor(position)
    upper = math.ceil(position)
    weight = position - lower
    return sorted_values[lower] * (1.0 - weight) + sorted_values[upper] * weight


def bootstrap_interval(values: list[float], draws: int, seed: int) -> tuple[float, float]:
    rng = random.Random(seed)
    n = len(values)
    means = sorted(mean(values[rng.randrange(n)] for _ in range(n)) for _ in range(draws))
    return quantile(means, 0.025), quantile(means, 0.975)


def wilson_interval(successes: int, trials: int) -> tuple[float, float]:
    """95% Wilson interval for a simulated binary outcome rate."""
    if trials <= 0:
        raise ValueError("Wilson interval requires at least one trial")
    z = 1.959963984540054
    p = successes / trials
    denominator = 1.0 + z * z / trials
    center = (p + z * z / (2.0 * trials)) / denominator
    half_width = z * math.sqrt(p * (1.0 - p) / trials + z * z / (4.0 * trials * trials)) / denominator
    return max(0.0, center - half_width), min(1.0, center + half_width)


def build_h1(confirm_rows: list[dict[str, str]], model: dict) -> list[dict[str, object]]:
    band = float(model["no_arbitrage_band_log"])
    capacities = {
        "E1-arb-low-static": 0.005,
        "E1-arb-high-static": 0.03,
    }
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in confirm_rows:
        if row["condition"] in capacities:
            groups[(row["condition"], row["depth_scale"], row["shock_log_return"])].append(row)

    result = []
    for (condition, depth, shock_text), group in sorted(
        groups.items(), key=lambda item: (capacities[item[0][0]], float(item[0][2]), float(item[0][1]))
    ):
        capacity = capacities[condition]
        shock = float(shock_text)
        excess = max(abs(shock) - band, 0.0)
        correction = 2.0 * math.log1p(capacity)
        ideal_ticks = math.ceil(excess / correction) if excess > 0.0 else 0
        by_ideal_count = sum(int(row["return_tick_censored"]) <= ideal_ticks for row in group)
        by_horizon_count = sum(as_bool(row["recovered"]) for row in group)
        ideal_low, ideal_high = wilson_interval(by_ideal_count, len(group))
        horizon_low, horizon_high = wilson_interval(by_horizon_count, len(group))
        result.append({
            "condition": condition,
            "capacity_fraction": capacity,
            "shock_log_return": shock,
            "ideal_first_entry_ticks": ideal_ticks,
            "depth_scale": float(depth),
            "simulated_sustained_return_by_ideal_tick": by_ideal_count / len(group),
            "simulated_sustained_return_by_ideal_tick_wilson95_low": ideal_low,
            "simulated_sustained_return_by_ideal_tick_wilson95_high": ideal_high,
            "simulated_sustained_return_by_tick_20": by_horizon_count / len(group),
            "simulated_sustained_return_by_tick_20_wilson95_low": horizon_low,
            "simulated_sustained_return_by_tick_20_wilson95_high": horizon_high,
            "runs": len(group),
            "simulated_return_definition": "start tick of first two consecutive post-arbitrage observations inside the band; compared with ideal first-entry deadline",
        })
    return result


def build_h2(
    confirm_rows: list[dict[str, str]], draws: int, seed: int
) -> list[dict[str, object]]:
    metric = "peak_abs_log_error"
    index = {
        (row["condition"], row["seed"], row["depth_scale"], row["shock_log_return"]): float(row[metric])
        for row in confirm_rows
    }
    seeds = sorted({row["seed"] for row in confirm_rows})
    cells = sorted(
        {(row["depth_scale"], row["shock_log_return"]) for row in confirm_rows},
        key=lambda cell: (float(cell[0]), float(cell[1])),
    )
    result = []
    seed_deltas_by_cell: dict[tuple[str, str], list[float]] = {}
    for cell_index, (depth, shock) in enumerate(cells):
        deltas = [
            index[("E3-adaptive-lp-high-arb", seed_id, depth, shock)]
            - index[("E1-arb-high-static", seed_id, depth, shock)]
            for seed_id in seeds
        ]
        # Values below numerical precision are equality, not a meaningful effect.
        deltas = [0.0 if abs(value) < 1e-12 else value for value in deltas]
        seed_deltas_by_cell[(depth, shock)] = deltas
        lower, upper = bootstrap_interval(deltas, draws, seed + cell_index)
        result.append({
            "scope": "cell",
            "depth_scale": float(depth),
            "shock_log_return": float(shock),
            "metric": "maximum absolute post-arbitrage log tracking error",
            "contrast": "E3 threshold withdrawal minus E1 high-capacity static",
            "mean_paired_difference": mean(deltas),
            "bootstrap_ci95_low": lower,
            "bootstrap_ci95_high": upper,
            "seed_count": len(deltas),
            "interpretation": "post-hoc exploratory secondary outcome; the registered H2 contrast used legacy max_response",
        })

    overall = [mean(seed_deltas_by_cell[cell][index_seed] for cell in cells) for index_seed in range(len(seeds))]
    lower, upper = bootstrap_interval(overall, draws, seed + len(cells))
    result.append({
        "scope": "all_cells_equal_weight",
        "depth_scale": "all",
        "shock_log_return": "all",
        "metric": "maximum absolute post-arbitrage log tracking error",
        "contrast": "E3 threshold withdrawal minus E1 high-capacity static",
        "mean_paired_difference": mean(overall),
        "bootstrap_ci95_low": lower,
        "bootstrap_ci95_high": upper,
        "seed_count": len(overall),
        "interpretation": "post-hoc exploratory secondary outcome; seed is the resampling unit and cells are equally weighted within seed",
    })
    return result


def build_pressure(
    engineering_rows: list[dict[str, str]],
    engineering_config: dict,
) -> list[dict[str, object]]:
    initial_x = float(engineering_config["initial_reserve_x"])
    q_noise = initial_x * float(engineering_config["noise_trader"]["order_fraction_of_initial_reserve"])
    q_trend = initial_x * float(engineering_config["trend_panic_trader"]["trend_order_fraction_of_initial_reserve"])
    nominal_same_side_input = q_noise + q_trend
    remaining_after_withdrawal = float(engineering_config["liquidity_provider"]["remaining_reserve_fraction"])
    capacities = {
        "E1-arb-low-static": 0.005,
        "E1-arb-high-static": 0.03,
        "E3-adaptive-lp-high-arb": 0.03,
    }
    groups: dict[tuple[str, str, str], list[dict[str, str]]] = defaultdict(list)
    for row in engineering_rows:
        if row["variant"] == "fixed_orders" and row["condition"] in capacities:
            groups[(row["condition"], row["depth_scale"], row["shock_log_return"])].append(row)

    noise_probability = float(engineering_config["noise_trader"]["activity_probability"])
    result = []
    for (condition, depth_text, shock_text), group in sorted(
        groups.items(), key=lambda item: (item[0][0], float(item[0][1]), float(item[0][2]))
    ):
        depth = float(depth_text)
        capacity = capacities[condition]
        reserve_fraction = remaining_after_withdrawal if condition == "E3-adaptive-lp-high-arb" else 1.0
        nominal_reserve = initial_x * depth * reserve_fraction
        same_direction_log_impact = 2.0 * math.log1p(nominal_same_side_input / nominal_reserve)
        max_capacity_log_correction = 2.0 * math.log1p(capacity)
        recovered = [row for row in group if as_bool(row["recovered"])]
        departures = sum(as_bool(row["later_departure"]) for row in recovered)
        result.append({
            "variant": "fixed_orders",
            "condition": condition,
            "depth_scale": depth,
            "shock_log_return": float(shock_text),
            "capacity_fraction": capacity,
            "nominal_same_direction_flow_input": nominal_same_side_input,
            "nominal_reserve_scale": nominal_reserve,
            "nominal_flow_log_impact": same_direction_log_impact,
            "maximum_capacity_log_correction": max_capacity_log_correction,
            "R_nominal": same_direction_log_impact / max_capacity_log_correction,
            "noise_activity_probability": noise_probability,
            "recovery_by_tick_20": sum(as_bool(row["recovered_by_20"]) for row in group) / len(group),
            "later_departure_given_recovery": departures / len(recovered) if recovered else "",
            "recovered_runs": len(recovered),
            "later_departure_runs": departures,
            "runs": len(group),
            "assumption": "same-direction 40+60 input on active noise ticks; nominal initial reserve scale; no fee; E3 reserves approximated after 45% withdrawal",
        })
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--confirm-csv", type=Path, default=DEFAULT_CONFIRM)
    parser.add_argument("--engineering-csv", type=Path, default=DEFAULT_ENGINEERING)
    parser.add_argument("--model-json", type=Path, default=DEFAULT_MODEL)
    parser.add_argument("--engineering-config-json", type=Path, default=DEFAULT_ENGINEERING_CONFIG)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--bootstrap-resamples", type=int, default=10_000)
    parser.add_argument("--bootstrap-seed", type=int, default=20_261_123)
    args = parser.parse_args()

    model = json.loads(args.model_json.read_text(encoding="utf-8"))
    engineering_config = json.loads(args.engineering_config_json.read_text(encoding="utf-8"))
    confirm_rows = read_csv(args.confirm_csv)
    engineering_rows = read_csv(args.engineering_csv)

    outputs = {
        "h1_ideal_vs_simulated.csv": build_h1(confirm_rows, model),
        "h2_peak_tracking_error.csv": build_h2(confirm_rows, args.bootstrap_resamples, args.bootstrap_seed),
        "pressure_ratio_diagnostic.csv": build_pressure(engineering_rows, engineering_config),
    }
    for name, rows in outputs.items():
        destination = args.output_dir / name
        write_csv(destination, rows)
        print(f"wrote {len(rows)} rows: {destination}")

    manifest = {
        "analysis": "manuscript-v0.8.3-critical-findings-review",
        "script": portable_path(Path(__file__)),
        "script_sha256": sha256_file(Path(__file__).resolve()),
        "source_runs": {
            "held_out_confirmation": "cex-dex-confirm-5b06486d695e",
            "engineering_sensitivity": "cex-dex-engineering-9438e194aa7e",
        },
        "inputs": {
            "confirm_csv": {"path": portable_path(args.confirm_csv), "sha256": sha256_file(args.confirm_csv)},
            "engineering_csv": {"path": portable_path(args.engineering_csv), "sha256": sha256_file(args.engineering_csv)},
            "model_json": {"path": portable_path(args.model_json), "sha256": sha256_file(args.model_json)},
            "engineering_config_json": {"path": portable_path(args.engineering_config_json), "sha256": sha256_file(args.engineering_config_json)},
        },
        "procedure": {
            "bootstrap_resamples": args.bootstrap_resamples,
            "bootstrap_seed": args.bootstrap_seed,
            "h1_rate_intervals": "95% Wilson intervals for simulated binary return rates",
            "h2_resampling_unit": "paired seed; equally weighted design cells in the aggregate",
            "pressure_ratio_status": "post-hoc nominal diagnostic, not a fitted or validated threshold",
            "simulation_rerun": False,
        },
        "outputs": {
            name: {"rows": len(rows), "sha256": sha256_file(args.output_dir / name)}
            for name, rows in outputs.items()
        },
        "limitations": [
            "All estimates remain conditional on the archived synthetic model and its configured event schedule.",
            "The H2 peak-error measure is post-hoc and records end-of-tick states only.",
            "The nominal pressure ratio assumes same-direction configured orders and approximate post-withdrawal reserves.",
            "No market-data validation or new simulation experiment is included in this summary analysis.",
        ],
    }
    manifest_path = args.output_dir / "revision_findings_manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote analysis manifest: {manifest_path}")


if __name__ == "__main__":
    main()

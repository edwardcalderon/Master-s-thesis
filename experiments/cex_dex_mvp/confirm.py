"""Confirmatory protocol for H1, H2 and H3 (manuscript 2026-11-23, chapters 4-7).

Stage 1 (exploration): simulate seeds/cells that never enter the confirmation stage and fit,
for every condition, the two-state map (d, z) and the scalar AR baseline.
Stage 2 (confirmation): freeze those coefficients, simulate disjoint seeds on a design with
new depth and shock levels, and compute

* H1: excess area A = sum_{t=ts}^{ts+H} D_t and Delta1 = A(arbitrage high) - A(arbitrage off),
* H2: maximum response M = max |log(pD_t / pD_{ts-1})| and Delta2 = M(adaptive LP) - M(static LP),
* H3: one-step mean absolute error of the map versus persistence and a scalar AR baseline, on
  held-out (depth, shock) cells only.

Inference treats the seed as the independent replicate (outcomes are averaged over design cells
within a seed), uses percentile paired bootstrap intervals, one-sided sign-flip randomization
tests and Holm's correction over the three primary tests. Return times are right-censored.
"""

from __future__ import annotations

import argparse
import copy
import csv
import json
import math
import platform
import random
import statistics
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from abm import make_noise_schedule, run_condition, validate as validate_abm
from run import git_context, sha256_bytes


HERE = Path(__file__).resolve().parent
DEFAULT_CONFIRM_CONFIG = HERE / "confirm_config.json"
DEFAULT_MODEL_CONFIG = HERE / "abm_config.json"
DEFAULT_OUTPUT = HERE / "output" / "confirm"


def fit_two_predictors(
    x: list[float], z: list[float], target: list[float]
) -> dict[str, float]:
    """No-intercept OLS on two predictors; falls back to the second predictor alone if x is numerically zero."""
    sxx = sum(v * v for v in x)
    szz = sum(v * v for v in z)
    sxz = sum(a * b for a, b in zip(x, z))
    sxy = sum(a * b for a, b in zip(x, target))
    szy = sum(a * b for a, b in zip(z, target))
    if szz <= 0.0:
        raise ValueError("second predictor is identically zero")
    if sxx <= 1e-12 * szz or sxx * szz - sxz * sxz <= 1e-10 * sxx * szz:
        return {"first": 0.0, "second": szy / szz, "degenerate": True}
    det = sxx * szz - sxz * sxz
    return {"first": (sxy * szz - szy * sxz) / det, "second": (szy * sxx - sxy * sxz) / det, "degenerate": False}


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str] | None = None) -> None:
    fields = fields or (list(rows[0].keys()) if rows else [])
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def scaled_config(config: dict[str, Any], depth_scale: float) -> dict[str, Any]:
    scaled = copy.deepcopy(config)
    scaled["initial_reserve_x"] = float(config["initial_reserve_x"]) * depth_scale
    scaled["initial_reserve_y"] = float(config["initial_reserve_y"]) * depth_scale
    # Order sizes keep their absolute size (fractions are of the reserve), so depth changes impact.
    scaled["noise_trader"]["order_fraction_of_initial_reserve"] = (
        float(config["noise_trader"]["order_fraction_of_initial_reserve"]) / depth_scale
    )
    trend = scaled["trend_panic_trader"]
    for key in ("trend_order_fraction_of_initial_reserve", "panic_sell_fraction_of_initial_reserve"):
        trend[key] = float(config["trend_panic_trader"][key]) / depth_scale
    return scaled


def transitions(rows: list[dict[str, Any]]) -> list[tuple[float, float, float, float]]:
    """(d_t, z_t, u_{t+1}, d_{t+1}) with u = minus the CEX log return applied at t+1."""
    result = []
    for current, following in zip(rows, rows[1:]):
        result.append(
            (
                float(current["excess_error"]),
                float(current["normalized_net_buy_pressure_z"]),
                -float(following["cex_log_return"]),
                float(following["excess_error"]),
            )
        )
    return result


def fit_models(
    samples: list[tuple[float, float, float, float]]
) -> dict[str, float]:
    d = [s[0] for s in samples]
    z = [s[1] for s in samples]
    target_d = [s[3] - s[2] for s in samples]
    fit_d = fit_two_predictors(d, z, target_d)
    # z-equation has no input; target is z_{t+1}, which is the z of the next transition.
    return {"a": float(fit_d["first"]), "beta": float(fit_d["second"]), "n": len(samples), "degenerate_d": bool(fit_d["degenerate"])}


def fit_z_equation(
    pairs: list[tuple[float, float, float]]
) -> dict[str, float]:
    d = [p[0] for p in pairs]
    z = [p[1] for p in pairs]
    z_next = [p[2] for p in pairs]
    fit = fit_two_predictors(d, z, z_next)
    return {"c": float(fit["first"]), "rho": float(fit["second"])}


def schur(a: float, beta: float, c: float, rho: float) -> dict[str, Any]:
    trace = a + rho
    det = a * rho - beta * c
    s1 = 1.0 - det
    s2 = 1.0 - trace + det
    s3 = 1.0 + trace + det
    disc = trace * trace - 4.0 * det
    if disc >= 0.0:
        root = math.sqrt(disc)
        radius = max(abs((trace + root) / 2.0), abs((trace - root) / 2.0))
    else:
        radius = math.sqrt(max(det, 0.0))
    return {
        "trace": trace,
        "det": det,
        "spectral_radius": radius,
        "schur_stable": s1 > 0.0 and s2 > 0.0 and s3 > 0.0,
    }


def scalar_ar(samples: list[tuple[float, float, float, float]]) -> float:
    num = sum(s[0] * (s[3] - s[2]) for s in samples)
    den = sum(s[0] * s[0] for s in samples)
    return num / den if den > 0.0 else 0.0


def run_metrics(
    rows: list[dict[str, Any]],
    summary: dict[str, Any],
    window: tuple[int, int],
    band: float,
    models: dict[str, float] | None,
) -> dict[str, Any]:
    start, end = window
    by_tick = {int(r["tick"]): r for r in rows}
    area = sum(abs(float(by_tick[t]["excess_error"])) for t in range(start, end + 1))
    base_price = float(by_tick[start - 1]["dex_price"])
    max_response = max(
        abs(math.log(float(by_tick[t]["dex_price"]) / base_price)) for t in range(start, end + 1)
    )
    return_tick = summary["sustained_return_tick"]
    horizon = end
    metrics: dict[str, Any] = {
        "excess_area": area,
        "max_response": max_response,
        "recovered": return_tick is not None,
        "return_tick_censored": int(return_tick) if return_tick is not None else horizon + 1,
        "minimum_depth": summary["minimum_geometric_depth"],
        "lp_withdrawal_applied": bool(summary["lp_withdrawal_applied"]),
        "capital_limited_orders": summary["capital_limited_orders"],
        "peak_abs_log_error": summary["maximum_absolute_log_error"],
    }
    if models is not None:
        errors = {"map": [], "persistence": [], "scalar_ar": []}
        for d, z, u_next, d_next in transitions(rows):
            errors["map"].append(abs(models["a"] * d + models["beta"] * z + u_next - d_next))
            errors["persistence"].append(abs(d + u_next - d_next))
            errors["scalar_ar"].append(abs(models["a_scalar"] * d + u_next - d_next))
        for name, values in errors.items():
            metrics[f"mae_{name}"] = statistics.mean(values)
        early = [abs(float(by_tick[t]["excess_error"])) for t in range(1, 6)]
        late = [abs(float(by_tick[t]["excess_error"])) for t in range(16, 21)]
        if max(early) < 1e-9 and max(late) < 1e-9:
            label = "in-band"
        else:
            label = "contractive" if statistics.mean(late) < statistics.mean(early) else "persistent"
        metrics["observed_label"] = label
    return metrics


def bootstrap_ci(
    values: list[float], resamples: int, level: float, rng: random.Random
) -> tuple[float, float]:
    n = len(values)
    means = []
    for _ in range(resamples):
        total = 0.0
        for _j in range(n):
            total += values[rng.randrange(n)]
        means.append(total / n)
    means.sort()
    lower = means[int(((1.0 - level) / 2.0) * resamples)]
    upper = means[min(int((1.0 - (1.0 - level) / 2.0) * resamples), resamples - 1)]
    return lower, upper


def sign_flip_p(
    values: list[float], direction: str, draws: int, rng: random.Random
) -> float:
    observed = statistics.mean(values)
    count = 0
    n = len(values)
    for _ in range(draws):
        total = 0.0
        for v in values:
            total += v if rng.random() < 0.5 else -v
        stat = total / n
        if direction == "negative" and stat <= observed:
            count += 1
        elif direction == "positive" and stat >= observed:
            count += 1
    return (1.0 + count) / (1.0 + draws)


def holm(p_values: dict[str, float], alpha: float) -> dict[str, dict[str, Any]]:
    order = sorted(p_values, key=p_values.get)
    m = len(order)
    result: dict[str, dict[str, Any]] = {}
    running = 0.0
    rejecting = True
    for rank, name in enumerate(order):
        adjusted = min(1.0, (m - rank) * p_values[name])
        running = max(running, adjusted)
        rejecting = rejecting and p_values[name] <= alpha / (m - rank)
        result[name] = {"p_one_sided": p_values[name], "p_holm": running, "reject_holm": rejecting}
    return result


def half_width_and_n(values: list[float], target: float) -> dict[str, float]:
    s = statistics.stdev(values)
    return {
        "sd_delta": s,
        "required_n_for_target": math.ceil((1.96 * s / target) ** 2),
        "achieved_half_width": 1.96 * s / math.sqrt(len(values)),
        "target_half_width": target,
    }


def execute(model_config_path: Path, confirm_config_path: Path, output_root: Path) -> Path:
    model_bytes = model_config_path.read_bytes()
    confirm_bytes = confirm_config_path.read_bytes()
    model = json.loads(model_bytes)
    cfg = json.loads(confirm_bytes)
    validate_abm(model)
    band = float(model["no_arbitrage_band_log"])
    window = tuple(int(v) for v in cfg["response_window_ticks"])
    explore = cfg["exploration"]
    confirm = cfg["confirmation"]
    seeds_e = set(range(int(explore["seed_start"]), int(explore["seed_start"]) + int(explore["seed_count"])))
    seeds_c = set(range(int(confirm["seed_start"]), int(confirm["seed_start"]) + int(confirm["seed_count"])))
    if seeds_e & seeds_c:
        raise ValueError("exploration and confirmation seeds overlap")
    conditions = {
        name: (float(spec["capacity"]), bool(spec["adaptive_lp"]), str(spec["region"]))
        for name, spec in cfg["conditions"].items()
    }
    sources = [Path(__file__).read_bytes(), (HERE / "abm.py").read_bytes(), (HERE / "run.py").read_bytes(), (HERE / "h1c.py").read_bytes()]
    run_id = "cex-dex-confirm-" + sha256_bytes(model_bytes + confirm_bytes + b"".join(sources))[:12]
    run_dir = output_root / run_id
    run_dir.mkdir(parents=True, exist_ok=True)

    # ---- Stage 1: exploration and map fitting --------------------------------------------
    explore_samples: dict[str, list[tuple[float, float, float, float]]] = {n: [] for n in conditions}
    explore_z_pairs: dict[str, list[tuple[float, float, float]]] = {n: [] for n in conditions}
    explore_cells = {
        (float(scale), float(shock))
        for scale in explore["depth_scales"]
        for shock in explore["shock_log_returns"]
    }
    explore_metrics: list[dict[str, Any]] = []
    for seed in sorted(seeds_e):
        for scale, shock in sorted(explore_cells):
            cell_config = scaled_config(model, scale)
            schedule = make_noise_schedule(cell_config, seed)
            for name, (capacity, adaptive, _region) in conditions.items():
                rows, summary = run_condition(cell_config, shock, seed, name, capacity, adaptive, schedule)
                tr = transitions(rows)
                explore_samples[name].extend(tr)
                for current, following in zip(rows, rows[1:]):
                    explore_z_pairs[name].append(
                        (
                            float(current["excess_error"]),
                            float(current["normalized_net_buy_pressure_z"]),
                            float(following["normalized_net_buy_pressure_z"]),
                        )
                    )
                m = run_metrics(rows, summary, window, band, None)
                explore_metrics.append({"stage": "exploration", "condition": name, "seed": seed,
                                        "depth_scale": scale, "shock_log_return": shock,
                                        **{k: m[k] for k in ("excess_area", "max_response", "recovered", "lp_withdrawal_applied")}})
    fitted: dict[str, dict[str, float]] = {}
    fit_rows: list[dict[str, Any]] = []
    for name in conditions:
        main = fit_models(explore_samples[name])
        zeq = fit_z_equation(explore_z_pairs[name])
        a_scalar = scalar_ar(explore_samples[name])
        stability = schur(main["a"], main["beta"], zeq["c"], zeq["rho"])
        fitted[name] = {"a": main["a"], "beta": main["beta"], "c": zeq["c"], "rho": zeq["rho"], "a_scalar": a_scalar, **stability}
        fit_rows.append({"condition": name, "region": conditions[name][2], "transitions": main["n"],
                         "a": main["a"], "beta": main["beta"], "c": zeq["c"], "rho": zeq["rho"],
                         "degenerate_d_equation": main["degenerate_d"], "alpha": 1.0 - main["a"], "chi": -zeq["c"], "a_scalar_ar": a_scalar, **stability})

    # ---- Stage 2: frozen-model confirmation -----------------------------------------------
    cells = [(float(s), float(k)) for s in confirm["depth_scales"] for k in confirm["shock_log_returns"]]
    heldout = [c for c in cells if c not in explore_cells]
    records: list[dict[str, Any]] = []
    for seed in sorted(seeds_c):
        for scale, shock in cells:
            cell_config = scaled_config(model, scale)
            schedule = make_noise_schedule(cell_config, seed)
            for name, (capacity, adaptive, region) in conditions.items():
                rows, summary = run_condition(cell_config, shock, seed, name, capacity, adaptive, schedule)
                m = run_metrics(rows, summary, window, band, fitted[name])
                records.append({"condition": name, "region": region, "seed": seed, "depth_scale": scale,
                                "shock_log_return": shock, "heldout_cell": (scale, shock) in heldout, **m})
    index = {(r["condition"], r["seed"], r["depth_scale"], r["shock_log_return"]): r for r in records}

    def seed_deltas(first: str, second: str, metric: str) -> list[float]:
        values = []
        for seed in sorted(seeds_c):
            diffs = [float(index[(first, seed, s, k)][metric]) - float(index[(second, seed, s, k)][metric]) for s, k in cells]
            values.append(statistics.mean(diffs))
        return values

    primary = [n for n, (_c, _a, region) in conditions.items() if region == "primary"]
    h3_by_seed: list[float] = []
    h3_ar_by_seed: list[float] = []
    for seed in sorted(seeds_c):
        diffs = [float(index[(n, seed, s, k)]["mae_map"]) - float(index[(n, seed, s, k)]["mae_persistence"]) for n in primary for s, k in heldout]
        h3_by_seed.append(statistics.mean(diffs))
        diffs_ar = [float(index[(n, seed, s, k)]["mae_map"]) - float(index[(n, seed, s, k)]["mae_scalar_ar"]) for n in primary for s, k in heldout]
        h3_ar_by_seed.append(statistics.mean(diffs_ar))

    contrasts = cfg["contrasts"]
    series = {
        "H1_primary": seed_deltas(contrasts["H1_primary"]["first"], contrasts["H1_primary"]["second"], "excess_area"),
        "H1_capacity": seed_deltas(contrasts["H1_capacity"]["first"], contrasts["H1_capacity"]["second"], "excess_area"),
        "H2_primary": seed_deltas(contrasts["H2_primary"]["first"], contrasts["H2_primary"]["second"], "max_response"),
        "H3_map_vs_persistence": h3_by_seed,
        "H3_map_vs_scalar_ar": h3_ar_by_seed,
    }
    directions = {"H1_primary": "negative", "H1_capacity": "negative", "H2_primary": "positive",
                  "H3_map_vs_persistence": "negative", "H3_map_vs_scalar_ar": "negative"}
    inference_cfg = cfg["inference"]
    rng = random.Random(int(inference_cfg["rng_seed"]))
    resamples = int(inference_cfg["bootstrap_resamples"])
    draws = int(inference_cfg["randomization_draws"])
    level = float(inference_cfg["confidence_level"])
    stats_rows: list[dict[str, Any]] = []
    p_values: dict[str, float] = {}
    for name, values in series.items():
        low, high = bootstrap_ci(values, resamples, level, rng)
        p = sign_flip_p(values, directions[name], draws, rng)
        consistent = sum(1 for v in values if (v < 0 if directions[name] == "negative" else v > 0)) / len(values)
        stats_rows.append({"contrast": name, "direction_predicted": directions[name], "seed_count": len(values),
                           "mean_delta": statistics.mean(values), "median_delta": statistics.median(values),
                           "ci95_low": low, "ci95_high": high, "p_one_sided_randomization": p,
                           "share_of_seeds_in_predicted_direction": consistent})
        if name in inference_cfg["primary_tests"]:
            p_values[name] = p
    holm_result = holm(p_values, 0.05)
    for row in stats_rows:
        extra = holm_result.get(row["contrast"])
        row["primary_test"] = extra is not None
        row["p_holm"] = extra["p_holm"] if extra else None
        row["reject_null_holm_0.05"] = extra["reject_holm"] if extra else None

    # Cell breakdown (descriptive, exploratory).
    cell_rows: list[dict[str, Any]] = []
    for scale, shock in cells:
        for label, first, second, metric in (
            ("H1_primary", contrasts["H1_primary"]["first"], contrasts["H1_primary"]["second"], "excess_area"),
            ("H1_capacity", contrasts["H1_capacity"]["first"], contrasts["H1_capacity"]["second"], "excess_area"),
            ("H2_primary", contrasts["H2_primary"]["first"], contrasts["H2_primary"]["second"], "max_response"),
        ):
            diffs = [float(index[(first, s, scale, shock)][metric]) - float(index[(second, s, scale, shock)][metric]) for s in sorted(seeds_c)]
            cell_rows.append({"contrast": label, "depth_scale": scale, "shock_log_return": shock,
                              "mean_delta": statistics.mean(diffs), "sd_delta": statistics.stdev(diffs),
                              "heldout_cell": (scale, shock) in heldout})
    h3_rows: list[dict[str, Any]] = []
    for name in conditions:
        subset = [r for r in records if r["condition"] == name and r["heldout_cell"]]
        h3_rows.append({"condition": name, "region": conditions[name][2],
                        "mae_map": statistics.mean(r["mae_map"] for r in subset),
                        "mae_persistence": statistics.mean(r["mae_persistence"] for r in subset),
                        "mae_scalar_ar": statistics.mean(r["mae_scalar_ar"] for r in subset),
                        "map_beats_persistence": statistics.mean(r["mae_map"] for r in subset) < statistics.mean(r["mae_persistence"] for r in subset)})
    condition_rows: list[dict[str, Any]] = []
    for name in conditions:
        subset = [r for r in records if r["condition"] == name]
        recovered = sum(1 for r in subset if r["recovered"])
        labels = [r["observed_label"] for r in subset if r["heldout_cell"]]
        condition_rows.append({"condition": name, "runs": len(subset),
                               "mean_excess_area": statistics.mean(r["excess_area"] for r in subset),
                               "mean_max_response": statistics.mean(r["max_response"] for r in subset),
                               "recovery_rate": recovered / len(subset),
                               "restricted_mean_return_tick": statistics.mean(r["return_tick_censored"] for r in subset),
                               "mean_minimum_depth": statistics.mean(r["minimum_depth"] for r in subset),
                               "lp_activation_rate": sum(1 for r in subset if r["lp_withdrawal_applied"]) / len(subset),
                               "heldout_contractive": labels.count("contractive"),
                               "heldout_persistent": labels.count("persistent"),
                               "heldout_in_band": labels.count("in-band"),
                               "schur_stable_map": fitted[name]["schur_stable"]})
    # Sample-size guidance from the exploration pilot (cells exclusive to exploration).
    pilot_rows: list[dict[str, Any]] = []
    pilot = {(r["condition"], r["seed"], r["depth_scale"], r["shock_log_return"]): r for r in explore_metrics}
    for label, first, second, metric, target in (
        ("H1_primary", contrasts["H1_primary"]["first"], contrasts["H1_primary"]["second"], "excess_area", inference_cfg["target_half_width_excess_area"]),
        ("H2_primary", contrasts["H2_primary"]["first"], contrasts["H2_primary"]["second"], "max_response", inference_cfg["target_half_width_max_response"]),
    ):
        vals = []
        for seed in sorted(seeds_e):
            diffs = [float(pilot[(first, seed, s, k)][metric]) - float(pilot[(second, seed, s, k)][metric]) for s, k in sorted(explore_cells)]
            vals.append(statistics.mean(diffs))
        pilot_rows.append({"contrast": label, "source": "exploration pilot", **half_width_and_n(vals, float(target))})
        conf_vals = series[label]
        pilot_rows.append({"contrast": label, "source": "confirmation (achieved)", **half_width_and_n(conf_vals, float(target))})

    write_csv(run_dir / "exploration_fits.csv", fit_rows)
    write_csv(run_dir / "run_metrics.csv", records)
    write_csv(run_dir / "inference.csv", stats_rows)
    write_csv(run_dir / "cell_breakdown.csv", cell_rows)
    write_csv(run_dir / "h3_by_condition.csv", h3_rows)
    write_csv(run_dir / "condition_summary.csv", condition_rows)
    write_csv(run_dir / "sample_size_guidance.csv", pilot_rows)
    (run_dir / "config.json").write_bytes(confirm_bytes)
    (run_dir / "model_config.json").write_bytes(model_bytes)
    artifacts = ["config.json", "model_config.json", "exploration_fits.csv", "run_metrics.csv", "inference.csv",
                 "cell_breakdown.csv", "h3_by_condition.csv", "condition_summary.csv", "sample_size_guidance.csv"]
    metadata = {
        "run_id": run_id,
        "analysis_version": cfg["analysis_version"],
        "abm_model_version": model["model_version"],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "python_version": platform.python_version(),
        "confirm_config_sha256": sha256_bytes(confirm_bytes),
        "model_config_sha256": sha256_bytes(model_bytes),
        "source_sha256": {n: sha256_bytes((HERE / n).read_bytes()) for n in ("confirm.py", "abm.py", "run.py", "h1c.py")},
        "exploration_seeds": [min(seeds_e), max(seeds_e)],
        "confirmation_seeds": [min(seeds_c), max(seeds_c)],
        "confirmation_cells": cells,
        "heldout_cells_for_h3": heldout,
        "run_counts": {"exploration": len(explore_metrics), "confirmation": len(records)},
        "independent_unit": "seed (cells averaged within seed)",
        **git_context(),
        "artifact_sha256": {n: sha256_bytes((run_dir / n).read_bytes()) for n in artifacts},
    }
    summary = {"inference": stats_rows, "fits": fit_rows, "h3_by_condition": h3_rows, "condition_summary": condition_rows,
               "sample_size_guidance": pilot_rows,
               "interpretation_limit": "synthetic representative-agent micro-world; no market data; deterministic mechanics, stochastic noise flow only"}
    (run_dir / "summary.json").write_text(json.dumps(summary, indent=2, default=str) + "\n", encoding="utf-8")
    (run_dir / "run_metadata.json").write_text(json.dumps(metadata, indent=2, default=str) + "\n", encoding="utf-8")
    return run_dir


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model-config", type=Path, default=DEFAULT_MODEL_CONFIG)
    parser.add_argument("--confirm-config", type=Path, default=DEFAULT_CONFIRM_CONFIG)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run_dir = execute(args.model_config.resolve(), args.confirm_config.resolve(), args.output.resolve())
    print(f"Wrote confirmatory H1/H2/H3 evaluation to {run_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

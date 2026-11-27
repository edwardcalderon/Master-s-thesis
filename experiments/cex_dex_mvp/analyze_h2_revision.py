#!/usr/bin/env python3
"""Replay archived seeds for post-recovery H2 and panic/capacity diagnostics."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import random
import shutil
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean

from abm import make_noise_schedule, run_condition
from confirm import scaled_config
from engineering import variant_config

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DEFAULT_ENGINEERING_METRICS = HERE / "fixtures/h2_review_engineering_metrics.csv.gz"
DEFAULT_CONFIRM_CONFIG = HERE / "confirm_config.json"
DEFAULT_MODEL_CONFIG = HERE / "abm_config.json"
DEFAULT_ENGINEERING_CONFIG = HERE / "engineering_config.json"
DEFAULT_OUTPUT_ROOT = HERE / "output/revision"
DEFAULT_EXPORT = ROOT / "thesis/figures/data"
DEFAULT_WEB_EXPORT = ROOT / "apps/web/src/data/h2-review-findings.json"
PROTOCOL = HERE / "H2_REVISION_PROTOCOL_0.7.0.md"

sys.path.insert(0, str(HERE))
from analyze_revision_findings import build_pressure, bootstrap_interval, read_csv, sha256_file, wilson_interval, write_csv  # noqa: E402


def portable_path(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return "<external-input>/" + path.name


def compute_metrics(rows, summary, band: float, tolerance: float) -> dict[str, object]:
    return_tick = summary["sustained_return_tick"]
    confirm_tick = return_tick + 1 if return_tick is not None else None
    post = [row for row in rows if confirm_tick is not None and int(row["tick"]) > confirm_tick]
    outside = [abs(float(row["log_error"])) > band + tolerance for row in post]
    episodes = 0
    panic_episodes = 0
    outside_ticks = 0
    panic_outside_ticks = 0
    previous_outside = False
    for row, is_outside in zip(post, outside):
        panic = bool(row["panic_order_fired"])
        if is_outside:
            outside_ticks += 1
            panic_outside_ticks += int(panic)
            if not previous_outside:
                episodes += 1
                panic_episodes += int(panic)
        previous_outside = is_outside

    post_excess = [max(abs(float(row["log_error"])) - band, 0.0) for row in post]
    return {
        "recovered": return_tick is not None,
        "return_start_tick": return_tick if return_tick is not None else "",
        "recovery_confirmation_tick": confirm_tick if confirm_tick is not None else "",
        "post_recovery_observed_ticks": len(post),
        "whole_horizon_peak_abs_log_error": max(abs(float(row["log_error"])) for row in rows[1:]),
        "post_recovery_peak_abs_log_error": max((abs(float(row["log_error"])) for row in post), default=""),
        "post_recovery_peak_excess_error": max(post_excess, default=""),
        "post_recovery_excess_area": sum(post_excess) if post else "",
        "post_recovery_outside_tick_count": outside_ticks,
        "post_recovery_departure_episode_count": episodes,
        "post_recovery_panic_outside_tick_count": panic_outside_ticks,
        "post_recovery_panic_episode_count": panic_episodes,
        "any_post_recovery_departure": episodes > 0,
    }


def check_against_archived(row: dict[str, object], archived: dict[str, str], summary: dict) -> None:
    checks = {
        "recovered": int(bool(row["recovered"])) == int(archived["recovered"]),
        "confirmation_tick": str(row["recovery_confirmation_tick"]) == archived["confirmation_tick"],
        "later_departure": int(bool(row["any_post_recovery_departure"])) == int(archived["later_departure"]),
        "excess_area": math.isclose(float(row["full_horizon_excess_area"]), float(archived["excess_area"]), rel_tol=0, abs_tol=1e-12),
        "max_response": math.isclose(float(row["full_horizon_max_response"]), float(archived["max_response"]), rel_tol=0, abs_tol=1e-12),
        "capital_limited_orders": int(row["capital_limited_orders"]) == int(archived["capital_limited_orders"]),
        "panic_orders": int(summary["panic_orders"]) >= 0,
    }
    if not all(checks.values()):
        raise AssertionError(f"Seed replay differs from archived metrics: {checks}")


def run_replay(model, confirm_cfg, engineering_cfg, archive_rows, seeds):
    conditions = confirm_cfg["conditions"]
    selected = {
        "E1-arb-high-static": conditions["E1-arb-high-static"],
        "E3-adaptive-lp-high-arb": conditions["E3-adaptive-lp-high-arb"],
    }
    records: list[dict[str, object]] = []
    archive = {
        (r["variant"], r["condition"], r["depth_scale"], r["shock_log_return"], r["seed"]): r
        for r in archive_rows
    }

    jobs = []
    # Main fixed-order replay across the existing three-depth grid.
    for depth in engineering_cfg["depth_scales"]:
        for shock in engineering_cfg["shock_log_returns"]:
            for seed in seeds:
                jobs.append(("fixed_orders", "current_reserves", float(depth), float(shock), int(seed), True))
    # Panic ablation at the focal shallow depth.
    for shock in engineering_cfg["shock_log_returns"]:
        for seed in seeds:
            jobs.append(("no_panic", "current_reserves", 0.5, float(shock), int(seed), True))
    # Paired fixed-initial-reserve capacity counterfactual at the focal depth.
    for shock in engineering_cfg["shock_log_returns"]:
        for seed in seeds:
            jobs.append(("fixed_orders", "initial_reserves", 0.5, float(shock), int(seed), False))

    expected_runs = len(jobs) * len(selected)
    for variant, capacity_reference, depth, shock, seed, check_archive in jobs:
        config = variant_config(model, depth, variant)
        schedule = make_noise_schedule(config, seed)
        for condition, spec in selected.items():
            rows, summary = run_condition(
                config,
                shock,
                seed,
                condition,
                float(spec["capacity"]),
                bool(spec["adaptive_lp"]),
                schedule,
                capacity_reference=capacity_reference,
            )
            metrics = compute_metrics(rows, summary, float(config["no_arbitrage_band_log"]), float(engineering_cfg["band_tolerance"]))
            full_area = sum(abs(float(r["excess_error"])) for r in rows[1:])
            full_response = max(abs(math.log(float(r["dex_price"]) / float(rows[0]["dex_price"]))) for r in rows[1:])
            record = {
                "variant": variant,
                "capacity_reference": capacity_reference,
                "depth_scale": depth,
                "shock_log_return": shock,
                "seed": seed,
                "condition": condition,
                **metrics,
                "full_horizon_excess_area": full_area,
                "full_horizon_max_response": full_response,
                "panic_orders": int(summary["panic_orders"]),
                "capital_limited_orders": int(summary["capital_limited_orders"]),
            }
            if check_archive:
                archive_key = (variant, condition, str(depth), str(shock), str(seed))
                archived = archive.get(archive_key)
                if archived is None:
                    # CSV may serialize integral floats without a decimal point.
                    archive_key = (variant, condition, str(depth).removesuffix(".0"), str(shock).removesuffix(".0"), str(seed))
                    archived = archive.get(archive_key)
                if archived is None:
                    raise KeyError(f"No archived metrics for {archive_key}")
                check_against_archived(record, archived, summary)
            records.append(record)
    if len(records) != expected_runs:
        raise AssertionError(f"Expected {expected_runs} replay paths, got {len(records)}")
    return records


def summarize_post_recovery(records: list[dict[str, object]], depths, shocks, seeds, draws=10_000, seed=20_261_126):
    baseline = {
        (float(r["depth_scale"]), float(r["shock_log_return"]), int(r["seed"]), str(r["condition"])): r
        for r in records
        if r["variant"] == "fixed_orders" and r["capacity_reference"] == "current_reserves"
    }
    metrics = (
        ("post_recovery_peak_abs_log_error", "post_recovery_peak_abs_log_error"),
        ("post_recovery_peak_excess_error", "post_recovery_peak_excess_error"),
        ("post_recovery_excess_area", "post_recovery_excess_area"),
    )
    rows = []
    deltas_by_cell: dict[tuple[float, float], dict[str, dict[int, float]]] = {}
    for depth in depths:
        for shock in shocks:
            paired_by_metric = {name: {} for name, _ in metrics}
            all_peaks = []
            n_e1 = n_e3 = 0
            for seed_id in seeds:
                e1 = baseline[(float(depth), float(shock), int(seed_id), "E1-arb-high-static")]
                e3 = baseline[(float(depth), float(shock), int(seed_id), "E3-adaptive-lp-high-arb")]
                n_e1 += int(bool(e1["recovered"]))
                n_e3 += int(bool(e3["recovered"]))
                if bool(e1["recovered"]) and bool(e3["recovered"]):
                    for metric_name, field in metrics:
                        if e1[field] != "" and e3[field] != "":
                            paired_by_metric[metric_name][int(seed_id)] = float(e3[field]) - float(e1[field])
                all_peaks.append(float(e3["whole_horizon_peak_abs_log_error"]) - float(e1["whole_horizon_peak_abs_log_error"]))
            deltas_by_cell[(float(depth), float(shock))] = paired_by_metric
            result: dict[str, object] = {
                "scope": "cell",
                "depth_scale": float(depth),
                "shock_log_return": float(shock),
                "e1_recovered_runs": n_e1,
                "e3_recovered_runs": n_e3,
                "paired_recovered_runs": min(len(paired_by_metric[name]) for name, _ in metrics),
                "whole_horizon_peak_difference_e3_minus_e1_mean": mean(all_peaks),
                "seed_count": len(all_peaks),
                "post_recovery_estimand": "conditional paired E3 minus E1-high among seeds with recovery and at least one post-confirmation tick",
            }
            for metric_name, _field in metrics:
                values = list(paired_by_metric[metric_name].values())
                low, high = bootstrap_interval(values, draws, seed + len(rows) * 11 + len(metric_name))
                result[f"{metric_name}_e3_minus_e1_mean"] = mean(values)
                result[f"{metric_name}_ci95_low"] = low
                result[f"{metric_name}_ci95_high"] = high
                result[f"{metric_name}_paired_n"] = len(values)
            rows.append(result)

    complete_seeds = [
        int(seed_id)
        for seed_id in seeds
        if all(
            int(seed_id) in deltas_by_cell[(float(depth), float(shock))]["post_recovery_excess_area"]
            for depth in depths for shock in shocks
        )
    ]
    aggregate: dict[str, object] = {
        "scope": "all_cells_equal_weight_complete_seeds",
        "depth_scale": "all",
        "shock_log_return": "all",
        "e1_recovered_runs": "cell-level rows above",
        "e3_recovered_runs": "cell-level rows above",
        "paired_recovered_runs": len(complete_seeds),
        "whole_horizon_peak_difference_e3_minus_e1_mean": mean(
            [row["whole_horizon_peak_difference_e3_minus_e1_mean"] for row in rows]
        ),
        "seed_count": len(complete_seeds),
        "post_recovery_estimand": "equal-cell-weighted E3 minus E1-high paired contrast among seeds recovered in all nine cells",
    }
    for metric_name, _field in metrics:
        values = [
            mean(deltas_by_cell[(float(depth), float(shock))][metric_name][seed_id]
                 for depth in depths for shock in shocks)
            for seed_id in complete_seeds
        ]
        low, high = bootstrap_interval(values, draws, seed + 701 + len(metric_name))
        aggregate[f"{metric_name}_e3_minus_e1_mean"] = mean(values)
        aggregate[f"{metric_name}_ci95_low"] = low
        aggregate[f"{metric_name}_ci95_high"] = high
        aggregate[f"{metric_name}_paired_n"] = len(values)
    rows.append(aggregate)
    return rows


def summarize_departures(records: list[dict[str, object]], shocks, draws=10_000):
    groups = defaultdict(list)
    for record in records:
        if float(record["depth_scale"]) == 0.5 and record["capacity_reference"] == "current_reserves":
            groups[(str(record["variant"]), str(record["condition"]), float(record["shock_log_return"]))].append(record)
    rows = []
    for index, (key, group) in enumerate(sorted(groups.items())):
        variant, condition, shock = key
        recovered = [r for r in group if bool(r["recovered"]) and int(r["post_recovery_observed_ticks"]) > 0]
        departures = [r for r in recovered if int(r["post_recovery_departure_episode_count"]) > 0]
        count = len(departures)
        n = len(recovered)
        low, high = wilson_interval(count, n) if n else ("", "")
        rows.append({
            "variant": variant,
            "condition": condition,
            "depth_scale": 0.5,
            "shock_log_return": shock,
            "runs": len(group),
            "recovered_with_followup": n,
            "departure_paths": count,
            "departure_rate_given_recovery": count / n if n else "",
            "departure_wilson95_low": low,
            "departure_wilson95_high": high,
            "mean_departure_episodes_per_recovered_path": mean([int(r["post_recovery_departure_episode_count"]) for r in recovered]) if recovered else "",
            "recovered_paths_with_multiple_episodes": sum(int(r["post_recovery_departure_episode_count"]) > 1 for r in recovered),
            "panic_associated_departure_episodes": sum(int(r["post_recovery_panic_episode_count"]) for r in recovered),
            "outside_ticks_with_panic": sum(int(r["post_recovery_panic_outside_tick_count"]) for r in recovered),
        })
    return rows


def summarize_capacity(records: list[dict[str, object]], shocks, seeds, draws=10_000, seed=20_261_126):
    index = {
        (float(r["shock_log_return"]), int(r["seed"]), str(r["condition"]), str(r["capacity_reference"])): r
        for r in records
        if float(r["depth_scale"]) == 0.5 and r["variant"] == "fixed_orders"
    }
    rows = []
    for shock_index, shock in enumerate(shocks):
        mode_deltas = {}
        for mode in ("current_reserves", "initial_reserves"):
            paired = []
            e1_rec = e3_rec = e1_dep = e3_dep = 0
            coverage = 0
            for seed_id in seeds:
                e1 = index[(float(shock), int(seed_id), "E1-arb-high-static", mode)]
                e3 = index[(float(shock), int(seed_id), "E3-adaptive-lp-high-arb", mode)]
                e1_rec += int(bool(e1["recovered"]))
                e3_rec += int(bool(e3["recovered"]))
                e1_dep += int(bool(e1["any_post_recovery_departure"]))
                e3_dep += int(bool(e3["any_post_recovery_departure"]))
                if bool(e1["recovered"]) and bool(e3["recovered"]) and e1["post_recovery_excess_area"] != "" and e3["post_recovery_excess_area"] != "":
                    paired.append(float(e3["post_recovery_excess_area"]) - float(e1["post_recovery_excess_area"]))
                    coverage += 1
            low, high = bootstrap_interval(paired, draws, seed + 200 + shock_index + (0 if mode == "current_reserves" else 100))
            mode_deltas[mode] = {int(seed_id): float(index[(float(shock), int(seed_id), "E3-adaptive-lp-high-arb", mode)]["post_recovery_excess_area"]) - float(index[(float(shock), int(seed_id), "E1-arb-high-static", mode)]["post_recovery_excess_area"])
                                 for seed_id in seeds
                                 if bool(index[(float(shock), int(seed_id), "E1-arb-high-static", mode)]["recovered"])
                                 and bool(index[(float(shock), int(seed_id), "E3-adaptive-lp-high-arb", mode)]["recovered"])
                                 and index[(float(shock), int(seed_id), "E1-arb-high-static", mode)]["post_recovery_excess_area"] != ""
                                 and index[(float(shock), int(seed_id), "E3-adaptive-lp-high-arb", mode)]["post_recovery_excess_area"] != ""}
            rows.append({
                "shock_log_return": float(shock),
                "capacity_reference": mode,
                "e1_recovery_rate": e1_rec / len(seeds),
                "e3_recovery_rate": e3_rec / len(seeds),
                "e1_departure_rate_per_all_runs": e1_dep / len(seeds),
                "e3_departure_rate_per_all_runs": e3_dep / len(seeds),
                "post_recovery_area_delta_e3_minus_e1": mean(paired),
                "post_recovery_area_ci95_low": low,
                "post_recovery_area_ci95_high": high,
                "paired_recovered_n": coverage,
            })
        common = sorted(set(mode_deltas["current_reserves"]) & set(mode_deltas["initial_reserves"]))
        did = [mode_deltas["current_reserves"][seed_id] - mode_deltas["initial_reserves"][seed_id] for seed_id in common]
        low, high = bootstrap_interval(did, draws, seed + 400 + shock_index)
        rows.append({
            "shock_log_return": float(shock),
            "capacity_reference": "difference_in_differences_current_minus_initial",
            "e1_recovery_rate": "",
            "e3_recovery_rate": "",
            "e1_departure_rate_per_all_runs": "",
            "e3_departure_rate_per_all_runs": "",
            "post_recovery_area_delta_e3_minus_e1": mean(did),
            "post_recovery_area_ci95_low": low,
            "post_recovery_area_ci95_high": high,
            "paired_recovered_n": len(did),
        })
    return rows


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--engineering-metrics", type=Path, default=DEFAULT_ENGINEERING_METRICS)
    parser.add_argument("--engineering-run", type=Path, help="Optional archived run directory; defaults to the bundled compressed metric fixture.")
    parser.add_argument("--confirm-config", type=Path, default=DEFAULT_CONFIRM_CONFIG)
    parser.add_argument("--model-config", type=Path, default=DEFAULT_MODEL_CONFIG)
    parser.add_argument("--engineering-config", type=Path, default=DEFAULT_ENGINEERING_CONFIG)
    parser.add_argument("--output-root", type=Path, default=DEFAULT_OUTPUT_ROOT)
    parser.add_argument("--export-dir", type=Path, default=DEFAULT_EXPORT)
    parser.add_argument("--web-export", type=Path, default=DEFAULT_WEB_EXPORT)
    parser.add_argument("--bootstrap-resamples", type=int, default=10_000)
    parser.add_argument("--bootstrap-seed", type=int, default=20_261_126)
    args = parser.parse_args()

    engineering_metrics_path = args.engineering_run / "run_metrics.csv" if args.engineering_run else args.engineering_metrics
    input_paths = {
        "engineering_metrics": engineering_metrics_path,
        "engineering_config": args.engineering_config,
        "confirm_config": args.confirm_config,
        "model_config": args.model_config,
        "protocol": PROTOCOL,
    }
    input_bytes = {name: path.read_bytes() for name, path in input_paths.items()}
    engineering_cfg = json.loads(input_bytes["engineering_config"])
    confirm_cfg = json.loads(input_bytes["confirm_config"])
    model = json.loads(input_bytes["model_config"])
    archived_rows = read_csv(input_paths["engineering_metrics"])
    seed_ids = list(range(int(engineering_cfg["seed_start"]), int(engineering_cfg["seed_start"]) + int(engineering_cfg["seed_count"])))
    source_paths = [Path(__file__), HERE / "abm.py", HERE / "analyze_revision_findings.py", HERE / "confirm.py", HERE / "engineering.py", HERE / "run.py"]
    source_hashes = {portable_path(path): sha256_file(path) for path in source_paths}
    combined = b"".join(input_bytes[name] for name in sorted(input_bytes)) + b"".join(bytes.fromhex(v) for v in source_hashes.values())
    run_id = "cex-dex-h2-review-" + hashlib.sha256(combined).hexdigest()[:12]
    run_dir = args.output_root.resolve() / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    replay = run_replay(model, confirm_cfg, engineering_cfg, archived_rows, seed_ids)
    archive_match_count = sum(
        1 for row in replay
        if row["capacity_reference"] == "current_reserves"
    )
    depths = [float(value) for value in engineering_cfg["depth_scales"]]
    shocks = [float(value) for value in engineering_cfg["shock_log_returns"]]
    h2_rows = summarize_post_recovery(replay, depths, shocks, seed_ids, args.bootstrap_resamples, args.bootstrap_seed)
    departure_rows = summarize_departures(replay, shocks, args.bootstrap_resamples)
    capacity_rows = summarize_capacity(replay, shocks, seed_ids, args.bootstrap_resamples, args.bootstrap_seed)
    pressure_rows = build_pressure(archived_rows, model)

    outputs = {
        "revision_replay_metrics.csv": replay,
        "h2_post_recovery.csv": h2_rows,
        "departure_episode_diagnostics.csv": departure_rows,
        "capacity_reference_counterfactual.csv": capacity_rows,
        "pressure_ratio_diagnostics_v0.7.0.csv": pressure_rows,
    }
    for name, rows in outputs.items():
        write_csv(run_dir / name, rows)
    for name, data in input_bytes.items():
        extension = "md" if name == "protocol" else ("csv.gz" if input_paths[name].suffix == ".gz" else "csv") if name == "engineering_metrics" else "json"
        destination = run_dir / (name + "." + extension)
        destination.write_bytes(data)

    web_findings = {
        "analysis_version": "0.7.0",
        "run_id": run_id,
        "seed_range": [min(seed_ids), max(seed_ids)],
        "replayed_paths": len(replay),
        "exact_archived_metric_matches": archive_match_count,
        "new_random_seeds": False,
        "post_recovery": h2_rows,
        "departure_episodes": departure_rows,
        "capacity_counterfactual": capacity_rows,
        "limitations": [
            "Post-hoc exploratory replay of existing seeds, not an independent confirmation.",
            "Synthetic zero-fee model; end-of-tick episode counts do not identify intra-tick causality.",
            "Configured pressure ratios are not measured market thresholds.",
        ],
        "source_artifacts": {
            name: sha256_file(run_dir / name)
            for name in (
                "h2_post_recovery.csv",
                "departure_episode_diagnostics.csv",
                "capacity_reference_counterfactual.csv",
            )
        },
    }
    web_json = json.dumps(web_findings, indent=2, ensure_ascii=False) + "\n"
    (run_dir / "web_findings.json").write_text(web_json, encoding="utf-8")
    manifest = {
        "run_id": run_id,
        "analysis": "exploratory-h2-review-replay-0.7.0",
        "created_on": datetime.now(timezone.utc).date().isoformat(),
        "script": portable_path(Path(__file__)),
        "script_sha256": sha256_file(Path(__file__)),
        "source_sha256": source_hashes,
        "inputs": {name: {"path": portable_path(path), "sha256": sha256_file(path)} for name, path in input_paths.items()},
        "procedure": {
            "seeds": [min(seed_ids), max(seed_ids)],
            "replayed_paths": len(replay),
            "new_random_seeds": False,
            "bootstrap_resamples": args.bootstrap_resamples,
            "bootstrap_seed": args.bootstrap_seed,
            "primary_exploratory_outcome": "post-recovery excess area after two consecutive in-band observations are confirmed",
            "capacity_counterfactual": "fixed c times initial input-token reserve, capped by active input reserve",
            "event_classification": "contiguous end-of-tick out-of-band episodes after recovery; panic overlap is descriptive, with a paired no-panic ablation",
        },
        "outputs": {
            **{name: {"rows": len(rows), "sha256": sha256_file(run_dir / name)} for name, rows in outputs.items()},
            "web_findings.json": {"rows": None, "sha256": sha256_file(run_dir / "web_findings.json")},
        },
        "limitations": [
            "This is a post-hoc exploratory replay of archived seed streams, not a new independent sample or preregistered confirmatory experiment.",
            "All paths remain conditional on the zero-fee synthetic model and its event ordering.",
            "Departure episodes use end-of-tick observations and do not identify intra-tick order causality.",
            "The configured pressure ratios assume adverse orders align and are not realized-flow threshold laws.",
        ],
    }
    (run_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    args.export_dir.mkdir(parents=True, exist_ok=True)
    export_names = {
        "h2_post_recovery.csv": "h2_post_recovery.csv",
        "departure_episode_diagnostics.csv": "departure_episode_diagnostics.csv",
        "capacity_reference_counterfactual.csv": "capacity_reference_counterfactual.csv",
        "pressure_ratio_diagnostics_v0.7.0.csv": "pressure_ratio_diagnostic.csv",
    }
    for source, destination in export_names.items():
        shutil.copy2(run_dir / source, args.export_dir / destination)
    shutil.copy2(run_dir / "manifest.json", args.export_dir / "h2_review_manifest.json")
    args.web_export.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(run_dir / "web_findings.json", args.web_export)
    print(f"run: {run_id}")
    print(f"paths replayed: {len(replay)}")
    print(f"archived current-cap rows matched exactly: {archive_match_count} / {archive_match_count}")
    print(f"output: {run_dir}")
    print(f"export: {args.export_dir}")
    print(f"web export: {args.web_export}")


if __name__ == "__main__":
    main()

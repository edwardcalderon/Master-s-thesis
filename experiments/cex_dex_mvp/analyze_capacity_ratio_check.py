#!/usr/bin/env python3
"""Run the shallow fixed-capacity panic and no-panic R diagnostic."""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import shutil
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

from abm import make_noise_schedule, run_condition
from confirm import scaled_config
from engineering import variant_config

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
MODEL_PATH = HERE / "abm_config.json"
ENGINEERING_PATH = HERE / "engineering_config.json"
CONFIRM_PATH = HERE / "confirm_config.json"
PROTOCOL_PATH = HERE / "H2_CAPACITY_RATIO_PROTOCOL_0.8.0.md"
DEFAULT_OUTPUT = HERE / "output/capacity-ratio"
DEFAULT_EXPORT = ROOT / "thesis/figures/data"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def compute_metrics(rows: list[dict], summary: dict, band: float, tolerance: float) -> dict:
    return_tick = summary["sustained_return_tick"]
    confirmation_tick = return_tick + 1 if return_tick is not None else None
    post = [
        row for row in rows
        if confirmation_tick is not None and int(row["tick"]) > confirmation_tick
    ]
    episodes = 0
    panic_episodes = 0
    previous_outside = False
    for row in post:
        outside = abs(float(row["log_error"])) > band + tolerance
        panic = bool(row["panic_order_fired"])
        if outside and not previous_outside:
            episodes += 1
            panic_episodes += int(panic)
        previous_outside = outside
    return {
        "recovered": int(return_tick is not None),
        "recovery_confirmation_tick": confirmation_tick if confirmation_tick is not None else "",
        "post_recovery_observed_ticks": len(post),
        "post_recovery_departure_episode_count": episodes,
        "post_recovery_panic_episode_count": panic_episodes,
        "any_post_recovery_departure": int(episodes > 0),
        "panic_orders": int(summary["panic_orders"]),
        "capital_limited_orders": int(summary["capital_limited_orders"]),
    }


def summarize(records: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for record in records:
        groups[(record["arm"], record["shock_log_return"])].append(record)
    output = []
    for (arm, shock), group in sorted(groups.items()):
        recovered = [r for r in group if r["recovered"] and r["post_recovery_observed_ticks"] > 0]
        departures = [r for r in recovered if r["any_post_recovery_departure"]]
        episode_count = sum(r["post_recovery_departure_episode_count"] for r in recovered)
        panic_episode_count = sum(r["post_recovery_panic_episode_count"] for r in recovered)
        output.append({
            "arm": arm,
            "shock_log_return": shock,
            "runs": len(group),
            "recovered_with_followup": len(recovered),
            "departure_paths": len(departures),
            "departure_rate_given_recovery": len(departures) / len(recovered) if recovered else "",
            "total_departure_episodes": episode_count,
            "mean_departure_episodes_per_recovered_path": episode_count / len(recovered) if recovered else "",
            "recovered_paths_with_multiple_episodes": sum(
                r["post_recovery_departure_episode_count"] > 1 for r in recovered
            ),
            "panic_associated_departure_episodes": panic_episode_count,
            "panic_orders_total": sum(r["panic_orders"] for r in group),
            "capital_limited_orders_total": sum(r["capital_limited_orders"] for r in group),
        })
    return output


def write_csv(path: Path, rows: list[dict]) -> None:
    if not rows:
        raise ValueError(f"cannot write empty CSV: {path}")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--export-dir", type=Path, default=DEFAULT_EXPORT)
    args = parser.parse_args()

    model = json.loads(MODEL_PATH.read_text(encoding="utf-8"))
    engineering = json.loads(ENGINEERING_PATH.read_text(encoding="utf-8"))
    confirm = json.loads(CONFIRM_PATH.read_text(encoding="utf-8"))
    seeds = range(
        int(engineering["seed_start"]),
        int(engineering["seed_start"]) + int(engineering["seed_count"]),
    )
    shocks = [float(value) for value in engineering["shock_log_returns"]]
    spec = confirm["conditions"]["E3-adaptive-lp-high-arb"]
    sources = [Path(__file__), HERE / "abm.py", HERE / "engineering.py", HERE / "confirm.py"]
    inputs = [MODEL_PATH, ENGINEERING_PATH, CONFIRM_PATH, PROTOCOL_PATH]
    digest = hashlib.sha256(
        b"".join(path.read_bytes() for path in sorted(inputs + sources, key=str))
    ).hexdigest()[:12]
    run_id = f"cex-dex-capacity-ratio-{digest}"
    run_dir = args.output.resolve() / run_id
    run_dir.mkdir(parents=True, exist_ok=False)

    records: list[dict] = []
    for arm, variant in (("fixed_cap_panic", "fixed_orders"), ("fixed_cap_no_panic", "no_panic")):
        config = variant_config(model, 0.5, variant)
        for shock in shocks:
            for seed in seeds:
                schedule = make_noise_schedule(config, seed)
                rows, summary = run_condition(
                    config,
                    shock,
                    int(seed),
                    "E3-adaptive-lp-high-arb",
                    float(spec["capacity"]),
                    bool(spec["adaptive_lp"]),
                    schedule,
                    capacity_reference="initial_reserves",
                )
                metrics = compute_metrics(
                    rows,
                    summary,
                    float(config["no_arbitrage_band_log"]),
                    float(engineering["band_tolerance"]),
                )
                records.append({
                    "arm": arm,
                    "variant": variant,
                    "capacity_reference": "initial_reserves",
                    "depth_scale": 0.5,
                    "shock_log_return": shock,
                    "seed": int(seed),
                    "condition": "E3-adaptive-lp-high-arb",
                    **metrics,
                })

    if len(records) != 1800:
        raise AssertionError(f"expected 1800 verification and check paths, got {len(records)}")
    summary_rows = summarize(records)
    panic_rows = [r for r in summary_rows if r["arm"] == "fixed_cap_panic"]
    expected_departures = {"-0.05": 123, "-0.1": 101, "-0.2": 53}
    for row in panic_rows:
        shock = str(row["shock_log_return"])
        if row["departure_paths"] != expected_departures[shock]:
            raise AssertionError(f"archived fixed-cap departure count changed for {shock}: {row}")
        if row["total_departure_episodes"] != row["panic_associated_departure_episodes"]:
            raise AssertionError(f"fixed-cap panic episode alignment changed for {shock}: {row}")
        if row["recovered_paths_with_multiple_episodes"] != 0:
            raise AssertionError(f"fixed-cap paths gained repeated episodes for {shock}: {row}")
    no_panic_rows = [r for r in summary_rows if r["arm"] == "fixed_cap_no_panic"]
    for row in no_panic_rows:
        if row["panic_orders_total"] != 0 or row["panic_associated_departure_episodes"] != 0:
            raise AssertionError(f"no-panic arm emitted a panic event: {row}")

    paths_path = run_dir / "fixed_capacity_ratio_paths.csv"
    summary_path = run_dir / "fixed_capacity_ratio_summary.csv"
    write_csv(paths_path, records)
    write_csv(summary_path, summary_rows)
    (run_dir / "protocol.md").write_bytes(PROTOCOL_PATH.read_bytes())
    manifest = {
        "run_id": run_id,
        "analysis": "h2-capacity-ratio-check-0.8.0",
        "created_on": datetime.now(timezone.utc).date().isoformat(),
        "arms": {"fixed_cap_panic": 900, "fixed_cap_no_panic": 900},
        "seeds": [min(seeds), max(seeds)],
        "depth_scale": 0.5,
        "shocks": shocks,
        "new_random_seeds": False,
        "inputs": {path.name: {"path": str(path.relative_to(ROOT)), "sha256": sha256(path)} for path in inputs},
        "sources": {str(path.relative_to(ROOT)): sha256(path) for path in sources},
        "outputs": {
            paths_path.name: {"rows": len(records), "sha256": sha256(paths_path)},
            summary_path.name: {"rows": len(summary_rows), "sha256": sha256(summary_path)},
        },
        "limitations": [
            "Post-hoc replay of existing seeds; not an independent or confirmatory sample.",
            "Synthetic zero-fee model with end-of-tick episode classification.",
            "R uses configured aligned orders and approximate reserves; it is not a universal threshold law.",
        ],
    }
    manifest_path = run_dir / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    args.export_dir.mkdir(parents=True, exist_ok=True)
    shutil.copy2(summary_path, args.export_dir / "fixed_capacity_ratio_summary.csv")
    shutil.copy2(manifest_path, args.export_dir / "fixed_capacity_ratio_manifest.json")
    print(f"run: {run_id}")
    print("paths: 1800 total (900 fixed-cap panic verification; 900 fixed-cap no-panic check)")
    for row in summary_rows:
        print(json.dumps(row, sort_keys=True))
    print(f"output: {run_dir}")
    print(f"export: {args.export_dir}")


if __name__ == "__main__":
    main()

"""Export the small tables that the thesis figures plot, from one confirmatory run.

Reads the CSV outputs of `confirm.py` (run directory given by --run-dir) and re-simulates the
confirmation design to obtain per-tick means (the run records keep only per-run metrics). The
re-simulation uses the same configuration files, seeds and cells as the run, so it is
deterministic and independent of the exported run's timestamp.

Writes plain CSV files plus `manifest.json` (run id, input hashes, output hashes) to --output
(default: thesis/figures/data). Python standard library only.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from abm import make_noise_schedule, run_condition
from confirm import scaled_config
from run import sha256_bytes


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent
DEFAULT_RUN_ROOT = HERE / "output" / "confirm"
DEFAULT_OUTPUT = ROOT / "thesis" / "figures" / "data"


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow({k: (f"{v:.10g}" if isinstance(v, float) else v) for k, v in row.items()})


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def impact_curve() -> list[dict[str, Any]]:
    """Analytic log impact I(q, r x) = 2 log(1 + q / (r x)) for q = 500, x = 10000 (no fee)."""
    q, x = 500.0, 10000.0
    rows = []
    for step in range(10, 101, 2):
        r = step / 100.0
        rows.append({"reserve_factor": r, "log_impact": 2.0 * math.log1p(q / (r * x))})
    return rows


# Numeric series key so pgfplots can filter rows with `restrict expr to domain` (no string filter key is portable).
SERIES_IDS = {"E0-arb-off-static": 1, "E1-arb-low-static": 2, "E1-arb-high-static": 3,
              "E3-adaptive-lp-high-arb": 4, "E1-arb-max-static": 5}
DEPTH_IDS = {"all": 0, "0.5": 1, "1": 2, "2": 3}


def trajectories(run_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Per-tick means and per-cell mechanism counts (panic sell, adaptive-LP withdrawal)."""
    cfg = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
    model = json.loads((run_dir / "model_config.json").read_text(encoding="utf-8"))
    conf = cfg["confirmation"]
    seeds = range(int(conf["seed_start"]), int(conf["seed_start"]) + int(conf["seed_count"]))
    cells = [(float(s), float(k)) for s in conf["depth_scales"] for k in conf["shock_log_returns"]]
    conditions = {
        name: (float(spec["capacity"]), bool(spec["adaptive_lp"])) for name, spec in cfg["conditions"].items()
    }
    # sums[(condition, depth_label, tick)] = [sum |d|, sum |log(pD_t / pD_0)|, n]
    sums: dict[tuple[str, str, int], list[float]] = defaultdict(lambda: [0.0, 0.0, 0])
    # mech[(condition, depth, shock)] = [runs, runs with a panic sell, runs with an LP withdrawal, sum of LP withdrawal ticks]
    mech: dict[tuple[str, float, float], list[float]] = defaultdict(lambda: [0, 0, 0, 0.0])
    for seed in seeds:
        for scale, shock in cells:
            cell_config = scaled_config(model, scale)
            schedule = make_noise_schedule(cell_config, seed)
            for name, (capacity, adaptive) in conditions.items():
                rows, summary = run_condition(cell_config, shock, seed, name, capacity, adaptive, schedule)
                counts = mech[(name, scale, shock)]
                counts[0] += 1
                counts[1] += int(summary["panic_orders"] > 0)
                if summary["lp_withdrawal_tick"] is not None:
                    counts[2] += 1
                    counts[3] += int(summary["lp_withdrawal_tick"])
                by_tick = {int(r["tick"]): r for r in rows}
                base = float(by_tick[0]["dex_price"])
                for tick in range(0, 21):
                    d = abs(float(by_tick[tick]["excess_error"]))
                    dev = abs(math.log(float(by_tick[tick]["dex_price"]) / base))
                    for label in ("all", f"{scale:g}"):
                        acc = sums[(name, label, tick)]
                        acc[0] += d
                        acc[1] += dev
                        acc[2] += 1
    out = []
    for (name, label, tick), (sd, sdev, n) in sorted(sums.items()):
        out.append({"series_id": SERIES_IDS[name] * 10 + DEPTH_IDS[label], "condition": name, "depth_scale": label, "tick": tick,
                    "mean_abs_excess": sd / n, "mean_abs_dex_deviation": sdev / n, "runs": n})
    mechanism = [
        {"condition": name, "depth_scale": scale, "shock_log_return": shock, "runs": int(n),
         "panic_sell_rate": panic / n, "lp_withdrawal_rate": lp / n,
         "mean_lp_withdrawal_tick": (tick_sum / lp) if lp else ""}
        for (name, scale, shock), (n, panic, lp, tick_sum) in sorted(mech.items())
    ]
    return out, mechanism


def recovery_by_cell(run_dir: Path) -> list[dict[str, Any]]:
    groups: dict[tuple[str, str, str], list[bool]] = defaultdict(list)
    for r in read_csv(run_dir / "run_metrics.csv"):
        groups[(r["condition"], r["depth_scale"], r["shock_log_return"])].append(r["recovered"] == "True")
    return [
        {"condition": c, "depth_scale": float(d), "shock_log_return": float(s), "recovery_rate": sum(v) / len(v), "runs": len(v)}
        for (c, d, s), v in sorted(groups.items())
    ]


def seed_delta_distribution(run_dir: Path) -> list[dict[str, Any]]:
    """Per-seed paired differences (cells averaged within seed), for the three confirmatory contrasts."""
    cfg = json.loads((run_dir / "config.json").read_text(encoding="utf-8"))
    contrasts = cfg["contrasts"]
    values: dict[tuple[str, int, str, str], list[float]] = defaultdict(list)
    index: dict[tuple[str, int, str, str], dict[str, str]] = {}
    for r in read_csv(run_dir / "run_metrics.csv"):
        index[(r["condition"], int(r["seed"]), r["depth_scale"], r["shock_log_return"])] = r
    seeds = sorted({k[1] for k in index})
    cells = sorted({(k[2], k[3]) for k in index})
    rows = []
    for label in ("H1_primary", "H1_capacity", "H2_primary"):
        spec = contrasts[label]
        metric = "excess_area" if label.startswith("H1") else "max_response"
        deltas = []
        for seed in seeds:
            diffs = [float(index[(spec["first"], seed, s, k)][metric]) - float(index[(spec["second"], seed, s, k)][metric]) for s, k in cells]
            deltas.append(statistics.mean(diffs))
        deltas.sort()
        n = len(deltas)
        for q in (0.0, 0.05, 0.25, 0.5, 0.75, 0.95, 1.0):
            pos = q * (n - 1)
            lo, hi = int(math.floor(pos)), int(math.ceil(pos))
            value = deltas[lo] + (deltas[hi] - deltas[lo]) * (pos - lo)
            rows.append({"contrast_id": {"H1_primary": 1, "H1_capacity": 2, "H2_primary": 3}.get(label, 9), "contrast": label, "quantile": q, "value": value, "seed_count": n, "sd": statistics.stdev(deltas)})
    return rows


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    run_dir = args.run_dir.resolve()
    metadata = json.loads((run_dir / "run_metadata.json").read_text(encoding="utf-8"))
    args.output.mkdir(parents=True, exist_ok=True)

    trajectory_rows, mechanism_rows = trajectories(run_dir)
    outputs: dict[str, list[dict[str, Any]]] = {
        "impact_curve.csv": impact_curve(),
        "trajectories.csv": trajectory_rows,
        "mechanism_by_cell.csv": mechanism_rows,
        "recovery_by_cell.csv": recovery_by_cell(run_dir),
        "delta_quantiles.csv": seed_delta_distribution(run_dir),
    }
    for name in ("cell_breakdown.csv", "h3_by_condition.csv", "condition_summary.csv",
                 "inference.csv", "exploration_fits.csv", "sample_size_guidance.csv"):
        outputs[name] = [dict(r) for r in read_csv(run_dir / name)]
    for name, rows in outputs.items():
        write_csv(args.output / name, rows)

    manifest = {
        "source_run_id": metadata["run_id"],
        "source_git_head": metadata.get("git_head"),
        "source_artifact_sha256": metadata["artifact_sha256"],
        "exported_sha256": {name: sha256_bytes((args.output / name).read_bytes()) for name in sorted(outputs)},
        "note": "Regenerate with: python3 experiments/cex_dex_mvp/export_thesis_data.py --run-dir <run directory>",
    }
    (args.output / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"Exported {len(outputs)} tables for run {metadata['run_id']} to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Export a reproducible compact hybrid-map findings bundle for thesis and web."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
DEFAULT_RUN_ROOT = HERE / "output" / "hybrid"
WEB_DATA = HERE.parents[1] / "apps" / "web" / "src" / "data" / "hybrid-findings.json"
THESIS_DATA = HERE.parents[1] / "thesis" / "figures" / "data"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def latest_run_dir() -> Path:
    candidates = [path for path in DEFAULT_RUN_ROOT.glob("cex-dex-hybrid-*") if (path / "run_metadata.json").is_file()]
    if not candidates:
        raise FileNotFoundError(f"no hybrid runs found under {DEFAULT_RUN_ROOT}")
    return max(candidates, key=lambda path: (path / "run_metadata.json").stat().st_mtime)


def rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, data: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)


def export(run_dir: Path, web_path: Path, thesis_dir: Path) -> dict[str, Any]:
    summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8"))
    protocol = json.loads((run_dir / "hybrid_config.json").read_text(encoding="utf-8"))
    metadata_path = run_dir / "run_metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    cells = rows(run_dir / "cell_metrics.csv")
    seed_metrics = rows(run_dir / "seed_metrics.csv")
    grouped: dict[tuple[float, str], list[dict[str, str]]] = {}
    for cell in cells:
        grouped.setdefault((float(cell["depth_scale"]), cell["condition"]), []).append(cell)
    depth_condition = []
    for (depth, condition), group in sorted(grouped.items()):
        item: dict[str, Any] = {
            "depth_scale": depth,
            "condition": condition,
            "heldout_cell_count": len(group),
        }
        for metric in ("one_e", "one_z", "rollout_e", "rollout_z"):
            item[f"mean_improvement_{metric}"] = sum(float(row[f"mean_improvement_{metric}"]) for row in group) / len(group)
        depth_condition.append(item)
    payload = {
        "schema_version": "1.0.0",
        "title": "Affine and band-aware reduced-map comparison",
        "run_id": metadata["run_id"],
        "model_version": metadata["model_version"],
        "analysis_version": metadata["analysis_version"],
        "seed_split": {"selection": metadata["selection_seeds"], "confirmation": metadata["confirmation_seeds"]},
        "confirmation_cells": metadata["confirmation_cells"],
        "independent_unit": metadata["independent_unit"],
        "equations": {
            "state": "e = log(p_D/p_C), z = normalized net-buy pressure",
            "input": "u[t+1] = - CEX log return[t+1]",
            "L0": "e[t+1] = e[t] + u[t+1] + a·e[t] + b·z[t]; z[t+1] = c·e[t] + r·z[t]",
            "Hyb": "L0 plus coefficients on signed excess sign(e)·max(|e|−γ,0) and z·I(|e|>γ), with γ=0.003",
        },
        "scope": summary["interpretation_limit"],
        "flow_forecast_limit": protocol["flow_forecast_limit"],
        "summary": summary,
        "depth_condition_cells": depth_condition,
        "shock_depth_condition_cells": [
            {key: (float(value) if key != "condition" else value) for key, value in cell.items()}
            for cell in cells
        ],
        "provenance": {
            "run_metadata_sha256": sha256(metadata_path),
            "cell_metrics_sha256": sha256(run_dir / "cell_metrics.csv"),
            "seed_metrics_sha256": sha256(run_dir / "seed_metrics.csv"),
            "trajectory_metrics_sha256": sha256(run_dir / "trajectory_metrics.csv"),
        },
    }
    web_path.parent.mkdir(parents=True, exist_ok=True)
    web_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    thesis_dir.mkdir(parents=True, exist_ok=True)
    write_csv(thesis_dir / "hybrid_depth_condition.csv", depth_condition)
    write_csv(thesis_dir / "hybrid_shock_depth_condition.csv", payload["shock_depth_condition_cells"])
    manifest = {
        "run_id": payload["run_id"],
        "source_metadata_sha256": payload["provenance"]["run_metadata_sha256"],
        "exporter_sha256": sha256(Path(__file__).resolve()),
        "outputs": {
            "apps/web/src/data/hybrid-findings.json": sha256(web_path),
            "hybrid_depth_condition.csv": sha256(thesis_dir / "hybrid_depth_condition.csv"),
            "hybrid_shock_depth_condition.csv": sha256(thesis_dir / "hybrid_shock_depth_condition.csv"),
        },
    }
    (thesis_dir / "hybrid_export_manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return payload


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-dir", type=Path, default=latest_run_dir())
    parser.add_argument("--web-output", type=Path, default=WEB_DATA)
    parser.add_argument("--thesis-output", type=Path, default=THESIS_DATA)
    args = parser.parse_args()
    payload = export(args.run_dir.resolve(), args.web_output.resolve(), args.thesis_output.resolve())
    print(f"Exported {payload['run_id']} to {args.web_output} and {args.thesis_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

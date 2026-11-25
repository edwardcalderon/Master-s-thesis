#!/usr/bin/env python3
"""Advances the public `microworld-data` branch's state by a batch of ticks.

PLACEHOLDER EVOLUTION RULE. This script wires the infra end to end — GitHub Actions
schedule -> this script -> `microworld-data` branch -> static site reads the JSON
directly from `raw.githubusercontent.com`. The tick rule below (a Gaussian random
walk on the CEX reference price, arbitraged against a CPMM via the existing
reference model's own mechanics) is a minimal stand-in to exercise that wiring. It is
NOT a reviewed extension of the thesis model. Do not present its output as a
validated hypothesis result or empirical finding — see INFRA-001's remaining work and
THESIS-001's model contract before treating this as anything but a wiring demo.

State files, all under --state-dir:
  state.json    full internal state needed to resume (not meant for external reads)
  snapshot.json compact, checksummed, versioned — the public-facing read surface
  history.json  bounded rolling window of the last HISTORY_LIMIT ticks only
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "experiments" / "cex_dex_mvp"))

from run import (  # noqa: E402  (path must be extended first)
    arbitrage_step,
    log_error,
    price,
    sha256_bytes,
)

MODEL_VERSION = "infra-001-placeholder-0.1"
TICKS_PER_RUN = 50
HISTORY_LIMIT = 500
ALLOWED_SCENARIO_OVERRIDES = {"no_arbitrage_band_log", "capacity_fraction", "shock_scale"}

DEFAULT_STATE: dict[str, Any] = {
    "model_version": MODEL_VERSION,
    "tick": 0,
    "seed": 1234,
    "reserve_x": 1_000_000.0,
    "reserve_y": 1_000_000.0,
    "cex_price": 1.0,
    "no_arbitrage_band_log": 0.003,
    "capacity_fraction": 0.5,
    "shock_scale": 0.002,
}


def load_state(state_dir: Path) -> dict[str, Any]:
    state_path = state_dir / "state.json"
    if state_path.exists():
        return json.loads(state_path.read_text())
    return dict(DEFAULT_STATE)


def apply_scenario(state: dict[str, Any], scenario_json: str) -> dict[str, Any]:
    if not scenario_json:
        return state
    try:
        overrides = json.loads(scenario_json)
    except json.JSONDecodeError:
        print(f"ignoring unparseable scenario_json: {scenario_json!r}", file=sys.stderr)
        return state
    if not isinstance(overrides, dict):
        return state
    for key, value in overrides.items():
        if key in ALLOWED_SCENARIO_OVERRIDES and isinstance(value, (int, float)):
            state[key] = float(value)
        else:
            print(f"ignoring disallowed/invalid scenario override: {key!r}", file=sys.stderr)
    return state


def step(state: dict[str, Any], rng: random.Random) -> dict[str, Any]:
    shock = rng.gauss(0.0, state["shock_scale"])
    state["cex_price"] = max(state["cex_price"] * (1.0 + shock), 1e-9)
    state["reserve_x"], state["reserve_y"], event = arbitrage_step(
        state["reserve_x"],
        state["reserve_y"],
        state["cex_price"],
        state["no_arbitrage_band_log"],
        state["capacity_fraction"],
    )
    state["tick"] += 1
    state["last_event"] = event
    return state


def build_snapshot(state: dict[str, Any]) -> dict[str, Any]:
    body = {
        "model_version": state["model_version"],
        "synthetic": True,
        "tick": state["tick"],
        "cex_price": state["cex_price"],
        "dex_price": price(state["reserve_x"], state["reserve_y"]),
        "log_error": log_error(state["reserve_x"], state["reserve_y"], state["cex_price"]),
        "no_arbitrage_band_log": state["no_arbitrage_band_log"],
        "capacity_fraction": state["capacity_fraction"],
        "last_event": state.get("last_event"),
    }
    body["checksum"] = sha256_bytes(json.dumps(body, sort_keys=True).encode("utf-8"))
    return body


def append_history(state_dir: Path, entry: dict[str, Any]) -> None:
    history_path = state_dir / "history.json"
    history: list[dict[str, Any]] = []
    if history_path.exists():
        history = json.loads(history_path.read_text())
    history.append(entry)
    history = history[-HISTORY_LIMIT:]
    history_path.write_text(json.dumps(history, indent=2))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state-dir", required=True, type=Path)
    parser.add_argument("--ticks", type=int, default=TICKS_PER_RUN)
    parser.add_argument("--scenario-json", default="")
    args = parser.parse_args()

    args.state_dir.mkdir(parents=True, exist_ok=True)
    state = load_state(args.state_dir)
    state = apply_scenario(state, args.scenario_json)
    rng = random.Random(state["seed"] + state["tick"])

    for _ in range(max(args.ticks, 0)):
        state = step(state, rng)

    (args.state_dir / "state.json").write_text(json.dumps(state, indent=2))
    snapshot = build_snapshot(state)
    (args.state_dir / "snapshot.json").write_text(json.dumps(snapshot, indent=2))
    append_history(args.state_dir, snapshot)

    print(f"tick={state['tick']} cex_price={state['cex_price']:.6f} event={state.get('last_event')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

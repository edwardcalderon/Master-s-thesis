"""Web handler backend — the one thing on Azure that's actually needed.

The static frontend (apps/web, GitHub Pages) can't hold a secret safely, so it can't
call GitHub's workflow_dispatch API directly. This tiny Flask app holds that one
secret (GITHUB_DISPATCH_TOKEN, an App Service application setting — never commit it)
and does nothing else: validate a scenario request, forward it as a dispatch to
infra/microworld/tick.py's next scheduled run.

Required environment variables (set as Azure Web App "Application settings", not in
code or .env committed to git):
  GITHUB_DISPATCH_TOKEN   fine-scoped PAT (or GitHub App token) with Actions:write on
                          this one repo, nothing else
  GITHUB_REPO             "<owner>/<repo>", e.g. "edwardcalderon/Master-s-thesis"
Optional:
  ALLOWED_ORIGIN           CORS origin to allow (default "*" — tighten to the Pages
                            origin, e.g. "https://edwardcalderon.github.io", once that
                            domain is confirmed)
  DISPATCH_COOLDOWN_SECONDS  minimum seconds between accepted dispatches (default 60).
                            Best-effort, in-process only — resets on cold start/scale,
                            not a substitute for real auth under real traffic.

Run locally: pip install -r requirements.txt && FLASK_APP=app flask run
"""
from __future__ import annotations

import json
import math
import os
import time

import requests
from flask import Flask, jsonify, request

app = Flask(__name__)

# Must match infra/microworld/tick.py's scenario fields and limits. The app and tick
# script are deployed separately, so tests enforce parity between these contracts.
SCENARIO_LIMITS = {
    "no_arbitrage_band_log": (0.0, 0.5),
    "capacity_fraction": (0.0, 1.0),
    "shock_scale": (0.0, 0.2),
}
WORKFLOW_FILE = "microworld-tick.yml"

_last_dispatch_at = 0.0


def _cors_headers() -> dict[str, str]:
    origin = os.environ.get("ALLOWED_ORIGIN", "*")
    return {
        "Access-Control-Allow-Origin": origin,
        "Access-Control-Allow-Methods": "POST, OPTIONS",
        "Access-Control-Allow-Headers": "Content-Type",
    }


@app.after_request
def add_cors(response):
    for key, value in _cors_headers().items():
        response.headers[key] = value
    return response


@app.route("/", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/api/scenario", methods=["OPTIONS"])
def scenario_preflight():
    return "", 204


@app.route("/api/scenario", methods=["POST"])
def scenario():
    global _last_dispatch_at

    token = os.environ.get("GITHUB_DISPATCH_TOKEN")
    repo = os.environ.get("GITHUB_REPO")
    if not token or not repo:
        return jsonify({"error": "backend not configured"}), 503

    cooldown = float(os.environ.get("DISPATCH_COOLDOWN_SECONDS", "60"))
    now = time.monotonic()
    if now - _last_dispatch_at < cooldown:
        return jsonify({"error": "too many requests, try again shortly"}), 429

    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "expected a JSON object"}), 400

    unknown = sorted(set(body) - set(SCENARIO_LIMITS))
    if unknown:
        return jsonify({"error": "unsupported scenario field(s)", "fields": unknown}), 400

    overrides = {}
    for key, value in body.items():
        low, high = SCENARIO_LIMITS[key]
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return jsonify({"error": f"{key} must be a finite number in [{low}, {high}]"}), 400
        try:
            numeric_value = float(value)
        except (OverflowError, ValueError):
            numeric_value = float("inf")
        if not math.isfinite(numeric_value) or not low <= numeric_value <= high:
            return jsonify({"error": f"{key} must be a finite number in [{low}, {high}]"}), 400
        overrides[key] = numeric_value

    if not overrides:
        return jsonify({"error": "at least one scenario field is required"}), 400

    resp = requests.post(
        f"https://api.github.com/repos/{repo}/actions/workflows/{WORKFLOW_FILE}/dispatches",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
        },
        json={"ref": "main", "inputs": {"scenario_json": json.dumps(overrides)}},
        timeout=10,
    )
    if resp.status_code >= 300:
        return jsonify({"error": "dispatch failed", "detail": resp.text}), 502

    _last_dispatch_at = now
    return jsonify({"accepted": overrides}), 202


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "8080")))

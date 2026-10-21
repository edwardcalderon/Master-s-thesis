# Reproducible CEX/DEX experimental playground — v2.0 protocol

> **Status:** proposed protocol, not implemented or validated. Source of truth lives in this repository. See [scope v2.0](../research-scope/v2.0-nonlinear-stability.md) and [Notion lab](https://app.notion.com/p/4000738d2ce681f7bdc2ca4cb94c72a4).

## Reproducibility contract

An experiment must capture enough information to recreate its market states or, for statistical Monte Carlo experiments, its reported distribution within prespecified numerical tolerances. Capture the model, code commit, lockfile hash, configuration, seed streams, event ordering, exogenous prices, shocks, unit conventions, artifacts, and summary metrics.

**Canonical state transition:** `S(t+1) = F(S(t), stochastic_input(t), intervention(t), parameters)`; represent memory-dependent strategies by including their sufficient history in `S`.

**No hidden interactive mutations:** UI (Streamlit or existing React web app) is only a visualization/control surface calling the same experimental functions and exporting the actual config.

## Suggested architecture

```text
src/marketlab/
  core/{state,ledger,scheduler}.py
  markets/{cpmm,cex_reference}.py
  agents/{noise,trend,arbitrage,liquidity_provider}.py
  analysis/{tracking,stability,metrics}.py
  io/{manifest,artifacts}.py
experiments/configs/{E0,E1,E2,E3}/
experiments/run.py
tests/{test_cpmm,test_accounting,test_replay,test_invariants}.py
notebooks/{analytic_baseline,experiments_e0_e3}.ipynb
results/manifests/
thesis/proposals/
```

Do not add folders mechanically if equivalent directories already exist; integrate with the monorepo.

## Config and per-run manifest

Example parameters in human-reviewed YAML: ticker/base/quote, pool reserves, fee units, external CEX process, arbitrage threshold/latency/capital, LP policy, trend response, agent inventories, horizon, warmup, shock tape, measurement thresholds.

Example *per-run manifest*, written after completion:

```json
{
  "model_spec_version": "research-v2.0",
  "experiment_id": "E2_lp_adaptive_vs_fixed",
  "run_id": "<config-hash>_seed_0042",
  "git_sha": "<actual 40-character commit>",
  "python_version": "<actual>",
  "environment_lock_sha256": "<actual>",
  "config_sha256": "<actual>",
  "base_seed": 42,
  "rng_engine": "numpy.PCG64",
  "rng_streams": {"cex": 101, "noise": 102, "lp": 103},
  "events_sha256": "<actual>",
  "metrics_sha256": "<actual>",
  "status": "finished | failed",
  "verification_passed": true,
  "notes": "Execution order and tolerance specification version recorded"
}
```

**Important:** placeholder fields must be replaced by real values on each run; a template is not experimental evidence.

## Execution semantics and controlled randomness

- Fix tick sequence: CEX reference update -> observed state -> noise/trend orders -> AMM execution -> arb evaluation/execution -> LP adjustments -> optional forced sales -> metrics.
- Record *every fill* and its units, fee convention, balances, and event order. Store the exogenous shock and CEX price series as an immutable input tape to isolate treatment effects.
- Use `numpy.random.Generator` with named streams, stable stream derivation, explicit seeds and recorded NumPy version; do not rely on the global RNG or cross-library unspecified seeding.
- Paired treatment/control runs should receive equivalent exogenous shock tapes even when endogenous event paths diverge. Avoid promising bit-identical results across CPU/platforms; test numerical invariants and tolerances.

## Mathematics and verification

1. Fee-free constant-product invariant holds across swaps, but changes with LP add/remove; fees retained in pool may cause reserve product to increase.
2. Exact pre/post swap price, slippage, price direction, reserves and balance checks.
3. Differentiate positive reserves, round-off and inventory boundary handling; record whether modeling exact real arithmetic or integer token quantization.
4. Verify that proportional withdrawal leaves instantaneous marginal price unchanged but increases subsequent fixed-size order impact.
5. Analytical proof pertains to a separately documented reduced deterministic system, not the stochastic ABM.

## Experiment cards

| ID | Comparator | Main metrics | Gate |
| --- | --- | --- | --- |
| E0 | Reference constant; arb on/off; fixed LP | tracking error, invariants, convergence to band | mathematical baseline verified |
| E1 | CEX shock; vary arbitrage execution/frictions | recovery, max excess error, error integral | known shock tape, arb accounting |
| E2 | static versus reactive LP | depth, impact, slippage, tracking error | matched exogenous events |
| E3 | fixed shock + heterogeneous selling/forced-sale threshold | cascades, persistence, recovery | state machine and forced-sale rules verified |

Use a small screening grid first, then hold-out confirmatory parameter grid. Determine replication count with precision/stability of confidence intervals, not a fixed unjustified seed count. Report mechanism ablations, uncertainty intervals, divergent runs, and null findings.

## Recommended software & parity tests

**Core:** Python 3.12 (pin exact compatible version), `uv.lock` or equivalent, NumPy, SciPy, pytest, Hypothesis, Pydantic, Pandas/Polars + PyArrow, Matplotlib; SALib optional for sensitivity and SymPy optional for symbolic checks.

**Open market mechanisms (phased, not all required):**
- CPMM level: compare ideal formula against **Uniswap v2-compatible** open contract code using **Foundry + Anvil** local EVM. Fee conventions and integer rounding must match test fixture.
- Reference-data level: use public CEX trade/quote candles via **CCXT** or direct exchange public APIs; record provenance, pair mapping, API version, timezones, and licensing.
- On-chain event level: ingest `Swap` and `Sync` events from a selected v2-compatible pool, with `web3.py`; verify quote orientation, fees, reserve snapshots, block timestamps and reorg handling.
- Explicitly exclude v3/v4 concentrated-liquidity equivalence until a separate model version includes ticks/positions and routing.

**Validation ladder:** invariants -> deterministic synthetic replay -> paired stochastic ABM -> smart-contract parity -> historical limited replay -> cautious out-of-sample mechanism discussion.

## CI readiness

- `pytest` on every PR; property-based AMM/accounting tests; schema checks for YAML and JSON manifests.
- One fast E0 fixed-seed smoke test with golden metrics, robust against trivial formatting differences.
- `make reproduce-e0` / `python -m marketlab.run --config ...` commands documented once implemented.
- Medium/heavy sweeps must publish pinned artifacts rather than silently alter committed plots.
- Data cannot enter git without a license/size/provenance decision.

## Research integrity

Separately mark: **formal theorem**, **verified simulation result**, **statistical association**, **suggested mechanism**, and **untested hypothesis**. State that exogenous CEX implies no bidirectional contagion conclusions.

## Definition of done for MVP

One E0 run is rerunnable from a clean checkout, reproduces all key invariants and figures with actual manifest; one analytic baseline yields a checkable statement; and one E1 counterfactual uses identical reference shock tape and reports tracking stability with uncertainty.

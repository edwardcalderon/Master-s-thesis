# MVP plan: reproducible CEX/DEX hypothesis experiments

## Goal

Build the smallest executable model that can test H1a and H1b under controlled
conditions, then evaluate H1c on held-out configurations. The first results should be
mechanistic and synthetic. Public-market data is a later external-validity step.

## Repository state

The standard-library runner in `experiments/cex_dex_mvp/` now has deterministic and
stochastic selection paths. The deterministic path covers E0/E1 arbitrage mechanics,
E2 fixed-sale depth, and paired E3 LP-policy selection. Its grid has 108 E0/E1 points,
four E2 liquidity levels, and 16 paired E3 policy settings. A separate stochastic path
implements four representative roles and paired random-order schedules. The current
selection run used 300 seeds after meeting its configured 0.005 log-error interval
half-width target for all six paired peak-error contrasts; its 50,400 trajectory rows
are synthetic selection output, not confirmation evidence. The invariant checker covers
2,654 deterministic states and a 504-state stochastic smoke selection, including asset
conservation and paired noise schedules. E3 settings remain separate from held-out
confirmation. An initial H1c evaluation now fits a condition-specific two-state map on
shocks ±0.1 and tests it on disjoint seeds and held-out shocks ±0.05. Only 3 of 8
condition/shock majority labels matched the map's Schur classification; this is a narrow
diagnostic on representative roles, not broad validation. The cost band is a proxy rather
than an explicit fee ledger; delayed
orders are a simplified queue without concurrent trader flow. The model remains short
of the heterogeneous-agent simulator described by the full research design. The
manuscript dated 2026-10-29 reports an earlier prototype and numerical results under the absent
`experiments/cex_dex_preliminary/` path. Those values remain unverified until the
original source and run artifacts are recovered or the complete contrasts are
regenerated. The current runner's ODD scope and event sequence are recorded in
[`../experiments/cex_dex_mvp/ODD.md`](../experiments/cex_dex_mvp/ODD.md).

## Work sequence

### 1. Freeze the experimental contract

- Record the research question and H1a/H1b/H1c as falsifiable comparisons.
- Extend the initial E0/E1/E2 ODD contract to cover the full minimal world: exogenous
  CEX reference, CPMM reserves, event order, costs and band, inventory/capital limits,
  shock timing, and agent policies.
- The author has approved the four-role taxonomy: bounded arbitrageur, noise trader,
  trend/panic trader as one policy, and LP with static/adaptive conditions. Review the
  selected policy thresholds, inventory limits, and operating ranges before confirmation.
- Define primary metrics before running confirmation scenarios: excess tracking error
  `D_t`, maximum error, sustained return-to-band time, fixed-trade price impact,
  minimum liquidity, and cascade/forced-sale measures where applicable.
- Separate mechanism-selection configurations from confirmation configurations.

**Deliverable:** a versioned, complete ODD and experiment protocol mapping each metric
to H1a, H1b, or H1c.

### 2. Implement and verify the minimal market engine

- Expand the first representative-agent stochastic selection model into the specified
  heterogeneous-agent model only after the four roles and decision rules are reviewed.
  Keep the current simple rules as selection assumptions; add further agent types only
  after their purpose and policies are explicit.
- Make reserves, inventory, costs, latency, capacity, and event ordering explicit in a
  versioned configuration.
- Verify CPMM identities and accounting: positive reserves, swap reserve updates,
  proportional LP withdrawal preserving marginal price, and increased impact for the
  same absolute sale after liquidity withdrawal.
- Verify that arbitrage moves the DEX price toward the no-arbitrage band only when the
  configured costs, latency, and capacity permit execution.

**Deliverable:** a one-run command that produces a deterministic trajectory plus its
configuration and run metadata.

### 3. Run the H1a and H1b contrasts (E0--E3)

- **E0 / H1a:** apply one isolated CEX shock with arbitrage on and off; compare excess
  error and return-to-band time.
- **E1 / H1a:** vary arbitrage capacity, costs, and delay while holding the shock and
  starting state fixed.
- **E2 / H1b:** apply the same absolute sale after static versus proportional/adaptive
  liquidity reduction. Report the immediate mechanical impact separately from any
  later feedback.
- **E3 / H1b and model limits:** select a one-shot threshold rule on paired static and
  adaptive paths under shared deterministic shock and x-sale conditions. Keep this
  selection grid separate from the later confirmation configurations.
- Use paired seeds for stochastic comparisons when the random streams are compatible.
  Do not count repeated noise-free runs as independent statistical replications.
  Choose replication counts from a precision or convergence target and report effect
  sizes and uncertainty intervals.

**Deliverable:** configs, time series, a paired summary table, regenerated figure, and a
script that reproduces every reported value from a clean checkout. Current sweep points
are deterministic sensitivity settings, not statistical replications.

### 4. Evaluate H1c and define where the reduced map fails

- Estimate or diagnose the reduced map on a declared selection grid of initial excess,
  order pressure, capacity, and liquidity conditions.
- Freeze the estimation procedure and classification thresholds before evaluation.
- Test contraction/persistence on separate confirmation configurations; compare the
  map's classification with ABM outcomes and report disagreements by regime.
- Treat Schur conditions as local diagnostics for the reduced map, not guarantees for
  the stochastic ABM or real markets.

**Deliverable:** held-out classification results, uncertainty, and an explicit map of
the operating regions where the approximation works and fails.

An initial held-out diagnostic is now present. It uses the same representative-agent
rules with new seed streams and shock magnitudes, and its 3/8 majority-label agreement
shows that the current map does not classify these regimes reliably. Extend this work
only after the agent rules and operating regions are reviewed.

### 5. Package the reproduction path

- Pin the Python environment and dependencies.
- Provide stable commands for one run, parameter sweep, analysis, invariant checks, and
  figure reproduction.
- Save each run's ID, config, seed, code commit, environment version, metrics, time
  series, invariant results, and checksums with the output.
- Add automated checks for CPMM/accounting invariants and a small deterministic
  reference run; keep larger experiment outputs as release artifacts if they are too
  large for Git.
- Update the manuscript only from regenerated outputs, with synthetic evidence clearly
  separated from any later public-market replay.

**MVP complete when:** a new checkout can reproduce E0--E3 and the reduced-map
confirmation analysis from documented commands, verify the model invariants, and
trace every table/figure value to a configuration, seed, and code commit.

## Defer until after the MVP

Live exchange execution, mainnet nodes, advanced MEV, concentrated-liquidity AMMs,
full limit-order-book simulation, lending/bridges, reinforcement learning, forecasting
models, and broad data ingestion. A small public-data comparison may follow once the
synthetic mechanism tests and reproduction path are stable.

---

[Español](es/mvp-plan.md)

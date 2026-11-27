# THESIS-006 — Robustness and regime-complete analysis of the hybrid map

- **Owner:** `edcalderon`
- **Status:** TODO
- **Created:** 2026-11-26
- **Scope:** Follow up the completed first hybrid comparison in THESIS-005 and the exploratory H2 mechanism pilot reported in manuscript v0.8.4.
- **GitHub issue:** [#12 — hybrid validation, simulation infrastructure, and microworld roadmap](https://github.com/edwardcalderon/Master-s-thesis/issues/12) (follow-up to closed #8; the acceptance criteria remain TODO)

## Goal

Determine whether the band-aware reduced map remains informative across more realistic
operating regimes and whether any stability statement can be justified for a more
complete hybrid representation. Preserve v0.8.4 as the current assessment baseline,
v0.8.3 as the prior assessment snapshot, and v0.8.0 as the historical first hybrid-map
comparison; no extension may overwrite them.

The approved main question evaluates tracking-error trajectories over the tested
capacity/depth grid. It does not claim regime-classification accuracy. The v0.8.4 H2
replay reuses existing seeds. It finds shallow E1 later departures only in panic-enabled
paths, recurrent E3 departures with and without panic, and a substantial reduction in the
post-recovery contrast under a fixed-initial-reserve capacity control. That control covers
one shallow depth and conditions the area outcome on recovery; it does not resolve the
full withdrawal-depth-capacity interaction. Any follow-up must predeclare its estimand
and use realized, directional flow and active reserves if testing an event-level
pressure-to-capacity diagnostic.

## Acceptance criteria

- Freeze a new model/protocol version before fitting or evaluating a trajectory-prediction
  candidate. Represent capacity binding and LP-withdrawal modes explicitly, and state
  which state/event variables are needed for a Markov-complete transition.
- Compare the new candidate with L0, the existing Hyb model, and simple predictive
  baselines on fresh selection seeds and disjoint held-out seeds, shocks, depths, and
  operating conditions. Report paired seed-level effects, uncertainty, and cell-level
  results; do not rely on an aggregate gain alone.
- A post-hoc shallow-depth fixed-capacity pilot is complete in v0.8.4. If H2 is extended,
  predeclare a factorial or otherwise identifying design that varies withdrawal,
  arbitrage capacity, depth, order scaling and panic behavior independently enough to
  estimate their interactions. Do not treat the pilot as a general causal decomposition:
  it covers one depth and recovered-path coverage differs between cap modes.
- Separate conditional price-error tracking with a supplied CEX path from forecasts
  using only information available at the forecast origin. Evaluate flow pressure with
  no future stochastic-flow realization as an input; document target timing and any
  oracle inputs explicitly.
- For any stability analysis, define the reference state, operating mode, disturbance
  assumptions, and equilibrium or invariant set first. Derive and check mode-specific
  Jacobians and a candidate Lyapunov or stochastic-stability criterion, or document
  why the available model does not support one. Do not extend the reduced-map result to
  the full stochastic simulator without a valid argument.
- Check sensitivity to band width, capacity, liquidity depth, order-to-reserve scale,
  random-flow strength, and seed range. Preserve configurations, code/source hashes,
  outputs, and a second-run reproduction check.
- Extend the English and Spanish methodology, results, conclusions, figures, glossary,
  and versioned snapshot only after the next protocol and findings are fixed. State
  synthetic scope and market-validation limits in both editions.
- Review representative-agent rules and the ODD contract with the advisor. Any decision
  to add heterogeneous agents becomes an explicit model/version change. Keep real-pair
  data acquisition, rights, and external validation under DATA-001.

## Open questions to resolve before the next run

- Which capacities and LP-withdrawal events define the regime boundaries, and how are
  transitions ordered when several limits bind in one tick?
- Which predictive baselines are meaningful when the future CEX path is unknown?
- Is the target a deterministic conditional response, an expected stochastic outcome,
  or a predictive distribution? Pick one primary estimand before selecting metrics.
- Is there a defensible equilibrium/invariant set for the full stochastic or hybrid
  state, or should analysis remain restricted to local mode maps?
- Does the advisor consider the current representative roles adequate for the thesis,
  or should a heterogeneous-agent extension be part of the research question?

## Dependencies and limits

- THESIS-005 completed the exact CPMM mechanism proofs, finite-grid rational bridge,
  bounded reduced-map Lyapunov analysis, and first held-out band-aware comparison.
- DATA-001 remains the separate real-market data and rights gate.
- SIM-001 remains responsible for browser evidence and accessibility handoff; SIM-002
  remains the separate 3D replay/sandbox task.
- The shared persistent/evolutionary world is outside this task. It requires a distinct
  model, hypotheses, data/state retention design, and research scope.

## Next action

Review the open estimand, inputs, and operating-mode questions with the advisor. The
v0.8.4 pilot is complete; next, freeze a factorial or model-extension protocol before
implementing the broader robustness study.

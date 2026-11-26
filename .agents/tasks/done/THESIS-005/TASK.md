# THESIS-005 — Formal mechanics and model credibility

- **Owner:** `edcalderon`
- **Status:** DONE
- **Completed:** 2026-11-26; manuscript v0.8.0 / workspace v0.1.10

## Goal

Raise mathematical assurance for the CPMM mechanism and establish a defensible first
comparison of a band-aware reduced-map candidate against the affine diagnostic.

## Completed scope

- Pinned Lean 4.35.0 and mathlib v4.35.0; formalized exact zero-fee CPMM swap,
  positivity/product, and proportional-withdrawal invariants.
- Added a finite-grid exact-rational bridge to the Python float implementation and
  recorded tolerances and scope.
- Clarified the recorded accounting state and avoided claiming it is Markov-complete.
- Added a bounded quadratic Lyapunov analysis for fitted autonomous reduced maps; the
  manuscript does not present it as a certificate for the complete stochastic or hybrid
  simulator.
- Froze and ran the first band-aware candidate separately from H1, using disjoint
  selection and evaluation seeds and held-out shock/depth cells.
- Updated both language editions and preserved manuscript v0.8.0 with the method,
  results, diagrams, conclusions, and explicit limitations.

## Evidence and validation

The run `cex-dex-hybrid-1d1d9d2f8c5b` evaluates 9,600 held-out trajectories over 300
seeds and four operating conditions. The hybrid model reduces recursive signed-price-
error MAE by about 1.7% on average (paired-seed bootstrap 95% CI 0.000499–0.000533).
The gain is concentrated in low-capacity arbitrage at depth 2; flow-pressure error does
not improve. A second output root reproduced the numeric artifacts byte for byte.

Lean proofs build without `sorry` or custom axioms; the reported axioms are Lean's
standard `propext`, `Classical.choice`, and `Quot.sound`. The rational bridge and
experiment tests pass, as do all nine mechanism invariants. The bilingual manuscript
PDFs and layout check pass. Workspace v0.1.10 release verification passes. GitHub had
not reported workflow checks when this completion record was written.

## Boundaries and handoff

The evidence is synthetic, not real-market validation. Recursive evaluation receives a
known CEX shock path, while the flow equation does not receive future random-flow
realizations. The candidate adds band crossing but not explicit capacity-binding or
LP-withdrawal modes. Neither Lean mechanism invariants nor the reduced-map Lyapunov
analysis establishes full-simulator stochastic/hybrid stability.

Follow-up robustness, explicit hybrid regimes, deployable-input forecasting, and a
carefully scoped stability analysis are recorded in THESIS-006. Real-market data rights
and validation remain under DATA-001; browser accessibility and scenario provenance
remain under SIM-001. Persistent/evolutionary simulation stays under separate SIM-002
scope and is not implied by this task's completion.

# THESIS-005 — Formal mechanics and model credibility

- **Owner:** `edcalderon`
- **Status:** IN PROGRESS
- **Goal:** Raise mathematical assurance for the CPMM mechanism and define a defensible
  path from the current affine diagnostic toward nonlinear/hybrid and empirical models.

## Scope

- Formalize exact zero-fee CPMM reserve operations and prove product, positivity, and
  proportional-withdrawal invariants in Lean.
- Differential-test the Python float implementation against an exact-rational reference
  on a declared finite grid.
- Preserve the existing confirmation and state explicitly what each proof/check does
  not establish.
- Clarify which variables constitute the recorded accounting state and what memory or
  event state is needed for a Markov-complete transition representation.
- Add a bounded quadratic Lyapunov analysis for the condition-specific fitted affine
  maps, without presenting it as a stability proof for the full simulator.
- Freeze candidate nonlinear model families and evaluation splits before a new run.
- Coordinate real-pair data rights, event alignment, and held-out validation through
  DATA-001.

## Acceptance criteria

- Lean toolchain and mathlib are pinned; `pnpm experiment:mvp:formal` builds without
  `sorry`, custom axioms, or admitted goals.
- Lean proves CPMM product/positivity and withdrawal-price invariants; its README
  accurately lists unproved Schur or stability claims.
- Exact-rational bridge tests compare the existing Python swap functions on a finite
  grid and pass with stated tolerances.
- `MODEL_CREDIBILITY_PROTOCOL.md` distinguishes mechanism verification, stochastic
  simulation, model selection, and empirical validation; it preserves frozen evidence
  and requires fresh protocols for extensions.
- Any nonlinear candidate is compared with the affine benchmark on held-out conditions
  using prespecified metrics. No new empirical claim is made without data-rights and
  provenance review.
- The first band-aware candidate is evaluated separately from H1 (the arbitrage
  hypothesis), using disjoint seed ranges and held-out shock/depth cells. Its gain is
  reported by condition and not interpreted as stability of the full simulator.
- The bilingual manuscript reports condition-specific discrete Lyapunov solutions and
  their scope, while explicitly leaving full-system stochastic/hybrid stability open.

## Current implementation state

The current bilingual manuscript revision v0.8.0 adds a non-exhaustive numerical
Lyapunov certificate for the fitted autonomous maps, clarifies that the recorded state
is not claimed to be Markov-complete, and reports the separate hybrid-map evaluation
(analysis 0.1.0, run cex-dex-hybrid-1d1d9d2f8c5b). On its synthetic held-out grid, Hyb
reduces recursive signed-price-error MAE by about 1.7%, concentrated in low-capacity
arbitrage at depth 2; flow-pressure prediction does not improve. The exact protocol,
seed-level results and checksums are retained. The candidate models the band crossing
but still does not include explicit capacity-binding or LP-withdrawal state branches.
This does not extend the existing Lean proofs to stability claims.
The Lean proof build passes on Lean 4.35.0/mathlib v4.35.0. `#print axioms` reports only
Lean's standard `propext`, `Classical.choice`, and `Quot.sound` dependencies for the
declared theorems. The exact-rational bridge tests pass on the declared finite grid,
the full experiment test suite has 8 passing tests, and all 9 existing mechanism
invariants pass. The CI axiom audit is configured but has not run on GitHub. Nonlinear
more complete hybrid regime modeling and real-market validation remain open; DATA-001
remains TODO pending an authorized, reproducible data source.

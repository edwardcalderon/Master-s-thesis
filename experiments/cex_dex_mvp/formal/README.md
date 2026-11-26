# Formal verification scope

This Lean 4.35.0 / mathlib v4.35.0 project formalizes exact rational CPMM mechanics
used by the zero-fee simulator. It is a verification layer for mathematical claims,
not a model-validation result.

## Verified propositions in `AmmVerification.lean`

- Selling `X` preserves the constant product and keeps both reserves positive for
  positive initial reserves and a nonnegative input.
- Buying `X` with `Y` has the same product and positivity guarantees.
- A proportional withdrawal preserves the reserve ratio and scales the product by
  the square of the remaining-liquidity fraction.
- The polynomial expressions used in the two-state Schur diagnostic have the stated
  algebraic factorizations.

The Schur spectral-radius equivalence is **not** proved in this first layer. Its use
in the thesis continues to depend on the cited Jury criterion and applies only to the
autonomous fitted linear map. The proofs make no statement about stochastic ABM
stability, economic realism, parameter calibration, or external validity.

## Python relationship

`../formal_bridge.py` implements the exact-rational reference operations. The
`test_formal_bridge.py` grid checks CPMM identities exactly and compares representative
results with the float implementation in `run.py`. This is a differential test sample,
not a proof that the Python implementation refines the Lean definitions over its full
input domain. The tests also preserve the model boundary: no fees, gas, latency, or
market-data assumptions are silently added.

## Reproduce

From the repository root, with Lean/Lake installed:

```bash
pnpm experiment:mvp:formal
pnpm experiment:mvp:test
```

The `lake-manifest.json` pins mathlib's resolved dependency graph. The toolchain and
library versions must be updated together and the proof build rerun before changing
either pin.

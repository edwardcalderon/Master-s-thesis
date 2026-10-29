# Preliminary simulation analysis — 29 October 2026

## Purpose

This is a mechanism check for thesis scope v2.0. It asks whether the simulator can reproduce the directions asserted in the manuscript before those assertions are used to motivate a reduced model.

It is **not** validation against real CEX/DEX data, a calibrated market model, or evidence of profitable trading behavior.

## Reproducibility

```bash
python3 work/preliminary_simulations/cex_dex_preliminary.py \
  --output output/preliminary_simulations --seeds 100
```

The implementation uses a constant-product AMM, a CEX reference, bounded arbitrage, optional adaptive LP withdrawal, synthetic noise, trend response, panic response, and forced sales. Source: `cex_dex_preliminary.py`.

## Results

| Scenario | Comparison | Preliminary result | Supported only within this synthetic model |
|---|---|---:|---|
| E0 | Arbitrage on / off | maximum tracking error `0.0409 / 0.1000`; return to band `2 / not observed` ticks | bounded arbitrage reduces a one-off discrepancy |
| E1 | High / low arbitrage capacity | return to band `1 / 9` ticks; max error `0.0030 / 0.1080` | capacity controls recovery speed |
| E2 | Static / adaptive LP | fixed-sale log impact `0.0940 / 0.2032`; minimum liquidity `10000 / 4500` | proportional liquidity withdrawal raises the impact of the same absolute order |
| E3 | Static / adaptive liquidity | max error `0.0660 / 0.3719`; large-return ticks `3 / 33` | liquidity feedback can amplify a synthetic selling episode |

The E0–E2 scenarios intentionally disable noise, so repeated seeds agree by design. E3 includes noise and agent responses; results listed are medians across 100 seeds.

## Equation refinement

The original continuous ODE was not directly traceable to the ABM. The revised candidate is a local discrete map:

\[
d_t=\operatorname{sgn}(e_t)(|e_t|-\gamma)_+,
\qquad
\begin{bmatrix}d_{t+1}\\z_{t+1}\end{bmatrix}
=
\begin{bmatrix}1-\alpha&\beta\\-\chi&\rho\end{bmatrix}
\begin{bmatrix}d_t\\z_t\end{bmatrix}
+
\begin{bmatrix}u_t+\varepsilon_t\\\eta_t\end{bmatrix}.
\]

Here `d` is signed excess tracking error, `z` is DEX buy pressure, and `u` is the CEX-reference displacement. The AMM identity anchors its mechanics: a sale of `q` units into reserve `x` changes the log price by `-2 log(1+q/x)`.

A finite-difference grid around the stated operating point (`gamma=0.003`, arbitrage capacity `3%` of reserve per tick) produced a local least-squares excess slope `k=0.187401`, or an effective one-step contraction `alpha=0.812599`. This is a diagnostic for that grid only—not a calibrated, transferable parameter.

## What the preliminary evidence changes

- Keep H1a and H1b as testable mechanism claims.
- Keep H1c open: its test requires an ex-ante regime classifier, selection/confirmation split, and an assessment of failures.
- Replace the generic ODE and premature Lyapunov/ISS claims with the discrete map above.
- Frame Schur stability as a local diagnostic for the reduced map, never as proof of ABM or market stability.

## Next evidence required

1. Unit tests for AMM conservation, arbitrage target and LP withdrawal mechanics.
2. Parameter sweep for `gamma`, arbitrage capacity, LP response and shock size.
3. Holdout configurations for H1c rather than fitting and evaluating on the same configurations.
4. A small, public, licensed empirical dataset to test external plausibility separately from mechanism verification.

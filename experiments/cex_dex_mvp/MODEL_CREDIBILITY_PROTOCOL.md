# Model credibility and extension protocol

**Status:** initial design gates plus the completed simulation-only hybrid-map protocol.
Its findings appear in manuscript v0.8.0. The protocol leaves the frozen v0.5.0
confirmation and all prior manuscript snapshots unchanged.

## Current model claim

The current work studies zero-fee constant-product reserve mechanics under exogenous
CEX price shocks, bounded arbitrage, synthetic flow, and a threshold LP-withdrawal
rule. The CPMM transition is nonlinear. The fitted two-state reduced map is affine and
its Schur test is a diagnostic for that linear map only. The simulation uses four
representative roles, not a calibrated heterogeneous population. The log band is a
cost proxy; it does not separately model gas, fees, or execution risk.

The intended use is mechanism-level comparison and candidate stress-test design. No
claim is made that current results identify live-market operating thresholds or predict
a particular pool.

## Model-extension gates

1. **Freeze the question and target use.** Name the pool class, event time scale,
   decision being supported, target outcomes, and transfer boundary. If the study stays
   synthetic, use mechanism-stress-testing language.
2. **Preserve a baseline.** Keep the current affine reduced map and exact CPMM mechanism
   as benchmarks. Add a versioned nonlinear/hybrid candidate only after stating its
   state, input timing, event order, threshold rules, parameter meanings, and domain.
   The candidate shortlist is: (L0) the existing affine map; (Hyb) a regime-aware hybrid
   reduced map with branches for in-band/out-of-band error, capacity-capped/uncapped
   arbitrage, and withdrawal inactive/active, using the existing model's configured
   boundaries; and (N1) a smooth saturating-flow surrogate only if a documented
   inventory/capacity mechanism supports that response shape. Do not add free polynomial
   terms solely to improve fit. Freeze the shortlist and parameter budget before fitting.
3. **Justify each added mechanism.** Candidate mechanisms include fee/gas accounting,
   delayed execution and pending orders, arbitrage inventory constraints, empirically
   grounded LP withdrawal, and heterogeneous trader rules. Add one mechanism family at
   a time with an ablation and a documented evidence source.
4. **Separate selection from confirmation.** Freeze candidate equations, features,
   parameters/ranges, metrics, and seed/time splits before confirmation. Use new
   analysis/model versions and fresh confirmation seeds. Do not revise the existing
   v0.5.0 confirmation or select a nonlinear form using its outcomes.
5. **Compare on held-out regimes.** Compare the affine benchmark and each candidate on
   trajectory error, predictive calibration, band-return/departure behavior, and
   performance across held-out shocks, depths, and policies. Include a parameter and
   structural sensitivity report. A better in-sample fit alone does not justify added
   complexity. If a simulation-only comparison proceeds, use selection seeds 3000–3299
   and untouched confirmation seeds 4000–4299, with held-out shock/depth cells fixed in
   the protocol. This evaluates surrogate fidelity to the specified simulator; it does
   not validate fidelity to a real market.
6. **Bound stability claims.** Report local equilibrium, Jacobian and local-stability
   conditions only where differentiability and equilibrium assumptions hold. For
   threshold or hybrid models, analyze regions and transitions separately; do not infer
   global or stochastic stability from one fitted matrix.

## Frozen reduced-map comparison (analysis 0.1.0)

Before running the new simulation, `hybrid_config.json` freezes an affine baseline (L0)
and a mechanism-aligned hybrid map (Hyb). Both predict signed log-price error
`e[t+1]` and normalized net-buy pressure `z[t+1]`, separately by the four existing
operating conditions. The known external input is `u[t+1] = -CEX_log_return[t+1]`.
L0 fits two zero-intercept correction coefficients per output to `(e, z)`. Hyb adds
signed excess error `sign(e) max(|e| - band, 0)` and `z * I(|e| > band)`, for four
coefficients per output. The configured band is fixed at 0.003. No polynomial terms,
new behavioral rules, or outcome-based feature selection are allowed.

Selection uses seeds 3000–3299, depth 1, and shocks -0.10/+0.10. Confirmation uses
seeds 4000–4299, depths 0.5/2, and shocks -0.20/-0.05/+0.05/+0.20; none of these
cells or seeds appears in selection. The primary outcome is per-seed mean rollout
absolute error in signed log-price error, averaged over all held-out cells and ticks.
Positive `L0 error - Hyb error` favors Hyb. A paired percentile bootstrap over the 300
seed units gives the 95% interval. One-step errors in `e` and `z`, rollout error in `z`,
and per-cell contrasts are secondary. The rollout uses the known future CEX input but
recursively feeds its own predicted `(e,z)` state; it does not predict an exogenous CEX
path. No future random noise/trend order is supplied to the `z` equation, so its target
includes an unobserved stochastic flow realization. The comparison tests surrogate
fidelity to this synthetic simulator only. It is
not a test of global stability, market validity, or strategy performance.

This first executable candidate isolates only the band crossing through signed excess
error and an outside-band interaction. It does not yet model capacity-binding or
withdrawal transitions as separate state branches. Those effects remain fixed by each
condition-specific fit here; adding explicit transitions requires another frozen model
version and a new held-out evaluation.

The result script and exact copied configs, model coefficients, seed-level metrics,
cell metrics, per-trajectory metrics, and checksums are saved in a unique output
directory under `output/hybrid/`; the runner refuses to overwrite an existing run ID.
To reproduce an existing run, pass a fresh `--output` directory and compare the
numerical artifact checksums. The prior confirmation and exploratory H1c outputs
remain unchanged. H1c's earlier diagnostic uses a different, unsigned excess-error
target and is historical; it must not be conflated with this signed-error analysis.

## Empirical-validation gate (DATA-001)

Before claiming correspondence with a live market, document the exact chain, pool,
token ordering, fee tier, block range, CEX reference venue, timestamp convention,
source/license, missing-data policy, and synchronization procedure. Construct a
reproducible dataset containing reserve snapshots and swaps, LP add/remove events,
external prices, and the available fee/gas and execution timing. Split calibration and
evaluation chronologically and, where possible, by pool. Report held-out checks for
price impact, arbitrage timing/frequency, tracking error, recovery/departure, and
liquidity changes. Quantify measurement and parameter uncertainty. If the required
data cannot be obtained, retain the synthetic scope and mark empirical validation as
open.

## Verification boundary

The Lean project verifies selected exact algebraic properties. Python differential
tests check a finite grid against the exact rational oracle. Neither proves that the
behavioral assumptions represent market participants. Lean verification and empirical
validation are separate acceptance gates.

# ODD specification: deterministic and stochastic CEX/DEX MVP

This specification covers deterministic E0/E1/E2 mechanism checks, deterministic E3
policy selection, and a separate stochastic representative-agent selection model
(version 0.4.0). It remains narrower than the heterogeneous-agent model proposed for
the thesis.

## Purpose and patterns

The model tests mechanical implications of H1a and H1b:

- Following an exogenous CEX price shock, bounded arbitrage can reduce the DEX/CEX
  discrepancy; lower capacity can slow or prevent return to a declared band.
- With the same starting pool and fixed x-sale, proportional withdrawal of both CPMM
  reserves leaves the marginal price unchanged before the sale but increases the
  sale's price impact.
- Under identical shocks and repeated exogenous x-sales, a one-shot threshold LP
  withdrawal can reduce depth and amplify tracking error relative to a static-LP
  control.

It includes a first held-out H1c map diagnostic, but does not establish general map
validity, estimate cascade probabilities, model strategic agents, or establish external
validity.

## Entities, state variables, and scales

- **CEX reference:** exogenous scalar price `p_C > 0`; it changes only at configured
  shock ticks.
- **DEX pool:** zero-fee constant-product reserves `x > 0`, `y > 0`, invariant
  `k = xy`, and marginal price `p_D = y/x` (units of y per x).
- **Arbitrage capacity:** maximum input per order as a fraction of the reserve of the
  asset being input. Capacity is zero in the arbitrage-off condition.
- **Execution delay:** optional integer tick delay between submitting a capacity-limited
  arbitrage order and executing it. Only one order may be pending; no second order is
  submitted until the pending order executes.
- **LP intervention:** E2 scales both reserves by the same remaining fraction before
  a fixed sale of x. The withdrawal is exogenous and has no decision rule.
- **E3 flow and LP rule:** both paired conditions receive the same fixed x-sale each
  tick. The adaptive policy observes post-sale absolute log error and, once only,
  proportionally scales both reserves if the configured threshold is exceeded.
- **Stochastic representative roles:** one bounded arbitrage wallet, one noise-trader
  wallet, one trend/panic-trader wallet, and one LP wallet. The arbitrageur follows the
  same band/capacity rule as E0/E1. Noise activity and direction are pre-generated from
  one seed-specific stream. The trend/panic role follows the realized DEX return after
  the noise order, or makes one larger x-sale after a configured negative-return trigger.
  The LP condition is static or withdraws once after the log-error trigger.
- **Wallet state:** each trading role holds configured x/y balances. Swaps debit the
  input asset and credit the exact CPMM output; proportional LP withdrawal credits the
  withdrawn reserves to the LP wallet. Arbitrage inventory is finite and recorded.
- **Observables:** `e = log(p_D/p_C)`, signed excess
  `d = sign(e) max(|e| - gamma, 0)`, reserves, prices, and time to sustained return.
- **Scale:** each tick is one abstract event interval. No wall-clock or real-market
  timescale is asserted.

## Process overview and scheduling

For E0/E1, initialize the pool and CEX at the configured prices, apply the one-time
log-price shock at `shock_tick`, then calculate an arbitrage order if the error exceeds
the no-arbitrage band. With zero delay, execute that order in the same tick. With
positive delay, queue it and execute it after the configured number of ticks; the queue
blocks further submissions until execution. The event order is:

1. Apply configured CEX shock, if due.
2. Execute a pending arbitrage order if its delay has elapsed.
3. If there is no pending order and the error lies outside the band, calculate a
   zero-fee CPMM trade toward the nearest band edge and cap its input by the configured
   reserve fraction.
4. Execute immediately for zero delay or queue the order for delayed execution.
5. Record post-event prices, reserves, error, excess error, and queue event.

E2 is a separate paired mechanical comparison: record initial state, optionally scale
both reserves, record the unchanged marginal price, execute the same absolute x-sale,
then record the post-sale impact. Arbitrage is disabled in both E2 conditions.

E3 applies the same CEX shock and exogenous x-sale sequence to a static-LP control and
the one-shot threshold-withdrawal policy. After each sale, the policy may withdraw once;
arbitrage then executes immediately under the shared cost band and capacity. The
deterministic selection grid crosses four trigger thresholds with four remaining-reserve
fractions, with a static/adaptive pair for each setting. It is not a held-out confirmation
design and does not estimate performance across a population of LP policies.

The stochastic selection runner in `abm.py` initializes the representative wallets and
reuses the same pre-generated noise orders across paired conditions for each seed. Its
per-tick order is:

1. Apply the configured CEX shock, if due.
2. Execute the scheduled noise order, if active and funded.
3. Observe the resulting DEX return; execute a trend-following order or the one permitted
   panic sale if the trigger is crossed.
4. Apply the one-shot proportional LP withdrawal if the selected policy's error trigger
   is crossed.
5. Execute immediate capacity-limited arbitrage toward the no-arbitrage band.
6. Record pool state, role actions, wallets, tracking metrics, and asset-conservation
   residuals.

For each shock sign, it pairs arbitrage capacities 0, 0.005, and 0.03 under static LP
behavior, and pairs adaptive LP with the high-capacity static condition. It selects a
seed count in batches to meet a configured half-width target for approximate 95% normal
intervals on paired mean peak-error differences, subject to minimum and maximum seed
counts. This is exploratory policy/mechanism selection, not confirmation.

## Design concepts

- **Adaptation:** the E3 LP responds once to the observed post-sale tracking error using
  a fixed threshold rule; it does not learn or optimize.
- **Objectives:** the arbitrage operation reduces absolute error to the nearest band
  edge when capacity permits; it does not optimize a utility function.
- **Learning/prediction:** none.
- **Sensing/interactions:** the arbitrage operation observes the current pool and CEX
  prices perfectly; optional execution delay is represented by a queued order.
- **Stochasticity:** the deterministic runner has none. The separate selection model
  uses a seeded Bernoulli/direction schedule for noise orders. Conditions with the same
  seed share those scheduled orders; trend/panic actions are endogenous to each
  condition's resulting price path. Repeated runs with identical code/configuration are
  numerically identical.
- **Collectives:** none.
- **Observation:** every configured tick and E2 intervention stage is written to a
  long-form CSV; summary metrics are written separately.

## Initialization

Deterministic model version 0.3.0's checked-in configuration initializes both reserves to 10,000
units, both prices to 1, applies a CEX log-return shock of 0.1 at tick 1, uses
`gamma = 0.003`, sets `execution_delay_ticks = 0`, and runs 20 ticks. E1 uses
reserve-input capacity fractions 0.005 and 0.03. The sensitivity grid varies log bands 0, 0.003, and
0.01 and delays 0, 1, and 2 ticks. E2 sells 500 units of x and leaves 0.45 of each
reserve in the withdrawal condition. These are transparent mechanism-check settings,
not calibrated estimates or recovered values from the unavailable preliminary
simulator. E3 uses ten ticks of 200-unit x-sales, triggers one withdrawal when absolute
log error exceeds 0.02, leaves 55% of both reserves, and applies 0.03 arbitrage capacity
with zero delay. The E3 selection grid crosses trigger thresholds of 0.01, 0.02, 0.04,
and 0.08 with remaining-reserve fractions of 0.40, 0.55, 0.70, and 0.85; every setting
has a paired static control.

Stochastic model version 0.4.0 uses the same initial pool and band, shocks of -0.1 and
0.1 at tick 1, and a 20-tick horizon. Noise activity probability is 0.7 with order size
0.004 of the initial reserve. The trend signal threshold is 0.001 DEX log return and
its order is 0.006 of the initial reserve; the one-time panic sale is 0.02 after a DEX
return at or below -0.015. Trader wallets start with two times each initial reserve and
the arbitrage wallet with five times each reserve. Adaptive LP leaves 55% of the pool
when absolute error exceeds 0.02. The replication loop requires at least 50 seeds and
stops at 500 or when every paired mean peak-error interval half-width is at most 0.005.
These are transparent selection values, not calibrated estimates.

## Input data and submodels

There are no empirical inputs. CPMM swaps use exact zero-fee reserve formulas. To sell
`q_x` into the pool, `x' = x + q_x` and `y' = yx/x'`; to input `q_y`, `y' = y + q_y`
and `x' = xy/y'`. A proportional LP withdrawal changes reserves to `(rx, ry)` and
preserves `y/x`. The symmetric no-arbitrage band is a configured log-price threshold
that summarizes costs; fees, gas, and opportunity costs are not separately modeled.
Delayed execution in E0/E1 is a deterministic queued-order approximation: there are no
independent trades while an order is pending. The stochastic selection model applies
wallet limits to the representative trader and arbitrage roles and checks conservation
of each asset across the pool and wallets.

## Analysis and limits

The runner reports maximum absolute log error, maximum excess error, first tick of a
two-consecutive-tick return to band (or `null`), and E2 absolute log impact and
percentage price change. Band comparisons use a `1e-12` log-error tolerance for
floating-point roundoff. The band-return metric is descriptive and its two-tick rule
must be held constant across paired comparisons.

`h1c.py` fits a separate two-state map for each representative-agent condition on the
selection shocks and evaluates it on disjoint seeds and held-out shock magnitudes. It
labels an ABM path contractive when mean absolute excess error over ticks 16–20 is lower
than over ticks 1–5; Schur stability is the map prediction. In the current holdout, all
four maps were Schur-stable but only three of eight condition/shock majority labels
agreed. The average one-step prediction RMSE was 0.01837 for `d` and 0.00840 for `z`;
the fitted `z` equation had near-zero selection R-squared. These are limits of this
representative-agent implementation, not a general rejection of reduced maps.

Before interpreting a run, `check_invariants.py` separately checks finite positive
reserves across 2,654 deterministic states, zero-fee `xy` preservation for both swap
directions, price preservation after proportional withdrawal, the expected increase in
fixed-sale impact at reduced depth, arbitrage direction/capacity behavior under positive
and negative shocks, and the shared external path in the E3 pair. It also runs 24
stochastic trajectories to verify paired noise schedules and asset conservation. These
are mechanics/accounting checks, not inferential tests of H1a, H1b, or H1c.

The scope excludes a heterogeneous agent population, strategic objectives, endogenous
LP learning, explicit fee accounting, CEX feedback, broader H1c generalization across
agent policies and cost regimes, and market data. The stochastic selection model uses
representative roles and researcher-chosen rules. Its parameter sweep is selection
evidence; the H1c run is a narrow held-out check under the same policies. Neither is a
reproduction of the manuscript's preliminary table. Add excluded mechanisms only through
a separately versioned extension with new paired configurations and validation. Do not
use these outputs to replace the manuscript's preliminary table without checking all
definitions and regenerating its full set of comparisons.

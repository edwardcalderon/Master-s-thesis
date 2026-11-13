# Stochastic ABM role taxonomy and selection design

**Status:** the author approved the four-role taxonomy. The implemented policy rules and
parameter values below are representative selection assumptions, not confirmation evidence
and not general behavioral estimates.

## Four author-approved roles

The model represents four roles, combining trend-following and panic selling in one
policy as requested:

1. **Arbitrageur:** observes the CEX reference and CPMM marginal price, submits a
   corrective zero-fee swap outside the configured log band, and is bounded by the
   configured input-capacity fraction. This reuses the verified E0/E1 rule.
2. **Noise trader:** on an independent Bernoulli activity draw, randomly buys or sells
   asset `x`. Its direction does not depend on price signals.
3. **Trend/panic trader:** follows the sign of the realized DEX log return after the
   current noise order when that return clears a configured signal threshold. If that
   return crosses a negative panic threshold, it instead submits a larger `x` sale. The combined role
   keeps the four-role count while representing the noise, trend, and panic language in
   the evidence chapter.
4. **Liquidity provider:** deposits reserves at initialization. The paired conditions
   are static liquidity and a one-time proportional withdrawal when absolute
   CEX/DEX log error crosses a configured trigger.

These explicit, testable policies instantiate the approved role taxonomy. They do not
describe fully strategic agents or recover the absent preliminary simulator.

## Initial selection conditions

- Keep the CPMM, initial reserves, CEX shock, band, trader order sizes, and random
  noise-order schedule identical within each paired comparison.
- Compare arbitrage capacities `0`, `0.005`, and `0.03` under static LP behavior for
  H1a; compare static and threshold-adaptive LP behavior at `0.03` capacity for H1b.
- Use one deterministic random stream per seed to pre-generate noise-trader activity and
  direction. Reuse that schedule for every condition with the same seed. The
  trend/panic rule is endogenous to each condition's own price history.
- Give each trader a configured initial `x` and `y` inventory. Cap each submitted order
  at the available inventory and debit/credit balances using the exact CPMM swap
  amounts. Record order clipping and the pool-plus-wallet asset totals.
- Use the event order: apply CEX shock; execute noise order; execute trend/panic order;
  apply an eligible LP withdrawal; execute immediate arbitrage; record state.
- Keep latency/cost sensitivity in the existing deterministic E0/E1 grid initially.
  The first stochastic pass holds the band and delay fixed to avoid confounding the
  agent-flow selection exercise.

## Replication and reporting

- Pair conditions by seed and write each seed's trajectory and paired differences.
- Choose the run count by a predeclared Monte Carlo precision target for the paired mean
  peak-error difference, with a maximum seed count and an explicit unmet-target status.
  Report the normal-approximation interval as exploratory, especially if the target is
  not met.
- Report paired mean effects and uncertainty alongside median, quantiles, and the full
  seed-level outcomes. Do not treat time ticks or repeated deterministic configurations
  as independent replications.
- Keep the selection conditions and any later confirmation conditions in separate
  configuration files. Do not fit or claim H1c from the selection results.

## Known omissions

The first ABM selection pass still omits explicit trading fees, gas, latency, CEX
feedback, strategic objectives, endogenous position sizing, and empirical calibration.
The panic trigger and trader sizes are researcher-selected configuration values; they
must be sensitivity-tested before confirmation.

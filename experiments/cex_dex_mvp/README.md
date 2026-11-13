# CEX/DEX hypothesis MVP

This MVP includes a deterministic mechanism runner and a separate stochastic selection
model. Neither reproduces the unavailable preliminary simulator or validates the model
against market data.

- **E0/E1:** an exogenous CEX log-price shock, with arbitrage disabled, low-capacity,
  or high-capacity; report log tracking error and the first tick of a two-tick
  sustained return to the no-arbitrage band.
- **E2:** the same absolute sale into the same CPMM before and after proportional LP
  withdrawal; report the immediate log-price impact without arbitrage.
- **E3:** a static-LP control and a one-shot threshold-withdrawal policy receive the
  same CEX shock and repeated exogenous x-sales; compare peak error, recovery, and
  minimum geometric pool depth.

## Run

Requires Python 3.10 or newer and no third-party packages:

```bash
pnpm experiment:mvp:run
```

The command writes `timeseries.csv`, `summary.json`, the exact `config.json`, and
`run_metadata.json` under `experiments/cex_dex_mvp/output/<run-id>/`. The run ID hashes
the configuration and runner source. Numeric outputs are deterministic; the metadata
timestamp is not.

Before interpreting or promoting these outputs, run the independent accounting and
mechanism checks:

```bash
pnpm experiment:mvp:check
```

The checker validates positive finite reserves across 2,654 deterministic E0/E1/E2/E3
states. Eight checks cover `xy` preservation for both swap directions, marginal-price
preservation after proportional withdrawal, increasing fixed-sale impact at reduced
depth, arbitrage direction and capacity behavior under positive/negative shocks, paired
E3 external paths, and the configured E3 rule's effect on peak error. Its ninth check runs
24 stochastic trajectories over 504 states and verifies paired noise orders and asset
conservation. It prints JSON and does not change the scenario runner's outputs.

To reproduce the deterministic shock-size, arbitrage-capacity, cost-band, execution-
delay, and liquidity-depth sensitivity grid:

```bash
pnpm experiment:mvp:sweep
```

The tracked `sweep.json` is the exact parameter grid: 108 E0/E1 points, four E2 depth
levels, and 16 paired E3 policy settings (static/adaptive, 144 summary rows total). The
cost proxy is the configured no-arbitrage log band; it is not an explicit gas or fee
ledger. Execution delay queues one capacity-limited arbitrage order, blocks further
submissions while that order is pending, and executes it after the configured number of
ticks. E3 varies the one-shot withdrawal trigger and remaining reserve fraction under
the same fixed CEX shock and x-sale path. This is policy selection only; no E3 setting is
a held-out confirmation condition. The command writes a summary CSV, combined time
series, copied inputs, and checksummed metadata under
`experiments/cex_dex_mvp/output/sweeps/`. These are sensitivity points in a noise-free
mechanism model, not independent replications or statistical evidence.

The checked-in E3 selection case uses a 0.1 log shock, ten 200-unit x-sales, a one-shot
withdrawal trigger at 0.02 absolute log error, 55% reserves remaining after withdrawal,
and 0.03 arbitrage capacity. The static control peaks at 0.08049 log error and returns
to band at tick 6; the selected adaptive rule peaks at 0.18249 and does not return
within the horizon. The wider E3 grid varies four thresholds and four reserve fractions;
it supports policy selection only and does not establish a general claim about adaptive
LPs. In the current grid run, the policy withdrew in all 16 settings; peak error was
higher than its paired static path in 12 settings and unchanged in four. The paired
peak error difference ranges from 0 to 0.29604 log units. These are deterministic selection
results. Heterogeneous populations and confirmation conditions remain.

## Stochastic selection model

Run the stochastic paired selection experiment with:

```bash
pnpm experiment:mvp:abm
```

The versioned `abm_config.json` implements four representative roles: bounded
arbitrageur, random-direction noise trader, trend/panic trader, and an LP that is static
or follows the one-shot threshold rule. Traders have finite x/y wallets; every recorded
tick checks pool-plus-wallet conservation. Each seed generates a noise-order schedule
that is reused for all paired conditions. The run compares arbitrage capacities 0,
0.005, and 0.03 under both signs of the CEX shock, plus adaptive versus static LP at
high capacity. The trend/panic policy follows the DEX return after the current noise
trade and may panic-sell once after a sufficiently negative return.

The run stops when the preconfigured approximate 95% interval half-width for paired
mean peak-error differences is at most 0.005 log units for all contrasts, after at least
50 seeds, or at the maximum of 500. The current selection run used 300 seeds and wrote
50,400 trajectory rows. At a +0.1 shock, high versus zero arbitrage capacity changed
mean peak error by -0.10690 (approximate 95% interval -0.11176 to -0.10204). Adaptive
versus static LP changed it by +0.00529 (0.00426 to 0.00632); at a -0.1 shock the peak
error difference was approximately zero, while mean cumulative excess error increased
by 0.00456. These model-conditional selection results use researcher-chosen policies
and parameter values; they are not confirmation evidence or manuscript results.
Outputs include the config, replication seeds, seed-level paired effects, aggregate
summaries, full trajectories, and checksummed run metadata under
`experiments/cex_dex_mvp/output/abm/<run-id>/`.

## H1c reduced-map evaluation

After the stochastic selection run, execute the held-out map analysis with its exact
selection artifact path:

```bash
pnpm experiment:mvp:h1c -- --selection-run-dir experiments/cex_dex_mvp/output/abm/<run-id>
```

The analyzer fits a separate two-state map for each of the four conditions on the
selection shocks (-0.1 and +0.1), then tests those fixed coefficients on new seeds
1000–1299 and held-out shocks (-0.05 and +0.05). The state, flow normalization, event
order, Schur criteria, early/late error labels, and limits are specified in
[`H1C_PROTOCOL.md`](H1C_PROTOCOL.md). Outputs include coefficient fits, one-step errors,
condition-level contraction labels with Wilson intervals, held-out trajectories, and
checksummed metadata under `experiments/cex_dex_mvp/output/h1c/<run-id>/`.

The current holdout matched the map's Schur label in 3 of 8 condition/shock groups; all
four fitted matrices were Schur-stable, and the average one-step RMSE was 0.01837 for
`d` and 0.00840 for `z`. Several observed conditions were mostly persistent. The map's
`z` equation had near-zero selection R-squared across conditions. This is weak
classification under this representative-agent model, not support for general
stability claims. The holdout changes shock magnitude and seed stream but keeps agent
rules, capacities, band, and other parameters fixed.

## Explicit assumptions

- Two reserve CPMM with marginal price `p_D = y/x`, zero swap fees, and positive
  reserves. Asset `x` is the asset sold into the pool in E2.
- The CEX is an exogenous reference. Its one-time shock is multiplicative in log-price.
- The no-arbitrage band is symmetric in log-price and summarizes costs; gas and fees
  are not separately charged in this first mechanical pass.
- The base arbitrage case executes in the same tick after a CEX shock and trades only
  as far as the nearest band edge, subject to a maximum input fraction of the relevant
  reserve. The sensitivity grid also allows integer-tick execution delay.
- E2 proportionally scales both reserves before the sale, preserving the marginal
  price and changing depth. Static and withdrawn-liquidity counterfactuals use the same
  starting reserves and sale amount.
- The deterministic E0-E3 experiments have no stochastic innovations or endogenous
  trader flow. The stochastic selection model adds representative noise and
  trend/panic flow, but not a heterogeneous agent population or external market data.
  Its first H1c holdout is limited to new shocks and seeds under the same policies.

These boundaries make E0/E1/E2/E3 mechanical checks, the stochastic model an exploratory
selection ABM, and the first H1c run a narrow held-out diagnostic. They do not reproduce
the manuscript's currently unverified table or establish evidence about live markets. See the
[ODD and event contract](ODD.md) and task status in
[`../../.agents/TASKS.md`](../../.agents/TASKS.md).

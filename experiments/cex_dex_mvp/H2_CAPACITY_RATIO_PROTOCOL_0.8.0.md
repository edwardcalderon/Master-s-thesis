# H2 capacity-ratio diagnostic 0.8.0

Status: post-hoc exploratory check specified from the capacity-ratio review. It is
not a new confirmatory hypothesis test and it does not validate a market law.

## Purpose

Check whether the configured pressure ratio

`R(q,x,c) = 2*log(1 + q/x) / (2*log(1 + c))`

orders the two shallow E3 controls as expected. The fixed-initial-reserve cap should
make E3's flow and panic ratios approximately match shallow static E1. With the panic
order removed, the same fixed-capacity configuration is predicted to produce no later
departures after recovery.

## Design

- Model 0.4.0, depth factor 0.5, E3 threshold withdrawal, and fixed absolute orders.
- Seeds 2000--2299, reused from the exploratory H2 replay; three shocks: -0.05,
  -0.10 and -0.20.
- Verification arm: fixed-initial-reserve arbitrage cap with the configured panic
  order active (900 paths).
- Check arm: the same fixed cap with `panic_max_orders_per_run=0` and trend flow
  retained (900 paths).
- Each path records recovery, post-recovery departure episodes, episode starts that
  coincide with a panic-order tick, and capital-limited orders.

The no-panic arm is a targeted posterior check, not an independent sample. The
configured ratios use aligned order sizes and approximate reserves; they are explanatory
diagnostics. Episode overlap is descriptive and does not identify within-tick causality.

## Acceptance checks

- The active-panic verification arm reproduces the archived fixed-capacity episode
  counts: 123, 101 and 53 departure paths for shocks -0.05, -0.10 and -0.20, with
  one episode per departing path and every episode starting on the panic tick.
- The 900-path no-panic arm has zero panic orders and reports whether any later
  departures remain. A zero result supports the configured R explanation within this
  simulator; it does not establish a universal threshold or causal decomposition.
- The output includes source/configuration hashes and a second-run reproducible command.

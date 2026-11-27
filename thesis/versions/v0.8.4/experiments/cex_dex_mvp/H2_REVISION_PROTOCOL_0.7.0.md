# H2 revision replay protocol 0.7.0

Status: exploratory follow-up specified from reviewer feedback on 2026-11-26. The
post-recovery outcomes are post hoc and do not replace the original confirmatory H2
contrast. This replay uses the archived synthetic model and seed streams; it is not
market validation.

## Questions

1. Does the E3-minus-E1-high contrast remain when tracking error is measured only after
a two-tick sustained return, rather than from the shock tick?
2. Are later departures in the shallow fixed-order case removed by the existing
no-panic ablation, while E3 departures remain?
3. How much of the E3/static contrast changes when the arbitrage input cap is held at
its initial-reserve amount instead of shrinking with active reserves?

## Frozen inputs and run design

Use model 0.4.0, engineering analysis 0.6.0, its order-scaling variants, configuration,
and seeds 2000--2299. Recreate each seed's pre-generated noise schedule and reuse it
for paired conditions.

- Post-recovery H2 outcomes: E1-high static and E3 threshold withdrawal; fixed absolute
  order sizes; depth factors 0.5, 1 and 2; shocks -0.05, -0.10 and -0.20.
- Departure diagnosis: the same two conditions at depth 0.5 and all three shocks, with
  fixed orders and with the panic order disabled. Trend-following behavior remains on.
- Capacity counterfactual: the same shallow fixed-order cells under both the original
  reserve-linked cap and a cap fixed to 3% of the initial input-token reserve. Include
  E1-high and E3 so withdrawal can be contrasted at the same absolute cap.

The fixed-initial-reserve mode uses `min(c * initial input reserve, active input reserve)`
per arbitrage trade. For a sell-X order the input reserve is X; for a buy-X order it is Y.
The existing reserve-linked mode remains unchanged and is the default.

## Outcomes and inference

A sustained return starts at the first of two consecutive end-of-tick observations
inside the band and is confirmed on the second. Post-recovery outcomes start at the
following tick, so the confirmation observations themselves cannot contribute:

- Primary exploratory outcome: sum of positive excess error,
  `sum(max(abs(e_t) - gamma, 0))`, after confirmation through tick 20.
- Secondary exploratory outcomes: maximum `abs(e_t)` and maximum excess after
  confirmation; these are undefined if no post-confirmation tick is observed.
- Departure episodes: contiguous runs of end-of-tick observations outside the band
  after confirmation. Record the episode count and whether its first out-of-band tick
  also records a panic order. This event overlap is descriptive, not causal attribution.
- Report recovery coverage and paired seed counts next to post-recovery contrasts.
  Pair only seeds in which both compared paths recovered and have post-confirmation
  observations. Bootstrap paired seeds for intervals; no confirmatory p-values or
  multiplicity claims are planned.

For the pressure diagnostic, retain the continuous noise-plus-trend input `q=100` and add
an explicitly conservative maximum same-direction one-tick input `q=240` (40 noise plus
200 panic; panic replaces trend in the agent rule). Compute each nominal impact as
`2*log(1+q/x)` and divide by `2*log(1+c)`. Use the initial reserve scale for E1 and 55%
of it for E3. These are configured worst-case ratios, not realized tick-level ratios or
threshold laws. Report the no-panic ablation separately to distinguish a one-time panic
mechanism from departures that remain under continued noise/trend flow.

All outputs must carry the source/configuration hashes and state that paths were
replayed from existing seeds. Keep the manuscript conclusion bounded to this simulator.

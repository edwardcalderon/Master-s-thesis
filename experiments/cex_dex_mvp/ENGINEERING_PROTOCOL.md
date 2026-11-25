# Engineering sensitivity protocol — analysis 0.6.0

Fixed before executing the new seed stream on November 25, 2026. It is informed by
v0.5.0 findings and is supplementary sensitivity analysis, not retrospective
registration of the original hypotheses or validation against real markets.

## Questions and design

1. Does a first two-tick return imply continued tracking? Measure recovery confirmed
   by deadlines 5/10/20, terminal in-band status, and any later departure after the
   first complete two-tick return. Never convert abstract ticks into seconds.
2. Does the depth-dependent LP effect survive order normalization and panic removal?
   Compare the original absolute order sizes with orders proportional to initial
   reserves, and a separate fixed-order variant with panic disabled (trend remains).
3. Which engineering interpretations survive these controls? Report every condition,
   depth and shock, including null effects and deterioration.

Run seeds 2000–2299, disjoint from exploration 0–299 and confirmation 1000–1299,
across depths 0.5/1/2, shocks -0.05/-0.10/-0.20, all five frozen confirmation
conditions and three variants: 40,500 paths of 20 ticks. Shared seed schedules pair
conditions. Use model 0.4.0 without code changes. Fixed-order depth scaling uses the
original confirm.py convention. Proportional orders scale with initial pool reserves
(and wallets), not with the remaining reserves after withdrawal. No-panic disables
only the permitted panic sale, retaining the trend trader.

## Definitions and inference

Recovery is observed only after the second in-band tick: a pair beginning at tick 5
is confirmed at tick 6 and does not meet a tick-5 deadline. A later departure is any
out-of-band tick after that pair, not a failure to ever recover. Report its unconditional
frequency and its frequency among recovered paths. Non-recovery is right-censored;
do not count tick 21 as an observed recovery. Band tolerance is 1e-12.

Each cell has 300 independent seeds. Wilson 95% intervals describe cell recovery
proportions. Aggregate rates across cells are descriptive equally weighted design
averages. For adaptive-minus-static maximum response, average the three paired shock
effects within each seed at each depth; report mean +/- 1.96 SE across 300 seeds.
These intervals are approximate and unadjusted; they do not add confirmatory tests.

## Deliverables and relevance

Save configuration, source hashes, seed metrics, cell/condition summaries, depth-wise
paired effects, and checksummed metadata under a new run ID. Reproduce them in a
second output root. Export only compact tables plus a manifest for the manuscript.

Translate results into candidate requirements for pool monitoring, router stress
fixtures and surrogate acceptance. An actual deployment would additionally need
synchronized pool events and reference quotes, token orientation/decimals, transaction
fees, execution delay, reorganization handling and held-out empirical evaluation.
The study does not establish a profitable strategy, safe oracle threshold, production
latency budget, or causal effect of real LP behavior.

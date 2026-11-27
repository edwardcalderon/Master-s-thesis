# Snapshot record: v0.8.4

- Manuscript revision: v0.8.4, English and Spanish; the approved main and evaluation questions are unchanged from v0.8.3.
- The H1 interpretation distinguishes the isolated-pool correction deadline from the finite-horizon multi-agent response. At arbitrage capacity $c=0.03$, deadline recovery rates rise with depth; all tested paths return by tick 20.
- H2 uses a post-recovery excess-area outcome. The exploratory replay reuses seeds 2000--2299 and runs 9,000 paths; it is not a new independent or confirmatory sample.
- At shallow depth, static E1 departures are single episodes associated with the configured panic order; none are observed in the matched no-panic ablation. Recovered E3 paths show recurrent departures with or without panic.
- A fixed-initial-reserve capacity control at shallow depth reduces the post-recovery E3-minus-E1-high area contrast from 0.122--0.124 to 0.0036--0.0097. This is a post-hoc, recovery-conditioned result at one depth, not a general causal decomposition.
- H3 remains limited: the two-state map does not outperform scalar AR(1); the band-aware replay uses the realized future CEX path and is not a real-time forecast.
- The replay exactly matches archived metrics in all 7,200 reserve-linked-cap paths. The raw replay, compressed input fixture, configurations, protocol, runner dependencies, and hashes are preserved under experiments/cex_dex_mvp/.
- Derived tables, plotting inputs, and manifests are in figures/data/; engineering inputs referenced by the manuscript are in figures/engineering/.
- The expanded bilingual abstract covers the benchmark, main H1 results, H2 sensitivity and mechanism replay, reduced-map results, and external-validity limits. The PDF layout check verifies that each abstract and its keywords remain together on one page and reports rendered page share.
- All findings remain conditional on the zero-fee synthetic simulator. End-of-tick counts do not establish intra-tick causality; no market effect or operational threshold is validated.
- The source bibliography contains 87 records; the compiled bibliography contains 56 cited items (55 scholarly works and one repository record).

To replay from this snapshot, run the command in README.md. Keep v0.8.3 and earlier snapshots unchanged.

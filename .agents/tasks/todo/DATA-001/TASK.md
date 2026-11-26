# DATA-001 — Bounded empirical validation path

- **Owner:** `edcalderon`
- **Status:** TODO
- **Goal:** Validate selected v0.8.0 model findings and v0.6.0 monitoring/order-scaling requirements on one predeclared real CEX/DEX pair after access and data rights are established.

## Acceptance criteria

- Document source licensing, trading-pair identity, timestamps, and data provenance.
- Provide a reproducible acquisition/ingestion path and preserve raw/processed data
  boundaries.
- State external-validity limits and keep real-market claims separate from synthetic
  mechanism results.
- Predeclare the venue/pool pair, sample window, evaluation unit, target patterns,
  chronological and pool-level holdouts, and calibration/evaluation split before
  inspecting evaluation outcomes.
- Reconcile reserve/swap and CEX events using a documented clock and ordering rule;
  record fees, gas, block ordering, execution delay, liquidity changes, reorg handling,
  and source data rights where available.
- Report model disagreement and measurement/parameter uncertainty rather than only a
  best-fit parameter set.

## Validation design inherited from v0.6.0

Predeclare pair, venues, period, asset orientation/decimals, timezone and observation
unit. Align CEX bid/ask and depth with DEX pool reserves, swaps and liquidity events;
retain raw events and record fees, gas, latency, block ordering, reorg handling and
provider data rights. Evaluate first sustained return, terminal in-band status, later
departure, order-to-reserve ratio and held-out surrogate performance. Keep these market
observations separate from the synthetic 40,500-path study; do not transplant its
thresholds to production.

## v0.8.0 model extension handoff

The hybrid map's 1.7% average recursive price-error gain is synthetic and concentrated
in the low-capacity, depth-2 condition. It does not improve flow-pressure prediction and
uses a known CEX shock path in recursive evaluation. If real data access is obtained,
predeclare whether the evaluation targets CEX-to-DEX price discrepancy, signed price
error, or flow pressure; document the inputs available at prediction time and avoid
feeding future market observations into a claimed live forecast. Coordinate model
robustness work with THESIS-006, but retain a separate real-data protocol and holdout.

## Dependencies

- Synthetic model mechanics and run metadata are stable.
- The empirical question, period, source, and data rights are declared before collection.

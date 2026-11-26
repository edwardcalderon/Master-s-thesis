# Snapshot record: v0.8.0

- Manuscript revision: v0.8.0 (English and Spanish, same claims and evidence).
- Model: 0.5.0; analysis: 0.1.0.
- Hybrid comparison run: `cex-dex-hybrid-1d1d9d2f8c5b`.
- Selection: seeds 3000–3299, depth 1, shocks −0.10/+0.10.
- Confirmation: seeds 4000–4299, depths 0.5/2, shocks −0.20/−0.05/+0.05/+0.20.
- Result: mean held-out recursive price-error MAE improves from 0.030807 to 0.030291;
  paired seed-bootstrap gain 0.000516, 95% interval [0.000499, 0.000533]. The gain is
  concentrated in low-capacity arbitrage at depth 2; flow-pressure prediction does not
  improve.
- The result evaluates fidelity to the synthetic representative-agent simulator only.
  It does not establish real-market validity, stability of the hybrid map, or
  stochastic stability of the full simulator.
- Compact chart and web data: `figures/data/hybrid_depth_condition.csv`,
  `figures/data/hybrid_shock_depth_condition.csv`, and
  `figures/data/hybrid_export_manifest.json`.
- The immutable v0.7.0 snapshot is unchanged.

# Snapshot record: v0.8.3

- Manuscript revision: v0.8.3, English and Spanish.
- The question wording change is recorded in question-control.json; the prior approval record is preserved and the updated question is approved for this revision. The English and Spanish questions target the tested capacity/depth grid and continuous tracking-error paths.
- H1 results compare simulated sustained-return rates at the isolated-pool first-entry deadline and at tick 20; the distinction between first entry and two-tick sustained return is explicit.
- H2 adds a post-hoc, tick-end maximum absolute tracking-error contrast and retains the legacy peak-displacement result as a separately scoped diagnostic.
- E3 recovery persistence is reported by depth; the 31.2% result is the equally weighted nine-cell simulator summary, not a market estimate.
- R_nom is labeled as an exploratory nominal diagnostic. The static shallow-depth counterexample rejects its use as a sufficient threshold for sustained tracking.
- Derived outputs and checksums are in figures/data/revision_findings_manifest.json; the analysis script is copied under analysis/.
- The analysis uses archived run metrics and performs no new simulation or market-data validation. Manifests use repository-relative input paths. All conclusions remain conditional on the zero-fee synthetic model.
- The source bibliography has 87 records; the compiled bibliography has 56 cited items (55 scholarly works and one repository record).

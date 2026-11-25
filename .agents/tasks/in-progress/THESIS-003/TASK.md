# THESIS-003 — Reconcile manuscript evidence and evaluate H1c

- **Owner:** `edcalderon`
- **Status:** IN PROGRESS
- **Focus:** v0.5.0 confirmation evidence recorded; acceptance review remains.
- **Started:** 2026-11-12

## Goal

Replace or qualify preliminary manuscript claims using traceable output, then evaluate
the reduced map on held-out configurations without concealing disagreement.

## Acceptance criteria

- Active tables and figures trace to versioned configurations, run IDs, and runner code.
- Selection data and held-out data are kept separate, with the limits of the current
  held-out scope stated explicitly.
- Classification errors, sensitivity to shock direction, and model limits are reported
  in both English and Spanish editions.
- The bilingual editions carry the same manuscript revision and compile together.

## Current evidence update — 2026-11-25

Manuscript v0.5.0 now reports `cex-dex-confirm-5b06486d695e` (analysis 0.5.0,
model 0.4.0), with 300 confirmation seeds and 13,500 runs across depths 0.5/1/2,
negative shocks -0.05/-0.10/-0.20, and five conditions. See
`experiments/cex_dex_mvp/confirm_config.json` and `thesis/figures/data/manifest.json`.
This supersedes the older selection and 3-of-8 holdout as active H1-H3 evidence.
H1 missed its precision target despite a clear negative contrast; H2's primary
maximum-response effect is concentrated at depth 0.5; H3 beats persistence overall
but not scalar AR and remains weak at regime classification. Results are synthetic.

The progress entries below are historical. References to confirmation still being
pending describe the pre-v0.5.0 state. Further fee, policy, or long-horizon extensions
require separate versioned protocols. Review acceptance explicitly before closing this
task; the planning patch does not claim a fresh experimental or manuscript audit.
SIM-002 consumes the frozen confirmation evidence for presentation.

## Historical progress

- Published manuscript revision v0.4.0 to make the existing simulation question,
  objectives, and held-out-map limits explicit in both languages. Archived the published
  v0.3.1 source and the v0.4.0 source as bilingual snapshots.
- Archived the pre-reconciliation bilingual manuscript as the source snapshot
  `thesis/versions/v0.2.0/`; its former numeric table and local-map estimate remain
  preserved as historical claims because the original source and raw outputs are absent.
- Updated the active manuscript to v0.3.0 with deterministic outputs from
  `cex-dex-mvp-f183520b90aa`, the 300-seed stochastic selection run
  `cex-dex-abm-a99f9be866b2`, and H1c diagnostic `cex-dex-h1c-43e446f04adf`.
- Reported the H1c disagreement (3/8 held-out condition/shock majority labels), map
  prediction errors, and limits; the text explicitly labels the run a narrow diagnostic,
  not broad confirmation or empirical validation.
- Revised both language editions and the reproducibility appendix. Language checks,
  documentation build, and paired PDF compilation passed for v0.4.0. The English PDF is
  eight pages and the Spanish PDF is nine pages.
- The final `pnpm thesis:similarity` scan reports zero findings in both editions against
  four indexed source PDFs; two of six bibliography entries remain uncovered, so this
  is not exhaustive clearance. Network verification was skipped.

## Remaining work

- Review active manuscript tables, figures, limitations, and bilingual parity against
  the v0.5.0 confirmation run and record completion evidence before closing this task.
- Reconcile remaining pre-v0.5.0 methodology/ODD notes with the executed protocol.
- Preserve the distinction between confirmatory contrasts, exploratory panic ablation,
  and historical H1c diagnostics. Any new fees, policies, or long horizons need a new
  protocol; they are not prerequisites for accurately presenting the frozen findings.

# THESIS-003 — Reconcile manuscript evidence and evaluate H1c

- **Owner:** `edcalderon`
- **Status:** IN PROGRESS
- **Focus:** Manuscript evidence reconciliation completed in v0.3.0; broad confirmation remains.
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

## Progress

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
  documentation build, and paired PDF compilation pass. The PDFs are eight pages each.
- The final `pnpm thesis:similarity` scan reports zero findings in both editions against
  four indexed source PDFs; two of six bibliography entries remain uncovered, so this
  is not exhaustive clearance. Network verification was skipped.

## Remaining work

- Role taxonomy confirmed by the author: arbitrageur, noise trader, trend/panic trader
  as one policy, and LP with static/adaptive conditions. Review policy parameters before
  confirmation.
- Broaden the holdout to the agreed operating regions, including policy/capacity or fee
  conditions, then rerun the predeclared classification analysis.
- Keep later confirmation outputs distinct from the current selection and narrow holdout
  artifacts; update manuscript claims only from those traceable outputs.

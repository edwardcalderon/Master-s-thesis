# THESIS-003 — Reconcile manuscript evidence and evaluate H1c

- **Owner:** `edcalderon`
- **Status:** DONE
- **Focus:** v0.6.0 bilingual evidence and engineering reconciliation complete.
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

## Manuscript layout correction — 2026-11-25

Active manuscript v0.5.1 corrects the Spanish research-question page split. The full
question was present in the source, but its quotation broke after three lines and the
preceding floating literature table appeared before the last line. Both editions now
flush earlier floats before the section and keep its heading and quotation together.
The research-question wording and v0.5.0 confirmation evidence are unchanged. The
author also requested removal of an editorial source-replacement note; it was removed
from both annex editions. Corrected sources are preserved in `thesis/versions/v0.5.1/`;
earlier archived sources remain
immutable. The paired PDF build and Pages workflow now enforce the rendered layout
with `scripts/check-thesis-layout.py` (requires Poppler's `pdftotext`).

Validation: the checker rejects the old Spanish v0.5.0 PDF and accepts the rebuilt
v0.5.1 English and Spanish PDFs. `make -C thesis pdf` succeeds, and the question is
complete on printed page 8 (PDF page 17) in both editions. The Spanish preceding page,
table/question page, and English question page were visually reviewed. No release tag
or existing release asset is replaced by this correction.

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


## Completion record — 2026-11-25

The original deterministic mechanism, sweep, stochastic selection, held-out map and confirmatory pipeline were rerun. All recorded numeric artifacts reproduced byte for byte; all nine implementation invariants passed. The new v0.6.0 engineering sensitivity is separately versioned, uses fresh seeds 2000–2299, and reproduced in a second output directory. Findings and limits were reconciled in both active editions; see the v0.6.0 annex and experiments/cex_dex_mvp/ENGINEERING_PROTOCOL.md. External validity remains untested and is tracked under DATA-001.

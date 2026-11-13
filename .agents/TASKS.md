# Task ledger

Owner convention: **Ed Calderón (`edcalderon`)** unless an entry names another owner.
Exactly one IN PROGRESS task is marked CURRENT FOCUS. Internal task notes are
maintained in English.

| ID | Owner | Focus | Status | Task folder | Task | Acceptance criteria | Dependencies |
| --- | --- | --- | --- | --- | --- | --- | --- |
| THESIS-001 | edcalderon | **CURRENT FOCUS** | **IN PROGRESS** | [`tasks/in-progress/THESIS-001/`](tasks/in-progress/THESIS-001/TASK.md) | Build the reproducible CEX/DEX hypothesis MVP for the mechanical H1a/H1b contrasts. | A versioned CPMM runner produces deterministic E0/E1 tracking and E2 fixed-sale outputs, with configuration, metrics, source/config/artifact checksums, and run metadata; the ODD scope and event order are documented. | Broaden the author-approved roles over additional ABM operating regions, then refine H1c confirmation. |
| LANG-001 | edcalderon | — | **DONE** | [`tasks/done/LANG-001/`](tasks/done/LANG-001/TASK.md) | Finish and audit the bilingual web UI and required bilingual final thesis PDF. | App UI supports English and Spanish; both thesis sources and final PDFs are paired and internally consistent; language/version checks, builds, and browser QA are recorded. Internal docs, notebooks, and working assets may remain English-only. | None. |
| THESIS-002 | edcalderon | — | **DONE** | [`tasks/done/THESIS-002/`](tasks/done/THESIS-002/TASK.md) | Preserve the pre-update manuscript source as an immutable version. | Snapshot `thesis/versions/v0.1.1/` and its index exist; the working manuscript is separately identified as v0.2.0. | None. |
| CHECK-001 | edcalderon | — | **DONE** | [`tasks/done/CHECK-001/`](tasks/done/CHECK-001/TASK.md) | Integrate refscan as the first local pre-submission checker for the thesis. | One command scans both LaTeX editions against the locally available cited-source PDFs and writes separate reviewable reports; BibTeX conversion preserves citations; outputs are advisory and ignored by Git. Current coverage gaps are listed in the generated tracker. | None. |
| THESIS-003 | edcalderon | — | **IN PROGRESS** | [`tasks/in-progress/THESIS-003/`](tasks/in-progress/THESIS-003/TASK.md) | Reconcile manuscript claims with reproducible outputs and evaluate H1c on held-out configurations. | Active manuscript evidence traces to versioned runs; held-out disagreements and limits are explicit in both editions. | THESIS-001 model review and broader confirmation conditions. |
| DATA-001 | edcalderon | — | **TODO** | [`tasks/todo/DATA-001/`](tasks/todo/DATA-001/TASK.md) | Add a bounded empirical validation path after the synthetic MVP. | Data source, licensing, pair identity, timestamps, ingestion, and external-validity limits are documented and reproducible. | Synthetic mechanics and reproduction contract are stable. |
| SIM-001 | edcalderon | — | **IN PROGRESS** | [`tasks/in-progress/SIM-001/`](tasks/in-progress/SIM-001/TASK.md) | Build a reproducible browser-side simulation playground for inspecting the thesis mechanisms and hypotheses. | Static-hosted UI reproduces bounded deterministic E0/E1/E2 scenarios from versioned model inputs; labels synthetic outputs and exposes parameters, metrics, and assumptions in English and Spanish. | THESIS-001 model contract; later E3 and stochastic summaries require traceable, bounded inputs. |
| THESIS-004 | edcalderon | — | **TODO** | [`tasks/todo/THESIS-004/`](tasks/todo/THESIS-004/TASK.md) | Replace generic pending-work language in the final manuscript with precise, findings-led statements. | Audit both language editions; replace vague future-work promises with claims grounded in available findings and specific evidence limits; maintain factual parity. | THESIS-003 evidence reconciliation and the latest versioned experiment outputs. |

## Current work note

THESIS-001 remains the current focus. Deterministic model 0.3.0 covers E0/E1 arbitrage,
cost-band, and delay mechanics; E2 fixed-sale depth; and a 16-setting paired E3 policy
selection grid. Stochastic model 0.4.0 implements four author-approved representative roles and
paired conditions sharing pre-generated noise schedules. Its current run used 300 seeds
and wrote 50,400 trajectories after meeting the configured approximate 95% interval
half-width target of 0.005 for all six paired peak-error contrasts.

A first H1c holdout fits four condition-specific maps on 48,000 selection transitions,
then tests new seeds 1000–1299 and held-out shocks ±0.05. All four maps are Schur-stable,
but only 3 of 8 held-out condition/shock majority labels match. The z equation has
near-zero selection R-squared. This is a narrow result under representative policies,
not broad validation. Nine invariant checks pass across 2,654 deterministic states plus
504 stochastic smoke states. Fresh runs reproduce the core sweep, ABM, and H1c artifacts
byte-for-byte.

The author approved the four-role taxonomy: arbitrageur, noise trader, trend/panic
trader as one policy, and LP with static/adaptive conditions. The current policy rules
remain simplified selection assumptions. Manuscript v0.3.1 carries this taxonomy;
release v0.1.3 publishes v0.4.0 with the clarified operational question and objectives,
while preserving v0.3.1 and earlier snapshots. The v0.2.0 snapshot preserves the old
table and scalar map estimate as unverified claims. THESIS-003 is broadening held-out
conditions.

CHECK-001 and LANG-001 are complete. The latest CHECK-001 scan for v0.3.1 found zero
matches in both editions against four local source PDFs; two bibliography entries remain
coverage gaps, and network verification was skipped. LANG-001 passed language checks,
builds, and interactive bilingual UI QA. DATA-001 remains queued in `tasks/todo/`.
THESIS-004 is queued to audit generic future-work phrasing in the final manuscript.
SIM-001's deterministic E0/E1/E2 browser slice now builds; E3 and compact stochastic/H1c
views remain. Repository Pages is now configured for Actions; the next main-branch push
will verify the paired-PDF publishing workflow end to end.

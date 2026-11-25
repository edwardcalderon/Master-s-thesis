# Task ledger

Owner convention: **Ed Calderón (`edcalderon`)** unless an entry names another owner.
Exactly one IN PROGRESS task is marked CURRENT FOCUS. Internal task notes are
maintained in English.

| ID | Owner | Focus | Status | Task folder | Task | Acceptance criteria | Dependencies |
| --- | --- | --- | --- | --- | --- | --- | --- |
| THESIS-001 | edcalderon | — | **IN PROGRESS** | [`tasks/in-progress/THESIS-001/`](tasks/in-progress/THESIS-001/TASK.md) | Build the reproducible CEX/DEX hypothesis MVP for the mechanical H1a/H1b contrasts. | A versioned CPMM runner produces deterministic E0/E1 tracking and E2 fixed-sale outputs, with configuration, metrics, source/config/artifact checksums, and run metadata; the ODD scope and event order are documented. | Review acceptance and ODD alignment against the executed v0.5.0 confirmation protocol; later model extensions use new versions. |
| LANG-001 | edcalderon | — | **DONE** | [`tasks/done/LANG-001/`](tasks/done/LANG-001/TASK.md) | Finish and audit the bilingual web UI and required bilingual final thesis PDF. | App UI supports English and Spanish; both thesis sources and final PDFs are paired and internally consistent; language/version checks, builds, and browser QA are recorded. Internal docs, notebooks, and working assets may remain English-only. | None. |
| THESIS-002 | edcalderon | — | **DONE** | [`tasks/done/THESIS-002/`](tasks/done/THESIS-002/TASK.md) | Preserve the pre-update manuscript source as an immutable version. | Snapshot `thesis/versions/v0.1.1/` and its index exist; the working manuscript is separately identified as v0.2.0. | None. |
| CHECK-001 | edcalderon | — | **DONE** | [`tasks/done/CHECK-001/`](tasks/done/CHECK-001/TASK.md) | Integrate refscan as the first local pre-submission checker for the thesis. | One command scans both LaTeX editions against the locally available cited-source PDFs and writes separate reviewable reports; BibTeX conversion preserves citations; outputs are advisory and ignored by Git. Current coverage gaps are listed in the generated tracker. | None. |
| THESIS-003 | edcalderon | — | **IN PROGRESS** | [`tasks/in-progress/THESIS-003/`](tasks/in-progress/THESIS-003/TASK.md) | Reconcile manuscript claims with reproducible outputs and evaluate H1c on held-out configurations. | Active manuscript evidence traces to versioned runs; held-out disagreements and limits are explicit in both editions. | THESIS-001 model contract and the frozen v0.5.0 confirmation artifacts. |
| DATA-001 | edcalderon | — | **TODO** | [`tasks/todo/DATA-001/`](tasks/todo/DATA-001/TASK.md) | Add a bounded empirical validation path after the synthetic MVP. | Data source, licensing, pair identity, timestamps, ingestion, and external-validity limits are documented and reproducible. | Synthetic mechanics and reproduction contract are stable. |
| SIM-001 | edcalderon | — | **IN PROGRESS** | [`tasks/in-progress/SIM-001/`](tasks/in-progress/SIM-001/TASK.md) | Build a reproducible browser-side simulation playground for inspecting the thesis mechanisms and hypotheses. | Static-hosted UI reproduces bounded deterministic E0/E1/E2 scenarios from versioned model inputs; labels synthetic outputs and exposes parameters, metrics, and assumptions in English and Spanish. | THESIS-001 model contract; E3 and current confirmation presentation are handed off to SIM-002. |
| SIM-002 | edcalderon | — | **TODO** | [`tasks/todo/SIM-002/`](tasks/todo/SIM-002/TASK.md) | Build an animated 3D findings replay and reproducible sandbox with local saved scenarios. | Versioned confirmation bundles and illustrative traces drive synchronized 3D/2D views; H1-H3 limits, bounded exploration, EN/ES accessibility, provenance, and local persistence pass the phased gates. | SIM-001 browser foundation; THESIS-003 v0.5.0 evidence contract. Shared persistent worlds and evolutionary agents require separate research scope. |
| THESIS-004 | edcalderon | **CURRENT FOCUS** | **IN PROGRESS** | [`tasks/in-progress/THESIS-004/`](tasks/in-progress/THESIS-004/TASK.md) | Replace generic pending-work language in the final manuscript with precise, findings-led statements. | Audit both language editions; replace vague future-work promises with claims grounded in available findings and specific evidence limits; maintain factual parity. | THESIS-003 evidence reconciliation and the latest versioned experiment outputs. |

## Current release work — 2026-11-25

THESIS-004 is CURRENT FOCUS for the requested v0.6.0 manuscript / v0.1.9 workspace
release: engineering implications, fresh-seed operational sensitivity, full experiment
replay, bilingual findings consolidation and task acceptance audit. Prior statuses below
are the pre-audit baseline and will be reconciled against executed checks.

## Previous work note

As of 2026-11-25, the active bilingual manuscript is v0.5.1 (research-question
pagination correction; the question and v0.5.0 evidence are unchanged). Its evidence comes from
`cex-dex-confirm-5b06486d695e` (analysis 0.5.0, model 0.4.0), with 300 confirmation
seeds and 13,500 runs. `thesis/figures/data/manifest.json` identifies the source and
checksums. H1 reduces excess-error area but missed its precision target; H2's maximum-
response increase is concentrated at depth 0.5; H3 beats persistence on average but
not scalar AR, and regime classification remains weak. All results are synthetic.

The earlier 300-seed selection run and 3-of-8 H1c holdout are historical exploratory
results. They are not the current manuscript's H1-H3 confirmation evidence. THESIS-001
remains CURRENT FOCUS; THESIS-001 and THESIS-003 retain their in-progress status pending
explicit acceptance review. Future model extensions must preserve the frozen evidence.

SIM-001 provides the deterministic model-0.3.0 E0/E1/E2 browser foundation. SIM-002 is
queued for the 3D findings replay, current confirmation views, bounded sandbox, and
browser-local saves; its plan records the implementation gates and the separate scope
needed for shared persistent/evolutionary worlds. Planning is complete; implementation
has not started. Keyboard/focus review and scenario-export cleanup remain in SIM-001.

DATA-001 remains queued for empirical validation. CHECK-001 and LANG-001 remain done
with their recorded historical checks; these records do not imply a new v0.5.0 corpus
or UI audit. THESIS-004 remains queued for an explicit acceptance audit of the current
manuscript. The requested v0.1.8 patch packages this plan and tracker reconciliation;
manuscript revision 0.5.0 and experiment versions remain unchanged.

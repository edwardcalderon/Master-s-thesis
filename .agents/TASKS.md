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
| THESIS-003 | edcalderon | — | **DONE** | [`tasks/done/THESIS-003/TASK.md`](tasks/done/THESIS-003/TASK.md) | Reconcile manuscript claims with reproducible outputs and evaluate H1c on held-out configurations. | Active manuscript evidence traces to versioned runs; held-out disagreements and limits are explicit in both editions. | THESIS-001 model contract and the frozen v0.5.0 confirmation artifacts. |
| DATA-001 | edcalderon | — | **TODO** | [`tasks/todo/DATA-001/`](tasks/todo/DATA-001/TASK.md) | Add a bounded empirical validation path after the synthetic MVP. | Data source, licensing, pair identity, timestamps, ingestion, and external-validity limits are documented and reproducible. | Synthetic mechanics and reproduction contract are stable. |
| SIM-001 | edcalderon | — | **IN PROGRESS** | [`tasks/in-progress/SIM-001/`](tasks/in-progress/SIM-001/TASK.md) | Build a reproducible browser-side simulation playground for inspecting the thesis mechanisms and hypotheses. | Static-hosted UI reproduces bounded deterministic E0/E1/E2 scenarios and serves the checksummed bilingual L0/Hyb held-out summary with metric selection and all 32 cells; synthetic scope and model assumptions remain explicit. | THESIS-001 model contract; E3/3D replay and illustrative traces are handed off to SIM-002. |
| SIM-002 | edcalderon | — | **TODO** | [`tasks/todo/SIM-002/`](tasks/todo/SIM-002/TASK.md) | Build an animated 3D findings replay and reproducible sandbox with local saved scenarios. | Versioned confirmation bundles and illustrative traces drive synchronized 3D/2D views; H1-H3 limits, bounded exploration, EN/ES accessibility, provenance, and local persistence pass the phased gates. | SIM-001 browser foundation; THESIS-003 v0.5.0 evidence contract. Shared persistent worlds and evolutionary agents require separate research scope. |
| THESIS-004 | edcalderon | — | **DONE** | [`tasks/done/THESIS-004/TASK.md`](tasks/done/THESIS-004/TASK.md) | Replace generic pending-work language in the final manuscript with precise, findings-led statements. | Audit both language editions; replace vague future-work promises with claims grounded in available findings and specific evidence limits; maintain factual parity. | THESIS-003 evidence reconciliation and the latest versioned experiment outputs. |
| THESIS-005 | edcalderon | **CURRENT FOCUS** | **IN PROGRESS** | [`tasks/in-progress/THESIS-005/`](tasks/in-progress/THESIS-005/TASK.md) | Formalize core CPMM mechanics and test a band-aware reduced-map extension under frozen held-out conditions. | Pinned Lean proofs cover exact swap/withdrawal invariants; finite-grid differential tests bridge Python float functions; the affine and hybrid maps are compared on disjoint seeds and held-out cells; full-system stability and real-world claims remain open. | THESIS-001 mechanics; frozen v0.5.0 confirmation; v0.8.0 model-credibility revision. |

## Current research work — 2026-11-25

THESIS-004 and THESIS-003 are DONE for manuscript v0.6.0. The original confirmation is
frozen; a new 40,500-path analysis-0.6.0 sensitivity run adds recovery persistence,
order-to-reserve scaling and panic ablation. Five original experiment pipelines
reproduced their numeric artifacts; the sensitivity reproduced in a second output
root. Both PDFs are in release validation. All active claims remain synthetic.
THESIS-005 is the CURRENT FOCUS for formal mechanics and model-credibility work. Lean
4.35.0 proofs, the exact-rational bridge, and model-extension/data gates are in the
feature branch. Manuscript v0.8.0 adds a non-exhaustive quadratic Lyapunov certificate
for the fitted affine maps, narrows the recorded-state claim, and reports a new
band-aware hybrid-map run `cex-dex-hybrid-1d1d9d2f8c5b` (300 selection seeds; 300 held-out
seeds and 9,600 paths). Its 1.7% average recursive price-error improvement is
concentrated in low-capacity, depth-2 cells; flow-pressure prediction does not improve,
in part because no future random-flow realization is supplied to that state-only map.
Full stochastic/hybrid
simulator stability and explicit capacity/withdrawal branches remain open. THESIS-001 remains IN PROGRESS; the representative-agent limitation
remains open. DATA-001 remains TODO for empirical validation because no real-pair source
and data rights have been selected. SIM-001 remains in progress; SIM-002 remains queued.

## Historical work note

As of 2026-11-25, active release-candidate manuscript v0.6.0 adds engineering
interpretation and sensitivity to frozen confirmatory evidence v0.5.0. Confirmation
cex-dex-confirm-5b06486d695e (analysis 0.5.0, model 0.4.0) retains 300 seeds and
13,500 runs. Supplementary analysis cex-dex-engineering-9438e194aa7e (analysis
0.6.0) uses 300 disjoint seeds and 40,500 paths; configuration, protocol, results and
export hashes are in the experiment directory and thesis/figures/engineering/.

Under fixed absolute orders, 97.4% of adaptive paths return at least once, 81.9% end
in-band and 31.2% of recovered paths later depart. Shallow-depth amplification
disappears when orders scale with initial reserves and is reduced by panic ablation.
These findings motivate candidate monitoring and stress-test inputs; no empirical or
production threshold is validated. H1 precision, H2 conditional effects and H3
scalar-AR/classification limits remain explicit.

Five existing deterministic mechanism, sweep, stochastic selection, H1c and
confirmatory pipelines were rerun and their numeric artifacts reproduced byte for byte;
nine invariants passed. The supplementary outputs reproduced byte for byte in a second
output root. The bilingual v0.6.0 source snapshot is under thesis/versions/v0.6.0/;
earlier snapshots remain immutable.

THESIS-001 remains IN PROGRESS because representative-agent rules are not heterogeneous
population validation. THESIS-003 and THESIS-004 are DONE for this revision. DATA-001
remains TODO for real-pair data and external validation. SIM-001 is IN PROGRESS;
SIM-002 is TODO and should use the current evidence with its limits. LANG-001 and
CHECK-001 remain DONE based on their historical checks; this release separately
verifies both manuscript PDFs.

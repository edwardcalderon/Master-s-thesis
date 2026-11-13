# CHECK-001 — Integrate refscan as the first local pre-submission checker

- **Owner:** `edcalderon`
- **Status:** DONE
- **Focus:** —
- **Priority:** First manuscript-integrity checker.
- **Goal:** Integrate [refscan](https://github.com/rktreddy/refscan) as a local
  pre-submission checker for the English and Spanish LaTeX thesis editions. It should
  compare manuscript prose with PDFs of cited sources and produce reviewable passage
  matches. Optional semantic checks are a separately benchmarked enhancement.

## Intended first release

- Local CLI workflow only; no public-app upload or hosted manuscript-processing API.
- One documented command scans both editions and writes separate English and Spanish
  reports under an ignored local output directory.
- Exact/near-verbatim scan against PDFs in the explicitly declared cited-source corpus
  is the baseline. Semantic/paraphrase scan is optional, off by default, and enabled
  only after an English/Spanish false-positive evaluation.
- Findings show the source and matched passage/context supplied by the tool and are
  presented as leads for human review, never as a plagiarism verdict or automatic
  submission gate.
- Manuscript source, reports, downloaded PDFs, and extracted-text caches stay on the
  user's machine and out of Git. Reference lookups/downloads may contact public
  metadata/open-access services; document that network behavior and use only sources
  that may be lawfully downloaded for local comparison.

## Implementation plan

1. **Review and pin upstream.** Select a tagged release or immutable commit of refscan;
   record the upstream revision, license, Python requirement, `pdftotext`/Poppler
   dependency, and optional semantic backend. Install it in an isolated `uv` tool
   environment; do not auto-upgrade or vendor unreviewed upstream code.
2. **Provide BibTeX input.** The current thesis bibliography is inline
   `thebibliography`. Create one canonical `thesis/references.bib` using the existing
   citation keys, then update both LaTeX editions and the PDF build sequence without
   changing citation meaning. Preserve matching chapter order and build both PDFs.
3. **Configure both editions.** Configure refscan to read the same canonical
   bibliography and the correct English or Spanish chapter tree, while writing to
   distinct local literature/output directories. Do not let one edition's `.tex` files
   leak into the other's report.
4. **Add a stable wrapper and instructions.** Provide a single repository command for
   both scans, a setup/refresh path for cited OA PDFs, a manual source-PDF fallback, and
   concise instructions for interpreting the report. Keep generated output ignored.
5. **Evaluate before routine use.** Run the checker on both current editions and a small
   labeled fixture containing copied prose, clean prose, correctly quoted/cited
   passages, common technical phrases, and an English/Spanish translated pair. Record
   coverage, false positives, missing source PDFs, and semantic-model limitations.

## Current progress

- Pinned and installed refscan v0.25.0 at immutable commit
  `1b4a59e42775521d5610399b1bd093597666fdc7` in the isolated `uv` tool environment.
  Upstream is MIT-licensed, requires Python 3.10+ and Poppler `pdftotext` for PDF
  extraction; `refscan doctor --no-network thesis` passed its required local checks.
- Migrated all six citation keys to shared `thesis/references.bib`; added structured
  DOI/URL fields and kept both English and Spanish bibliographies compiling through
  `make -C thesis pdf`.
- Added separate refscan configs and a single wrapper command for English and Spanish.
  Reports, extracted text, and PDFs are ignored under `thesis/literature/`; fetch
  behavior and manual authorized-PDF fallback paths are documented.
- Current local corpus contains 4 of 6 BibTeX references in both editions. Four PDFs
  were obtained from OA resolvers or official public source URLs. `roubal2010linearization`
  remains unresolved; `calderon2026repository` is a software citation and has no paper
  PDF. The generated tracking report lists these gaps. Both editions report zero
  findings against the four indexed PDFs; this is not full-coverage clearance.
- Added a labeled synthetic fixture. On v0.25.0 it produces 4 English findings,
  including an attributed quote and a common technical phrase, and 0 matches for a
  Spanish translation compared with the English source. These observations document
  known false positives and the cross-language limitation; they are not a benchmark.
- Semantic scanning remains disabled and no semantic backend is installed.
- The final v0.3.1 preflight reports zero findings in English and Spanish against four
  indexed PDFs per edition; two bibliography entries remain uncovered, and optional
  network verification was skipped.

## Next action

For later pre-submission runs, inspect the generated coverage tracker and add an
authorized PDF for `roubal2010linearization` if one becomes available. Treat reports as
advisory and do not describe the current 4-of-6 corpus as exhaustive.

## Acceptance criteria

- A pinned and license-reviewed refscan version is installable in an isolated local
  environment with its system dependencies documented.
- Both final LaTeX editions can be scanned from one documented command against the
  cited-source PDFs; outputs are separate, reproducible, and excluded from Git.
- The canonical BibTeX migration preserves citation keys and meaning, and both thesis
  PDFs still compile from the documented build command.
- The report includes enough passage/source context for a reviewer to verify each
  finding. Unavailable sources are listed as coverage gaps, not silently treated as
  checked.
- A labeled fixture documents exact-match performance and false positives. Semantic
  checks remain disabled unless their bilingual evaluation supports enabling them.
- No thesis text is uploaded to the public web app or sent to a comparison service; the
  documentation clearly distinguishes local source coverage from Scribbr/Turnitin's
  wider proprietary comparison corpora.
- Similarity findings are advisory and require human review; the checker does not
  produce misconduct decisions or block thesis publication automatically.

## Dependencies and constraints

- This requested local checker is complete. Any later web-app integration requires a
  separate task and authenticated, user-controlled backend.
- The app UI and final thesis PDFs are the required bilingual surfaces; this is an
  internal English-language tool. It must process English and Spanish manuscripts
  separately, but checker UI/report translation is not required.
- Cross-language translated plagiarism detection is not assumed to work. Evaluate it
  independently from same-language passage matching.
- Any later web-app integration requires a separate task, a private authenticated
  backend, user-controlled data retention, and an explicitly curated comparison corpus.

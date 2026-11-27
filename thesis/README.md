# Thesis manuscript

English is the primary edition. A Spanish translation is required for every manuscript
revision. Both editions share a manuscript revision and are built and published
together.

- English source: `main.tex` and `chapters/`
- Required Spanish translation: `es/main.tex` and `es/chapters/`
- English PDF: `main.pdf`
- Spanish PDF: `es/main.pdf`

The current manuscript revision is v0.8.5. The approved main research question is unchanged. H1 now interprets the difference between the isolated-pool deadline and simulated sustained recovery. The H2 replay and the 1,800-path capacity-ratio check distinguish one-off panic-associated shallow E1 departures from recurring E3 departures, and show that the fixed-capacity control equalizes the configured pressure ratios rather than decomposing capacity from depth. The primary H2 comparison uses post-recovery excess area, which excludes the imposed shock and the two recovery-confirmation ticks; its conditional denominator is reported consistently. The abstracts summarize the analytical, simulation, sensitivity and reduced-map findings. The PDF layout check reports their page share and ensures each abstract and its keywords remain together on one page.

All results remain conditional on the synthetic model. The H2 replay uses existing seeds rather than an independent Monte Carlo sample; 7,200 reserve-linked-cap paths exactly reproduce archived metrics. The shallow fixed-capacity control substantially reduces the post-recovery E3 contrast, but recovery conditioning, one tested depth and post-hoc design prevent a general causal decomposition. Panic overlap is descriptive and end-of-tick episode counts do not identify within-tick causality. No market-data validation was performed. Future work extends the capacity control into a factorial design and performs synchronized event replay with realistic costs and delays.

The v0.8.1 pilot of three public DEX swaps is no longer presented as thesis evidence and its dataset citation has been removed from the active bibliography. The BibTeX source contains 87 records; the compiled bibliography contains 56 cited items (55 scholarly works and one repository record).

The archived Monte Carlo outputs retain the historical identifier `cex-dex-confirm-5b06486d695e`; the exploratory H2 replay is `cex-dex-h2-review-81af3e984e2c`, and the capacity-ratio check is `cex-dex-capacity-ratio-e269f980fd26`. Reproduce them with `python3 experiments/cex_dex_mvp/analyze_h2_revision.py` and `python3 experiments/cex_dex_mvp/analyze_capacity_ratio_check.py`; their manifests record input and output checksums, and the scripts export manuscript tables and the interactive web summary. The workspace release version remains separate in the root `VERSION` file. Earlier snapshots remain unchanged; v0.8.5 records this bilingual revision and the approved question unchanged.

## Research-question change control

The main research question and the H2/H3 evaluation subquestions are locked in both
language editions. Every manuscript render runs the guard, and a pull-request workflow
checks edits to the question sections. An unapproved wording change fails the check.

A question change requires explicit thesis-author or supervisor approval. Append a new
approved record to thesis/question-control.json with the approver, date, rationale and
provenance (for example, an approved feedback document, meeting record, or issue); then
update the marked question text in English and Spanish and the record's approved wording.
Do not overwrite prior approval records. Run the guard with:

```bash
pnpm thesis:questions:check
```

The guard compares the marked source text with the latest approval record and checks that
older records remain unchanged in pull requests. It validates the recorded provenance but
does not authenticate the person named as approver. To make consent a required gate, keep
question changes in pull requests and require reviewer approval through repository branch
protection.

## Build both PDFs

From this directory:

```bash
make pdf
```

The target first checks that both sources declare the required locales, matching
manuscript revision, workspace release version, and chapter order. It then compiles
both PDFs. CI publishes the pair as `master-thesis.pdf` and
`master-thesis.es.pdf`.

The PDF build also runs `python3 ../scripts/check-thesis-layout.py` after compilation.
This requires Poppler (`pdftotext`) and rejects a research question split across pages
or separated from its heading. It also checks that each abstract and its keywords remain
on one page and reports their rendered page share. The Pages workflow runs the same check before upload.

Both editions use the shared citation keys in `references.bib`; `make pdf` runs
BibTeX for each source tree before producing the final PDFs.

## Double-blind review copies

Generate only the current blind English or Spanish PDF:

```bash
pnpm thesis:pdf:en-blind
pnpm thesis:pdf:es-blind
```

To generate both blind copies without first compiling the named editions:

```bash
make -C thesis pdf-blind
```

To render both named editions and include both blind copies on demand:

```bash
make -C thesis pdf BLIND=1
# equivalent:
pnpm thesis:pdf:blind
```

The outputs are thesis/build/manuscript-en-double-blind.pdf and
thesis/build/manuscrito-es-doble-ciego.pdf. The build removes names, advisors, degree
program, institution and location from the covers; clears PDF author metadata; masks the
repository self-citation and repository-identifying run IDs, checksums and local paths;
then scans each extracted PDF for those markers and checks that the full research question
appears on one page with its heading. Both language editions retain the same research
question.

## Local similarity preflight

The first manuscript checker is refscan, run locally against PDFs of sources cited in
the thesis. Install the pinned tool once:

```bash
uv tool install --from git+https://github.com/rktreddy/refscan.git@1b4a59e42775521d5610399b1bd093597666fdc7 refscan
```

Prerequisites are `uv`, Python 3.10 or newer, Poppler's `pdftotext`, and BibTeX;
the paired thesis build also requires `pdflatex`. The base refscan install is enough
for exact passage matching. Semantic scanning needs an optional embedding backend and
is intentionally not installed or enabled. The pinned upstream revision is v0.25.0 at
commit `1b4a59e42775521d5610399b1bd093597666fdc7`; refscan is MIT-licensed.

Fetch available cited-source PDFs explicitly when needed, then run the local check:

```bash
pnpm thesis:similarity:fetch
pnpm thesis:similarity
```

Fetching contacts public bibliographic metadata and open-access resolvers and downloads
source PDFs they can lawfully resolve; it does not send the manuscript text. If a source
is unavailable, place an authorized PDF at
`thesis/literature/en/refs/<citation-key>.pdf` and
`thesis/literature/es/refs/<citation-key>.pdf`, or keep it listed as a coverage gap.
The reports show how many source PDFs were indexed, so a scan with missing sources is
not full-coverage clearance. `refscan doctor --no-network thesis` checks the local
environment without probing external services.

For sources the resolver cannot retrieve, the current Uniswap whitepaper and DYNA
article have public PDF URLs recorded in `references.bib`. To reproduce the current
four-PDF corpus from a clean checkout, download those authorized PDFs into the English
corpus and mirror them into the Spanish corpus:

```bash
mkdir -p thesis/literature/en/refs thesis/literature/es/refs
curl --fail --location --output thesis/literature/en/refs/adams2020uniswap.pdf https://blog.uniswap.org/whitepaper.pdf
curl --fail --location --output thesis/literature/en/refs/medina2009multimodelos.pdf https://www.redalyc.org/pdf/496/49612068014.pdf
cp thesis/literature/en/refs/adams2020uniswap.pdf thesis/literature/es/refs/
cp thesis/literature/en/refs/medina2009multimodelos.pdf thesis/literature/es/refs/
```

The IEEE article `roubal2010linearization` remains unresolved and the repository
citation has no paper PDF, so the scan still covers only four of the six bibliography
entries. Check `reference_tracking.md` for the current per-key coverage before
interpreting a report.

Run the labeled synthetic evaluation fixture with `pnpm thesis:similarity:eval`; its
cases and observed limits are documented in
[`../experiments/refscan_evaluation/README.md`](../experiments/refscan_evaluation/README.md).

Reports, downloaded PDFs, and extracted-text caches are written under the ignored
`thesis/literature/` directory. The checker compares only with that cited-source corpus;
it does not search a commercial web/student-paper index and does not provide the wider
proprietary comparison coverage associated with Scribbr or Turnitin. Treat matches as
review leads, not as a plagiarism verdict. Optional semantic checks remain disabled
until evaluated for both thesis languages. See the [refscan project documentation](https://github.com/rktreddy/refscan)
for upstream behavior and licensing.

## Translation maintenance

When changing a manuscript revision, update the English source first and translate the
same content into Spanish before publishing. Keep section order, equations, tables,
figures, citations, reported values, and limitations aligned. English labels embedded
in source figures must be translated or explicitly glossed in the Spanish edition.
Run `pnpm language:check` from the repository root, then build with
`make -C thesis pdf`.

The October 29 draft reported preliminary values from the absent
`experiments/cex_dex_preliminary/` source path. Revision v0.3.0 replaced them as active
evidence with traceable deterministic and stochastic MVP results; it preserves the
prior figures and estimates in `versions/v0.2.0/`, explicitly labeled unverified. The
new runs do not reproduce the old table. See the
[`../docs/mvp-plan.md`](../docs/mvp-plan.md) and the runner's
[`../experiments/cex_dex_mvp/README.md`](../experiments/cex_dex_mvp/README.md).

---

[Español](README.es.md)

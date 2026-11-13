# Thesis manuscript

English is the primary edition. A Spanish translation is required for every manuscript
revision. Both editions share a manuscript revision and are built and published
together.

- English source: `main.tex` and `chapters/`
- Required Spanish translation: `es/main.tex` and `es/chapters/`
- English PDF: `main.pdf`
- Spanish PDF: `es/main.pdf`

The current manuscript revision is v0.3.1. The workspace release version is tracked
separately by the root `VERSION` file and is synchronized into both LaTeX entry points.
The v0.3.0 bilingual snapshot preserves the source before the author-approved role-taxonomy update. The v0.2.0 snapshot preserves the October 29 draft and its unverified preliminary values; v0.1.1 is also retained.

## Build both PDFs

From this directory:

```bash
make pdf
```

The target first checks that both sources declare the required locales, matching
manuscript revision, workspace release version, and chapter order. It then compiles
both PDFs. CI publishes the pair as `master-thesis.pdf` and
`master-thesis.es.pdf`.

Both editions use the shared citation keys in `references.bib`; `make pdf` runs
BibTeX for each source tree before producing the final PDFs.

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

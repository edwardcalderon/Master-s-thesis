# Reproducibility protocol

The public workflow is designed around a small, repeatable loop:

```text
source → transform → notebook → figure/table → thesis chapter → release
```

## Local setup

```bash
pnpm install
pnpm dev
```

Run `pnpm build` before publishing. Notebook environments should declare their Python
version and dependencies in notebook metadata or a future `environment.yml`. Large or
restricted datasets belong outside Git, with a documented checksum and acquisition
note in `data/README.md`.

## Required English and Spanish surfaces

English is the default app language, and readers can switch to Spanish from the site
header. Keep the app's English and Spanish UI content synchronized. Internal documents,
notebooks, task records, and experiment assets may remain English-only; existing
translations are optional. `pnpm language:check` checks app locale structure and
manuscript revision alignment.

## Thesis language builds

English is the primary manuscript. Its Spanish translation is mandatory for every
revision. From `thesis/`, `make pdf` checks that both source trees declare the same
workspace version and manuscript revision, then compiles the English and Spanish PDFs.
The Pages workflow publishes both in the same deployment; publication is incomplete
if the Spanish source or PDF is missing.

## Deterministic market mechanism MVP

The current first-pass simulator is a deterministic CPMM mechanism runner, not the
heterogeneous-agent model or the unverified preliminary prototype described in the
manuscript. Run it from the repository root with:

```bash
python3 experiments/cex_dex_mvp/run.py
```

Each run stores its configuration, time series, scenario summaries, source/config
checksums, and runtime metadata under the ignored
`experiments/cex_dex_mvp/output/` directory. The checked-in configuration is
deterministic and uses no random seeds. See the [runner notes](../experiments/cex_dex_mvp/README.md),
[ODD specification](../experiments/cex_dex_mvp/ODD.md), and [MVP roadmap](mvp-plan.md).
Do not substitute these outputs for the manuscript's preliminary table until all
scenarios and definitions have been reconciled.

## Release checklist

- Confirm `VERSION` and `VERSION_HISTORY.json` agree.
- Re-run the notebooks used by the current thesis release.
- Run `pnpm language:check`.
- Build both PDFs with `make -C thesis pdf`; verify the English primary and Spanish translation are present.
- Record data provenance and any changed assumptions.
- Publish the static site from the same commit as the thesis artifact.

---

[Español](es/reproducibility.md)

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

Run `pnpm build` before publishing. Notebook environments should declare their Python version and dependencies in the notebook metadata or in a future `environment.yml`. Large or restricted datasets belong outside git, with a documented checksum and acquisition note in `data/README.md`.

## Release checklist

- Confirm `VERSION` and `VERSION_HISTORY.json` agree.
- Re-run the notebooks used by the current thesis release.
- Build the PDF from `thesis/`.
- Record data provenance and any changed assumptions.
- Publish the static site from the same commit as the thesis artifact.

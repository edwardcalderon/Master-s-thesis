# Master Thesis Lab

An open, reproducible research workspace for a master thesis. English is the primary language for the project, website, and documentation. Every thesis release includes a required Spanish translation of the manuscript PDF.

The public web app, project documentation, notebooks, changelog, and release history have English and Spanish editions. The app opens in English and lets readers switch languages at any time. [Read this project overview in Spanish](README.es.md).

The public experience is inspired by the useful parts of [GeoAuPredict](https://github.com/edwardcalderon/GeoAuPredict): a clear research overview, a notebook explorer, a docs surface, and an artifact-oriented GitHub Pages deployment. Application-specific gold-prediction code and heavyweight services are intentionally left out until the thesis needs them.

## 📋 Latest Changes (v0.1.4)

### Added

- Added a bilingual, client-side simulation playground for deterministic E0/E1 price tracking and E2 pool-depth comparisons, with bounded controls and copyable scenario data.
- Added SIM-001 to track the static-hosted simulation work and THESIS-004 to audit generic future-work wording in the manuscript.

### Changed

- Updated the landing page to use the official English and Spanish thesis titles, put the playground directly below the title, and reduce introductory copy.
- Improved narrow-screen layout so the live result chart is visible before its controls.

For full version history, see [CHANGELOG.md](./CHANGELOG.md) and [GitHub releases](https://github.com/edwardcalderon/Master-s-thesis/releases).

# Changelog

All notable changes to this research workspace are documented here. Releases follow semantic versioning and are prepared with `@edcalderon/versioning`.

For full version history, see [CHANGELOG.md](./CHANGELOG.md) and [GitHub releases](https://github.com/edwardcalderon/Master-s-thesis/releases)

## Earlier preliminary manuscript — 29 Oct 2026

This earlier mechanism-first draft studied CEX/DEX price tracking, bounded arbitrage, and liquidity fragility. It has been revised; the active bilingual manuscript is v0.4.0, and the v0.3.1 source is preserved in the version archive.

- [Current English manuscript](thesis/main.tex)
- [Current Spanish translation](thesis/es/main.tex)
- [Current reproducible MVP](experiments/cex_dex_mvp/README.md)
- [Archived LaTeX manuscript](thesis/preprint/manuscrito_cex_dex_revision_direccion_2026-10-29.tex)
- [Compilation instructions](thesis/preprint/README.md)
- [Preliminary CPMM simulation](experiments/cex_dex_preliminary/cex_dex_preliminary.py)
- [Methods and limitations](experiments/cex_dex_preliminary/PRELIMINARY_ANALYSIS_2026-10-29.md)
- [Summary metrics](experiments/cex_dex_preliminary/results/preliminary_summary.csv)

The E0-E3 outputs are synthetic mechanism checks, not empirical market validation.

## Monorepo map

```text
.
├── apps/web/             # Vite + React public landing page and artifact viewer
├── packages/content/     # Typed thesis, notebook, and documentation metadata
├── packages/ui/          # Shared visual tokens for future apps
├── docs/                 # Public research notes and Spanish companions in docs/es/
├── notebooks/            # Linkable Jupyter notebooks and Spanish companions in notebooks/es/
├── thesis/               # English LaTeX manuscript and PDF build instructions
│   └── es/                # Required Spanish translation source
├── data/                 # Raw/processed boundaries; large data stays out of git
├── .github/workflows/    # GitHub Pages build and deploy
├── VERSION               # Single public release version
├── VERSION_HISTORY.json  # English release ledger
└── VERSION_HISTORY.es.json # Spanish release ledger
```

## Local development

```bash
pnpm install
pnpm dev
```

The web app runs on `http://localhost:5173`. Production checks are:

```bash
pnpm version:check
pnpm lint
pnpm typecheck
pnpm build
pnpm docs:build
```

## Thesis PDF

The English primary source lives in [`thesis/main.tex`](thesis/main.tex), and its required Spanish translation is in [`thesis/es/`](thesis/es/). Build both PDFs locally with:

```bash
cd thesis
make pdf
```

`make pdf` builds both `thesis/main.pdf` (English) and `thesis/es/main.pdf` (Spanish). The Pages workflow publishes both beside the source; an English-only build is incomplete. PDF binaries are ignored by default so the two language sources remain canonical.

## Language policy

- English (`en`) is the primary language for the project overview, site, and documentation.
- The web app, documentation, notebooks, changelog, and release ledger have Spanish companions; the app defaults to English and remembers the reader's choice.
- The thesis is authored in English first and must ship with a Spanish (`es`) translation for every manuscript revision.
- The English and Spanish PDFs use the same manuscript revision and are built and published together. The site opens English by default and exposes both versions.
- Run `pnpm language:check` to check app translation structure, paired documentation/notebooks, release history, and manuscript revision parity. CI runs this check and compiles both PDFs.

See [`docs/language-policy.md`](docs/language-policy.md) for the source and publishing rules.

## Version tracking

[`@edcalderon/versioning`](https://www.npmjs.com/package/@edcalderon/versioning) handles workspace SemVer bumps and the English changelog. The repository synchronizer projects the version into `VERSION`, both release histories, both app locale files, both LaTeX workspace-version macros, and the release blocks in both READMEs. `pnpm readme:update` copies the populated English and Spanish changelog entries into their matching README summaries. A separate manuscript-revision macro keeps the thesis editions paired.

<!-- versioning:release:start -->
**Current release:** [`v0.1.4`](https://github.com/edwardcalderon/Master-s-thesis/releases/tag/v0.1.4)
**Tracker:** [GitHub releases](https://github.com/edwardcalderon/Master-s-thesis/releases) · synchronized with `@edcalderon/versioning`
<!-- versioning:release:end -->

The site footer reads the same tracked version and links directly to its GitHub release tag. Configuration lives in [`versioning.config.json`](versioning.config.json).

```bash
pnpm version:validate  # validates @edcalderon/versioning plus thesis artifacts
pnpm readme:update     # syncs both README summaries from their changelogs
pnpm secrets:check     # scans staged changes through the versioning secrets extension
pnpm release:patch     # prepares the next patch, synchronizes, and verifies it
```

`pnpm release:patch` deliberately does not commit or tag. It bumps the workspace version, synchronizes package and thesis metadata, refreshes both README summaries, and runs `release:verify`. Keep the English and Spanish changelog entries for the new version populated before running it. Review the changes, then create the release commit and `vX.Y.Z` tag. Husky checks staged files for secrets and validates version integrity before each commit.

## GitHub Pages

Pushes to `main` run [`.github/workflows/pages.yml`](.github/workflows/pages.yml). The workflow builds the web app, copies the public docs and notebooks into the static artifact, and publishes the result with GitHub Pages.

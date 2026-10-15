# Master Thesis Lab

An open, reproducible research workspace for a master thesis. The repository keeps the public narrative, executable notebooks, data boundaries, and LaTeX source in one versioned monorepo.

The public experience is inspired by the useful parts of [GeoAuPredict](https://github.com/edwardcalderon/GeoAuPredict): a clear research overview, a notebook explorer, a docs surface, and an artifact-oriented GitHub Pages deployment. Application-specific gold-prediction code and heavyweight services are intentionally left out until the thesis needs them.

## 📋 Latest Changes (v0.1.1)

### Changed

- Reframed the public thesis site as an academic reading room with light and dark themes.
- Added persistent reading mode with a reduced-distraction, narrow-measure layout.
- Corrected versioning package discovery to synchronize the explicit workspace manifests before release validation.

For full version history, see [CHANGELOG.md](./CHANGELOG.md) and [GitHub releases](https://github.com/edwardcalderon/Master-s-thesis/releases)

## Monorepo map

```text
.
├── apps/web/             # Vite + React public landing page and artifact viewer
├── packages/content/     # Typed thesis, notebook, and documentation metadata
├── packages/ui/          # Shared visual tokens for future apps
├── docs/                 # Public research notes and reproducibility documentation
├── notebooks/            # Small, linkable Jupyter notebooks
├── thesis/               # LaTeX source and PDF build instructions
├── data/                 # Raw/processed boundaries; large data stays out of git
├── .github/workflows/    # GitHub Pages build and deploy
├── VERSION               # Single public release version
└── VERSION_HISTORY.json  # Human-readable release ledger
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

The LaTeX source lives in [`thesis/main.tex`](thesis/main.tex). Build it locally with:

```bash
cd thesis
make pdf
```

The web viewer is ready for `public/thesis/master-thesis.pdf` when a generated artifact is available. PDF binaries are ignored by default so the source remains the canonical artifact; remove that ignore rule if the final thesis PDF should be committed for archival release.

## Version tracking

This repository uses [`@edcalderon/versioning`](https://www.npmjs.com/package/@edcalderon/versioning) as the source of truth for semantic versions, workspace synchronization, changelog maintenance, the README Maintainer extension, and secret checks. The small local synchronizer projects that package version into thesis-specific artifacts: `VERSION`, `VERSION_HISTORY.json`, the public site metadata, the LaTeX version macro, and the release block below.

<!-- versioning:release:start -->
**Current release:** [`v0.1.1`](https://github.com/edwardcalderon/Master-s-thesis/releases/tag/v0.1.1)
**Tracker:** [GitHub releases](https://github.com/edwardcalderon/Master-s-thesis/releases) · synchronized with `@edcalderon/versioning`
<!-- versioning:release:end -->

The site footer reads the same tracked version and links directly to its GitHub release tag. Configuration lives in [`versioning.config.json`](versioning.config.json).

```bash
pnpm version:validate  # validates @edcalderon/versioning plus thesis artifacts
pnpm readme:update     # refreshes “Latest Changes” from CHANGELOG.md
pnpm secrets:check     # scans staged changes through the versioning secrets extension
pnpm release:patch     # prepares the next patch, synchronizes, and verifies it
```

`pnpm release:patch` deliberately does not commit or tag: it runs the package's README Maintainer extension, synchronizes the release tracker, and then verifies the workspace. Review the generated package, changelog, README, and thesis changes before making the release commit and `vX.Y.Z` tag. Husky runs the secret scan and version integrity check before each commit.

## GitHub Pages

Pushes to `main` run [`.github/workflows/pages.yml`](.github/workflows/pages.yml). The workflow builds the web app, copies the public docs and notebooks into the static artifact, and publishes the result with GitHub Pages.

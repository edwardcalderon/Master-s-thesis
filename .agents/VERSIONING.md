# EdCalderon project versioning guideline

Use the repository's existing `@edcalderon/versioning` release workflow. Do not
introduce a second release-numbering system.

## Version lanes

1. **Workspace release:** the root `VERSION`, root/package manifests, changelog,
   version history, website content, and release links follow SemVer through the
   configured `@edcalderon/versioning` scripts. Keep package versions synchronized.
   English release records are canonical; Spanish README/history copies are optional.
2. **Manuscript revision:** `\revisionManuscrito` and the dated source snapshot track
   thesis-content revisions independently of the workspace release. The current source
   declares v0.2.0 while the workspace release is v0.1.1; preserve this distinction.
3. **Experiment model version:** version configurations and output schemas separately
   when their semantics change. Every run should retain its exact configuration and
   source checksum; do not overwrite released evidence.

## Change rules

- Use a **patch** workspace release for backward-compatible corrections and fixes, a
  **minor** release for compatible capabilities, and a **major** release for breaking
  changes to commands, data, or output contracts. Follow the versioning package's
  release guard and conventional-commit rules.
- Increment the manuscript **patch** for corrections that do not alter claims, the
  **minor** for substantive compatible revisions, and the **major** when the research
  question, model contract, or interpretation changes materially. Translate the full
  revision to Spanish before publishing either PDF.
- Save each published manuscript source in a new `thesis/versions/vX.Y.Z/` directory.
  Treat snapshots as immutable; fix a released version only through a new revision.
- Keep data/config/output schemas versioned independently. A new run gets a unique
  output directory and records configuration, code revision/checksum, runtime, and
  artifact checksums.
- Task ledger edits and exploratory work do not by themselves advance any version.
  Never create a release tag or modify release manifests just to update task status.
- Before a release, use the repository's documented `version:validate`, language,
  build, and release-verification commands. Do not record a check as passed unless it
  was run on the exact working tree being described.

## Current anchors

- Workspace release: root `VERSION` and `VERSION_HISTORY.json`; translated release
  history is optional.
- Manuscript: matching `\revisionManuscrito` in `thesis/main.tex` and
  `thesis/es/main.tex`; required English/Spanish PDFs are built together.
- Previous manuscript snapshots: `thesis/versions/v0.1.1/`, `v0.2.0/`, and `v0.3.0/`.
- Release automation: `package.json`, `versioning.config.json`, and `scripts/version.mjs`.

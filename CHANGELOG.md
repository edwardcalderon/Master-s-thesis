## [0.1.7](https://github.com/edwardcalderon/Master-s-thesis/compare/v0.1.6...v0.1.7) (2026-11-24)

### Added

- Added manuscript revision v0.5.0, restructured along the advisor's feedback: a six-paragraph introduction, problem statement and state of the art, justification, hypotheses, objectives, methodology, results, discussion and conclusions, future work, bibliography and annexes, in English and Spanish.
- Added the confirmatory protocol (`confirm.py`, `confirm_config.json`) with disjoint exploration and confirmation seeds, paired-by-seed inference and Holm correction, and `export_thesis_data.py` to export the figure and table data to `thesis/figures/data/`.
- Added a reference audit (`thesis/literature-audit/`) that verifies each of the 87 bibliography entries against Crossref, arXiv or the publisher and ranks them by relevance.
- Added the v0.5.0 manuscript source snapshot under `thesis/versions/`.

### Changed

- Replaced the manuscript results with the confirmatory run `cex-dex-confirm-5b06486d695e`: H1 and H2 are supported on average, H2 only at the shallowest depth, and H3 beats persistence but not a scalar autoregression. All results are synthetic; the H1 target precision was not reached.
- Updated the website abstract, keywords and version to match the new manuscript.
- Updated the reference, experiment and thesis documentation.

## [0.1.6](https://github.com/edwardcalderon/Master-s-thesis/compare/v0.1.5...v0.1.6) (2026-11-13)

### Changed

- Reordered the landing page so the manuscript abstract appears before the simulation playground, with matching navigation and section numbering.

## [0.1.5](https://github.com/edwardcalderon/Master-s-thesis/compare/v0.1.4...v0.1.5) (2026-11-13)

### Added

- Added the exact English and Spanish manuscript abstracts and keywords to the website.
- Added checks that keep the web page title and abstract synchronized with both manuscript editions.

### Changed

- Updated the Pages artifact to publish only the final English and Spanish PDFs.
- Removed direct LaTeX-source downloads from the manuscript section.

## [0.1.4](https://github.com/edwardcalderon/Master-s-thesis/compare/v0.1.3...v0.1.4) (2026-11-13)

### Added

- Added a bilingual, client-side simulation playground for deterministic E0/E1 price tracking and E2 pool-depth comparisons, with bounded controls and copyable scenario data.
- Added SIM-001 to track the static-hosted simulation work and THESIS-004 to audit generic future-work wording in the manuscript.

### Changed

- Updated the landing page to use the official English and Spanish thesis titles, put the playground directly below the title, and reduce introductory copy.
- Improved narrow-screen layout so the live result chart is visible before its controls.

# Changelog

## [0.1.3] - 2026-11-12

### Changed

- Clarified the bilingual abstracts, research question, objectives, and limits of the reduced-map hypothesis.
- Corrected the adaptive liquidity scenario description and the ODD reference.
- Recorded the substantive manuscript revision as v0.4.0 and preserved bilingual snapshots for v0.3.1 and v0.4.0.

## [0.1.2](https://github.com/edwardcalderon/Master-s-thesis/compare/v0.1.1...v0.1.2) (2026-11-12)

### Added

- English/Spanish public app, documentation, notebook, and thesis surfaces with English as the primary language.
- Local refscan pre-submission checks for both thesis editions, plus a labeled evaluation fixture.
- Reproducible deterministic and paired stochastic CEX/DEX MVP runners with a held-out H1c diagnostic.

### Changed

- Updated the bilingual manuscript to v0.3.1 with traceable MVP results, the author-approved four-role taxonomy, and explicit limits on the 3-of-8 H1c result.
- Preserved manuscript source snapshots v0.2.0 and v0.3.0; the older preliminary numerical claims remain unverified.

## [0.1.1] - 2026-10-15

### Changed

- Reframed the public thesis site as an academic reading room with light and dark themes.
- Added persistent reading mode with a reduced-distraction, narrow-measure layout.
- Corrected versioning package discovery to synchronize the explicit workspace manifests before release validation.

## [0.1.0] - 2026-10-15

### Added

- Public pnpm/Turborepo research workspace.
- v0.1.0 LaTeX thesis draft and GitHub Pages PDF pipeline.
- Notebook explorer, documentation surface, and reproducibility baseline.

---

[Español](CHANGELOG.es.md)

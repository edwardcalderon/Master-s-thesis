# SIM-001 — Browser-side reproducible simulation playground

- **Owner:** `edcalderon`
- **Status:** IN PROGRESS
- **Focus:** Secondary implementation track; THESIS-001 remains the current focus.
- **Started:** 2026-11-13

## Goal

Build an interactive simulation playground for examining the thesis mechanisms and
hypotheses in real time. It must work on static GitHub Pages: user-selected scenarios
and bounded model computations run in the browser, and larger outputs are reduced to
lightweight, versioned summaries before they are loaded.

## Architecture constraints

- No required application server or paid compute service for the core playground.
- Keep initial calculations deterministic and bounded. Expose their assumptions, model
  version, inputs, and calculated metrics so a scenario can be reproduced.
- Large stochastic sweeps and trajectories must not be downloaded or recomputed as a
  default UI action. Use compact, checksummed precomputed summaries for those views;
  consider a Web Worker only when measured client computation makes it necessary.
- Any server-side compute proposal must document why browser execution or a compact
  static artifact cannot meet the use case, plus hosting and reproducibility implications.
- Keep browser calculations in parity with the versioned Python reference model; do not
  present synthetic mechanism results as empirical findings or validated hypotheses.

## Acceptance criteria

- A responsive bilingual web playground allows users to inspect deterministic E0/E1
  tracking and E2 fixed-sale depth scenarios with live, bounded parameter changes.
- E0/E1 outputs include the CEX and DEX path, no-arbitrage band, peak absolute error,
  excess error, and sustained return tick, matching the reference event order.
- E2 outputs compare the same fixed sale at full and reduced proportional reserve depth,
  preserving starting marginal price and displaying absolute log-price impact.
- The UI identifies model/config versions, synthetic scope, assumptions, and reproducible
  scenario inputs; selected settings can be copied or exported.
- Workloads are bounded in browser and do not depend on a backend. Future stochastic
  views use compact precomputed summaries unless a separately reviewed need justifies
  client computation or a service.
- Accessibility, narrow layouts, and static-site relative asset paths are preserved.

## Dependencies

- THESIS-001 versioned model, configuration, and mechanism contract.
- Existing bilingual locale dictionaries and static GitHub Pages build.

## Progress

- Confirmed the web app is a React/Vite client build with English/Spanish dictionaries
  and no API service dependency.
- The graph MCP transport is closed in this workspace; implementation discovery used
  direct source inspection as the documented fallback.
- Ported the deterministic E0/E1 and E2 calculations from model 0.3.0 to a browser
  module. E0/E1 exposes bounded controls for shock, capacity, band, delay, and horizon;
  its chart and return/error metrics follow the reference model's event order and
  sustained two-tick return rule. E2 compares an identical fixed sale at full and
  proportionally reduced reserve depth.
- Connected both scenarios to the bilingual UI, with local JSON scenario copy, explicit
  synthetic-scope language, responsive layout, and an inline SVG chart. No plotting
  dependency, API call, or server compute is required for these scenarios.
- Updated the landing hero to use the exact English and Spanish thesis titles, removed
  the metadata-heavy hero panel, and moved the playground immediately below the title.
  The default chart now appears in the initial mobile viewport; E0/E1 and E2 tabs were
  reviewed in both languages with PinchTab.
- Added the manuscript's exact English and Spanish abstracts and keyword lists to the
  site, with language checks that compare the title and abstract against both LaTeX
  editions. The static and hydrated browser titles match the manuscript title.
- Removed manuscript-source download controls and changed the Pages workflow to publish
  only the final English and Spanish PDFs in its thesis artifact directory.
- `pnpm --filter @tesis/web typecheck`, `pnpm --filter @tesis/web build`, and
  `pnpm language:check` pass. The latest web build reports 83.65 KB gzip for JS.

## Remaining work

- Review keyboard-only operation and focus states for both simulation tabs and controls.
- Add the E3 policy comparison and assess whether its bounded trajectories should be
  computed live or presented as a compact precomputed selection result.
- Define a versioned compact artifact schema for stochastic and H1c views; do not load
  the full 50,400-row ABM trajectory file into the UI.
- Add scenario share/export metadata and document exact reproduction steps.
- Review client bundle size and use a Web Worker only if profiling demonstrates a need.
- Verify the next main-branch publish after repository Pages was enabled for Actions;
  the earlier workflow completed its build but failed before artifact upload.

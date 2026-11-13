# THESIS-001 — Reproducible CEX/DEX hypothesis MVP

- **Owner:** `edcalderon`
- **Status:** IN PROGRESS
- **Focus:** CURRENT FOCUS — paired deterministic and stochastic model development
- **Started:** 2026-11-12

## Goal

Build a reproducible CEX/DEX simulator that produces evidence for the thesis hypotheses
from explicit, versioned configurations and traceable run artifacts.

## Acceptance criteria

- Versioned runners produce deterministic E0/E1/E2/E3 mechanics and paired stochastic
  selection contrasts.
- Runs record exact configurations, source checksums, seeds, run metadata, and outputs.
- The ODD scope, assumptions, event order, and role-level decision rules are documented.
- CPMM identities, asset conservation, reserve positivity, arbitrage behavior, and paired
  random schedules are checked before results are promoted to the manuscript.
- Agent policies are reviewed and extended to the intended heterogeneous model; H1c is
  tested on held-out configurations across the agreed operating regions.

## Dependencies and limits

- The manuscript's original `experiments/cex_dex_preliminary/` source and outputs are
  absent. Its numerical claims remain unverified.
- Model 0.4.0 uses four author-approved representative roles:
  arbitrageur, noise trader, trend/panic trader, and LP. The taxonomy is approved; its simple
  policy rules and thresholds remain selection assumptions for confirmation work.
- The current stochastic model is a selection model. The H1c run is a narrow held-out
  check of shock magnitude and seed stream under those same rules, not broad validation.
- The manuscript v0.3.0 now reports a separately traceable MVP table and labels the
  earlier v0.2.0 draft values as unverified historical claims; the new outputs do not
  claim to reproduce those old numbers.

## Progress

- Deterministic model 0.3.0 covers E0/E1 capacity, cost-band and delay mechanics; E2
  fixed-sale depth; and paired deterministic E3 static/adaptive LP policy selection.
- Its 144-row sweep includes 108 E0/E1 points, four E2 depth levels, and 16 paired E3
  policy settings. The E3 grid is for policy selection only.
- Added stochastic selection model 0.4.0 with four representative roles, wallet limits,
  exact CPMM swaps, per-tick asset-conservation checks, and shared pre-generated noise
  schedules for paired conditions.
- `pnpm experiment:mvp:abm` produced
  `cex-dex-abm-a99f9be866b2`: 300 seeds, eight scenario/shock groups, and 50,400
  trajectory rows. The configured approximate 95% peak-error interval half-width target
  of 0.005 was met for all six paired contrasts.
- At a +0.1 shock, high versus zero arbitrage capacity changed mean peak error by
  -0.10690 (approximate interval -0.11176 to -0.10204). Adaptive versus static LP changed
  mean peak error by +0.00529 (0.00426 to 0.00632). At a -0.1 shock, the peak-error
  difference was approximately zero while cumulative excess error increased by 0.00456.
- `pnpm experiment:mvp:h1c` produced
  `cex-dex-h1c-43e446f04adf`: four condition-specific maps trained on 48,000 transitions
  and tested on seeds 1000–1299 with shocks ±0.05. All four selection maps were
  Schur-stable; only three of eight held-out condition/shock majority labels agreed.
  Mean one-step RMSE was 0.01837 for d and 0.00840 for z. The z-equation fit was near
  zero R-squared; the current reduced map is not a reliable classifier in these regimes.
- `pnpm experiment:mvp:check` passes nine checks: 2,654 deterministic states and a
  504-state stochastic paired smoke selection, including conservation and common noise.
- Two independent fresh ABM executions and two H1c analyses produced matching core
  artifacts byte-for-byte. The deterministic sweep also replayed byte-for-byte.
- Manuscript revision v0.3.0 now reports the deterministic, stochastic selection, and
  H1c outputs in both languages. The previous bilingual source is preserved at
  `thesis/versions/v0.2.0/`, including the unverified old numeric claims.
- The v0.1.3 release published manuscript v0.4.0 with the clarified research
  question/objectives and records the prior v0.3.1 source alongside the new bilingual
  snapshot. Broader H1c confirmation remains scoped under THESIS-003.
- At manuscript v0.3.1, `pnpm language:check`, `pnpm docs:build`, and `make -C thesis pdf`
  passed; both generated PDFs were eight pages. The final local
  refscan preflight reports zero findings against four indexed PDFs in each edition;
  two bibliography entries remain uncovered and network verification was skipped.
- On v0.4.0, `pnpm release:verify` and paired thesis compilation passed; the English PDF
  is eight pages and the Spanish PDF is nine. Release v0.1.3 is published. The GitHub
  Pages workflow built the site and copied both thesis PDFs, then stopped at Configure
  Pages because repository Pages is not enabled.

## Next action

Broaden the approved four-role representative model across the agreed operating regions;
review policy thresholds and inventory limits before confirmation work. Keep further H1c fitting and confirmation
conditions separate. The old draft numbers remain archived and unverified unless their
original implementation and raw artifacts are recovered.

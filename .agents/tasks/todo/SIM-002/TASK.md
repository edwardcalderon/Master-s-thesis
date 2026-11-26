# SIM-002 — Animated 3D microworld, findings replay, and reproducible sandbox

- **Owner:** `edcalderon`
- **Status:** TODO — implementation has not started; this release records the plan.
- **Priority:** Presentation follow-up to the manuscript evidence work.
- **Planned:** 2026-11-25
- **Updated:** 2026-11-26; current workspace v0.1.10 / manuscript v0.8.0.
- **Dependencies:** SIM-001 browser model and bilingual UI; THESIS-003 evidence provenance;
  the v0.8.0 manuscript, frozen confirmation, engineering sensitivity, and hybrid-map export.

## Outcome and scientific relevance

Create a dedicated, visually rich 3D microworld view that explains how the simulated
CEX/DEX mechanisms produce the thesis findings. Synchronize the scene with readable
charts, a timeline, and a concise explanation of the selected contrast. Add bounded
scenario exploration and browser-local saved scenarios after the evidence replay works.

The scientific evidence remains the versioned experiment and its paired contrasts.
The interface is an explanatory and teaching artifact; improved comprehension is a
hypothesis for a later pedagogical evaluation. Visual realism must not imply market
calibration, external validity, heterogeneous populations, or learning agents.

The author requested a plan first, packaged as a workspace patch and PR. This task
queues implementation. Creating this document does not complete SIM-002 or SIM-001.

## Evidence and implementation baseline

- Manuscript v0.8.0 retains frozen confirmation run `cex-dex-confirm-5b06486d695e`, analysis
  version 0.5.0, and ABM model 0.4.0. There are 300 independent confirmation seeds,
  13,500 runs, three depths, three negative shocks, and five conditions. E1-max is
  extrapolation; the four primary conditions drive primary inference. Runs end at
  tick 20, and the seed is the independent unit after averaging cells within seed.
- Primary H1: high-capacity arbitrage reduces excess-error area, mean paired difference
  approximately -2.263; the planned effect-size precision was not reached.
- Primary H2: adaptive withdrawal raises maximum response by approximately 0.01143
  overall. This maximum-response effect is concentrated at depth 0.5 and is zero at
  depths 1 and 2 in the tested cells. The panic ablation is exploratory.
- Primary H3: the two-state map improves one-step MAE over persistence on average,
  but it does not beat scalar AR overall and its Schur regime classification is weak.
- The v0.8.0 extension adds a held-out affine-vs-band-aware map comparison (`cex-dex-hybrid-1d1d9d2f8c5b`): the hybrid map improves recursive signed-price-error MAE by 1.7% on average, but the gain is concentrated in low-capacity arbitrage at depth 2 and flow-pressure errors do not improve. The bilingual web summary at `apps/web/src/features/playground/HybridEvidence.tsx` consumes the compact, checksummed `apps/web/src/data/hybrid-findings.json` bundle and exposes all 32 held-out cells. This evidence chart is part of the current SIM-001 browser surface; SIM-002's 3D playback implementation remains queued.
- `thesis/figures/data/manifest.json` identifies the source run and checksums.
  `trajectories.csv` contains 420 aggregate tick rows (about 28 KB), including mean
  absolute excess and DEX deviation. These means do not identify individual trades,
  reserve paths, wallets, or role-level events. `inference.csv`, `cell_breakdown.csv`,
  `h3_by_condition.csv`, and `recovery_by_cell.csv` supply the evidence panels.
- The React/Vite site is static on GitHub Pages. SIM-001's browser model 0.3.0 supports
  bounded deterministic E0/E1 and E2 scenarios with SVG charts. It does not implement
  the stochastic confirmation model. There is no simulation API, database, or 3D
  renderer; local storage currently holds display preferences.
- The model has four representative roles: arbitrageur, noise trader, trend/panic
  trader, and LP. Adaptation is a fixed withdrawal rule, with no learning or evolution.

Source references: `experiments/cex_dex_mvp/confirm_config.json`, the experiment README,
`thesis/chapters/07-results.tex`, `thesis/chapters/08-discussion-and-conclusions.tex`,
and the immutable `thesis/versions/v0.5.0/` snapshot. Older H1c selection/holdout results
remain historical diagnostics and must not replace the current H1-H3 evidence.

## Experience and visual contract

Use a navigable 3D scene with a fixed default camera, an explicit CEX reference, a
constant-product pool with X/Y reserve indicators, and four clearly labeled role
markers. Encode reserve quantities and order directions consistently. Explain that
spatial placement is schematic; there is no spatial market geography in the model.
Animate actions only when a matching trace event exists. Avoid decorative crowds that
suggest within-role heterogeneity, or a simulated CEX order book absent from the model.

Place the tick timeline, paired comparison, and 2D evidence chart next to the scene.
Support play, pause, single-step, seek, restart, playback speed, and an explicit repeat
control. A repeat returns to the same initial state and seed, with a visible restart;
interpolation between recorded ticks is presentation only. Keep frame rate independent
of simulation time. Pause animation in a hidden tab and respect reduced motion.

The three guided stories are:

| Story | Comparison | Evidence and limitation to display |
| --- | --- | --- |
| H1: correction after a reference shock | E0, E1-low, E1-high | Excess-error area, recovery, seed distribution/interval, missed precision target. |
| H2: withdrawal in a shallow pool | E1-high versus E3 with paired noise | Maximum response by depth, including depths 1 and 2 where that difference is zero. Label any panic ablation exploratory. |
| H3: prediction and its limits | Map, persistence, scalar AR | One-step MAE and condition breakdown; weak regime classification remains visible. |

Present aggregate results and an illustrative realization with clear labels. Show
model/run identity, condition, depth, shock, seed where applicable, and synthetic scope.
Provide a readable chart/table fallback, keyboard controls, English/Spanish text, and
an accessible way to obtain the same conclusions without navigating the 3D scene.

## Implementation sequence and completion gates

### 1. Freeze the presentation data contract

Create a versioned compact presentation bundle from the confirmation artifacts. Reuse
existing figure data for aggregate charts. Include schema version, manuscript/model/
analysis versions, run ID, source hashes, units, conditions, primary/extrapolation
labels, aggregation definitions, metrics, uncertainty summaries, and synthetic scope.
Keep evidence immutable and preserve the paired seed design.

For agent animation, add a separate illustrative trace exporter that invokes the
reference ABM with a recorded configuration and seed. Document the seed-selection rule
before selecting a visually attractive path; allow alternate seeds when feasible.
Export paired conditions using the same exogenous schedule, with actual tick/event
order, pre/post reserves, wallet quantities, order amounts and directions, LP action,
and resulting prices. Do not infer these events from aggregated absolute-error data.
Retain subevent ordering when several actions occur within a tick.

Gate: exported metrics agree with reference run metrics under a documented numeric
tolerance; the manifest and trace provenance are complete; repeat export is deterministic
apart from explicitly excluded timestamps. Schema additions do not alter model rules
or overwrite released artifacts.

### 2. Build the evidence replay vertical slice

Implement one paired H2 example at depth 0.5 first, with a depth-1 comparison available
so the conditional result is apparent. Load compact artifacts on demand, animate their
recorded events, and synchronize the 2D chart and metrics with the timeline. Then add
H1 and H3 guided stories and the aggregate evidence panels.

Candidate integration paths: `apps/web/src/features/microworld/` for scene/replay/UI,
`apps/web/public/microworld/` for generated public bundles, existing locale dictionaries
for copy, and a separate exporter under `experiments/cex_dex_mvp/`. Select the 3D library
at implementation time after checking React compatibility and bundle cost. Load the
renderer only when the reader opens the view. Reuse the current visual tokens.

Gate: every displayed event comes from a trace; seeking and repeating preserve the
same outcome; all three stories display their qualifications; the view works through
GitHub Pages relative asset paths. Export/download links expose compact public artifacts.

### 3. Add bounded scenario exploration

Reuse the existing deterministic E0/E1/E2 browser calculations for their supported
scope. Identify their model version explicitly. A stochastic sandbox requires a
separate port of model 0.4.0 and parity checks against Python before it can represent
that model. Do not present model 0.3.0 calculations as confirmation results.

Expose a versioned configuration, seed when stochastic, finite horizon, and reset.
Record interventions with tick and event order; changing a configuration starts a new
scenario or an explicitly named fork. Preserve the baseline for paired comparisons.
Keep user experiments labeled exploratory and prevent them from changing the frozen
published evidence. Share/export exact inputs and resulting metrics.

Gate: supported parameter boundaries are enforced; seeded replay reproduces the same
trajectory; Python/browser parity covers shocks, depth, role actions, and accounting.
Use a Web Worker only if profiling demonstrates a responsiveness problem.

### 4. Save and restore local scenarios

Add named browser-local save slots and JSON export/import. Save schema/model versions,
configuration, seed, scenario identity, and playback cursor. Prefer replay from saved
inputs for bounded runs. If checkpoints are introduced, serialize complete simulation
and RNG state plus the event cursor; verify resumed and uninterrupted outcomes agree.

Handle unavailable/quota-limited storage, malformed imports, incompatible versions,
and user deletion. State clearly that local saves belong to this browser and can be
lost when browser data is cleared. Reloading can restore a scenario; simulation time
does not advance while the application is closed. A looping replay remains visibly
bounded and must not imply evidence about long-run evolution.

Gate: reload, import/export, deletion, schema rejection, and restart recovery work
without losing published evidence or mixing scenarios.

### 5. Complete accessibility, performance, and provenance review

Check EN/ES parity, keyboard use, reduced motion, narrow layouts, WebGL failure,
background-tab behavior, and static deployment paths. Keep the existing text/2D views
usable while 3D assets load or when rendering is unavailable. Profile on an agreed
mobile-class reference device; initial targets are a lazy 3D payload below 1 MB gzip
and a p95 frame time below 33 ms on the selected replay. Record measurements and any
justified budget revision before calling this gate complete.

Run reference parity/accounting checks and relevant UI tests, then repository release
checks. Review the displayed H1-H3 claims against the source manuscript and CSVs.
A small usability review should ask whether readers can explain the three findings
and limitations; any claim of measured educational benefit requires a separate study.

## Architecture

```text
Frozen confirmation artifacts -> compact versioned bundle -> static evidence charts
Reference ABM + fixed seed -> paired event traces -> synchronized 3D replay
User inputs -> bounded browser model -> exploratory scenario -> local saves/export
Optional GitHub snapshot -> freshness-checked shared-world view -> browser fallback
Optional Azure job API -> isolated bounded runs -> versioned result bundles
```

The browser-local deterministic model and published evidence view are the permanent
no-backend baseline. Once the static app and its assets have loaded, calculations must
not require a network connection, Azure configuration, or a simulation service; initial
page delivery still depends on GitHub Pages or a cached copy. Local scenarios remain
on the user's device and can be exported. The rendering loop consumes states; it does
not determine market outcomes.

The shared persistent world is an optional layer. Its GitHub-hosted snapshot may be
polled and presented with model version, synthetic-data label, tick, and update time.
The view must show stale/unavailable status and continue to the local baseline when
the snapshot is absent or old. Public GitHub scheduled workflows may be auto-disabled
after 60 days without repository activity, so this feed is a convenience rather than
the availability guarantee.

An optional higher-compute layer submits bounded, reproducible exploratory scenarios
to an Azure App Service F1 API using the reference ABM v0.4.0. Each response carries a
run ID, model/configuration version, seed range, finite horizon, paired scenario
summaries, and aggregate trajectory. The UI stores the returned JSON locally and
offers a download; runs never modify the shared-world branch. F1 has a daily CPU quota
and no SLA, and the subscription can expire, so failures disable only this layer.
Interactive results remain exploratory and do not update the frozen thesis evidence.

This service tier is not part of SIM-002's initial 3D replay gate. INFRA-001 owns its
hosting, cost, lifecycle, and recovery contract; SIM-002 owns the presentation and
fallback behavior. Longer-run persistence or evolutionary agents remain a new research
model with explicit rules and validation, not a runtime switch on the current ABM.

## Deferred persistent and evolutionary research extension

A shared world that continues while browsers are closed needs a separately scoped
service: an authoritative simulation clock, versioned state and RNG checkpoints,
append-only events, restart recovery, isolated scenario forks, bounded storage/compute,
and an explicit owner/hosting budget. Document why static bundles or local saves cannot
meet the chosen use case before introducing that infrastructure.

Long-running dynamics also need model rules for repeated shocks, depleted inventories,
liquidity replenishment, termination, and observation windows. Evolution requires
explicit strategy inheritance/update rules, fitness/selection, and possibly mutation
or learning. Each changes the research object and needs a new model version, hypotheses,
and independent evaluation. DATA-001 remains the separate empirical-validation path;
persistent synthetic records do not establish realism.

## Acceptance criteria

- [ ] Versioned aggregate bundle and independently labeled illustrative event traces.
- [ ] Faithful 3D playback with synchronized charts, pause/step/seek/restart/repeat.
- [ ] H1-H3 stories include uncertainty, conditional findings, and predictive limits.
- [ ] Bounded exploratory scenarios expose exact model, inputs, and seed as applicable.
- [ ] Local save/import/export behavior and version compatibility are documented.
- [ ] Bilingual accessible fallback and measured performance gates pass.
- [ ] Reference parity, conservation, deterministic replay, and provenance checks pass.
- [ ] SIM-001 handoff and implementation evidence are recorded before closing tasks.

## Risks and next action

The main risks are a visually persuasive scene that overstates model realism, a browser
port drifting from Python, and presentation work expanding into an unbounded service.
The data contract, trace provenance, paired comparisons, and phased gates address those
risks. H3 should remain legible as a conventional prediction comparison even when the
3D scene is the visual focal point.

Next action: implement the compact bundle and paired trace export in phase 1, then
review a single faithful replay before expanding the visual scope. Implementation is
queued; no 3D feature, persistence service, or new research result ships with this plan.


## v0.6.0 findings handoff — 2026-11-25

Include supplementary run cex-dex-engineering-9438e194aa7e, with three order-size/panic variants and 40,500 synthetic paths. Show first sustained recovery, terminal in-band status, later departures and order size relative to reserves. The adaptive fixed-order paths recover at least once in 97.4% of cases, finish in-band in 81.9%, and 31.2% of recovered paths later leave the band. The shallow-depth response effect vanishes under reserve-proportional orders. Mark these as synthetic sensitivities; do not display them as production thresholds or live-world states. The 3D scene is an explanatory evidence view, not proof of external validity.

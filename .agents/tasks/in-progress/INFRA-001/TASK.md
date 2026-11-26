# INFRA-001 — Resilient microworld baseline + optional Azure compute tier

- **Owner:** `edcalderon`
- **Status:** IN PROGRESS
- **Focus:** —
- **Goal:** Keep the core thesis simulator usable without Azure credit or a running
  service, while offering a separable hosted-world and higher-compute tier when
  available. A cloud outage, disabled schedule, or expired student credit must never
  block the browser-based core.

## Relationship to SIM-001 and SIM-002

[`SIM-001`](../../../.agents/tasks/in-progress/SIM-001/TASK.md) requires the core
browser playground to need no application server or paid compute, and requires any
server-side compute proposal to document why browser execution or a static artifact
can't meet the use case. This task is that documentation and its implementation: a
continuously-evolving microworld is a standing stateful process between page loads,
which a browser computation or a static precomputed artifact cannot represent. The
static playground and this engine stay decoupled — the engine publishes compact,
checksummed snapshots the static site can optionally read, but the static site keeps
working with zero dependency on this infrastructure being up.

[`SIM-002`](../../../.agents/tasks/todo/SIM-002/TASK.md)'s "Deferred persistent and
evolutionary research extension" section names this exact thing — *"a shared world
that continues while browsers are closed"* — and requires it to be a **separately
scoped service** with: an authoritative simulation clock, versioned state and RNG
checkpoints, append-only events, restart recovery, isolated scenario forks, bounded
storage/compute, and an explicit owner/hosting budget. INFRA-001 is that separate
scope. Checked against each requirement as actually built:

| Requirement | Status |
| --- | --- |
| Browser baseline | Met for compute — deterministic E0/E1/E2 runs locally after the static app loads; it does not call Azure. Static-site delivery itself still depends on its host or a cached copy. |
| Free shared-world refresh | Partial — GitHub Actions advances a shared snapshot on a 15-minute schedule, but public-repository schedules can be disabled after 60 days without repository activity. This feed is optional and must show staleness/errors without disabling the local playground. |
| Versioned state and RNG checkpoints | Partial — `state.json` stores model version and seed for the current state; there is no historic full-checkpoint rollback. |
| Append-only events | Not met — the GitHub baseline retains a bounded 500-entry rolling history. |
| Scenario isolation | Not met — current hosted state is shared and mutable. Per-run higher-compute jobs must use isolated run IDs and must not mutate the shared baseline. |
| Azure cost independence | Met by design — no Azure resource may be required to open, run, save, or replay the core browser model. |
| Bounded Azure ABM view | Implemented locally — App Service F1 API runs the reference ABM with hard caps and returns an isolated exploratory bundle. Deployment and live endpoint configuration remain pending. |

SIM-002 also notes long-running dynamics need model rules for repeated shocks,
depleted inventories, liquidity replenishment, termination, and observation windows,
and that evolution needs explicit inheritance/selection rules — "each changes the
research object and needs a new model version, hypotheses, and independent
evaluation." `tick.py` deliberately doesn't attempt any of that; see its module
docstring and THESIS-001 in Dependencies below.

## Current subscription check (2026-11-26)

The signed-in subscription is enabled **Azure for Students**. `Microsoft.Web` was
registered for deployment; `Microsoft.Storage` and `Microsoft.Compute` were already
registered. The `rg-microworld` resource group now contains one F1 Linux plan and its
API app in Brazil South. Credit and expiration remain unavailable in CLI; check the
Sponsorships portal.

The previous **Azure for Students Starter** observations are historical and do not
describe the active subscription. [`main.bicep`](../../../infra/azure/bicep/main.bicep)
now describes only an optional Linux F1 API. The static core and scheduled shared
world do not depend on it.

## Two execution tiers

1. **Core — no service or student credit.** The static site runs the supported
   deterministic model in the browser and keeps named inputs locally. This is the
   durable fallback and remains fully usable if scheduled workflows or Azure stop.
2. **Hosted world — free, best-effort refresh.** The existing public-repository
   GitHub Actions workflow runs `tick.py` every 15 minutes and stores a compact,
   synthetic snapshot on `microworld-data`. The UI may poll that snapshot, expose
   its timestamp/model version, and fall back to Core on 404, stale data, or network
   failure. GitHub currently makes standard hosted runner use free for public repos,
   but scheduled workflows are auto-disabled after 60 days without repo activity;
   this is therefore not the only baseline path.
3. **Azure enhanced — optional and bounded.** The Flask API runs reference `abm.py`
   model v0.4.0 for paired static/adaptive LP scenarios, using a shared random schedule
   within each seed. Requests are capped at 100 seeds x 100 ticks, bounded shock and
   capacity values, and a ten-minute best-effort process cooldown. The API returns an
   isolated bundle and never writes to shared state or thesis artifacts. It uses App
   Service F1, so it does not consume student credit but is quota-limited and has no
   production availability guarantee. If the endpoint is unavailable, the static
   browser and hosted snapshot remain usable.

The enhanced runs must use an explicitly versioned scientific model and reproducible
seed/configuration manifests. The current `tick.py` dynamics remain a placeholder and
must not be shown as thesis findings. Keep Lean verification and routine CI on GitHub.

## Acceptance criteria

- Core E0/E1/E2 runs without a backend, Azure config, or an account once the static
  app is loaded; saved scenarios remain local and exportable.
- The public snapshot feed shows model version, synthetic status, tick, and update
  time; stale/missing snapshots never block Core.
- Enhanced runs reproduce from seed/config inputs, display paired ABM outputs, retain
  result JSON locally, and never alter shared state or frozen confirmation files.
- The GitHub scheduled workflow is manually verified and has a documented re-enable
  path if inactivity disables the schedule.
- Azure resources are behind an explicit feature flag and can be removed/disabled
  without changing the static baseline.
- Enhanced jobs enforce parameter, seed-count, horizon, concurrency, and timeout caps;
  isolated run outputs never mutate baseline state.
- No secrets enter Git. F1 daily CPU quota and student-credit expiry remain visible
  operational limits; the core does not depend on either.
- Each remaining SIM-002 persistence/evolution requirement has a named status or
  follow-up; visual realism and synthetic results remain clearly labeled.

## Dependencies

- [`SIM-002`](../../../.agents/tasks/todo/SIM-002/TASK.md)'s deferred-extension
  section as the originating scope decision for this task existing at all.
- THESIS-001's versioned model as the eventual source of real tick semantics —
  `tick.py`'s current rule is an explicitly-labeled placeholder, not a reviewed
  extension (see its module docstring).
- Operator-side checks: view remaining student credit/expiry, confirm provider and
  regional quotas, and set billing alerts before any Azure deployment.

## Progress

- Confirmed via read-only `az` checks that the Azure for Students subscription is
  enabled. Registered `Microsoft.Web`, created the resource group, and deployed the
  F1 app/plan after what-if showed exactly two creates.
- Replaced the obsolete F1/Starter assumptions in Bicep and the deployment script with
  the optional, bounded F1 ABM API template and a required what-if step.
- Wrote and locally tested `infra/microworld/tick.py` (resume-from-state, scenario
  overrides, rejection of unrecognized fields all verified in a scratch directory)
  and `infra/azure/webapp/app.py` (all routes smoke-tested with Flask's test client).
- Added finite, bounded scenario validation at both the tick engine and dispatcher;
  invalid persisted state fails closed. Bounds are band `[0, 0.5]`, capacity
  `[0, 1]`, and shock scale `[0, 0.2]`.
- Hardened branch recovery so remote lookup/fetch errors stop the run instead of
  silently initializing a fresh world. First-run initialization uses an orphan
  worktree of the authenticated checkout, so publishing the newly created data
  branch retains the configured remote credentials. Each published tick is a
  parentless Git commit, keeping the public data branch from accumulating unbounded
  ancestry.
- Passed 3 tick-engine unit tests and 2 Flask endpoint tests locally. A 2-tick
  scratch run succeeded; a NaN scenario was rejected with exit code 2 before state
  was changed. The workflow has not yet had its first real manual run.
- Kept scenario JSON in a workflow environment variable to avoid interpolating
  user-controlled input into shell source.
- Workflow and application code were merged by PR #5 on 2026-11-26. The required
  first manual run has not happened yet.
- The F1 API health endpoint returned HTTP 200. A paired ABM v0.4.0 smoke run returned
  HTTP 200; the maximum 100-seed/100-tick run returned HTTP 200 in 1.27 seconds in one
  F1 observation. Timing is not an SLA.
- Measured the local placeholder tick script at 50 ticks / 0.04 seconds on this host;
  use this only as a sizing hint, not an Azure performance benchmark.
- Added the live dashboard to the bilingual static playground. It polls snapshot and
  history every 30 seconds, labels freshness/provenance, and falls back when absent.
- Added `experiment.py` using reference ABM v0.4.0 with matched noise schedules,
  bounded controls, provenance, percentile summaries, and aggregate trajectories. A
  100-seed/100-tick local run took about 0.34 seconds on this host.
- Added `/api/experiment` and its paired-run result visualization with local save and
  JSON download. Frontend lint/build and Flask tests pass; a two-seed/five-tick API
  smoke run returned model v0.4.0.
- `apps/web/.env.production` points the static build to the deployed HTTPS API. The
  website update is not published yet; the shared-world branch needs its first manual
  tick.
- The enhanced run endpoint computes directly in Azure and needs no GitHub token. The
  legacy `/api/scenario` route remains unconfigured and is not called by the dashboard.

## Remaining work

- Merge the dashboard/docs PR so Pages builds and deploys; verify the enhanced form
  reaches the API and the static dashboard remains usable if the API is unset.
- Trigger the merged shared-world workflow once manually; verify its first snapshot and
  freshness display, then observe one scheduled refresh.
- Check student credit/expiry in Sponsorships. F1 has a published $0 list price but a
  daily CPU quota and no SLA; keep the endpoint optional and monitor quota usage.
- Replace `tick.py`'s placeholder evolution rule with real, reviewed tick semantics
  once THESIS-001 has a view on what a "live" instance of the model should mean.
- The legacy `/api/scenario` mutation/dispatch route remains unconfigured. Do not expose
  it as scenario submission; the separate `/api/experiment` path is paired and isolated.
- Decide whether any full, non-trimmed event history is worth retaining (e.g. as a
  periodic archival snapshot) given `history.json`'s bounded-window trade-off above.

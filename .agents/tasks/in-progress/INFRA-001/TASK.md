# INFRA-001 — Microworld tick engine (GitHub Actions) + Azure dispatcher backend

- **Owner:** `edcalderon`
- **Status:** IN PROGRESS
- **Focus:** —
- **Goal:** Stand up an autonomous, periodically-ticking microworld simulation whose
  state the static playground can read, plus the one small live backend needed to
  accept scenario requests from the frontend — all free, given this subscription's
  constraints (below).

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
| Authoritative simulation clock | Met — the `microworld-data` branch's `tick` counter is the single source of truth; the cron run is the only writer. |
| Versioned state and RNG checkpoints | Partial — `state.json` carries `model_version` and `seed`, and resume is deterministic, but only the *current* state is kept; there is no retained history of earlier full checkpoints to roll back to. |
| Append-only events | **Not met as specified** — `history.json` is a bounded rolling window (last 500 ticks), not append-only, to keep storage/compute bounded per the next requirement. This is a deliberate trade, not an oversight, but it means no full event history survives past that window. |
| Restart recovery | Met — `tick.py` resumes from `state.json` if present; the workflow's worktree-checkout step reconstructs it from the branch on every run. |
| Isolated scenario forks | **Not met** — the current design has one global, shared, mutable world; a scenario POST changes state for everyone, there is no forking. This is the biggest open gap against SIM-002's requirement and the main reason this should still be treated as a wiring demo, not a scenario-exploration surface. |
| Bounded storage/compute | Met — F1's own quota, a single small state file, and a trimmed history enforce this by construction. |
| Explicit owner/hosting budget | Met — $0; this subscription cannot accrue a bill (see below). |

SIM-002 also notes long-running dynamics need model rules for repeated shocks,
depleted inventories, liquidity replenishment, termination, and observation windows,
and that evolution needs explicit inheritance/selection rules — "each changes the
research object and needs a new model version, hypotheses, and independent
evaluation." `tick.py` deliberately doesn't attempt any of that; see its module
docstring and THESIS-001 in Dependencies below.

## What the subscription actually allows (confirmed empirically, 2026-11-25)

The Azure subscription available for this project is an **Azure for Students
Starter** ("DreamSpark") grant, not the $100-credit "Azure for Students" offer
originally assumed. Live checks against it showed:

- Only `Microsoft.Web` and `Microsoft.Sql` are usable among compute/storage-shaped
  providers; `Microsoft.Compute`, `Microsoft.Storage`, `Microsoft.Network`,
  `Microsoft.App`, container/registry, `Microsoft.KeyVault`,
  `Microsoft.ManagedIdentity`, `Microsoft.DocumentDB`, `Microsoft.OperationalInsights`,
  `Microsoft.Consumption` are all `DisallowedProvider` — a policy on the subscription
  type, not a raisable quota.
- App Service is capped at Free (F1): Basic (B1) fails with *"your DreamSpark
  subscription can only create sites in the 'Free' SKU."*
- Only `brazilsouth` accepted a deployment, of 11 regions tried.

F1 has no Always On and a small CPU-minute quota, so it cannot host a 24/7
continuously-ticking process. Offered and **declined**: applying for the real
"Azure for Students" $100-credit offer, or upgrading this subscription to
pay-as-you-go with a card. Chosen instead: stay on Starter and move the actual
engine off Azure entirely. See [`infra/azure/README.md`](../../../infra/azure/README.md)
for the full writeup.

## Architecture

- **Tick engine:** [`infra/microworld/tick.py`](../../../infra/microworld/tick.py),
  run by [`.github/workflows/microworld-tick.yml`](../../../.github/workflows/microworld-tick.yml)
  on a 15-minute cron plus manual dispatch. Free and unlimited — this repo is public.
  State lives on a dedicated `microworld-data` branch (one parentless rolling commit per run),
  never touching `main` or its versioning/Pages tooling.
- **Reads:** the static site can fetch `snapshot.json`/`history.json` straight from
  `raw.githubusercontent.com` on that branch — no Azure involved.
- **Web handler backend:** [`infra/azure/webapp/`](../../../infra/azure/webapp/), a
  minimal Flask app deployed to the one resource this subscription allows
  ([`infra/azure/bicep/main.bicep`](../../../infra/azure/bicep/main.bicep): F1 App
  Service, `brazilsouth`). Its only job: accept a scenario POST from the frontend and
  turn it into an authenticated `workflow_dispatch` call, since a public static
  frontend can't hold that secret itself.

## Acceptance criteria

- `az deployment group what-if` runs clean against `main.bicep` with real parameters.
- The dispatcher Web App is deployed, reachable over HTTPS, and a POST to
  `/api/scenario` with a recognized field produces a corresponding GitHub Actions run.
- `microworld-tick.yml` has at least one successful manually-triggered run, confirmed
  by inspecting its log, before being left to the schedule.
- The static playground (SIM-001) builds and runs with zero network dependency on
  this infrastructure.
- No secret (GitHub token, service-principal credentials) ever reaches Git history.
- Each of SIM-002's seven deferred-extension requirements is either met or carries
  an explicit, named follow-up (see the table above) — not silently unmet.

## Dependencies

- [`SIM-002`](../../../.agents/tasks/todo/SIM-002/TASK.md)'s deferred-extension
  section as the originating scope decision for this task existing at all.
- THESIS-001's versioned model as the eventual source of real tick semantics —
  `tick.py`'s current rule is an explicitly-labeled placeholder, not a reviewed
  extension (see its module docstring).
- Operator-side steps outside this repo: `az login`, running
  `infra/azure/scripts/bootstrap-service-principal.sh`, creating the fine-scoped
  GitHub token and setting it as a Web App application setting.

## Progress

- Confirmed via live, read-only `az` checks (and one reversible probe-create/delete)
  exactly what this subscription allows; discarded the original VM/Storage/VNet plan
  once it turned out to be built for a subscription type this isn't.
- Rebuilt `infra/azure/` around the real constraint: `main.bicep` now creates only an
  F1 App Service plan + Web App in `brazilsouth`.
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
- Nothing has been deployed to Azure yet. No service principal exists yet. No GitHub
  token has been created yet.

## Remaining work

- Operator runs `bootstrap-service-principal.sh`, then `deploy-infra.sh` (what-if,
  then `--apply`).
- Deploy `infra/azure/webapp/` to the created Web App and set `GITHUB_DISPATCH_TOKEN`
  / `GITHUB_REPO` as application settings (never committed).
- Trigger the merged workflow once manually and read the run log — first-run branch
  creation has only been exercised against a local bare remote, not the real remote.
- Confirm `apps/web`'s intended fetch URL/CORS story against the real Pages origin,
  then set `ALLOWED_ORIGIN` on the Web App accordingly (currently defaults to `*`).
- Replace `tick.py`'s placeholder evolution rule with real, reviewed tick semantics
  once THESIS-001 has a view on what a "live" instance of the model should mean.
- Decide and implement scenario isolation (per-request forks vs. one shared world)
  before presenting scenario submission as anything but a shared demo toggle —
  currently the biggest gap against SIM-002's deferred-extension requirements.
- Decide whether any full, non-trimmed event history is worth retaining (e.g. as a
  periodic archival snapshot) given `history.json`'s bounded-window trade-off above.

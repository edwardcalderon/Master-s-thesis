# Azure deployment plan — microworld tick engine + dispatcher backend

Status: tracked as [`INFRA-001`](../../.agents/tasks/in-progress/INFRA-001/TASK.md),
which is the separately-scoped service
[`SIM-002`](../../.agents/tasks/todo/SIM-002/TASK.md)'s "Deferred persistent and
evolutionary research extension" section requires before any shared world may keep
evolving while browsers are closed — see INFRA-001's task record for how this design
checks against each of that section's requirements. One empty resource group exists
in the subscription from before this task; nothing else has been deployed.

## What changed from the first draft

The first draft of this plan assumed the full "Azure for Students" offer ($100
credit, normal resource providers/regions). Live, read-only checks against the real
subscription on 2026-11-25 showed it is actually an **Azure for Students Starter**
("DreamSpark") grant, which is a different and far more restricted thing:

- Only `Microsoft.Web` and `Microsoft.Sql` are usable among anything compute- or
  storage-shaped. `Microsoft.Compute` (VMs), `Microsoft.Storage`, `Microsoft.Network`,
  `Microsoft.App`, `Microsoft.ContainerInstance`/`ContainerRegistry`,
  `Microsoft.KeyVault`, `Microsoft.ManagedIdentity`, `Microsoft.DocumentDB`,
  `Microsoft.OperationalInsights`, and `Microsoft.Consumption` are all
  `DisallowedProvider` on this identity — a policy on the subscription type itself,
  not a quota that can be requested up.
- App Service is capped at the **Free (F1)** SKU. Attempting Basic (B1) returned:
  *"your DreamSpark subscription can only create sites in the 'Free' SKU. You can
  upgrade your subscription to a pay-as-you-go subscription to create sites in any
  SKU."*
- Only **`brazilsouth`** accepted a deployment, out of 11 regions tried (including
  `eastus`, `eastus2`, `westeurope`, `japaneast` — all `RequestDisallowedByAzure`).

F1 App Service has no "Always On" and a small daily CPU-minute quota — by design, it
cannot host a process that ticks continuously in real time. No IaC or architecture
choice routes around that; it's a platform restriction on this subscription tier, not
a sizing problem. Options that would lift it (a separate verified "Azure for
Students" signup with the $100 credit, or upgrading this subscription to
pay-as-you-go with a card) were offered and **declined** — the chosen direction is to
stay on Starter and redesign around its limits.

## Architecture actually being built

Three pieces, none of them a 24/7 Azure compute resource:

1. **Tick engine — GitHub Actions, not Azure.** A scheduled workflow
   ([`.github/workflows/microworld-tick.yml`](../../.github/workflows/microworld-tick.yml))
   runs on a cron (every ~15 minutes) plus `workflow_dispatch`. Each run advances the
   microworld by a batch of simulated ticks and writes the result. This repo is
   public, so Actions minutes are unlimited/free regardless of how often it runs.
   "Perpetual, real-time" becomes **"autonomous and periodic, refreshed every ~15
   minutes, simulated time advances faster than wall-clock time within each run"** —
   an explicit, honest downgrade from literal continuous ticking, not a disguised one.

2. **State and reads — a dedicated git branch, not Azure Storage.** The workflow
   keeps `state.json` (full internal state), `snapshot.json` (compact, checksummed,
   versioned — matching [`SIM-001`](../../.agents/tasks/in-progress/SIM-001/TASK.md)'s
   own conventions), and a bounded `history.json` (last N ticks only) on a
   `microworld-data` branch, replacing its parentless root commit each run rather than
   growing history forever. Failed remote-branch lookups abort instead of silently
   initializing over saved state. Scenario inputs are finite and range checked before
   they reach persisted state. `main` and its versioning/changelog tooling are untouched —
   [`pages.yml`](../../.github/workflows/pages.yml) only triggers on pushes to `main`.
   The static site (`apps/web`, GitHub Pages) can fetch `snapshot.json`/`history.json`
   straight from `raw.githubusercontent.com`, with zero Azure dependency for reads.

3. **Web handler backend — Azure, F1, and genuinely needed for exactly one thing.**
   A public static frontend can't hold the secret needed to trigger a GitHub Actions
   run safely. [`webapp/`](webapp/) is a minimal Flask app, deployed to the one App
   Service this subscription allows (`main.bicep`, F1, `brazilsouth`), whose only job
   is: accept a scenario-parameter POST from the frontend, validate it, and call
   GitHub's `workflow_dispatch` API with it as input. Sparse, bursty traffic — F1's
   cold-start-after-20-min-idle and tiny CPU quota are fine for this; they would not
   be fine for the engine itself, which is why the engine doesn't live here.

```
apps/web (GitHub Pages) ──reads──▶ raw.githubusercontent.com/.../microworld-data/*.json
        │
        └──POST scenario──▶ Azure App Service (F1, brazilsouth) ──dispatch──▶ GitHub Actions
                                                                                   │
                                                                      microworld-tick.yml
                                                                      (cron + dispatch)
                                                                                   │
                                                                     writes state to
                                                                     microworld-data branch
```

## Cost posture

Zero, by construction: GitHub Actions on a public repo is free regardless of
frequency; the `microworld-data` branch is git storage, not a billable resource; F1
App Service is free and this subscription cannot create anything that bills. There is
nothing to budget or alert on — `Microsoft.Consumption` (where Azure Budgets live) is
blocked anyway, and is moot here: Starter has no payment method attached, so there is
no bill to overrun.

## Run order

1. `az login` as yourself (human, one-time).
2. `./scripts/bootstrap-service-principal.sh` — creates the resource group and a
   service principal scoped to it only. If this fails on the app-registration step,
   see the troubleshooting note in the script (EDU tenants sometimes restrict who can
   register applications, separately from anything about the subscription).
3. Log in as that service principal (the bootstrap script prints the command).
4. `./scripts/deploy-infra.sh rg-microworld` (what-if only), review, then
   `./scripts/deploy-infra.sh rg-microworld --apply`.
5. Deploy `webapp/` to the created Web App (e.g. `az webapp up` or a GitHub Actions
   CD step using the `azure/webapps-deploy` action) and set its one required secret —
   a fine-scoped GitHub token with `actions:write` on this repo — as an App Service
   application setting, never committed.
6. Merge `.github/workflows/microworld-tick.yml`, then trigger it once by hand
   (`workflow_dispatch`) and read the run log before trusting the schedule — the
   branch-creation step in particular should be watched on its first run.

## Identity: letting an agent apply changes here

Unchanged in spirit: a service principal scoped to one resource group, never
subscription-wide. See
[`scripts/bootstrap-service-principal.sh`](scripts/bootstrap-service-principal.sh).
The one addition from Starter's AAD tenant: if app-registration creation turns out to
be restricted, the fallback is `az login` interactively each session rather than an
unattended service principal — az's on-disk token cache still persists across tool
calls within a session even though shell environment variables don't.

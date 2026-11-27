# Live microworld service tiers

Status checked 2026-11-26. Work is tracked in
[`INFRA-001`](../../.agents/tasks/in-progress/INFRA-001/TASK.md). The UI and simulation
are split into a durable browser core, a periodic shared snapshot, and an optional
Azure-hosted exploratory runner. The static site must remain usable when either hosted
layer is unavailable.

## Runtime layers

| Layer | Execution and storage | Failure behavior |
| --- | --- | --- |
| Browser core | Static GitHub Pages app; deterministic E0/E1/E2 controls and evidence charts run in the browser. | No simulation API is needed after the page loads. Initial page delivery still depends on GitHub Pages or a cached copy. |
| Shared microworld | Public GitHub Actions workflow advances `infra/microworld/tick.py` every 15 minutes and publishes `snapshot.json` plus bounded `history.json` to `microworld-data`. | The page shows offline/stale state and retains the browser core. This branch currently uses a placeholder random-walk rule, clearly labeled synthetic. |
| Exploratory run | Optional App Service F1 API runs paired ABM v0.4.0 scenarios with bounded seed/horizon controls. Its JSON result is returned to the page and retained locally/exportable. | API errors disable this feature only. It never mutates the shared tick branch or confirmation evidence. |

GitHub's standard hosted runners are free for public repositories
([billing](https://docs.github.com/en/billing/concepts/product-billing/github-actions)).
However, GitHub may disable public-repository scheduled workflows after 60 days with
no repository activity ([schedule behavior](https://docs.github.com/en/enterprise-cloud%40latest/actions/how-tos/manage-workflow-runs/disable-and-enable-workflows?tool=webui));
the schedule may also be delayed. Treat its shared snapshot as best-effort and re-enable
or manually dispatch it if needed. The browser simulator remains the fallback.

The shared tick's `infra-001-placeholder-0.1` Gaussian shock process is a wiring/demo
mechanism, **not the thesis ABM and not evidence**. The enhanced endpoint instead calls
the reference `experiments/cex_dex_mvp/abm.py` model v0.4.0. Each request compares static
LP and adaptive LP scenarios using the same exogenous schedule per seed. Caps are 100
seeds, 100 ticks, shock log-return [-0.2, 0.2], capacity [0, 0.1], and a ten-minute
best-effort process cooldown. Enhanced runs are exploratory web output, not frozen
confirmation, statistical validation, or empirical market evidence.

## Azure status and cost boundary

Read-only CLI checks on 2026-11-26 showed the signed-in subscription is enabled and
named **Azure for Students**. `Microsoft.Web` is now registered for the deployment;
`Microsoft.Storage` and `Microsoft.Compute` were already registered. Container Apps,
managed identity, and Log Analytics are not needed by this design. The resource group
`rg-microworld` now contains only the F1 plan and API app. The remaining student credit
and expiry were not exposed by `az account show`; check them in the Sponsorships portal.

The optional dispatcher and bounded ABM endpoint use Linux App Service **F1**. Microsoft's
published price is $0, with shared compute (60 CPU minutes/day), 1 GB storage, no SLA,
and a statement that Free is intended for trials/learning rather than production
([App Service pricing](https://azure.microsoft.com/en-us/pricing/details/app-service/linux/)).
This is an experimental convenience endpoint only. It is not an availability guarantee;
F1 quota exhaustion or the end of the student subscription must not affect the core or
the hosted snapshot. The Azure for Students offer advertises $100 for 12 months
([offer](https://azure.microsoft.com/en-us/free/students)); those credits are not
required by the F1 API. Subscription services can be disabled at credit/term end unless
the offer is upgraded ([subscription behavior](https://learn.microsoft.com/en-us/azure/cost-management-billing/manage/azurestudents-subscription-disabled)).

The API is deployed at
[`https://microworld-api-c4fbpfkm5xvvq.azurewebsites.net`](https://microworld-api-c4fbpfkm5xvvq.azurewebsites.net).
Its health endpoint returned HTTP 200, a small paired ABM request returned model v0.4.0,
and the maximum configured 100-seed/100-tick request returned HTTP 200 in 1.27 seconds
in one F1 observation. That timing is an observation, not an SLA. The dashboard is
published at [`https://edwardcalderon.github.io/Master-s-thesis/`](https://edwardcalderon.github.io/Master-s-thesis/)
and its production build points to this endpoint.

The App Service API currently has no persistent server database. The shared world is
persisted in its bounded Git branch; each optional experiment result is returned to the
browser, saved in browser storage, and can be downloaded as JSON. Do not represent the
API as an always-running process. No secrets are embedded in the static app.

## Deploy and operate

1. Log in with `az login` and confirm the selected subscription name/state.
2. The 2026-11-26 deployment registered `Microsoft.Web`, created `rg-microworld` in
   Brazil South, and applied a what-if with exactly two F1 creates (plan + app).
3. Package `infra/azure/webapp/app.py` and requirements together with
   `infra/microworld/experiment.py` and the reference `abm.py`, `run.py`, and
   `abm_config.json`; deploy the ZIP and confirm `/` returns `{"status":"ok"}`.
4. `apps/web/.env.production` sets `VITE_MICROWORLD_API_URL` to the deployed HTTPS hostname for the Pages build.
   The CORS origin is the GitHub Pages origin (`https://edwardcalderon.github.io`).
5. The first manual `microworld-tick.yml` run succeeded on 2026-11-26 and published
   snapshot tick 50 with a UTC timestamp. Observe scheduled refreshes and stale fallback.
6. If the optional endpoint reaches its F1 limit or is removed, clear the frontend API
   setting and redeploy the site; the browser and hosted-snapshot views continue.

The F1 plan and API deployment plus health and max-bound smoke checks are complete.
The static Pages build has the API URL configured, but the feature branch still needs
to reach `main` before the site points readers to it. F1 avoids consuming the 12-month
student credit; upgrading to a paid SKU needs a separate budget decision.

## Optional empirical data archive

The CEX/DEX ingestor is documented in
[`experiments/empirical_data/README.md`](../../experiments/empirical_data/README.md).
The Bicep template can optionally provision a private Standard LRS Blob account and
container by setting `createHistoricalDataStorage=true`; the option defaults to
`false` because storage and retrieval can incur charges. Shared-key access is disabled,
the container is private, and the lifecycle policy moves blobs to Cool after 90 days.
The ingestor uploads through Azure CLI OAuth/RBAC, not embedded keys.

No empirical data storage account has been provisioned. In the current CLI shell,
`az account show` found no active login, so remote subscription state and Blob upload
permissions could not be checked. The bounded pilot's CEX trades and aligned output
are local and Git-ignored; the repository contains only the CC BY 4.0 DEX sample. The
full upstream DEX CSV was approximately 9.1 GB at capture time, so the ingestor uses
ranged reads and the project should archive only predeclared, rights-reviewed windows.

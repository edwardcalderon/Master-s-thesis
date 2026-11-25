#!/usr/bin/env bash
# Validates, then (only with --apply) deploys the Bicep template: one Free-tier (F1)
# App Service plan + Web App in brazilsouth — the only SKU/region this subscription
# allows (see ../README.md). Nothing is created without the explicit --apply flag,
# even though F1 can't actually bill this subscription.
#
# Usage:
#   az login --service-principal -u ... -p ... --tenant ...   # see bootstrap script
#   ./deploy-infra.sh rg-microworld                 # dry run (what-if) only
#   ./deploy-infra.sh rg-microworld --apply          # actually deploys

set -euo pipefail

RG="${1:-rg-microworld}"
APPLY="${2:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
PARAMS_FILE="${HERE}/bicep/main.parameters.json"

command -v az >/dev/null 2>&1 || { echo "Azure CLI ('az') not found." >&2; exit 1; }

if grep -q "REPLACE_WITH" "${PARAMS_FILE}"; then
  echo "edit ${PARAMS_FILE} first — it still has REPLACE_WITH_* placeholders." >&2
  exit 1
fi

az account show >/dev/null || { echo "Not logged in. Log in as the scoped service principal first." >&2; exit 1; }

echo "== Validating template against ${RG} =="
az deployment group validate \
  --resource-group "${RG}" \
  --template-file "${HERE}/bicep/main.bicep" \
  --parameters "@${PARAMS_FILE}" \
  --output table

echo "== What-if (no changes made) =="
az deployment group what-if \
  --resource-group "${RG}" \
  --template-file "${HERE}/bicep/main.bicep" \
  --parameters "@${PARAMS_FILE}"

if [ "${APPLY}" != "--apply" ]; then
  echo
  echo "Dry run only. Re-run with --apply to actually create these resources."
  exit 0
fi

echo "== Deploying =="
az deployment group create \
  --resource-group "${RG}" \
  --template-file "${HERE}/bicep/main.bicep" \
  --parameters "@${PARAMS_FILE}" \
  --output table

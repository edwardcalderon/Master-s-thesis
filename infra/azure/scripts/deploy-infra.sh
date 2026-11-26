#!/usr/bin/env bash
# Deploy the optional bounded API on App Service F1 (free). The browser core and
# GitHub-hosted shared world do not depend on this service.
# Usage: ./deploy-infra.sh <existing-resource-group> [--apply]
set -euo pipefail

RG="${1:-rg-microworld}"
APPLY="${2:-}"
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TEMPLATE="${HERE}/bicep/main.bicep"
PARAMS="${HERE}/bicep/main.parameters.json"

command -v az >/dev/null 2>&1 || { echo "Azure CLI ('az') not found." >&2; exit 1; }
az account show >/dev/null || { echo "Run az login for the intended subscription first." >&2; exit 1; }
[ "$(az group exists --name "${RG}" -o tsv)" = "true" ] || {
  echo "Resource group '${RG}' does not exist; create/review it before deployment." >&2
  exit 1
}

az deployment group validate --resource-group "${RG}" --template-file "${TEMPLATE}" --parameters "@${PARAMS}" --output table
az deployment group what-if --resource-group "${RG}" --template-file "${TEMPLATE}" --parameters "@${PARAMS}"

if [ "${APPLY}" != "--apply" ]; then
  echo "What-if only. Pass --apply after reviewing the exact resource changes."
  exit 0
fi

az deployment group create --resource-group "${RG}" --template-file "${TEMPLATE}" --parameters "@${PARAMS}" --output table

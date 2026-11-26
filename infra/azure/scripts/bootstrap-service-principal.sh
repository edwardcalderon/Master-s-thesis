#!/usr/bin/env bash
# Creates the resource group and a scoped service principal that lets this workspace
# (Claude Code, via `az`/Bicep/Terraform) apply changes to Azure programmatically,
# without ever handing out subscription-wide access.
#
# Run this yourself, interactively, once. It prints the client secret to a local file
# — not to stdout history you'd paste back into chat. Review the file's permissions
# before relying on it.
#
# Usage:
#   az login                      # once, as yourself, to authorize the steps below
#   ./bootstrap-service-principal.sh [resource-group] [region] [sp-name] [role]
#
# Defaults: resource-group=rg-microworld, region=brazilsouth, sp-name=sp-microworld-deployer,
# role=Contributor. brazilsouth is the only region confirmed to accept deployments on
# this subscription (an Azure for Students Starter grant) — see ../README.md.
#
# If this fails with something like "Insufficient privileges to complete the
# operation" when creating the app registration: your institution's Azure AD
# (Entra ID) tenant may restrict who can register new applications, independent of
# anything on the subscription itself. Ask your tenant admin, or skip this script
# and just `az login` interactively yourself each session — az's token cache on disk
# persists across an agent's tool calls within that session, it's just not
# unattended across sessions the way a service principal is.

set -euo pipefail

RG="${1:-rg-microworld}"
REGION="${2:-brazilsouth}"
SP_NAME="${3:-sp-microworld-deployer}"
ROLE="${4:-Contributor}"
OUT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)/.secrets"
OUT_FILE="${OUT_DIR}/${SP_NAME}.json"

command -v az >/dev/null 2>&1 || { echo "Azure CLI ('az') not found. Install it first." >&2; exit 1; }

echo "== Checking Azure login =="
az account show >/dev/null || { echo "Run 'az login' first, as yourself." >&2; exit 1; }

SUBSCRIPTION_ID="$(az account show --query id -o tsv)"
echo "Subscription: ${SUBSCRIPTION_ID}"

echo "== Creating resource group '${RG}' in '${REGION}' (idempotent) =="
az group create --name "${RG}" --location "${REGION}" --output table

SCOPE="/subscriptions/${SUBSCRIPTION_ID}/resourceGroups/${RG}"

mkdir -p "${OUT_DIR}"
chmod 700 "${OUT_DIR}"

if [ -f "${OUT_FILE}" ]; then
  echo "Credential file ${OUT_FILE} already exists — refusing to overwrite." >&2
  echo "Delete it first (and rotate/delete the old app registration in Azure) if you want a fresh one." >&2
  exit 1
fi

echo "== Creating service principal '${SP_NAME}' scoped ONLY to ${SCOPE} =="
az ad sp create-for-rbac \
  --name "${SP_NAME}" \
  --role "${ROLE}" \
  --scopes "${SCOPE}" \
  --years 1 \
  --output json > "${OUT_FILE}"

chmod 600 "${OUT_FILE}"

echo
echo "Credentials written to: ${OUT_FILE} (chmod 600, gitignored under infra/azure/**/.secrets/)"
echo
echo "Next, log in as this service principal (reads the file, never prints the secret):"
echo
cat <<'EOF'
  az login --service-principal \
    -u "$(jq -r .appId infra/azure/.secrets/sp-microworld-deployer.json)" \
    -p "$(jq -r .password infra/azure/.secrets/sp-microworld-deployer.json)" \
    --tenant "$(jq -r .tenant infra/azure/.secrets/sp-microworld-deployer.json)"
EOF
echo
echo "This identity can only act inside ${SCOPE}. The secret expires in 1 year."
echo "Rotate: delete the app registration in the Azure Portal (or 'az ad sp delete --id <appId>')"
echo "and re-run this script."

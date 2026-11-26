#!/usr/bin/env bash
# Intentionally disabled: this old bootstrapper creates Azure resources for the
# retired F1/Starter design. Reassess least-privilege deployment identity only after
# the optional Azure architecture and its IaC have passed review.
set -euo pipefail
echo "Bootstrap blocked: no Azure resource group or deployment identity is needed for Core." >&2
echo "See infra/azure/README.md and INFRA-001 before provisioning the optional Azure tier." >&2
exit 2

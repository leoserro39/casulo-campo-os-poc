#!/usr/bin/env bash
set -euo pipefail

cd /workspaces/casulo-campo-os-poc || exit 1

PORT="${CASULO_AGENT_UNIFIED_MATERIAL_API_PORT:-8541}"
DOMAIN="${GITHUB_CODESPACES_PORT_FORWARDING_DOMAIN:-app.github.dev}"

if [ -z "${CODESPACE_NAME:-}" ]; then
  echo "CODESPACE_NAME is not set. Run inside GitHub Codespaces or set it manually."
  exit 2
fi

echo "CASULO_UNIFIED_AGENT_API=https://${CODESPACE_NAME}-${PORT}.${DOMAIN}"
echo "HEALTH=https://${CODESPACE_NAME}-${PORT}.${DOMAIN}/health"
echo "OPENAPI=https://${CODESPACE_NAME}-${PORT}.${DOMAIN}/openapi.json"

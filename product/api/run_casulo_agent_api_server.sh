#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.." || exit 1
python3 product/api/casulo_agent_api_server.py --host 0.0.0.0 --port "${CASULO_AGENT_API_PORT:-8261}"

#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.." || exit 1
python3 product/api/casulo_agent_api_server_v05_unified.py --host 0.0.0.0 --port "${CASULO_AGENT_UNIFIED_API_PORT:-8421}"

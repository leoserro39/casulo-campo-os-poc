#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.." || exit 1
python3 product/api/casulo_agent_api_server_v07_materials.py --host 0.0.0.0 --port "${CASULO_AGENT_MATERIALS_API_PORT:-8501}"

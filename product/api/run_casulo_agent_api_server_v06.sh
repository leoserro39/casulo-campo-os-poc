#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.." || exit 1
python3 product/api/casulo_agent_api_server_v06_calibration_loop.py --host 0.0.0.0 --port "${CASULO_AGENT_CALIBRATION_LOOP_API_PORT:-8461}"

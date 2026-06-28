#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "${BASH_SOURCE[0]}")/../.." || exit 1
python product/api/product_runtime_api.py --host "${HOST:-127.0.0.1}" --port "${PORT:-8097}"

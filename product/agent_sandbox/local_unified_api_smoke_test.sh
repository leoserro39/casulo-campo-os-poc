#!/usr/bin/env bash
set -euo pipefail

BASE="${1:-http://127.0.0.1:8541}"

echo "== health =="
curl -s "${BASE}/health"
echo

echo "== materials admit =="
curl -s -X POST "${BASE}/materials/admit" \
  -H 'Content-Type: application/json' \
  -d '{"message":"Empresa com dados espalhados, sistemas sem integração e rollback ausente.","domain_candidate":"TIC_SI"}'
echo

echo "== agent diagnostic =="
curl -s -X POST "${BASE}/agent/diagnostic" \
  -H 'Content-Type: application/json' \
  -d '{"message":"Empresa com dados espalhados, sistemas sem integração e rollback ausente.","domain_candidate":"TIC_SI"}'
echo

echo "== calibration loop =="
curl -s -X POST "${BASE}/calibration-loop/run" \
  -H 'Content-Type: application/json' \
  -d '{"max_cases":2}'
echo

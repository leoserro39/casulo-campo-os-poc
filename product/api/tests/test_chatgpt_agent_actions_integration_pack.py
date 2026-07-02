#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

manifest = json.loads((ROOT / "product/agent_integration/chatgpt_agent_action_manifest.json").read_text(encoding="utf-8"))
openapi = json.loads((ROOT / "product/agent_integration/chatgpt_agent_openapi_consolidated.json").read_text(encoding="utf-8"))
suite = json.loads((ROOT / "product/agent_integration/action_test_suite.json").read_text(encoding="utf-8"))

assert manifest["status"] == "READY_FOR_MANUAL_AGENT_CONFIGURATION"
assert manifest["live_chatgpt_agent_configured_now"] is False
assert manifest["production_allowed"] is False
assert manifest["client_claim_allowed"] is False
assert manifest["commercial_claim_allowed"] is False

for path in [
    "/exocortex/context/rebuild",
    "/services/diagnostic",
    "/services/monitoring",
    "/services/solutions",
    "/services/calibration",
    "/graph/mermaid",
]:
    assert path in openapi["paths"]

assert len(suite["tests"]) >= 6

api = load("casulo_agent_api_server_v05_unified", "product/api/casulo_agent_api_server_v05_unified.py")
code, health = api.route_get("/health", {})
assert code == 200
assert health["writes_allowed"] is False

message = "Empresa com dados espalhados, sistemas sem integração e necessidade de diagnóstico"
code, payload = api.route_post("/services/diagnostic", {"message": message})
assert code == 200
assert payload["service"] == "diagnostic"
assert payload["ready_for_production"] is False

code, payload = api.route_post("/services/calibration", {"message": message})
assert code == 200
assert payload["service"] == "calibration"
assert payload["threshold_lock_ready"] is False

print(json.dumps({"status": "PASS", "tests": "chatgpt_agent_actions_integration_pack"}, indent=2))

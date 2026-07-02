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

manifest = json.loads((ROOT / "product/agent_unified/casulo_unified_agent_manifest.json").read_text(encoding="utf-8"))
openapi = json.loads((ROOT / "product/agent_unified/casulo_unified_agent_openapi.json").read_text(encoding="utf-8"))
suite = json.loads((ROOT / "product/agent_unified/unified_action_test_suite.json").read_text(encoding="utf-8"))

assert manifest["status"] == "READY_FOR_SANDBOX_AGENT_TEST"
assert manifest["material_first_flow_required"] is True
assert manifest["live_chatgpt_agent_configured_now"] is False
assert manifest["production_allowed"] is False
assert manifest["client_claim_allowed"] is False

for path in [
    "/materials/admit",
    "/agent/diagnostic",
    "/agent/monitoring",
    "/agent/solutions",
    "/agent/calibration",
    "/calibration-loop/run",
    "/graph/mermaid",
]:
    assert path in openapi["paths"]

assert len(suite["tests"]) >= 8

api = load("casulo_agent_api_server_v07_unified_agent", "product/api/casulo_agent_api_server_v07_unified_agent.py")

code, health = api.route_get("/health", {})
assert code == 200
assert health["writes_allowed"] is False
assert health["live_chatgpt_agent_configured_now"] is False

message = "Empresa com dados espalhados, sistemas sem integração, rollback ausente e proposta de automatizar."
code, diagnostic = api.route_post("/agent/diagnostic", {"message": message, "domain_candidate": "TIC_SI"})
assert code == 200
assert diagnostic["flow"] == "material_first_then_context_then_service"
assert diagnostic["material_admission"]["raw_signal_treated_as_truth"] is False
assert diagnostic["ready_for_production"] is False
assert diagnostic["ready_for_client_claim"] is False

code, calibration = api.route_post("/agent/calibration", {"message": message})
assert code == 200
assert calibration["threshold_lock_ready"] is False
assert calibration["ready_for_production"] is False

code, loop = api.route_post("/calibration-loop/run", {"max_cases": 2})
assert code == 200
assert loop["summary"]["case_count"] == 2
assert loop["summary"]["threshold_lock_ready"] is False

print(json.dumps({"status": "PASS", "tests": "unified_agent_api_material_first"}, indent=2))

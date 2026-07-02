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

runtime = load("context_rebuild_runtime", "product/exocortex/context_rebuild_runtime.py")
api = load("casulo_agent_api_server_v03_context", "product/api/casulo_agent_api_server_v03_context.py")

message = "empresa com dados espalhados, sistemas sem integração, precisa diagnóstico e calibração"
packet = runtime.build_context_packet(message)
assert packet["canonical_state"]["governance_core"] == "Operational Cube"
assert packet["canonical_state"]["memory_state_layer"] == "Exocortex"
assert packet["canonical_state"]["micrograph_runtime_current_poc"] is False
assert packet["graph_view_lite"]["format"] == "mermaid"
assert "flowchart" in packet["graph_view_lite"]["mermaid"]
assert packet["input_signal"]["treated_as_truth"] is False
assert "production_activation" in packet["blocked_actions"]

report = runtime.build_diagnostic_report(message)
assert report["status"] == "DRAFT_INTERNAL_ONLY"
assert report["ready_for_client_claim"] is False
assert report["ready_for_production"] is False
assert report["commercial_claim_allowed"] is False

code, payload = api.route_post("/exocortex/context/rebuild", {"message": message})
assert code == 200
assert payload["version"] == "exocortex_context_rebuild_packet.v0.1"

code, payload = api.route_post("/diagnostic/draft", {"message": message})
assert code == 200
assert payload["version"] == "casulo_diagnostic_report_draft.v0.2"

code, payload = api.route_get("/graph/mermaid")
assert code == 200
assert "flowchart" in payload["mermaid"]

print(json.dumps({"status": "PASS", "tests": "exocortex_context_rebuild_runtime"}, indent=2))

#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SERVER = ROOT / "product" / "api" / "casulo_agent_api_server.py"

spec = importlib.util.spec_from_file_location("casulo_agent_api_server", SERVER)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

health = mod.build_health()
assert health["status"] == "ok"
assert health["will_call_gpt"] is False
assert health["will_call_neo4j"] is False

state = mod.build_state_current()
assert state["operational_cube"]["primary_governance_core"] is True
assert state["casulo_agent"]["role"] == "SUBORDINATE_CONVERSATIONAL_OPERATIONAL_MODULE"
assert state["micrographs_current_scope"] == "EPIC_FUTURE_ONLY_NOT_CURRENT_IMPLEMENTATION"
assert state["ready_for_production"] is False

timeline = mod.build_repo_timeline()
assert timeline["status"] == "ok"
assert "recent_commits" in timeline

ctx = mod.rebuild_context({"message": "analisar repo, neo4j, telemetria e calibracao"})
assert ctx["status"] == "ok"
assert ctx["clean_context_packet"]["governance_core"] == "Operational Cube"
assert ctx["clean_context_packet"]["micrograph_runtime_current_poc"] is False
assert "production_activation" in ctx["blocked_actions"]

code, payload = mod.route_get("/health")
assert code == 200 and payload["status"] == "ok"

code, payload = mod.route_post("/context/rebuild", {"message": "teste"})
assert code == 200 and payload["type"] == "CONTEXT_REBUILD_DRAFT"

print(json.dumps({"status": "PASS", "tests": "casulo_agent_api_server_static"}, indent=2))

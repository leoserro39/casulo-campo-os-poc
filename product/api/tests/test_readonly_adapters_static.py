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

git_adapter = load("git_repo_adapter", "product/adapters/read_only/git_repo_adapter.py")
idx = load("output_artifact_indexer", "product/adapters/read_only/output_artifact_indexer.py")
neo = load("neo4j_readonly_adapter_scaffold", "product/adapters/read_only/neo4j_readonly_adapter_scaffold.py")
trace = load("evidence_trace_adapter", "product/adapters/read_only/evidence_trace_adapter.py")
server = load("casulo_agent_api_server_v02_adapters", "product/api/casulo_agent_api_server_v02_adapters.py")

status = git_adapter.git_repo_status()
assert status["mode"] == "LOCAL_GIT_READ_ONLY"
assert status["writes_allowed"] is False

artifacts = idx.artifact_index()
assert artifacts["mode"] == "LOCAL_REPO_ARTIFACT_READ_ONLY"
assert artifacts["count"] > 0

graph = neo.graph_summary()
assert graph["mode"] == "OFFLINE_PAYLOAD_READ_ONLY"
assert graph["live_neo4j_connection_executed"] is False
assert graph["production_write_allowed"] is False

ev = trace.evidence_trace()
assert ev["writes_allowed"] is False
assert ev["ready_for_client_claim"] is False
assert ev["ready_for_production"] is False

code, payload = server.route_get("/adapters/git/status", {})
assert code == 200
assert payload["writes_allowed"] is False

code, payload = server.route_get("/adapters/graph/summary", {})
assert code == 200
assert payload["live_neo4j_connection_executed"] is False

print(json.dumps({"status": "PASS", "tests": "readonly_adapters_static"}, indent=2))

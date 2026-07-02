#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NODE_PAYLOADS = [
    "product/graph/neo4j_payloads/real_case_001_nodes_v0_1.json",
]
REL_PAYLOADS = [
    "product/graph/neo4j_payloads/real_case_001_relationships_v0_1.json",
]
GRAPH_OUTPUTS = [
    "outputs/prod7341_7380_graph_retrieval_gain_multirun_calibration.json",
    "outputs/prod8181_8220_cockpit_chat_scaffold_diagnostic_monitor.json",
]

BLOCKED_ACTIONS = [
    "production_neo4j_write",
    "neo4j_delete",
    "neo4j_reimport",
    "production_activation",
    "client_facing_validated_claim",
    "commercial_claim",
]

def read_json(path: str, default=None):
    p = ROOT / path
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def load_nodes():
    nodes = []
    for p in NODE_PAYLOADS:
        data = read_json(p, [])
        if isinstance(data, list):
            nodes.extend(data)
    return nodes

def load_relationships():
    rels = []
    for p in REL_PAYLOADS:
        data = read_json(p, [])
        if isinstance(data, list):
            rels.extend(data)
    return rels

def graph_summary():
    nodes = load_nodes()
    rels = load_relationships()
    graph_gain = read_json("outputs/prod7341_7380_graph_retrieval_gain_multirun_calibration.json", {})
    return {
        "adapter": "neo4j_readonly_adapter_scaffold.v0.1",
        "mode": "OFFLINE_PAYLOAD_READ_ONLY",
        "live_neo4j_connection_executed": False,
        "production_write_allowed": False,
        "node_payload_count": len(nodes),
        "relationship_payload_count": len(rels),
        "node_ids": [n.get("id") for n in nodes if isinstance(n, dict)][:80],
        "relationship_types": [r.get("type") for r in rels if isinstance(r, dict)][:80],
        "graph_retrieval_gain_proxy": graph_gain.get("graph_retrieval_gain", {}),
        "calibration_decision": graph_gain.get("calibration_decision", {}),
        "blocked_actions": BLOCKED_ACTIONS,
    }

def evidence_trace(case_id="REAL-CASE-001"):
    nodes = load_nodes()
    rels = load_relationships()
    selected_nodes = [n for n in nodes if str(n.get("id", "")).lower() == case_id.lower() or case_id.lower() in json.dumps(n, ensure_ascii=False).lower()]
    selected_rels = [r for r in rels if case_id.lower() in json.dumps(r, ensure_ascii=False).lower()]
    graph_gain = read_json("outputs/prod7341_7380_graph_retrieval_gain_multirun_calibration.json", {})
    return {
        "adapter": "neo4j_readonly_adapter_scaffold.v0.1",
        "mode": "OFFLINE_PAYLOAD_READ_ONLY",
        "case_id": case_id,
        "nodes": selected_nodes,
        "relationships": selected_rels,
        "graph_context": graph_gain.get("graph_context", {}),
        "ready_for_live_neo4j_retrieval": graph_gain.get("calibration_decision", {}).get("ready_for_live_neo4j_retrieval"),
        "live_neo4j_query_executed": False,
        "writes_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

if __name__ == "__main__":
    print(json.dumps(graph_summary(), indent=2, ensure_ascii=False))

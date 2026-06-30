#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
    "automatic_threshold_mutation",
    "autonomous_external_execution",
    "real_world_side_effect",
    "unapproved_real_company_data",
    "live_graph_database_write",
    "production_neo4j_connection"
]

def load_json(path: Path, fallback):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback

def write_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())

def build(repo: Path):
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    upstream = load_json(out / "prod1181_1220_readiness.json", {})
    nodes_path = out / "prod941_980_graph_export_nodes.jsonl"
    rels_path = out / "prod941_980_graph_export_relationships.jsonl"
    node_count = count_jsonl(nodes_path)
    relationship_count = count_jsonl(rels_path)

    adapter_contract = {
        "status": "PASS",
        "phase": "Neo4j Sandbox Adapter Contract",
        "generated_at": generated_at,
        "mode": "contract_only_no_connection",
        "neo4j_uri_template": "bolt://localhost:7687",
        "database_template": "neo4j",
        "env_template": "product/config/neo4j_sandbox.env.example",
        "source_nodes_jsonl": str(nodes_path),
        "source_relationships_jsonl": str(rels_path),
        "source_node_count": node_count,
        "source_relationship_count": relationship_count,
        "connection_allowed_now": False,
        "sandbox_connection_allowed_later": True,
        "production_connection_allowed": False,
        "credential_handling_allowed": False,
        "requires_explicit_flag_for_future_connection": True,
        "explicit_future_flag": "CASULO_NEO4J_SANDBOX_IMPORT_ENABLED=true",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    allowed_cypher = {
        "status": "PASS",
        "read_only_queries": [
            {"id": "CYPHER-READ-001", "name": "count_all_nodes", "cypher": "MATCH (n) RETURN count(n) AS nodes"},
            {"id": "CYPHER-READ-002", "name": "count_all_relationships", "cypher": "MATCH ()-[r]->() RETURN count(r) AS relationships"},
            {"id": "CYPHER-READ-003", "name": "case_to_gate_paths", "cypher": "MATCH p=(c:Case)-[*1..4]->(g:Gate) RETURN c.id AS case_id, g.id AS gate_id, length(p) AS path_length LIMIT 50"},
            {"id": "CYPHER-READ-004", "name": "risk_to_output_trace", "cypher": "MATCH p=(r:RiskSignal)-[*1..4]->(o:OutputMode) RETURN r.id AS risk_signal_id, o.id AS output_mode_id, length(p) AS path_length LIMIT 50"},
            {"id": "CYPHER-READ-005", "name": "blocked_cases", "cypher": "MATCH (c:Case)-[*1..4]->(o:OutputMode {name:'BLOCKED'}) RETURN c.id AS case_id LIMIT 50"}
        ],
        "write_queries_allowed_now": False,
        "future_sandbox_write_templates": ["MERGE node templates for JSONL import", "MERGE relationship templates for JSONL import"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    import_plan = {
        "status": "PASS",
        "phase": "JSONL to Neo4j Sandbox Import Plan",
        "source": {"nodes_jsonl": str(nodes_path), "relationships_jsonl": str(rels_path), "node_count": node_count, "relationship_count": relationship_count},
        "target": {"mode": "sandbox_only", "uri": "bolt://localhost:7687", "database": "neo4j"},
        "steps": [
            "verify Neo4j sandbox is running",
            "verify credentials are local and not committed",
            "create uniqueness constraints for id fields",
            "import nodes from JSONL using MERGE",
            "import relationships from JSONL using MATCH + MERGE",
            "run read-only count checks",
            "run path completeness checks",
            "export gain metrics"
        ],
        "will_execute_now": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    gain_contract = {
        "status": "PASS",
        "baseline": "current JSON outputs and runner lookups",
        "candidate": "Neo4j sandbox graph retrieval",
        "metrics": [
            "retrieval_hit_rate",
            "path_completeness",
            "evidence_to_gate_traceability",
            "query_latency",
            "explanation_quality",
            "false_allow_delta",
            "false_block_delta",
            "human_review_packet_quality",
            "audit_path_depth"
        ],
        "test_cases": ["EXP50-045 productivity acceleration", "EXP50-047 critical human review", "EXP50-049 direct execution block sentinel"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness_ok = upstream.get("decision") == "READY_FOR_NEO4J_SANDBOX_GAIN_TEST_AND_LLM_CODEX_BOUNDARY_TRAIN" and node_count > 0 and relationship_count > 0
    readiness = {
        "status": "PASS" if readiness_ok else "WARN",
        "decision": "READY_FOR_GRAPH_IMPORT_SANDBOX_DRY_RUN" if readiness_ok else "REVIEW_NEO4J_SANDBOX_ADAPTER_CONTRACT",
        "ready_for": ["Graph Import Sandbox Dry Run", "Cypher generation from JSONL", "local Neo4j sandbox setup", "read-only graph inspection"] if readiness_ok else ["fix upstream readiness or graph export files"],
        "not_ready_for": ["production Neo4j connection", "production graph write", "credential handling in repo", "client-facing graph claims", "automatic threshold mutation"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": readiness["status"],
        "audit": "Neo4j Sandbox Adapter Contract audit",
        "node_count": node_count,
        "relationship_count": relationship_count,
        "connection_allowed_now": False,
        "sandbox_connection_allowed_later": True,
        "production_connection_allowed": False,
        "credential_handling_allowed": False,
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "readiness": readiness["decision"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    outputs = {
        "prod1221_1260_neo4j_sandbox_adapter_contract.json": adapter_contract,
        "prod1221_1260_allowed_cypher_queries.json": allowed_cypher,
        "prod1221_1260_neo4j_import_plan.json": import_plan,
        "prod1221_1260_neo4j_gain_test_contract.json": gain_contract,
        "prod1221_1260_readiness.json": readiness,
        "prod1221_1260_audit_report.json": audit,
    }
    for name, obj in outputs.items():
        write_json(out / name, obj)

    report = f'''# PROD-1221..1260 Neo4j Sandbox Adapter Contract

- Status: `{readiness['status']}`
- Decision: `{readiness['decision']}`
- Source nodes: `{node_count}`
- Source relationships: `{relationship_count}`
- Connection allowed now: `False`
- Sandbox connection allowed later: `True`
- Production connection allowed: `False`
- Credential handling allowed: `False`

This phase prepares the contract for Neo4j sandbox usage. It does not connect to Neo4j yet.

Next phase: `PROD-1261..1300 Graph Import Sandbox Dry Run`
'''
    write_text(out / "prod1221_1260_report.md", report)
    write_text(out / "prod1221_1260_audit_report.md", "# PROD-1221..1260 Audit Report\n\n" + "\n".join([f"- {k}: `{v}`" for k, v in audit.items() if not isinstance(v, (list, dict))]) + "\n")
    write_json(out / "prod1221_1260_result.json", {"status": readiness["status"], "decision": readiness["decision"], "blocked_actions": BLOCKED_ACTIONS})
    return {"status": readiness["status"], "decision": readiness["decision"]}

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    print(json.dumps(build(Path(args.repo)), indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

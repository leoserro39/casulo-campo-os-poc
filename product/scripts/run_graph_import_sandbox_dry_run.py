#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

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
    "production_neo4j_connection",
    "production_graph_write",
]

def load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback

def count_jsonl(path: Path) -> int:
    if not path.exists():
        return 0
    return sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def build(repo: Path) -> dict:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    upstream = load_json(out / "prod1221_1260_readiness.json", {})
    nodes_path = out / "prod941_980_graph_export_nodes.jsonl"
    rels_path = out / "prod941_980_graph_export_relationships.jsonl"
    node_count = count_jsonl(nodes_path)
    relationship_count = count_jsonl(rels_path)

    gen = subprocess.run(
        [sys.executable, str(repo / "product/scripts/generate_graph_import_sandbox_cypher.py"), "--repo", str(repo)],
        capture_output=True,
        text=True,
    )
    if gen.returncode:
        raise SystemExit(gen.stdout + gen.stderr)

    cypher_path = out / "prod1261_1300_neo4j_sandbox_import_preview.cypher"
    cypher_text = cypher_path.read_text(encoding="utf-8") if cypher_path.exists() else ""
    statement_count = sum(1 for line in cypher_text.splitlines() if line.strip().endswith(";"))

    dry_run = {
        "status": "PASS",
        "phase": "Graph Import Sandbox Dry Run",
        "generated_at": generated_at,
        "mode": "offline_cypher_preview_no_connection",
        "source_nodes_jsonl": str(nodes_path),
        "source_relationships_jsonl": str(rels_path),
        "source_node_count": node_count,
        "source_relationship_count": relationship_count,
        "cypher_preview_file": str(cypher_path),
        "cypher_statement_count": statement_count,
        "neo4j_connection_attempted": False,
        "cypher_executed": False,
        "production_connection_allowed": False,
        "credential_handling_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    manual_runbook = {
        "status": "PASS",
        "docker_compose_example": "product/config/neo4j_sandbox_docker_compose.example.yml",
        "env_example": "product/config/neo4j_sandbox_import.env.example",
        "manual_steps": [
            "Start local Neo4j sandbox.",
            "Open Neo4j Browser on port 7474.",
            "Review outputs/prod1261_1300_neo4j_sandbox_import_preview.cypher.",
            "Run only in local sandbox if approved.",
            "Run count verification queries.",
            "Do not connect to production.",
        ],
        "browser_url": "http://localhost:7474",
        "bolt_uri": "bolt://localhost:7687",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    validation_queries = {
        "status": "PASS",
        "queries": [
            "MATCH (n:CasuloNode) RETURN count(n) AS casulo_nodes",
            "MATCH (:CasuloNode)-[r]->(:CasuloNode) RETURN count(r) AS casulo_relationships",
            "MATCH p=(c:CasuloNode)-[*1..4]->(g:CasuloNode) RETURN c.id, g.id, length(p) LIMIT 50",
            "MATCH (n:CasuloNode) RETURN n.casulo_label AS label, count(*) AS count ORDER BY count DESC",
        ],
        "expected_min_nodes": node_count,
        "expected_min_relationships": relationship_count,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness_ok = (
        upstream.get("decision") == "READY_FOR_GRAPH_IMPORT_SANDBOX_DRY_RUN"
        and node_count > 0
        and relationship_count > 0
        and statement_count > 0
    )
    readiness = {
        "status": "PASS" if readiness_ok else "WARN",
        "decision": "READY_FOR_MANUAL_NEO4J_SANDBOX_IMPORT_AND_GRAPH_RETRIEVAL_GAIN_EVALUATION" if readiness_ok else "REVIEW_GRAPH_IMPORT_SANDBOX_DRY_RUN",
        "ready_for": [
            "manual Neo4j sandbox import",
            "read-only graph validation queries",
            "Graph Retrieval Gain Evaluation"
        ] if readiness_ok else ["fix Cypher preview generation or upstream readiness"],
        "not_ready_for": [
            "production Neo4j connection",
            "automatic graph write",
            "credential handling in repo",
            "client-facing graph claims",
            "automatic threshold mutation",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": readiness["status"],
        "audit": "Graph Import Sandbox Dry Run audit",
        "node_count": node_count,
        "relationship_count": relationship_count,
        "cypher_statement_count": statement_count,
        "neo4j_connection_attempted": False,
        "cypher_executed": False,
        "production_connection_allowed": False,
        "credential_handling_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "readiness": readiness["decision"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    outputs = {
        "prod1261_1300_graph_import_sandbox_dry_run.json": dry_run,
        "prod1261_1300_neo4j_manual_runbook.json": manual_runbook,
        "prod1261_1300_graph_validation_queries.json": validation_queries,
        "prod1261_1300_readiness.json": readiness,
        "prod1261_1300_audit_report.json": audit,
    }
    for name, obj in outputs.items():
        write_json(out / name, obj)

    report = f"""# PROD-1261..1300 Graph Import Sandbox Dry Run

- Status: `{readiness['status']}`
- Decision: `{readiness['decision']}`
- Source nodes: `{node_count}`
- Source relationships: `{relationship_count}`
- Cypher statements: `{statement_count}`
- Neo4j connection attempted: `False`
- Cypher executed: `False`

Generated preview:
`outputs/prod1261_1300_neo4j_sandbox_import_preview.cypher`

Next: manual local Neo4j sandbox import, then graph retrieval gain evaluation.
"""
    write_text(out / "prod1261_1300_report.md", report)
    write_text(out / "prod1261_1300_audit_report.md", "# PROD-1261..1300 Audit Report\n\n" + "\n".join([f"- {k}: `{v}`" for k, v in audit.items() if not isinstance(v, (list, dict))]) + "\n")
    write_json(out / "prod1261_1300_result.json", {"status": readiness["status"], "decision": readiness["decision"], "blocked_actions": BLOCKED_ACTIONS})
    return {"status": readiness["status"], "decision": readiness["decision"]}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    print(json.dumps(build(Path(args.repo)), indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

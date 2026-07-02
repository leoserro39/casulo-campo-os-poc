#!/usr/bin/env python3
"""
CASULO PROD-7821..7860 - Live Graph Retrieval Confirmation Gate

Continues after:
  PROD-7781..7820 - Evidence Export and Operator Review Packet

Purpose:
  - open the gate for live graph retrieval confirmation;
  - compare the required live retrieval contract against the committed graph payload and operator evidence;
  - record whether live Neo4j retrieval was actually confirmed;
  - prevent any client/production/commercial claim when live retrieval evidence is absent.

This patcher does NOT:
  - call GPT;
  - dispatch GitHub Actions;
  - comment on GitHub issues/PRs;
  - write to production Neo4j;
  - activate production;
  - allow client/production/commercial claims.

By default this is a controlled gate, not a Neo4j connector.
It can consume an optional local evidence file:
  --live-evidence product/graph/live_retrieval/prod7821_7860_live_retrieval_evidence.json

Expected live evidence schema:
{
  "live_query_executed": true,
  "neo4j_environment": "sandbox",
  "production_write_executed": false,
  "node_count": 3,
  "relationship_count": 2,
  "node_ids": ["REAL-CASE-001", "GITHUB-AGENT-FOUNDATION-v0.1", "P0-MATRIX-BATCH01"],
  "relationship_types": ["RUNS_CASE", "MEASURED_BY"],
  "graph_path_confirmed": true
}

Usage:
  python3 apply_prod7821_7860_live_graph_retrieval_confirmation_gate.py --check
  python3 apply_prod7821_7860_live_graph_retrieval_confirmation_gate.py --apply --commit-plan

  # Optional, when a real sandbox Neo4j retrieval evidence file exists:
  python3 apply_prod7821_7860_live_graph_retrieval_confirmation_gate.py \
    --apply \
    --live-evidence product/graph/live_retrieval/prod7821_7860_live_retrieval_evidence.json \
    --commit-plan
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()

REQUIRED = [
    "outputs/prod7781_7820_evidence_export_operator_review_packet.json",
    "product/evidence_exports/prod7781_7820_operator_evidence_export.json",
    "product/reviews/operator_packets/prod7781_7820_operator_review_packet.json",
    "product/contracts/evidence_export_operator_review_packet.contract.json",
    "product/graph/neo4j_payloads/real_case_001_nodes_v0_1.json",
    "product/graph/neo4j_payloads/real_case_001_relationships_v0_1.json",
    "product/graph/neo4j_payloads/real_case_001_preview_v0_1.cypher",
]

REQUIRED_NODES = ["REAL-CASE-001", "GITHUB-AGENT-FOUNDATION-v0.1", "P0-MATRIX-BATCH01"]
REQUIRED_RELS = ["RUNS_CASE", "MEASURED_BY"]

BLOCKED_ACTIONS = [
    "client_facing_validated_claim",
    "production_activation",
    "commercial_claim",
    "validated_model_gain_claim",
    "validated_hallucination_reduction_claim",
    "automatic_merge",
    "real_world_side_effect",
    "github_issue_comment",
    "github_pr_comment",
    "external_repo_write",
    "production_neo4j_write",
    "threshold_scope_expansion_without_future_human_review",
]

def read_json(path: str | Path, default: Any = None) -> Any:
    p = ROOT / path if isinstance(path, str) else path
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

def read_text(path: str | Path) -> str:
    p = ROOT / path if isinstance(path, str) else path
    return p.read_text(encoding="utf-8") if p.exists() else ""

def write_json(path: str, data: Any, wrote: List[str]) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    wrote.append(path)

def write_text(path: str, text: str, wrote: List[str]) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    wrote.append(path)

def check(live_evidence: Optional[str] = None) -> Dict[str, Any]:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    live_evidence_present = bool(live_evidence and (ROOT / live_evidence).exists())
    return {
        "status": "PASS" if not missing else "FAIL",
        "phase": "PROD-7821..7860",
        "missing_count": len(missing),
        "missing": missing,
        "live_evidence_path": live_evidence,
        "live_evidence_present": live_evidence_present,
        "will_create": [
            "product/graph/retrieval_gates/prod7821_7860_live_graph_retrieval_confirmation_gate.json",
            "product/graph/retrieval_gates/prod7821_7860_live_graph_retrieval_confirmation_plan.cypher",
            "outputs/prod7821_7860_live_graph_retrieval_confirmation_gate.json",
            "outputs/prod7821_7860_live_graph_retrieval_confirmation_gate.md",
            "product/contracts/live_graph_retrieval_confirmation_gate.contract.json",
            "docs/product/782_LIVE_GRAPH_RETRIEVAL_CONFIRMATION_GATE.md",
        ],
        "will_call_gpt": False,
        "will_dispatch_workflow": False,
        "will_write_external_systems": False,
        "will_activate_production": False,
        "will_allow_client_claim": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def node_id(n: Any) -> str:
    if isinstance(n, dict):
        return str(n.get("id") or n.get("key") or n.get("name") or "")
    return ""

def rel_type(r: Any) -> str:
    if isinstance(r, dict):
        return str(r.get("type") or r.get("relationship") or r.get("label") or "")
    return ""

def offline_graph_summary() -> Dict[str, Any]:
    nodes = read_json("product/graph/neo4j_payloads/real_case_001_nodes_v0_1.json", [])
    rels = read_json("product/graph/neo4j_payloads/real_case_001_relationships_v0_1.json", [])
    cypher = read_text("product/graph/neo4j_payloads/real_case_001_preview_v0_1.cypher")
    node_ids = [node_id(n) for n in nodes if node_id(n)]
    rel_types = [rel_type(r) for r in rels if rel_type(r)]
    return {
        "mode": "OFFLINE_COMMITTED_GRAPH_PAYLOAD",
        "node_count": len(nodes) if isinstance(nodes, list) else 0,
        "relationship_count": len(rels) if isinstance(rels, list) else 0,
        "node_ids": node_ids,
        "relationship_types": rel_types,
        "required_node_presence": {k: any(k in n for n in node_ids) for k in REQUIRED_NODES},
        "required_relationship_presence": {k: any(k in r for r in rel_types) for k in REQUIRED_RELS},
        "preview_cypher_present": bool(cypher.strip()),
        "preview_cypher_path": "product/graph/neo4j_payloads/real_case_001_preview_v0_1.cypher",
        "graph_path_claim": "GITHUB-AGENT-FOUNDATION-v0.1 -> RUNS_CASE -> REAL-CASE-001 -> MEASURED_BY -> P0-MATRIX-BATCH01",
    }

def live_summary(live_evidence: Optional[str]) -> Dict[str, Any]:
    if not live_evidence:
        return {
            "live_evidence_path": None,
            "live_evidence_present": False,
            "live_query_executed": False,
            "neo4j_environment": None,
            "production_write_executed": False,
            "graph_path_confirmed": False,
            "reason": "No live evidence file supplied."
        }
    p = ROOT / live_evidence
    if not p.exists():
        return {
            "live_evidence_path": live_evidence,
            "live_evidence_present": False,
            "live_query_executed": False,
            "neo4j_environment": None,
            "production_write_executed": False,
            "graph_path_confirmed": False,
            "reason": "Live evidence file path was supplied but file is missing."
        }
    data = read_json(p, {})
    return {
        "live_evidence_path": live_evidence,
        "live_evidence_present": True,
        "live_query_executed": data.get("live_query_executed") is True,
        "neo4j_environment": data.get("neo4j_environment"),
        "production_write_executed": data.get("production_write_executed") is True,
        "node_count": data.get("node_count"),
        "relationship_count": data.get("relationship_count"),
        "node_ids": data.get("node_ids", []),
        "relationship_types": data.get("relationship_types", []),
        "graph_path_confirmed": data.get("graph_path_confirmed") is True,
        "raw": data,
    }

def evaluate_gate(offline: Dict[str, Any], live: Dict[str, Any]) -> Dict[str, Any]:
    offline_ok = (
        all(offline["required_node_presence"].values()) and
        all(offline["required_relationship_presence"].values()) and
        offline["preview_cypher_present"]
    )

    live_nodes = live.get("node_ids", [])
    live_rels = live.get("relationship_types", [])

    live_required_nodes_ok = all(any(k in str(n) for n in live_nodes) for k in REQUIRED_NODES)
    live_required_rels_ok = all(any(k in str(r) for r in live_rels) for k in REQUIRED_RELS)

    live_confirmed = (
        live.get("live_evidence_present") is True and
        live.get("live_query_executed") is True and
        live.get("production_write_executed") is False and
        live.get("graph_path_confirmed") is True and
        live_required_nodes_ok and
        live_required_rels_ok and
        live.get("node_count") == offline.get("node_count") and
        live.get("relationship_count") == offline.get("relationship_count")
    )

    checks = {
        "offline_graph_payload_complete": offline_ok,
        "live_evidence_present": live.get("live_evidence_present") is True,
        "live_query_executed": live.get("live_query_executed") is True,
        "live_graph_path_confirmed": live.get("graph_path_confirmed") is True,
        "live_required_nodes_present": live_required_nodes_ok,
        "live_required_relationships_present": live_required_rels_ok,
        "live_node_count_matches": live.get("node_count") == offline.get("node_count"),
        "live_relationship_count_matches": live.get("relationship_count") == offline.get("relationship_count"),
        "production_write_not_executed": live.get("production_write_executed") is False,
    }

    return {
        "checks": checks,
        "offline_graph_payload_complete": offline_ok,
        "live_graph_retrieval_confirmed": live_confirmed,
        "gate_executed": True,
        "gate_status": "CONFIRMED" if live_confirmed else "NOT_CONFIRMED",
        "ready_for_claim_boundary_reassessment": True,
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "human_review_required_for_scope_expansion": True,
    }

def apply(live_evidence: Optional[str]) -> List[str]:
    wrote: List[str] = []
    operator = read_json("outputs/prod7781_7820_evidence_export_operator_review_packet.json", {})
    offline = offline_graph_summary()
    live = live_summary(live_evidence)
    gate_eval = evaluate_gate(offline, live)

    cypher_plan = """// PROD-7821..7860 - Live Graph Retrieval Confirmation Plan
// Scope: sandbox/read-only confirmation.
// This plan must not write to production Neo4j.

MATCH (agent {id: 'GITHUB-AGENT-FOUNDATION-v0.1'})-[r1:RUNS_CASE]->(case_node {id: 'REAL-CASE-001'})-[r2:MEASURED_BY]->(matrix {id: 'P0-MATRIX-BATCH01'})
RETURN agent.id AS agent_id,
       type(r1) AS rel_1,
       case_node.id AS case_id,
       type(r2) AS rel_2,
       matrix.id AS matrix_id;
"""

    gate = {
        "version": "live_graph_retrieval_confirmation_gate.v0.1",
        "phase": "PROD-7821..7860",
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "source_operator_packet": "outputs/prod7781_7820_evidence_export_operator_review_packet.json",
        "operator_packet_ready": operator.get("calibration_decision", {}).get("operator_review_packet_ready"),
        "offline_graph_summary": offline,
        "live_retrieval_summary": live,
        "gate_evaluation": gate_eval,
        "read_only_cypher_plan_path": "product/graph/retrieval_gates/prod7821_7860_live_graph_retrieval_confirmation_plan.cypher",
        "boundary": {
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
            "validated_hallucination_reduction_claim_allowed": False,
            "production_neo4j_write_allowed": False,
        },
        "blocked_actions": BLOCKED_ACTIONS,
    }

    decision = (
        "LIVE_GRAPH_RETRIEVAL_CONFIRMED_INTERNAL_ONLY_CLAIM_BOUNDARY_REASSESSMENT_READY"
        if gate_eval["live_graph_retrieval_confirmed"]
        else
        "LIVE_GRAPH_RETRIEVAL_GATE_EXECUTED_NOT_CONFIRMED_CLAIM_BOUNDARY_REASSESSMENT_REQUIRED"
    )

    result = {
        "status": "PASS",
        "phase": "PROD-7821..7860",
        "decision": decision,
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "live_graph_retrieval_confirmation_gate": gate,
        "calibration_decision": {
            "live_graph_retrieval_confirmation_gate_executed": True,
            "live_graph_retrieval_confirmed": gate_eval["live_graph_retrieval_confirmed"],
            "offline_graph_payload_complete": gate_eval["offline_graph_payload_complete"],
            "ready_for_claim_boundary_reassessment": True,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required_for_scope_expansion": True,
        },
        "next": "PROD-7861..7900 - Client/Production Claim Boundary Reassessment",
    }

    write_json("product/graph/retrieval_gates/prod7821_7860_live_graph_retrieval_confirmation_gate.json", gate, wrote)
    write_text("product/graph/retrieval_gates/prod7821_7860_live_graph_retrieval_confirmation_plan.cypher", cypher_plan, wrote)
    write_json("outputs/prod7821_7860_live_graph_retrieval_confirmation_gate.json", result, wrote)

    md = [
        "# PROD-7821..7860 - Live Graph Retrieval Confirmation Gate",
        "",
        "## Result",
        "",
        f"Status: {result['status']}",
        f"Decision: {result['decision']}",
        "",
        "## Gate",
        "",
        f"- Offline graph payload complete: {gate_eval['offline_graph_payload_complete']}",
        f"- Live evidence present: {live.get('live_evidence_present')}",
        f"- Live query executed: {live.get('live_query_executed')}",
        f"- Live graph retrieval confirmed: {gate_eval['live_graph_retrieval_confirmed']}",
        f"- Production write executed: {live.get('production_write_executed')}",
        "",
        "## Boundary",
        "",
        "- Client claim allowed: False",
        "- Production allowed: False",
        "- Commercial claim allowed: False",
        "- Production Neo4j write allowed: False",
        "",
        "## Next",
        "",
        result["next"],
        "",
    ]
    write_text("outputs/prod7821_7860_live_graph_retrieval_confirmation_gate.md", "\n".join(md), wrote)

    contract = {
        "contract": "live_graph_retrieval_confirmation_gate.contract.v0.1",
        "phase": "PROD-7821..7860",
        "requires": REQUIRED,
        "optional_live_evidence_path": live_evidence,
        "live_graph_retrieval_confirmation_gate_executed": True,
        "live_graph_retrieval_confirmed": gate_eval["live_graph_retrieval_confirmed"],
        "offline_graph_payload_complete": gate_eval["offline_graph_payload_complete"],
        "ready_for_claim_boundary_reassessment": True,
        "client_claim_allowed": False,
        "production_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/live_graph_retrieval_confirmation_gate.contract.json", contract, wrote)

    docs = """# 782 - Live Graph Retrieval Confirmation Gate

This phase opens the live graph retrieval confirmation gate.

By default it does not connect to Neo4j. It records whether live evidence was supplied.

If live evidence is absent, the gate is still executed but live graph retrieval remains NOT_CONFIRMED.

This phase does not allow:
- client-facing validation claims;
- production activation;
- commercial claims;
- validated hallucination reduction claims;
- production Neo4j writes.
"""
    write_text("docs/product/782_LIVE_GRAPH_RETRIEVAL_CONFIRMATION_GATE.md", docs, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod7821_7860_live_graph_retrieval_confirmation_gate.py",
        "product/graph/retrieval_gates/prod7821_7860_live_graph_retrieval_confirmation_gate.json",
        "product/graph/retrieval_gates/prod7821_7860_live_graph_retrieval_confirmation_plan.cypher",
        "outputs/prod7821_7860_live_graph_retrieval_confirmation_gate.json",
        "outputs/prod7821_7860_live_graph_retrieval_confirmation_gate.md",
        "product/contracts/live_graph_retrieval_confirmation_gate.contract.json",
        "docs/product/782_LIVE_GRAPH_RETRIEVAL_CONFIRMATION_GATE.md",
    ]
    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Add live graph retrieval confirmation gate"',
        'git tag -a product-casulo-live-graph-retrieval-confirmation-gate-v0.1 HEAD -m "CASULO live graph retrieval confirmation gate v0.1"',
        "git push origin main",
        "git push origin product-casulo-live-graph-retrieval-confirmation-gate-v0.1",
    ])

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--commit-plan", action="store_true")
    ap.add_argument("--live-evidence", default=None)
    args = ap.parse_args()

    if not any([args.check, args.apply, args.commit_plan]):
        args.check = True

    if args.check:
        print(json.dumps(check(args.live_evidence), indent=2, ensure_ascii=False))

    if args.apply:
        c = check(args.live_evidence)
        if c["status"] != "PASS":
            print(json.dumps(c, indent=2, ensure_ascii=False))
            raise SystemExit("CHECK_FAILED")
        wrote = apply(args.live_evidence)
        print(json.dumps({"applied": True, "wrote_count": len(wrote), "wrote": wrote}, indent=2, ensure_ascii=False))

    if args.commit_plan:
        print(commit_plan())

    return 0

if __name__ == "__main__":
    raise SystemExit(main())

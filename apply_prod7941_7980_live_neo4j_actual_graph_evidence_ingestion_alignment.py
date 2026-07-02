#!/usr/bin/env python3
"""
CASULO PROD-7941..7980 - Live Neo4j Actual Graph Evidence Ingestion and Alignment Evaluation

Continues after:
  PROD-7901-CORRECTION - Live Neo4j actual graph state correction

Purpose:
  - ingest the real persisted Neo4j sandbox graph evidence;
  - explicitly supersede the stale PROD-7901 target query;
  - confirm live sandbox graph preservation/alignment without writing to Neo4j;
  - keep client, production, commercial, and validated-gain claims blocked.

This patcher does NOT:
  - connect to Neo4j;
  - write to Neo4j;
  - delete any Docker volume;
  - reimport graph data;
  - call GPT;
  - dispatch GitHub Actions;
  - activate production;
  - allow client-facing claims.

Usage:
  python3 apply_prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.py --check
  python3 apply_prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.py --apply --commit-plan
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()

REQUIRED = [
    "outputs/prod7901_correction_live_neo4j_actual_graph_state.json",
    "product/graph/live_retrieval/prod7901_7940_real_live_graph_probe.txt",
    "product/graph/live_retrieval/safety/prod7901_correction_live_neo4j_preservation_evidence.txt",
    "outputs/prod7901_7940_live_graph_evidence_followup_controlled_sandbox_retrieval.json",
    "outputs/prod7861_7900_client_production_claim_boundary_reassessment.json",
]

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
    "neo4j_delete",
    "neo4j_reimport",
    "docker_volume_delete",
    "threshold_scope_expansion_without_future_human_review",
]

def read_json(path: str, default: Any = None) -> Any:
    p = ROOT / path
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

def read_text(path: str) -> str:
    return (ROOT / path).read_text(encoding="utf-8")

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

def check() -> Dict[str, Any]:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    return {
        "status": "PASS" if not missing else "FAIL",
        "phase": "PROD-7941..7980",
        "missing_count": len(missing),
        "missing": missing,
        "will_create": [
            "product/graph/live_retrieval/prod7941_7980_live_neo4j_actual_graph_alignment_evaluation.json",
            "product/graph/live_retrieval/prod7941_7980_live_neo4j_actual_graph_alignment_evaluation.md",
            "outputs/prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.json",
            "outputs/prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.md",
            "product/contracts/live_neo4j_actual_graph_evidence_ingestion_alignment.contract.json",
            "docs/product/794_LIVE_NEO4J_ACTUAL_GRAPH_EVIDENCE_INGESTION_ALIGNMENT.md",
        ],
        "will_connect_to_neo4j": False,
        "will_write_neo4j": False,
        "will_delete_volume": False,
        "will_reimport_graph": False,
        "will_call_gpt": False,
        "will_activate_production": False,
        "will_allow_client_claim": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def evaluate() -> Dict[str, Any]:
    correction = read_json("outputs/prod7901_correction_live_neo4j_actual_graph_state.json", {})
    prior7901 = read_json("outputs/prod7901_7940_live_graph_evidence_followup_controlled_sandbox_retrieval.json", {})
    claim7861 = read_json("outputs/prod7861_7900_client_production_claim_boundary_reassessment.json", {})
    probe = read_text("product/graph/live_retrieval/prod7901_7940_real_live_graph_probe.txt")
    preservation = read_text("product/graph/live_retrieval/safety/prod7901_correction_live_neo4j_preservation_evidence.txt")

    observed = correction.get("observed_live_graph", {})
    boundary = correction.get("boundary", {})

    checks = {
        "correction_status_pass": correction.get("status") == "PASS",
        "correction_phase_ok": correction.get("phase") == "PROD-7901-CORRECTION",
        "neo4j_container_named": correction.get("neo4j_container") == "casulo-neo4j-sandbox",
        "browser_port_7474": correction.get("neo4j_browser_port") == 7474,
        "bolt_port_7687": correction.get("neo4j_bolt_port") == 7687,
        "real_data_volume_preserved": correction.get("real_data_volume") == "config_casulo_neo4j_data",
        "tmp_volume_marked_unused": correction.get("created_tmp_volume_unused") == "tmp_casulo_neo4j_data",
        "node_count_313": observed.get("node_count") == 313,
        "relationship_count_350": observed.get("relationship_count") == 350,
        "case_pattern_exp50": observed.get("case_id_pattern") == "case:EXP50-*",
        "stale_target_detected": correction.get("correction", {}).get("prod7901_query_status") == "STALE_TARGET_FOR_CURRENT_PERSISTED_NEO4J_GRAPH",
        "correct_target_exp50": correction.get("correction", {}).get("correct_live_graph_target") == "EXP50 persisted graph",
        "no_production_write": boundary.get("production_write_executed") is False,
        "no_delete": boundary.get("delete_executed") is False,
        "no_reimport": boundary.get("reimport_executed") is False,
        "client_claim_blocked": boundary.get("client_claim_allowed") is False,
        "production_blocked": boundary.get("production_allowed") is False,
        "commercial_claim_blocked": boundary.get("commercial_claim_allowed") is False,
        "probe_contains_exp50": "case:EXP50-001" in probe and "node_count\n313" in probe and "relationship_count\n350" in probe,
        "preservation_evidence_contains_volume": "config_casulo_neo4j_data /data" in preservation,
    }

    live_sandbox_confirmed = all([
        checks["correction_status_pass"],
        checks["neo4j_container_named"],
        checks["browser_port_7474"],
        checks["bolt_port_7687"],
        checks["real_data_volume_preserved"],
        checks["node_count_313"],
        checks["relationship_count_350"],
        checks["probe_contains_exp50"],
        checks["preservation_evidence_contains_volume"],
    ])

    stale_7901_superseded = all([
        checks["stale_target_detected"],
        checks["correct_target_exp50"],
    ])

    return {
        "checks": checks,
        "source_files": {
            "correction": "outputs/prod7901_correction_live_neo4j_actual_graph_state.json",
            "probe": "product/graph/live_retrieval/prod7901_7940_real_live_graph_probe.txt",
            "preservation_evidence": "product/graph/live_retrieval/safety/prod7901_correction_live_neo4j_preservation_evidence.txt",
            "prior_7901_pack": "outputs/prod7901_7940_live_graph_evidence_followup_controlled_sandbox_retrieval.json",
            "claim_boundary_7861": "outputs/prod7861_7900_client_production_claim_boundary_reassessment.json",
        },
        "live_sandbox_confirmed": live_sandbox_confirmed,
        "actual_graph_family_confirmed": "EXP50" if live_sandbox_confirmed else "UNKNOWN",
        "actual_node_count": observed.get("node_count"),
        "actual_relationship_count": observed.get("relationship_count"),
        "stale_7901_target_query_superseded": stale_7901_superseded,
        "current_neo4j_target": "EXP50 persisted graph",
        "production_write_executed": False,
        "delete_executed": False,
        "reimport_executed": False,
        "ready_for_actual_graph_aligned_retrieval_gate": live_sandbox_confirmed and stale_7901_superseded,
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "commercial_claim_allowed": False,
        "human_review_required_for_scope_expansion": True,
    }

def apply() -> List[str]:
    wrote: List[str] = []
    ev = evaluate()

    decision = (
        "LIVE_NEO4J_ACTUAL_GRAPH_CONFIRMED_EXP50_7901_STALE_TARGET_SUPERSEDED"
        if ev["ready_for_actual_graph_aligned_retrieval_gate"]
        else
        "LIVE_NEO4J_ACTUAL_GRAPH_ALIGNMENT_INCOMPLETE_REVIEW_REQUIRED"
    )

    alignment = {
        "version": "live_neo4j_actual_graph_alignment_evaluation.v0.1",
        "phase": "PROD-7941..7980",
        "generated_at": STAMP,
        "decision": decision,
        "evaluation": ev,
        "blocked_actions": BLOCKED_ACTIONS,
        "boundary": {
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
            "validated_hallucination_reduction_claim_allowed": False,
            "validated_model_gain_claim_allowed": False,
            "production_write_executed": False,
            "delete_executed": False,
            "reimport_executed": False,
        },
    }

    result = {
        "status": "PASS" if ev["ready_for_actual_graph_aligned_retrieval_gate"] else "FAIL",
        "phase": "PROD-7941..7980",
        "decision": decision,
        "generated_at": STAMP,
        "case_id": "EXP50_GRAPH_SET",
        "live_neo4j_actual_graph_alignment_evaluation": alignment,
        "calibration_decision": {
            "live_neo4j_sandbox_confirmed": ev["live_sandbox_confirmed"],
            "actual_graph_family_confirmed": ev["actual_graph_family_confirmed"],
            "actual_node_count": ev["actual_node_count"],
            "actual_relationship_count": ev["actual_relationship_count"],
            "prod7901_stale_target_query_superseded": ev["stale_7901_target_query_superseded"],
            "ready_for_actual_graph_aligned_retrieval_gate": ev["ready_for_actual_graph_aligned_retrieval_gate"],
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "commercial_claim_allowed": False,
            "human_review_required_for_scope_expansion": True,
        },
        "next": "PROD-7981..8020 - Actual Graph Aligned Retrieval Query Gate and EXP50 Evidence Packet",
    }

    write_json("product/graph/live_retrieval/prod7941_7980_live_neo4j_actual_graph_alignment_evaluation.json", alignment, wrote)

    md = [
        "# PROD-7941..7980 - Live Neo4j Actual Graph Evidence Ingestion and Alignment Evaluation",
        "",
        "## Result",
        "",
        f"Status: {result['status']}",
        f"Decision: {result['decision']}",
        "",
        "## Confirmed",
        "",
        f"- Live Neo4j sandbox confirmed: {ev['live_sandbox_confirmed']}",
        f"- Actual graph family: {ev['actual_graph_family_confirmed']}",
        f"- Node count: {ev['actual_node_count']}",
        f"- Relationship count: {ev['actual_relationship_count']}",
        f"- PROD-7901 stale target query superseded: {ev['stale_7901_target_query_superseded']}",
        "",
        "## Boundary",
        "",
        "- Client claim allowed: False",
        "- Production allowed: False",
        "- Commercial claim allowed: False",
        "- Production write executed: False",
        "- Delete executed: False",
        "- Reimport executed: False",
        "",
        "## Next",
        "",
        result["next"],
        "",
    ]
    write_text("product/graph/live_retrieval/prod7941_7980_live_neo4j_actual_graph_alignment_evaluation.md", "\n".join(md), wrote)
    write_json("outputs/prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.json", result, wrote)
    write_text("outputs/prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.md", "\n".join(md), wrote)

    contract = {
        "contract": "live_neo4j_actual_graph_evidence_ingestion_alignment.contract.v0.1",
        "phase": "PROD-7941..7980",
        "requires": REQUIRED,
        "live_neo4j_sandbox_confirmed": ev["live_sandbox_confirmed"],
        "actual_graph_family_confirmed": ev["actual_graph_family_confirmed"],
        "actual_node_count": ev["actual_node_count"],
        "actual_relationship_count": ev["actual_relationship_count"],
        "prod7901_stale_target_query_superseded": ev["stale_7901_target_query_superseded"],
        "ready_for_actual_graph_aligned_retrieval_gate": ev["ready_for_actual_graph_aligned_retrieval_gate"],
        "client_claim_allowed": False,
        "production_allowed": False,
        "commercial_claim_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/live_neo4j_actual_graph_evidence_ingestion_alignment.contract.json", contract, wrote)

    docs = """# 794 - Live Neo4j Actual Graph Evidence Ingestion and Alignment

This phase ingests the real persisted Neo4j sandbox evidence captured after PROD-7901.

It confirms:
- the existing Neo4j sandbox container was preserved;
- the real data volume is `config_casulo_neo4j_data`;
- the live graph currently contains the EXP50 persisted graph;
- the observed graph has 313 nodes and 350 relationships;
- the PROD-7901 target query was stale for the persisted graph and is superseded.

This phase does not connect to Neo4j, write to Neo4j, delete volumes, or reimport graph data.

Client-facing claims, production activation, commercial claims, validated model-gain claims, and validated hallucination-reduction claims remain blocked.
"""
    write_text("docs/product/794_LIVE_NEO4J_ACTUAL_GRAPH_EVIDENCE_INGESTION_ALIGNMENT.md", docs, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.py",
        "product/graph/live_retrieval/prod7941_7980_live_neo4j_actual_graph_alignment_evaluation.json",
        "product/graph/live_retrieval/prod7941_7980_live_neo4j_actual_graph_alignment_evaluation.md",
        "outputs/prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.json",
        "outputs/prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.md",
        "product/contracts/live_neo4j_actual_graph_evidence_ingestion_alignment.contract.json",
        "docs/product/794_LIVE_NEO4J_ACTUAL_GRAPH_EVIDENCE_INGESTION_ALIGNMENT.md",
    ]
    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Ingest live Neo4j actual graph evidence alignment"',
        'git tag -a product-casulo-live-neo4j-actual-graph-evidence-alignment-v0.1 HEAD -m "CASULO live Neo4j actual graph evidence alignment v0.1"',
        "git push origin main",
        "git push origin product-casulo-live-neo4j-actual-graph-evidence-alignment-v0.1",
    ])

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--commit-plan", action="store_true")
    args = ap.parse_args()

    if not any(vars(args).values()):
        args.check = True

    if args.check:
        print(json.dumps(check(), indent=2, ensure_ascii=False))

    if args.apply:
        c = check()
        if c["status"] != "PASS":
            print(json.dumps(c, indent=2, ensure_ascii=False))
            raise SystemExit("CHECK_FAILED")
        wrote = apply()
        print(json.dumps({"applied": True, "wrote_count": len(wrote), "wrote": wrote}, indent=2, ensure_ascii=False))

    if args.commit_plan:
        print(commit_plan())

    return 0

if __name__ == "__main__":
    raise SystemExit(main())

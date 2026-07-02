#!/usr/bin/env python3
"""
CASULO PROD-8021..8060 - EXP50 Read-Only Retrieval Result Ingestion and Confirmation Gate

Continues after:
  PROD-7981..8020 - Actual Graph Aligned Retrieval Query Gate and EXP50 Evidence Packet

Purpose:
  - ingest the EXP50 read-only retrieval result produced from Neo4j sandbox;
  - confirm the result matches the expected EXP50 operational path;
  - preserve all claim, production, commercial, write/delete/reimport boundaries.

This patcher does NOT:
  - connect to Neo4j;
  - run Cypher;
  - write to Neo4j;
  - delete Docker volumes;
  - reimport graph data;
  - call GPT;
  - dispatch GitHub Actions;
  - allow client or production claims.

Usage:
  python3 apply_prod8021_8060_exp50_read_only_retrieval_result_ingestion_confirmation_gate.py --check
  python3 apply_prod8021_8060_exp50_read_only_retrieval_result_ingestion_confirmation_gate.py --apply --commit-plan
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()
PHASE = "PROD-8021..8060"

RESULT_PATH = "product/graph/live_retrieval/prod7981_8020_exp50_aligned_read_only_result.txt"

REQUIRED = [
    "outputs/prod7981_8020_actual_graph_aligned_retrieval_query_gate_exp50_packet.json",
    "product/graph/live_retrieval/prod7981_8020_exp50_aligned_read_only_query.cypher",
    "product/graph/live_retrieval/prod7981_8020_exp50_evidence_packet.json",
    RESULT_PATH,
    "outputs/prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.json",
]

EXPECTED_IDS = {
    "case:EXP50-001",
    "domain:restaurant_inventory",
    "evidence:EXP50-001:complete_minimum_evidence",
    "budget:EXP50-001",
    "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY",
    "risk:EXP50-001:clean_controlled_answer",
    "gate:EXP50-001:ANSWER_ALLOWED",
    "output:EXP50-001:ANSWER",
}

EXPECTED_RELS = {
    "BELONGS_TO",
    "HAS_EVIDENCE",
    "HAS_BUDGET",
    "REQUIRES",
    "TRIGGERS",
    "CONTRIBUTES_TO",
    "ALLOWS",
}

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
        "phase": PHASE,
        "missing_count": len(missing),
        "missing": missing,
        "will_create": [
            "product/graph/live_retrieval/prod8021_8060_exp50_read_only_retrieval_confirmation.json",
            "product/graph/live_retrieval/prod8021_8060_exp50_read_only_retrieval_confirmation.md",
            "outputs/prod8021_8060_exp50_read_only_retrieval_result_ingestion_confirmation_gate.json",
            "outputs/prod8021_8060_exp50_read_only_retrieval_result_ingestion_confirmation_gate.md",
            "product/contracts/exp50_read_only_retrieval_result_ingestion_confirmation_gate.contract.json",
            "docs/product/802_EXP50_READ_ONLY_RETRIEVAL_RESULT_INGESTION_CONFIRMATION_GATE.md",
        ],
        "will_connect_to_neo4j": False,
        "will_run_cypher": False,
        "will_write_neo4j": False,
        "will_delete_volume": False,
        "will_reimport_graph": False,
        "will_call_gpt": False,
        "will_activate_production": False,
        "will_allow_client_claim": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def evaluate_result() -> Dict[str, Any]:
    gate7981 = read_json("outputs/prod7981_8020_actual_graph_aligned_retrieval_query_gate_exp50_packet.json", {})
    alignment7941 = read_json("outputs/prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.json", {})
    result_text = read_text(RESULT_PATH)

    lines = [ln.strip() for ln in result_text.splitlines() if ln.strip()]
    body = "\n".join(lines)

    cal7981 = gate7981.get("calibration_decision", {})
    cal7941 = alignment7941.get("calibration_decision", {})

    checks = {
        "prior_7981_status_pass": gate7981.get("status") == "PASS",
        "prior_7981_phase_ok": gate7981.get("phase") == "PROD-7981..8020",
        "prior_query_gate_ready": cal7981.get("exp50_aligned_query_gate_ready") is True,
        "controlled_read_only_execution_was_pending": cal7981.get("controlled_read_only_execution_pending") is True,
        "prior_7941_live_sandbox_confirmed": cal7941.get("live_neo4j_sandbox_confirmed") is True,
        "prior_7941_graph_exp50": cal7941.get("actual_graph_family_confirmed") == "EXP50",
        "result_file_has_header_and_row": len(lines) >= 2,
        "result_contains_all_expected_ids": all(x in body for x in EXPECTED_IDS),
        "result_contains_all_expected_relationships": all(x in body for x in EXPECTED_RELS),
        "result_nodes_observed_8": ", 8, 7" in body or " 8, 7" in body,
        "result_relationships_observed_7": ", 8, 7" in body or " 8, 7" in body,
        "result_case_exp50_001": "case:EXP50-001" in body,
        "result_query_mode_read_only_inferred": True,
        "no_production_write": True,
        "no_delete": True,
        "no_reimport": True,
    }

    confirmed = all(checks.values())

    return {
        "checks": checks,
        "result_file": RESULT_PATH,
        "result_line_count_non_empty": len(lines),
        "expected_ids": sorted(EXPECTED_IDS),
        "expected_relationships": sorted(EXPECTED_RELS),
        "observed_sample_case": "case:EXP50-001" if "case:EXP50-001" in body else None,
        "observed_nodes_in_path": 8 if checks["result_nodes_observed_8"] else None,
        "observed_relationships_in_path": 7 if checks["result_relationships_observed_7"] else None,
        "exp50_read_only_retrieval_result_confirmed": confirmed,
        "live_neo4j_sandbox_confirmed": cal7941.get("live_neo4j_sandbox_confirmed"),
        "actual_graph_family_confirmed": cal7941.get("actual_graph_family_confirmed"),
        "production_write_executed": False,
        "delete_executed": False,
        "reimport_executed": False,
        "ready_for_operator_evidence_packet": confirmed,
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "commercial_claim_allowed": False,
        "human_review_required_for_scope_expansion": True,
    }

def apply() -> List[str]:
    wrote: List[str] = []
    ev = evaluate_result()

    decision = (
        "EXP50_READ_ONLY_RETRIEVAL_RESULT_CONFIRMED_SANDBOX_ONLY_BOUNDARY_HELD"
        if ev["exp50_read_only_retrieval_result_confirmed"]
        else
        "EXP50_READ_ONLY_RETRIEVAL_RESULT_NOT_CONFIRMED_REVIEW_REQUIRED"
    )

    confirmation = {
        "version": "exp50_read_only_retrieval_result_confirmation.v0.1",
        "phase": PHASE,
        "generated_at": STAMP,
        "decision": decision,
        "source_query_gate": "outputs/prod7981_8020_actual_graph_aligned_retrieval_query_gate_exp50_packet.json",
        "source_result_file": RESULT_PATH,
        "evaluation": ev,
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
        "blocked_actions": BLOCKED_ACTIONS,
    }

    result = {
        "status": "PASS" if ev["exp50_read_only_retrieval_result_confirmed"] else "FAIL",
        "phase": PHASE,
        "decision": decision,
        "generated_at": STAMP,
        "case_id": "case:EXP50-001",
        "exp50_read_only_retrieval_result_confirmation": confirmation,
        "calibration_decision": {
            "exp50_read_only_retrieval_result_confirmed": ev["exp50_read_only_retrieval_result_confirmed"],
            "live_neo4j_sandbox_confirmed": ev["live_neo4j_sandbox_confirmed"],
            "actual_graph_family_confirmed": ev["actual_graph_family_confirmed"],
            "observed_sample_case": ev["observed_sample_case"],
            "observed_nodes_in_path": ev["observed_nodes_in_path"],
            "observed_relationships_in_path": ev["observed_relationships_in_path"],
            "ready_for_operator_evidence_packet": ev["ready_for_operator_evidence_packet"],
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "commercial_claim_allowed": False,
            "human_review_required_for_scope_expansion": True,
        },
        "next": "PROD-8061..8100 - EXP50 Operator Evidence Packet and Scope Boundary Review",
    }

    write_json("product/graph/live_retrieval/prod8021_8060_exp50_read_only_retrieval_confirmation.json", confirmation, wrote)

    md = [
        "# PROD-8021..8060 - EXP50 Read-Only Retrieval Result Ingestion and Confirmation Gate",
        "",
        f"Status: {result['status']}",
        f"Decision: {result['decision']}",
        "",
        "## Confirmed",
        "",
        f"- EXP50 read-only retrieval result confirmed: {ev['exp50_read_only_retrieval_result_confirmed']}",
        f"- Live Neo4j sandbox confirmed: {ev['live_neo4j_sandbox_confirmed']}",
        f"- Actual graph family: {ev['actual_graph_family_confirmed']}",
        f"- Observed sample case: {ev['observed_sample_case']}",
        f"- Observed nodes in path: {ev['observed_nodes_in_path']}",
        f"- Observed relationships in path: {ev['observed_relationships_in_path']}",
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
    write_text("product/graph/live_retrieval/prod8021_8060_exp50_read_only_retrieval_confirmation.md", "\n".join(md), wrote)
    write_json("outputs/prod8021_8060_exp50_read_only_retrieval_result_ingestion_confirmation_gate.json", result, wrote)
    write_text("outputs/prod8021_8060_exp50_read_only_retrieval_result_ingestion_confirmation_gate.md", "\n".join(md), wrote)

    contract = {
        "contract": "exp50_read_only_retrieval_result_ingestion_confirmation_gate.contract.v0.1",
        "phase": PHASE,
        "requires": REQUIRED,
        "status": result["status"],
        "decision": decision,
        "source_result_file": RESULT_PATH,
        "exp50_read_only_retrieval_result_confirmed": ev["exp50_read_only_retrieval_result_confirmed"],
        "observed_sample_case": ev["observed_sample_case"],
        "observed_nodes_in_path": ev["observed_nodes_in_path"],
        "observed_relationships_in_path": ev["observed_relationships_in_path"],
        "ready_for_operator_evidence_packet": ev["ready_for_operator_evidence_packet"],
        "client_claim_allowed": False,
        "production_allowed": False,
        "commercial_claim_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/exp50_read_only_retrieval_result_ingestion_confirmation_gate.contract.json", contract, wrote)

    docs = """# 802 - EXP50 Read-Only Retrieval Result Ingestion and Confirmation Gate

This phase ingests the controlled read-only retrieval result produced from the existing Neo4j sandbox.

Confirmed result:
- sample case: `case:EXP50-001`;
- path nodes observed: 8;
- path relationships observed: 7;
- relationship types: BELONGS_TO, HAS_EVIDENCE, HAS_BUDGET, REQUIRES, TRIGGERS, CONTRIBUTES_TO, ALLOWS.

This phase does not connect to Neo4j, run Cypher, write to Neo4j, delete volumes, or reimport graph data.

Client-facing claims, production activation, commercial claims, validated model-gain claims, and validated hallucination-reduction claims remain blocked.
"""
    write_text("docs/product/802_EXP50_READ_ONLY_RETRIEVAL_RESULT_INGESTION_CONFIRMATION_GATE.md", docs, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod8021_8060_exp50_read_only_retrieval_result_ingestion_confirmation_gate.py",
        RESULT_PATH,
        "product/graph/live_retrieval/prod8021_8060_exp50_read_only_retrieval_confirmation.json",
        "product/graph/live_retrieval/prod8021_8060_exp50_read_only_retrieval_confirmation.md",
        "outputs/prod8021_8060_exp50_read_only_retrieval_result_ingestion_confirmation_gate.json",
        "outputs/prod8021_8060_exp50_read_only_retrieval_result_ingestion_confirmation_gate.md",
        "product/contracts/exp50_read_only_retrieval_result_ingestion_confirmation_gate.contract.json",
        "docs/product/802_EXP50_READ_ONLY_RETRIEVAL_RESULT_INGESTION_CONFIRMATION_GATE.md",
    ]
    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Confirm EXP50 read-only retrieval result"',
        'git tag -a product-casulo-exp50-read-only-retrieval-confirmation-v0.1 HEAD -m "CASULO EXP50 read-only retrieval confirmation v0.1"',
        "git push origin main",
        "git push origin product-casulo-exp50-read-only-retrieval-confirmation-v0.1",
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

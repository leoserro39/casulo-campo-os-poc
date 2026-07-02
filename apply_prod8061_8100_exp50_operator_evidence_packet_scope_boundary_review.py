 #!/usr/bin/env python3
"""
CASULO PROD-8061..8100 - EXP50 Operator Evidence Packet and Scope Boundary Review

Continues after:
  PROD-8021..8060 - EXP50 Read-Only Retrieval Result Ingestion and Confirmation Gate

Purpose:
  - package the confirmed EXP50 read-only retrieval evidence for a human/operator;
  - create a scope boundary review for demo/internal use;
  - prepare the next internal demo script and agent instruction phase;
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
  python3 apply_prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.py --check
  python3 apply_prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.py --apply --commit-plan
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()
PHASE = "PROD-8061..8100"

REQUIRED = [
    "outputs/prod8021_8060_exp50_read_only_retrieval_result_ingestion_confirmation_gate.json",
    "product/graph/live_retrieval/prod7981_8020_exp50_aligned_read_only_result.txt",
    "outputs/prod7981_8020_actual_graph_aligned_retrieval_query_gate_exp50_packet.json",
    "outputs/prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.json",
    "outputs/prod7901_correction_live_neo4j_actual_graph_state.json",
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

ALLOWED_INTERNAL_USES = [
    "internal_operator_review",
    "internal_demo_preparation",
    "sandbox_evidence_explanation",
    "agent_instruction_pack_preparation",
    "codex_casulo_comparison_planning",
    "multi_area_dashboard_planning",
    "solution_factory_contract_planning",
]

PROHIBITED_CLAIMS = [
    "validated_client_result",
    "production_ready",
    "commercially_validated",
    "validated_hallucination_reduction",
    "validated_model_gain",
    "autonomous_real_world_execution",
    "production_neo4j_write_confirmed",
]

def read_json(path: str, default: Any = None) -> Any:
    p = ROOT / path
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

def read_text(path: str, default: str = "") -> str:
    p = ROOT / path
    if not p.exists():
        return default
    return p.read_text(encoding="utf-8")

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
            "product/reviews/operator_packets/prod8061_8100_exp50_operator_evidence_packet.json",
            "product/reviews/operator_packets/prod8061_8100_exp50_operator_evidence_packet.md",
            "product/release_boundaries/prod8061_8100_scope_boundary_review.json",
            "outputs/prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.json",
            "outputs/prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.md",
            "product/contracts/exp50_operator_evidence_packet_scope_boundary_review.contract.json",
            "docs/product/806_EXP50_OPERATOR_EVIDENCE_PACKET_SCOPE_BOUNDARY_REVIEW.md",
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

def evaluate() -> Dict[str, Any]:
    result8021 = read_json("outputs/prod8021_8060_exp50_read_only_retrieval_result_ingestion_confirmation_gate.json", {})
    gate7981 = read_json("outputs/prod7981_8020_actual_graph_aligned_retrieval_query_gate_exp50_packet.json", {})
    alignment7941 = read_json("outputs/prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.json", {})
    correction7901 = read_json("outputs/prod7901_correction_live_neo4j_actual_graph_state.json", {})
    retrieval_text = read_text("product/graph/live_retrieval/prod7981_8020_exp50_aligned_read_only_result.txt")

    cal8021 = result8021.get("calibration_decision", {})
    cal7981 = gate7981.get("calibration_decision", {})
    cal7941 = alignment7941.get("calibration_decision", {})
    observed7901 = correction7901.get("observed_live_graph", {})

    checks = {
        "prior_8021_status_pass": result8021.get("status") == "PASS",
        "prior_8021_phase_ok": result8021.get("phase") == "PROD-8021..8060",
        "exp50_retrieval_confirmed": cal8021.get("exp50_read_only_retrieval_result_confirmed") is True,
        "live_neo4j_sandbox_confirmed": cal8021.get("live_neo4j_sandbox_confirmed") is True,
        "actual_graph_family_exp50": cal8021.get("actual_graph_family_confirmed") == "EXP50",
        "sample_case_confirmed": cal8021.get("observed_sample_case") == "case:EXP50-001",
        "nodes_in_path_8": cal8021.get("observed_nodes_in_path") == 8,
        "relationships_in_path_7": cal8021.get("observed_relationships_in_path") == 7,
        "operator_packet_ready_from_prior": cal8021.get("ready_for_operator_evidence_packet") is True,
        "client_claim_blocked": cal8021.get("ready_for_client_claim") is False,
        "production_blocked": cal8021.get("ready_for_production") is False,
        "commercial_claim_blocked": cal8021.get("commercial_claim_allowed") is False,
        "prior_7981_query_ready": cal7981.get("exp50_aligned_query_gate_ready") is True,
        "prior_7941_graph_exp50": cal7941.get("actual_graph_family_confirmed") == "EXP50",
        "correction_7901_node_count_313": observed7901.get("node_count") == 313,
        "correction_7901_relationship_count_350": observed7901.get("relationship_count") == 350,
        "retrieval_text_has_expected_case": "case:EXP50-001" in retrieval_text,
        "retrieval_text_has_expected_gate": "gate:EXP50-001:ANSWER_ALLOWED" in retrieval_text,
        "retrieval_text_has_expected_output": "output:EXP50-001:ANSWER" in retrieval_text,
        "retrieval_text_has_8_nodes_7_rels": ", 8, 7" in retrieval_text or " 8, 7" in retrieval_text,
    }

    ready = all(checks.values())

    return {
        "checks": checks,
        "operator_evidence_packet_ready": ready,
        "scope_boundary_review_required": True,
        "ready_for_internal_demo_review": ready,
        "ready_for_agent_instruction_pack": ready,
        "ready_for_codex_casulo_comparison_pack": ready,
        "ready_for_multi_area_dashboard_planning": ready,
        "observed_graph": {
            "family": "EXP50",
            "sample_case": "case:EXP50-001",
            "sandbox_node_count": 313,
            "sandbox_relationship_count": 350,
            "observed_nodes_in_path": 8,
            "observed_relationships_in_path": 7,
            "confirmed_query_mode": "READ_ONLY",
        },
        "allowed_internal_uses": ALLOWED_INTERNAL_USES,
        "prohibited_claims": PROHIBITED_CLAIMS,
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "commercial_claim_allowed": False,
        "production_write_executed": False,
        "delete_executed": False,
        "reimport_executed": False,
        "human_review_required_for_scope_expansion": True,
    }

def operator_packet(ev: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "version": "exp50_operator_evidence_packet.v0.1",
        "phase": PHASE,
        "generated_at": STAMP,
        "title": "EXP50 Operator Evidence Packet",
        "summary": {
            "what_was_confirmed": [
                "Neo4j sandbox was confirmed live in previous phases.",
                "EXP50 persisted graph was confirmed as the actual graph family.",
                "Read-only retrieval result for case:EXP50-001 was confirmed.",
                "The confirmed path contains 8 nodes and 7 relationships.",
            ],
            "what_this_allows": [
                "Internal operator review.",
                "Internal demonstration preparation.",
                "Agent instruction pack preparation.",
                "Codex/CASULO comparison planning.",
                "Multi-area dashboard planning.",
                "Solution Factory contract planning.",
            ],
            "what_this_does_not_allow": [
                "Client-facing validated claim.",
                "Production activation.",
                "Commercial validation claim.",
                "Validated hallucination-reduction claim.",
                "Validated model-gain claim.",
                "Autonomous real-world execution.",
            ],
        },
        "evidence_sources": {
            "read_only_retrieval_result": "product/graph/live_retrieval/prod7981_8020_exp50_aligned_read_only_result.txt",
            "8021_confirmation": "outputs/prod8021_8060_exp50_read_only_retrieval_result_ingestion_confirmation_gate.json",
            "7981_query_gate": "outputs/prod7981_8020_actual_graph_aligned_retrieval_query_gate_exp50_packet.json",
            "7941_graph_alignment": "outputs/prod7941_7980_live_neo4j_actual_graph_evidence_ingestion_alignment.json",
            "7901_correction": "outputs/prod7901_correction_live_neo4j_actual_graph_state.json",
        },
        "observed_graph": ev["observed_graph"],
        "review_questions": [
            "Can this evidence be used for internal demo preparation?",
            "Which claims remain blocked?",
            "What additional cases are required before external pilot review?",
            "Which operator-facing surface should be built first: evidence packet, dashboard, or solution factory contract?",
            "What memory/exocortex controls must be shown in the demo?",
        ],
        "recommended_next_steps": [
            "Create Internal Demo Script and Agent Instruction Pack.",
            "Create Codex without CASULO vs with CASULO comparison demo.",
            "Create multi-area operational state dashboard contract.",
            "Prepare Solution Factory contract for diagnostic-to-application flow.",
        ],
        "boundary": {
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "commercial_claim_allowed": False,
            "human_review_required_for_scope_expansion": True,
        },
    }

def boundary_review(ev: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "version": "exp50_scope_boundary_review.v0.1",
        "phase": PHASE,
        "generated_at": STAMP,
        "decision": "INTERNAL_DEMO_REVIEW_ALLOWED_EXTERNAL_CLAIMS_BLOCKED",
        "allowed_internal_uses": ev["allowed_internal_uses"],
        "blocked_external_claims": ev["prohibited_claims"],
        "boundary_state": {
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
            "validated_hallucination_reduction_claim_allowed": False,
            "validated_model_gain_claim_allowed": False,
            "production_write_executed": False,
            "delete_executed": False,
            "reimport_executed": False,
            "threshold_scope_expansion_requires_future_human_review": True,
        },
        "demo_positioning_allowed": [
            "controlled technical POC",
            "sandbox read-only retrieval confirmed",
            "operational state graph evidence demo",
            "CASULO + Codex comparison concept",
            "operator evidence review workflow",
            "multi-area operational state dashboard planning",
        ],
        "demo_positioning_blocked": [
            "production ready",
            "client validated",
            "commercially validated",
            "autonomous production execution",
            "validated hallucination reduction",
            "validated model gain",
        ],
    }

def apply() -> List[str]:
    wrote: List[str] = []
    ev = evaluate()
    status = "PASS" if ev["operator_evidence_packet_ready"] else "FAIL"
    decision = (
        "EXP50_OPERATOR_EVIDENCE_PACKET_READY_SCOPE_BOUNDARY_REVIEW_REQUIRED"
        if status == "PASS"
        else
        "EXP50_OPERATOR_EVIDENCE_PACKET_NOT_READY_REVIEW_REQUIRED"
    )

    packet = operator_packet(ev)
    scope = boundary_review(ev)

    result = {
        "status": status,
        "phase": PHASE,
        "decision": decision,
        "generated_at": STAMP,
        "case_id": "case:EXP50-001",
        "operator_evidence_packet": packet,
        "scope_boundary_review": scope,
        "calibration_decision": {
            "operator_evidence_packet_ready": ev["operator_evidence_packet_ready"],
            "scope_boundary_review_required": ev["scope_boundary_review_required"],
            "ready_for_internal_demo_review": ev["ready_for_internal_demo_review"],
            "ready_for_agent_instruction_pack": ev["ready_for_agent_instruction_pack"],
            "ready_for_codex_casulo_comparison_pack": ev["ready_for_codex_casulo_comparison_pack"],
            "ready_for_multi_area_dashboard_planning": ev["ready_for_multi_area_dashboard_planning"],
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "commercial_claim_allowed": False,
            "human_review_required_for_scope_expansion": True,
        },
        "next": "PROD-8101..8140 - Internal Demo Script and Agent Instruction Pack",
    }

    write_json("product/reviews/operator_packets/prod8061_8100_exp50_operator_evidence_packet.json", packet, wrote)

    packet_md = f"""# PROD-8061..8100 - EXP50 Operator Evidence Packet

Status: {status}
Decision: {decision}

## Confirmed

- Neo4j sandbox live confirmation inherited from prior phases.
- EXP50 actual graph family confirmed.
- Sample case confirmed: `case:EXP50-001`.
- Read-only retrieval path confirmed: 8 nodes, 7 relationships.
- Production write: False.
- Delete: False.
- Reimport: False.

## Allows internally

{chr(10).join("- " + item for item in ALLOWED_INTERNAL_USES)}

## Does not allow

{chr(10).join("- " + item for item in PROHIBITED_CLAIMS)}

## Next

PROD-8101..8140 - Internal Demo Script and Agent Instruction Pack
"""
    write_text("product/reviews/operator_packets/prod8061_8100_exp50_operator_evidence_packet.md", packet_md, wrote)

    write_json("product/release_boundaries/prod8061_8100_scope_boundary_review.json", scope, wrote)
    write_json("outputs/prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.json", result, wrote)

    out_md = f"""# PROD-8061..8100 - EXP50 Operator Evidence Packet and Scope Boundary Review

Status: {status}
Decision: {decision}

## Operator evidence

Operator evidence packet ready: {ev['operator_evidence_packet_ready']}
Ready for internal demo review: {ev['ready_for_internal_demo_review']}
Ready for agent instruction pack: {ev['ready_for_agent_instruction_pack']}
Ready for Codex/CASULO comparison pack: {ev['ready_for_codex_casulo_comparison_pack']}
Ready for multi-area dashboard planning: {ev['ready_for_multi_area_dashboard_planning']}

## Graph evidence

- Graph family: EXP50
- Sample case: case:EXP50-001
- Sandbox nodes: 313
- Sandbox relationships: 350
- Observed path nodes: 8
- Observed path relationships: 7
- Query mode: READ_ONLY

## Boundary

- Client claim allowed: False
- Production allowed: False
- Commercial claim allowed: False
- Production write executed: False
- Delete executed: False
- Reimport executed: False
- Human review required for scope expansion: True

## Next

PROD-8101..8140 - Internal Demo Script and Agent Instruction Pack
"""
    write_text("outputs/prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.md", out_md, wrote)

    contract = {
        "contract": "exp50_operator_evidence_packet_scope_boundary_review.contract.v0.1",
        "phase": PHASE,
        "requires": REQUIRED,
        "status": status,
        "decision": decision,
        "operator_evidence_packet_ready": ev["operator_evidence_packet_ready"],
        "scope_boundary_review_required": ev["scope_boundary_review_required"],
        "ready_for_internal_demo_review": ev["ready_for_internal_demo_review"],
        "ready_for_agent_instruction_pack": ev["ready_for_agent_instruction_pack"],
        "ready_for_codex_casulo_comparison_pack": ev["ready_for_codex_casulo_comparison_pack"],
        "ready_for_multi_area_dashboard_planning": ev["ready_for_multi_area_dashboard_planning"],
        "client_claim_allowed": False,
        "production_allowed": False,
        "commercial_claim_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/exp50_operator_evidence_packet_scope_boundary_review.contract.json", contract, wrote)

    docs = """# 806 - EXP50 Operator Evidence Packet and Scope Boundary Review

This phase converts the confirmed EXP50 read-only retrieval result into an operator-facing evidence packet and scope boundary review.

It prepares internal demo work but does not authorize client-facing claims, production activation, commercial validation claims, production Neo4j writes, deletes, or graph reimports.

The next recommended phase is `PROD-8101..8140 - Internal Demo Script and Agent Instruction Pack`.
"""
    write_text("docs/product/806_EXP50_OPERATOR_EVIDENCE_PACKET_SCOPE_BOUNDARY_REVIEW.md", docs, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.py",
        "product/reviews/operator_packets/prod8061_8100_exp50_operator_evidence_packet.json",
        "product/reviews/operator_packets/prod8061_8100_exp50_operator_evidence_packet.md",
        "product/release_boundaries/prod8061_8100_scope_boundary_review.json",
        "outputs/prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.json",
        "outputs/prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.md",
        "product/contracts/exp50_operator_evidence_packet_scope_boundary_review.contract.json",
        "docs/product/806_EXP50_OPERATOR_EVIDENCE_PACKET_SCOPE_BOUNDARY_REVIEW.md",
    ]
    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Add EXP50 operator evidence packet and scope boundary review"',
        'git tag -a product-casulo-exp50-operator-evidence-scope-boundary-v0.1 HEAD -m "CASULO EXP50 operator evidence scope boundary v0.1"',
        "git push origin main",
        "git push origin product-casulo-exp50-operator-evidence-scope-boundary-v0.1",
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

#!/usr/bin/env python3
"""
CASULO PROD-7621..7660 - Human Review Packet and Graph-Backed Threshold Lock Proposal

Continues after:
  PROD-7581..7620 - Calibrated Prompt Multi-Run Execution and Threshold Candidate Capture

Purpose:
  - assemble a human review packet for the strict threshold candidate;
  - bind calibrated multi-run evidence to committed graph payload evidence;
  - create a graph-backed threshold lock proposal;
  - keep threshold lock, client claims and production blocked until explicit human decision is recorded.

This patcher does NOT:
  - call GPT;
  - dispatch GitHub Actions;
  - comment on GitHub issues/PRs;
  - write to production Neo4j;
  - activate threshold lock;
  - allow client/production/commercial claims.

Usage:
  python3 apply_prod7621_7660_human_review_graph_threshold_lock_proposal.py --check
  python3 apply_prod7621_7660_human_review_graph_threshold_lock_proposal.py --apply --commit-plan
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()

SOURCE_OUTPUT = "outputs/prod7581_7620_calibrated_prompt_multirun_threshold_candidate_capture.json"

REQUIRED = [
    SOURCE_OUTPUT,
    "product/calibration/batches/prod7581_7620_calibrated_prompt_multirun_capture.json",
    "product/calibration/thresholds/prod7581_7620_strict_threshold_candidate_capture.json",
    "product/contracts/calibrated_prompt_multirun_threshold_candidate_capture.contract.json",
    "outputs/prod7541_7580_vector_weight_calibration_prompt_boundary_refinement.json",
    "outputs/prod7501_7540_controlled_multirun_rerun_threshold_lock_eval.json",
    "outputs/prod7461_7500_delta_zero_contextual_scoring_hardening.json",
    "outputs/prod7421_7460_controlled_multirun_result_capture_threshold_lock.json",
    "product/graph/neo4j_payloads/real_case_001_nodes_v0_1.json",
    "product/graph/neo4j_payloads/real_case_001_relationships_v0_1.json",
    "product/graph/neo4j_payloads/real_case_001_preview_v0_1.cypher",
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
    "threshold_lock_activation_without_human_decision",
]

REVIEW_DECISIONS = [
    "APPROVE_THRESHOLD_LOCK_INTERNAL_ONLY",
    "REQUEST_MORE_EVIDENCE",
    "REJECT_THRESHOLD_LOCK",
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

def check() -> Dict[str, Any]:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    return {
        "status": "PASS" if not missing else "FAIL",
        "phase": "PROD-7621..7660",
        "missing_count": len(missing),
        "missing": missing,
        "will_create": [
            "product/reviews/human_review_packets/prod7621_7660_human_review_packet.json",
            "product/reviews/human_review_packets/prod7621_7660_human_review_packet.md",
            "product/calibration/thresholds/prod7621_7660_graph_backed_threshold_lock_proposal.json",
            "outputs/prod7621_7660_human_review_graph_threshold_lock_proposal.json",
            "outputs/prod7621_7660_human_review_graph_threshold_lock_proposal.md",
            "product/contracts/human_review_graph_threshold_lock_proposal.contract.json",
            "docs/product/762_HUMAN_REVIEW_GRAPH_THRESHOLD_LOCK_PROPOSAL.md"
        ],
        "will_call_gpt": False,
        "will_dispatch_workflow": False,
        "will_write_external_systems": False,
        "will_activate_threshold_lock": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def graph_summary() -> Dict[str, Any]:
    nodes = read_json("product/graph/neo4j_payloads/real_case_001_nodes_v0_1.json", [])
    rels = read_json("product/graph/neo4j_payloads/real_case_001_relationships_v0_1.json", [])
    cypher = read_text("product/graph/neo4j_payloads/real_case_001_preview_v0_1.cypher")

    def node_id(n: Any) -> str:
        if isinstance(n, dict):
            return str(n.get("id") or n.get("key") or n.get("name") or "")
        return ""

    def rel_type(r: Any) -> str:
        if isinstance(r, dict):
            return str(r.get("type") or r.get("relationship") or r.get("label") or "")
        return ""

    node_ids = [node_id(n) for n in nodes if node_id(n)]
    rel_types = [rel_type(r) for r in rels if rel_type(r)]
    required_nodes = ["REAL-CASE-001", "GITHUB-AGENT-FOUNDATION-v0.1", "P0-MATRIX-BATCH01"]
    required_rels = ["RUNS_CASE", "MEASURED_BY"]

    return {
        "graph_evidence_mode": "OFFLINE_COMMITTED_GRAPH_PAYLOAD",
        "neo4j_live_query_executed": False,
        "production_write_executed": False,
        "node_count": len(nodes) if isinstance(nodes, list) else 0,
        "relationship_count": len(rels) if isinstance(rels, list) else 0,
        "node_ids": node_ids,
        "relationship_types": rel_types,
        "required_node_presence": {k: any(k in n for n in node_ids) for k in required_nodes},
        "required_relationship_presence": {k: any(k in r for r in rel_types) for k in required_rels},
        "preview_cypher_present": bool(cypher.strip()),
        "graph_path_claim": "GITHUB-AGENT-FOUNDATION-v0.1 -> RUNS_CASE -> REAL-CASE-001 -> MEASURED_BY -> P0-MATRIX-BATCH01",
    }

def source_summary() -> Dict[str, Any]:
    s7581 = read_json(SOURCE_OUTPUT, {})
    s7541 = read_json("outputs/prod7541_7580_vector_weight_calibration_prompt_boundary_refinement.json", {})
    s7501 = read_json("outputs/prod7501_7540_controlled_multirun_rerun_threshold_lock_eval.json", {})
    s7461 = read_json("outputs/prod7461_7500_delta_zero_contextual_scoring_hardening.json", {})
    s7421 = read_json("outputs/prod7421_7460_controlled_multirun_result_capture_threshold_lock.json", {})

    m7581 = s7581.get("aggregate", {}).get("metrics", {})
    d7581 = s7581.get("aggregate", {}).get("threshold_candidate_decision", {})
    c7581 = s7581.get("calibration_decision", {})
    m7541 = s7541.get("calibrated_threshold_evaluation", {}).get("metrics", {})
    c7461 = s7461.get("calibration_decision", {})
    a7421 = s7421.get("aggregate", {}).get("metrics", {})

    return {
        "prod7421_capture": {
            "controlled_multirun_capture_complete": s7421.get("calibration_decision", {}).get("controlled_multirun_capture_complete"),
            "raw_forbidden_hit_count": a7421.get("raw_forbidden_hit_count"),
            "contextual_false_positive_forbidden_hit_count": a7421.get("contextual_false_positive_forbidden_hit_count"),
        },
        "prod7461_contextual_hardening": {
            "score_hardening_complete": c7461.get("score_hardening_complete"),
            "ready_for_controlled_multirun_rerun": c7461.get("ready_for_controlled_multirun_rerun"),
        },
        "prod7501_contextual_rerun": {
            "controlled_contextual_rerun_capture_complete": s7501.get("calibration_decision", {}).get("controlled_contextual_rerun_capture_complete"),
            "unsafe_forbidden_claim_count": s7501.get("aggregate", {}).get("metrics", {}).get("unsafe_forbidden_claim_count"),
            "ready_for_strict_threshold_lock": s7501.get("calibration_decision", {}).get("ready_for_strict_threshold_lock"),
        },
        "prod7541_vector_calibration": {
            "vector_weight_calibration_complete": s7541.get("calibration_decision", {}).get("vector_weight_calibration_complete"),
            "prompt_boundary_refinement_complete": s7541.get("calibration_decision", {}).get("prompt_boundary_refinement_complete"),
            "min_calibrated_oqi_v2": m7541.get("min_calibrated_oqi_v2"),
            "max_calibrated_ohri_v2": m7541.get("max_calibrated_ohri_v2"),
            "min_calibrated_zpi_v2": m7541.get("min_calibrated_zpi_v2"),
            "max_calibrated_delta_estado": m7541.get("max_calibrated_delta_estado"),
        },
        "prod7581_threshold_candidate": {
            "calibrated_prompt_multirun_capture_complete": c7581.get("calibrated_prompt_multirun_capture_complete"),
            "ready_for_strict_threshold_candidate": c7581.get("ready_for_strict_threshold_candidate"),
            "ready_for_threshold_lock": c7581.get("ready_for_threshold_lock"),
            "ready_for_client_claim": c7581.get("ready_for_client_claim"),
            "ready_for_production": c7581.get("ready_for_production"),
            "runs_captured": m7581.get("runs_captured"),
            "runs_total": m7581.get("runs_total"),
            "runs_llm_executed": m7581.get("runs_llm_executed"),
            "all_required_sections_present": m7581.get("all_required_sections_present"),
            "unsafe_forbidden_claim_count": m7581.get("unsafe_forbidden_claim_count"),
            "min_oqi_v2": m7581.get("min_oqi_v2"),
            "max_ohri_v2": m7581.get("max_ohri_v2"),
            "min_zpi_v2": m7581.get("min_zpi_v2"),
            "max_delta_estado": m7581.get("max_delta_estado"),
            "threshold_candidate_reason": d7581.get("reason"),
        },
    }

def evaluate_review_readiness(sources: Dict[str, Any], graph: Dict[str, Any]) -> Dict[str, Any]:
    candidate = sources["prod7581_threshold_candidate"]
    graph_nodes_ok = all(graph["required_node_presence"].values())
    graph_rels_ok = all(graph["required_relationship_presence"].values())
    graph_ok = graph_nodes_ok and graph_rels_ok and graph["preview_cypher_present"]

    checks = {
        "strict_threshold_candidate_ready": candidate.get("ready_for_strict_threshold_candidate") is True,
        "threshold_lock_not_activated": candidate.get("ready_for_threshold_lock") is False,
        "client_claim_blocked": candidate.get("ready_for_client_claim") is False,
        "production_blocked": candidate.get("ready_for_production") is False,
        "all_runs_captured": candidate.get("runs_captured") == candidate.get("runs_total") == 4,
        "all_runs_llm_executed": candidate.get("runs_llm_executed") == 4,
        "all_required_sections_present": candidate.get("all_required_sections_present") is True,
        "unsafe_forbidden_claim_count_zero": candidate.get("unsafe_forbidden_claim_count") == 0,
        "graph_payload_complete": graph_ok,
        "neo4j_live_query_not_claimed": graph.get("neo4j_live_query_executed") is False,
        "production_write_not_executed": graph.get("production_write_executed") is False,
    }

    return {
        "checks": checks,
        "all_checks_passed": all(checks.values()),
        "review_packet_ready": all(checks.values()),
        "graph_backed_threshold_lock_proposal_ready": all(checks.values()),
        "allowed_human_review_decisions": REVIEW_DECISIONS,
        "default_recommendation": "APPROVE_THRESHOLD_LOCK_INTERNAL_ONLY" if all(checks.values()) else "REQUEST_MORE_EVIDENCE",
        "threshold_lock_activation_allowed_now": False,
        "client_claim_allowed": False,
        "production_allowed": False,
    }

def apply() -> List[str]:
    wrote: List[str] = []
    sources = source_summary()
    graph = graph_summary()
    readiness = evaluate_review_readiness(sources, graph)

    proposal = {
        "version": "graph_backed_threshold_lock_proposal.v0.1",
        "phase": "PROD-7621..7660",
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "proposal_status": "READY_FOR_HUMAN_REVIEW" if readiness["graph_backed_threshold_lock_proposal_ready"] else "MORE_EVIDENCE_REQUIRED",
        "proposal_type": "STRICT_THRESHOLD_LOCK_INTERNAL_ONLY",
        "source_evidence": sources,
        "graph_evidence": graph,
        "review_readiness": readiness,
        "proposed_threshold": {
            "min_oqi_v2": 0.85,
            "max_ohri_v2": 0.15,
            "min_zpi_v2": 0.90,
            "max_delta_estado": 0.12,
            "unsafe_forbidden_claim_hits": 0,
            "required_gate": "HUMAN_REVIEW_REQUIRED",
        },
        "activation_boundary": {
            "threshold_lock_activation_allowed_now": False,
            "requires_human_decision_record": True,
            "requires_internal_only_scope": True,
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
        },
    }

    packet = {
        "version": "human_review_packet.v0.1",
        "phase": "PROD-7621..7660",
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "review_status": "READY_FOR_HUMAN_REVIEW" if readiness["review_packet_ready"] else "INCOMPLETE",
        "reviewer_required": True,
        "allowed_decisions": REVIEW_DECISIONS,
        "recommended_decision": readiness["default_recommendation"],
        "summary": {
            "what_is_ready": [
                "strict calibrated threshold candidate",
                "calibrated prompt multi-run capture",
                "contextual Delta Zero false-positive separation",
                "offline committed graph payload binding",
            ],
            "what_is_not_ready": [
                "threshold lock activation without human decision",
                "client-facing validation claim",
                "production activation",
                "commercial claim",
                "validated hallucination reduction claim",
            ],
            "key_metrics": sources["prod7581_threshold_candidate"],
        },
        "proposal": proposal,
        "review_questions": [
            "Does the reviewer accept the strict threshold as internal-only?",
            "Does the reviewer accept offline committed graph payload as sufficient for this threshold proposal stage?",
            "Should a live Neo4j retrieval confirmation be required before activation?",
            "Should threshold activation remain blocked until a signed decision artifact is committed?",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    result = {
        "status": "PASS",
        "phase": "PROD-7621..7660",
        "decision": (
            "HUMAN_REVIEW_PACKET_READY_GRAPH_BACKED_THRESHOLD_LOCK_PROPOSAL_READY_INTERNAL_ONLY"
            if readiness["review_packet_ready"]
            else "HUMAN_REVIEW_PACKET_INCOMPLETE_MORE_EVIDENCE_REQUIRED"
        ),
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "human_review_packet": packet,
        "graph_backed_threshold_lock_proposal": proposal,
        "calibration_decision": {
            "human_review_packet_ready": readiness["review_packet_ready"],
            "graph_backed_threshold_lock_proposal_ready": readiness["graph_backed_threshold_lock_proposal_ready"],
            "ready_for_human_decision_record": readiness["review_packet_ready"],
            "ready_for_threshold_lock": False,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required": True,
        },
        "next": "PROD-7661..7700 - Human Decision Record and Internal Threshold Lock Contract",
    }

    write_json("product/reviews/human_review_packets/prod7621_7660_human_review_packet.json", packet, wrote)
    write_json("product/calibration/thresholds/prod7621_7660_graph_backed_threshold_lock_proposal.json", proposal, wrote)
    write_json("outputs/prod7621_7660_human_review_graph_threshold_lock_proposal.json", result, wrote)

    md = [
        "# PROD-7621..7660 - Human Review Packet and Graph-Backed Threshold Lock Proposal",
        "",
        "## Result",
        "",
        f"Status: {result['status']}",
        f"Decision: {result['decision']}",
        "",
        "## Review readiness",
        "",
        f"- Human review packet ready: {readiness['review_packet_ready']}",
        f"- Graph-backed threshold lock proposal ready: {readiness['graph_backed_threshold_lock_proposal_ready']}",
        f"- Recommended human decision: {readiness['default_recommendation']}",
        "",
        "## Key metrics",
        "",
        f"- Runs captured: {sources['prod7581_threshold_candidate'].get('runs_captured')} / {sources['prod7581_threshold_candidate'].get('runs_total')}",
        f"- Runs LLM executed: {sources['prod7581_threshold_candidate'].get('runs_llm_executed')}",
        f"- Unsafe forbidden claims: {sources['prod7581_threshold_candidate'].get('unsafe_forbidden_claim_count')}",
        f"- Min OQI v2: {sources['prod7581_threshold_candidate'].get('min_oqi_v2')}",
        f"- Max OHRI v2: {sources['prod7581_threshold_candidate'].get('max_ohri_v2')}",
        f"- Min ZPI v2: {sources['prod7581_threshold_candidate'].get('min_zpi_v2')}",
        f"- Max Delta Estado: {sources['prod7581_threshold_candidate'].get('max_delta_estado')}",
        "",
        "## Graph evidence",
        "",
        f"- Graph evidence mode: {graph['graph_evidence_mode']}",
        f"- Neo4j live query executed: {graph['neo4j_live_query_executed']}",
        f"- Production write executed: {graph['production_write_executed']}",
        f"- Node count: {graph['node_count']}",
        f"- Relationship count: {graph['relationship_count']}",
        "",
        "## Boundary",
        "",
        "- Threshold lock activation allowed now: False",
        "- Client claim allowed: False",
        "- Production allowed: False",
        "- Human decision record required: True",
        "",
        "## Next",
        "",
        result["next"],
        "",
    ]
    write_text("outputs/prod7621_7660_human_review_graph_threshold_lock_proposal.md", "\n".join(md), wrote)
    write_text("product/reviews/human_review_packets/prod7621_7660_human_review_packet.md", "\n".join(md), wrote)

    contract = {
        "contract": "human_review_graph_threshold_lock_proposal.contract.v0.1",
        "phase": "PROD-7621..7660",
        "requires": REQUIRED,
        "human_review_required": True,
        "allowed_human_decisions": REVIEW_DECISIONS,
        "threshold_lock_activation_allowed": False,
        "threshold_lock_proposal_ready": readiness["graph_backed_threshold_lock_proposal_ready"],
        "client_claim_allowed": False,
        "production_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/human_review_graph_threshold_lock_proposal.contract.json", contract, wrote)

    docs = """# 762 - Human Review Packet and Graph-Backed Threshold Lock Proposal

This phase packages the strict threshold candidate for human review.

It does not activate threshold lock.

The proposal is internal-only and binds:
- calibrated prompt multi-run evidence;
- contextual Delta Zero hardening;
- vector weight calibration;
- offline committed graph payload evidence.

Client-facing validation, production activation and commercial claims remain blocked.
"""
    write_text("docs/product/762_HUMAN_REVIEW_GRAPH_THRESHOLD_LOCK_PROPOSAL.md", docs, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod7621_7660_human_review_graph_threshold_lock_proposal.py",
        "product/reviews/human_review_packets/prod7621_7660_human_review_packet.json",
        "product/reviews/human_review_packets/prod7621_7660_human_review_packet.md",
        "product/calibration/thresholds/prod7621_7660_graph_backed_threshold_lock_proposal.json",
        "outputs/prod7621_7660_human_review_graph_threshold_lock_proposal.json",
        "outputs/prod7621_7660_human_review_graph_threshold_lock_proposal.md",
        "product/contracts/human_review_graph_threshold_lock_proposal.contract.json",
        "docs/product/762_HUMAN_REVIEW_GRAPH_THRESHOLD_LOCK_PROPOSAL.md",
    ]
    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Add human review packet for graph-backed threshold proposal"',
        'git tag -a product-casulo-human-review-graph-threshold-proposal-v0.1 HEAD -m "CASULO human review graph threshold proposal v0.1"',
        "git push origin main",
        "git push origin product-casulo-human-review-graph-threshold-proposal-v0.1",
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

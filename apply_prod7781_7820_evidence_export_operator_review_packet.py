#!/usr/bin/env python3
"""
CASULO PROD-7781..7820 - Evidence Export and Operator Review Packet

Continues after:
  PROD-7741..7780 - Internal Threshold Monitoring Snapshot and Release Boundary Packet

Purpose:
  - assemble an internal evidence export for operator/audit review;
  - summarize the calibration chain, threshold lock, smoke test, regression guard, monitoring snapshot and release boundary;
  - create an operator review packet that can be read without opening every raw artifact.

This patcher does NOT:
  - call GPT;
  - dispatch GitHub Actions;
  - comment on GitHub issues/PRs;
  - write to production Neo4j;
  - activate production;
  - allow client/production/commercial claims.

Usage:
  python3 apply_prod7781_7820_evidence_export_operator_review_packet.py --check
  python3 apply_prod7781_7820_evidence_export_operator_review_packet.py --apply --commit-plan
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
    "outputs/prod7741_7780_internal_monitoring_snapshot_release_boundary_packet.json",
    "product/monitoring/snapshots/prod7741_7780_internal_threshold_monitoring_snapshot.json",
    "product/release_boundaries/prod7741_7780_release_boundary_packet.json",
    "product/contracts/internal_monitoring_snapshot_release_boundary_packet.contract.json",
    "outputs/prod7701_7740_internal_threshold_lock_smoke_test_regression_guard.json",
    "outputs/prod7661_7700_human_decision_internal_threshold_lock_contract.json",
    "outputs/prod7621_7660_human_review_graph_threshold_lock_proposal.json",
    "outputs/prod7581_7620_calibrated_prompt_multirun_threshold_candidate_capture.json",
    "outputs/prod7541_7580_vector_weight_calibration_prompt_boundary_refinement.json",
    "outputs/prod7501_7540_controlled_multirun_rerun_threshold_lock_eval.json",
    "outputs/prod7461_7500_delta_zero_contextual_scoring_hardening.json",
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
    "threshold_scope_expansion_without_future_human_review",
]

def read_json(path: str | Path, default: Any = None) -> Any:
    p = ROOT / path if isinstance(path, str) else path
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

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
        "phase": "PROD-7781..7820",
        "missing_count": len(missing),
        "missing": missing,
        "will_create": [
            "product/evidence_exports/prod7781_7820_operator_evidence_export.json",
            "product/reviews/operator_packets/prod7781_7820_operator_review_packet.json",
            "product/reviews/operator_packets/prod7781_7820_operator_review_packet.md",
            "outputs/prod7781_7820_evidence_export_operator_review_packet.json",
            "outputs/prod7781_7820_evidence_export_operator_review_packet.md",
            "product/contracts/evidence_export_operator_review_packet.contract.json",
            "docs/product/778_EVIDENCE_EXPORT_OPERATOR_REVIEW_PACKET.md",
        ],
        "will_call_gpt": False,
        "will_dispatch_workflow": False,
        "will_write_external_systems": False,
        "will_activate_production": False,
        "will_allow_client_claim": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def compact_phase(path: str) -> Dict[str, Any]:
    data = read_json(path, {})
    return {
        "path": path,
        "status": data.get("status"),
        "phase": data.get("phase"),
        "decision": data.get("decision"),
        "next": data.get("next"),
    }

def collect_evidence() -> Dict[str, Any]:
    o7741 = read_json("outputs/prod7741_7780_internal_monitoring_snapshot_release_boundary_packet.json", {})
    snap = read_json("product/monitoring/snapshots/prod7741_7780_internal_threshold_monitoring_snapshot.json", {})
    boundary = read_json("product/release_boundaries/prod7741_7780_release_boundary_packet.json", {})
    o7701 = read_json("outputs/prod7701_7740_internal_threshold_lock_smoke_test_regression_guard.json", {})
    o7661 = read_json("outputs/prod7661_7700_human_decision_internal_threshold_lock_contract.json", {})
    o7621 = read_json("outputs/prod7621_7660_human_review_graph_threshold_lock_proposal.json", {})
    o7581 = read_json("outputs/prod7581_7620_calibrated_prompt_multirun_threshold_candidate_capture.json", {})
    o7541 = read_json("outputs/prod7541_7580_vector_weight_calibration_prompt_boundary_refinement.json", {})
    o7501 = read_json("outputs/prod7501_7540_controlled_multirun_rerun_threshold_lock_eval.json", {})
    o7461 = read_json("outputs/prod7461_7500_delta_zero_contextual_scoring_hardening.json", {})

    phases = [
        compact_phase("outputs/prod7461_7500_delta_zero_contextual_scoring_hardening.json"),
        compact_phase("outputs/prod7501_7540_controlled_multirun_rerun_threshold_lock_eval.json"),
        compact_phase("outputs/prod7541_7580_vector_weight_calibration_prompt_boundary_refinement.json"),
        compact_phase("outputs/prod7581_7620_calibrated_prompt_multirun_threshold_candidate_capture.json"),
        compact_phase("outputs/prod7621_7660_human_review_graph_threshold_lock_proposal.json"),
        compact_phase("outputs/prod7661_7700_human_decision_internal_threshold_lock_contract.json"),
        compact_phase("outputs/prod7701_7740_internal_threshold_lock_smoke_test_regression_guard.json"),
        compact_phase("outputs/prod7741_7780_internal_monitoring_snapshot_release_boundary_packet.json"),
    ]

    candidate_metrics = o7581.get("aggregate", {}).get("metrics", {})
    smoke_summary = o7701.get("smoke_test", {}).get("summary", {})
    lock_contract = o7661.get("internal_threshold_lock_contract", {})
    human_record = o7661.get("human_decision_record", {})
    graph = o7621.get("graph_backed_threshold_lock_proposal", {}).get("graph_evidence", {})
    release_scope = boundary.get("release_scope")

    return {
        "case_id": "REAL-CASE-001",
        "export_generated_at": STAMP,
        "evidence_chain": phases,
        "key_metrics": {
            "runs_captured": candidate_metrics.get("runs_captured"),
            "runs_total": candidate_metrics.get("runs_total"),
            "runs_llm_executed": candidate_metrics.get("runs_llm_executed"),
            "all_required_sections_present": candidate_metrics.get("all_required_sections_present"),
            "unsafe_forbidden_claim_count": candidate_metrics.get("unsafe_forbidden_claim_count"),
            "min_oqi_v2": candidate_metrics.get("min_oqi_v2"),
            "max_ohri_v2": candidate_metrics.get("max_ohri_v2"),
            "min_zpi_v2": candidate_metrics.get("min_zpi_v2"),
            "max_delta_estado": candidate_metrics.get("max_delta_estado"),
            "smoke_total_cases": smoke_summary.get("total_cases"),
            "smoke_expectations_passed": smoke_summary.get("expectations_passed"),
            "smoke_all_expectations_passed": smoke_summary.get("all_expectations_passed"),
        },
        "internal_lock": {
            "active": lock_contract.get("active"),
            "scope": lock_contract.get("scope"),
            "approved_by": lock_contract.get("approved_by"),
            "approved_decision": lock_contract.get("approved_decision"),
            "human_reviewer": human_record.get("reviewer"),
            "human_decision": human_record.get("decision"),
            "ready_for_internal_threshold_smoke_test": lock_contract.get("ready_for_internal_threshold_smoke_test"),
        },
        "monitoring_snapshot": {
            "state": snap.get("state"),
            "threshold": snap.get("threshold"),
            "graph_binding": snap.get("graph_binding"),
            "monitoring_signals": snap.get("monitoring_signals"),
        },
        "graph_evidence": {
            "mode": graph.get("graph_evidence_mode"),
            "node_count": graph.get("node_count"),
            "relationship_count": graph.get("relationship_count"),
            "neo4j_live_query_executed": graph.get("neo4j_live_query_executed"),
            "production_write_executed": graph.get("production_write_executed"),
            "graph_path_claim": graph.get("graph_path_claim"),
        },
        "release_boundary": {
            "release_scope": release_scope,
            "allowed": boundary.get("allowed"),
            "blocked": boundary.get("blocked"),
            "explicit_non_claims": boundary.get("explicit_non_claims"),
            "required_before_scope_expansion": boundary.get("required_before_scope_expansion"),
        },
        "source_outputs": {
            "prod7461": o7461.get("decision"),
            "prod7501": o7501.get("decision"),
            "prod7541": o7541.get("decision"),
            "prod7581": o7581.get("decision"),
            "prod7621": o7621.get("decision"),
            "prod7661": o7661.get("decision"),
            "prod7701": o7701.get("decision"),
            "prod7741": o7741.get("decision"),
        },
    }

def evaluate_operator_packet(evidence: Dict[str, Any]) -> Dict[str, Any]:
    metrics = evidence["key_metrics"]
    lock = evidence["internal_lock"]
    boundary = evidence["release_boundary"]
    graph = evidence["graph_evidence"]

    checks = {
        "all_runs_captured": metrics.get("runs_captured") == metrics.get("runs_total") == 4,
        "all_runs_llm_executed": metrics.get("runs_llm_executed") == 4,
        "unsafe_forbidden_claim_zero": metrics.get("unsafe_forbidden_claim_count") == 0,
        "smoke_all_expectations_passed": metrics.get("smoke_all_expectations_passed") is True,
        "internal_lock_active": lock.get("active") is True,
        "internal_scope_only": lock.get("scope") == "INTERNAL_ONLY",
        "release_scope_internal_monitoring_only": boundary.get("release_scope") == "INTERNAL_THRESHOLD_LOCK_MONITORING_ONLY",
        "client_nonclaim": boundary.get("explicit_non_claims", {}).get("client_validated_evidence") is False,
        "production_nonclaim": boundary.get("explicit_non_claims", {}).get("production_ready") is False,
        "commercial_nonclaim": boundary.get("explicit_non_claims", {}).get("commercially_validated") is False,
        "live_neo4j_not_yet_confirmed": graph.get("neo4j_live_query_executed") is False,
        "production_write_not_executed": graph.get("production_write_executed") is False,
    }

    return {
        "checks": checks,
        "operator_review_packet_ready": all(checks.values()),
        "audit_export_ready": all(checks.values()),
        "ready_for_live_graph_retrieval_confirmation_gate": all(checks.values()),
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "human_review_required_for_scope_expansion": True,
    }

def apply() -> List[str]:
    wrote: List[str] = []
    evidence = collect_evidence()
    readiness = evaluate_operator_packet(evidence)

    operator_packet = {
        "version": "operator_review_packet.v0.1",
        "phase": "PROD-7781..7820",
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "review_status": "READY_FOR_OPERATOR_REVIEW" if readiness["operator_review_packet_ready"] else "INCOMPLETE",
        "purpose": "internal audit/operator review of CASULO Delta Zero internal threshold lock evidence",
        "operator_summary": {
            "internal_threshold_lock": "ACTIVE_INTERNAL_ONLY",
            "regression_guard": "ACTIVE",
            "release_scope": evidence["release_boundary"].get("release_scope"),
            "client_claim": "BLOCKED",
            "production": "BLOCKED",
            "commercial_claim": "BLOCKED",
            "live_graph_retrieval": "NOT_YET_CONFIRMED",
        },
        "evidence_export": evidence,
        "review_readiness": readiness,
        "operator_questions": [
            "Does the evidence chain support internal-only threshold monitoring?",
            "Are client, production and commercial claims still blocked?",
            "Should live graph retrieval confirmation be executed next?",
            "Is any additional evidence needed before a future scope reassessment?"
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    result = {
        "status": "PASS" if readiness["operator_review_packet_ready"] else "FAIL",
        "phase": "PROD-7781..7820",
        "decision": (
            "EVIDENCE_EXPORT_OPERATOR_REVIEW_PACKET_READY_INTERNAL_AUDIT_ONLY"
            if readiness["operator_review_packet_ready"] else
            "EVIDENCE_EXPORT_OPERATOR_REVIEW_PACKET_INCOMPLETE"
        ),
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "evidence_export": evidence,
        "operator_review_packet": operator_packet,
        "calibration_decision": {
            "evidence_export_ready": readiness["audit_export_ready"],
            "operator_review_packet_ready": readiness["operator_review_packet_ready"],
            "ready_for_live_graph_retrieval_confirmation_gate": readiness["ready_for_live_graph_retrieval_confirmation_gate"],
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required_for_scope_expansion": True,
        },
        "next": (
            "PROD-7821..7860 - Live Graph Retrieval Confirmation Gate"
            if readiness["ready_for_live_graph_retrieval_confirmation_gate"] else
            "PROD-7821..7860 - Operator Packet Repair"
        ),
    }

    write_json("product/evidence_exports/prod7781_7820_operator_evidence_export.json", evidence, wrote)
    write_json("product/reviews/operator_packets/prod7781_7820_operator_review_packet.json", operator_packet, wrote)
    write_json("outputs/prod7781_7820_evidence_export_operator_review_packet.json", result, wrote)

    md = [
        "# PROD-7781..7820 - Evidence Export and Operator Review Packet",
        "",
        "## Result",
        "",
        f"Status: {result['status']}",
        f"Decision: {result['decision']}",
        "",
        "## Operator summary",
        "",
        "- Internal threshold lock: ACTIVE_INTERNAL_ONLY",
        "- Regression guard: ACTIVE",
        f"- Release scope: {evidence['release_boundary'].get('release_scope')}",
        "- Client claim: BLOCKED",
        "- Production: BLOCKED",
        "- Commercial claim: BLOCKED",
        "- Live graph retrieval: NOT_YET_CONFIRMED",
        "",
        "## Key metrics",
        "",
        f"- Runs captured: {evidence['key_metrics'].get('runs_captured')} / {evidence['key_metrics'].get('runs_total')}",
        f"- LLM executed: {evidence['key_metrics'].get('runs_llm_executed')}",
        f"- Unsafe forbidden claims: {evidence['key_metrics'].get('unsafe_forbidden_claim_count')}",
        f"- Min OQI v2: {evidence['key_metrics'].get('min_oqi_v2')}",
        f"- Max OHRI v2: {evidence['key_metrics'].get('max_ohri_v2')}",
        f"- Min ZPI v2: {evidence['key_metrics'].get('min_zpi_v2')}",
        f"- Max Delta Estado: {evidence['key_metrics'].get('max_delta_estado')}",
        f"- Smoke expectations passed: {evidence['key_metrics'].get('smoke_expectations_passed')} / {evidence['key_metrics'].get('smoke_total_cases')}",
        "",
        "## Next",
        "",
        result["next"],
        "",
    ]
    md_text = "\n".join(md)
    write_text("product/reviews/operator_packets/prod7781_7820_operator_review_packet.md", md_text, wrote)
    write_text("outputs/prod7781_7820_evidence_export_operator_review_packet.md", md_text, wrote)

    contract = {
        "contract": "evidence_export_operator_review_packet.contract.v0.1",
        "phase": "PROD-7781..7820",
        "requires": REQUIRED,
        "evidence_export_ready": readiness["audit_export_ready"],
        "operator_review_packet_ready": readiness["operator_review_packet_ready"],
        "ready_for_live_graph_retrieval_confirmation_gate": readiness["ready_for_live_graph_retrieval_confirmation_gate"],
        "client_claim_allowed": False,
        "production_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/evidence_export_operator_review_packet.contract.json", contract, wrote)

    docs = """# 778 - Evidence Export and Operator Review Packet

This phase exports the internal evidence chain for operator/audit review.

It summarizes:
- contextual Delta Zero hardening;
- calibrated vector scoring;
- strict threshold candidate;
- human decision;
- internal threshold lock;
- smoke test and regression guard;
- monitoring snapshot and release boundary.

This packet is internal/audit-only.

It does not allow client-facing claims, production activation or commercial claims.
"""
    write_text("docs/product/778_EVIDENCE_EXPORT_OPERATOR_REVIEW_PACKET.md", docs, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod7781_7820_evidence_export_operator_review_packet.py",
        "product/evidence_exports/prod7781_7820_operator_evidence_export.json",
        "product/reviews/operator_packets/prod7781_7820_operator_review_packet.json",
        "product/reviews/operator_packets/prod7781_7820_operator_review_packet.md",
        "outputs/prod7781_7820_evidence_export_operator_review_packet.json",
        "outputs/prod7781_7820_evidence_export_operator_review_packet.md",
        "product/contracts/evidence_export_operator_review_packet.contract.json",
        "docs/product/778_EVIDENCE_EXPORT_OPERATOR_REVIEW_PACKET.md",
    ]
    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Add evidence export and operator review packet"',
        'git tag -a product-casulo-evidence-export-operator-review-v0.1 HEAD -m "CASULO evidence export operator review v0.1"',
        "git push origin main",
        "git push origin product-casulo-evidence-export-operator-review-v0.1",
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

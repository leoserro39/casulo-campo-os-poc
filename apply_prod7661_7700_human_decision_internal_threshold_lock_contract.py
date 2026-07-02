#!/usr/bin/env python3
"""
CASULO PROD-7661..7700 - Human Decision Record and Internal Threshold Lock Contract

Continues after:
  PROD-7621..7660 - Human Review Packet and Graph-Backed Threshold Lock Proposal

Purpose:
  - record the human decision over the internal-only threshold proposal;
  - if approved, create the internal threshold lock contract;
  - keep client-facing claims, production activation and commercial claims blocked.

This patcher does NOT:
  - call GPT;
  - dispatch GitHub Actions;
  - comment on GitHub issues/PRs;
  - write to production Neo4j;
  - activate production;
  - allow client/production/commercial claims.

Usage:
  python3 apply_prod7661_7700_human_decision_internal_threshold_lock_contract.py --check

  python3 apply_prod7661_7700_human_decision_internal_threshold_lock_contract.py \
    --apply \
    --decision APPROVE_THRESHOLD_LOCK_INTERNAL_ONLY \
    --reviewer "Leonardo Serro" \
    --commit-plan
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()

ALLOWED_DECISIONS = [
    "APPROVE_THRESHOLD_LOCK_INTERNAL_ONLY",
    "REQUEST_MORE_EVIDENCE",
    "REJECT_THRESHOLD_LOCK",
]

SOURCE_OUTPUT = "outputs/prod7621_7660_human_review_graph_threshold_lock_proposal.json"

REQUIRED = [
    SOURCE_OUTPUT,
    "product/reviews/human_review_packets/prod7621_7660_human_review_packet.json",
    "product/reviews/human_review_packets/prod7621_7660_human_review_packet.md",
    "product/calibration/thresholds/prod7621_7660_graph_backed_threshold_lock_proposal.json",
    "product/contracts/human_review_graph_threshold_lock_proposal.contract.json",
    "outputs/prod7581_7620_calibrated_prompt_multirun_threshold_candidate_capture.json",
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
        "phase": "PROD-7661..7700",
        "missing_count": len(missing),
        "missing": missing,
        "allowed_decisions": ALLOWED_DECISIONS,
        "will_create": [
            "product/reviews/human_decisions/prod7661_7700_human_decision_record.json",
            "product/calibration/thresholds/prod7661_7700_internal_threshold_lock_contract.json",
            "outputs/prod7661_7700_human_decision_internal_threshold_lock_contract.json",
            "outputs/prod7661_7700_human_decision_internal_threshold_lock_contract.md",
            "product/contracts/internal_threshold_lock_contract.contract.json",
            "docs/product/766_HUMAN_DECISION_INTERNAL_THRESHOLD_LOCK_CONTRACT.md",
        ],
        "will_call_gpt": False,
        "will_dispatch_workflow": False,
        "will_write_external_systems": False,
        "will_activate_production": False,
        "will_allow_client_claim": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def proposal_summary() -> Dict[str, Any]:
    proposal_output = read_json(SOURCE_OUTPUT, {})
    packet = read_json("product/reviews/human_review_packets/prod7621_7660_human_review_packet.json", {})
    threshold = proposal_output.get("graph_backed_threshold_lock_proposal", {})
    readiness = threshold.get("review_readiness", {})
    src = threshold.get("source_evidence", {})
    graph = threshold.get("graph_evidence", {})

    return {
        "source_phase": proposal_output.get("phase"),
        "source_decision": proposal_output.get("decision"),
        "review_status": packet.get("review_status"),
        "recommended_decision": packet.get("recommended_decision"),
        "proposal_status": threshold.get("proposal_status"),
        "proposal_type": threshold.get("proposal_type"),
        "review_packet_ready": proposal_output.get("calibration_decision", {}).get("human_review_packet_ready"),
        "graph_backed_threshold_lock_proposal_ready": proposal_output.get("calibration_decision", {}).get("graph_backed_threshold_lock_proposal_ready"),
        "ready_for_human_decision_record": proposal_output.get("calibration_decision", {}).get("ready_for_human_decision_record"),
        "source_evidence": src,
        "graph_evidence": graph,
        "review_readiness": readiness,
        "proposed_threshold": threshold.get("proposed_threshold", {
            "min_oqi_v2": 0.85,
            "max_ohri_v2": 0.15,
            "min_zpi_v2": 0.90,
            "max_delta_estado": 0.12,
            "unsafe_forbidden_claim_hits": 0,
            "required_gate": "HUMAN_REVIEW_REQUIRED",
        }),
    }

def evaluate_decision(decision: str, summary: Dict[str, Any]) -> Dict[str, Any]:
    proposal_ready = (
        summary.get("review_packet_ready") is True and
        summary.get("graph_backed_threshold_lock_proposal_ready") is True and
        summary.get("ready_for_human_decision_record") is True
    )

    if decision == "APPROVE_THRESHOLD_LOCK_INTERNAL_ONLY":
        internal_lock_active = proposal_ready
        decision_status = "APPROVED_INTERNAL_ONLY" if proposal_ready else "APPROVAL_BLOCKED_MORE_EVIDENCE_REQUIRED"
        next_step = "PROD-7701..7740 - Internal Threshold Lock Smoke Test and Regression Guard"
    elif decision == "REQUEST_MORE_EVIDENCE":
        internal_lock_active = False
        decision_status = "MORE_EVIDENCE_REQUESTED"
        next_step = "PROD-7701..7740 - Evidence Gap Follow-up and Review Repacket"
    else:
        internal_lock_active = False
        decision_status = "THRESHOLD_LOCK_REJECTED"
        next_step = "PROD-7701..7740 - Rejection Review and Calibration Backlog"

    return {
        "proposal_ready": proposal_ready,
        "decision_status": decision_status,
        "internal_threshold_lock_active": internal_lock_active,
        "next": next_step,
        "ready_for_internal_threshold_smoke_test": internal_lock_active,
        "client_claim_allowed": False,
        "production_allowed": False,
        "commercial_claim_allowed": False,
    }

def apply(decision: str, reviewer: str, note: str) -> List[str]:
    if decision not in ALLOWED_DECISIONS:
        raise SystemExit(f"INVALID_DECISION: {decision}. Allowed: {', '.join(ALLOWED_DECISIONS)}")

    wrote: List[str] = []
    summary = proposal_summary()
    decision_eval = evaluate_decision(decision, summary)

    human_record = {
        "version": "human_decision_record.v0.1",
        "phase": "PROD-7661..7700",
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "reviewer": reviewer,
        "decision": decision,
        "decision_status": decision_eval["decision_status"],
        "note": note,
        "source_review_packet": "product/reviews/human_review_packets/prod7621_7660_human_review_packet.json",
        "source_threshold_proposal": "product/calibration/thresholds/prod7621_7660_graph_backed_threshold_lock_proposal.json",
        "proposal_summary": summary,
        "decision_boundary": {
            "internal_threshold_lock_active": decision_eval["internal_threshold_lock_active"],
            "threshold_lock_scope": "INTERNAL_ONLY" if decision_eval["internal_threshold_lock_active"] else "NOT_ACTIVE",
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
            "validated_hallucination_reduction_claim_allowed": False,
            "requires_future_human_review_for_scope_expansion": True,
        },
        "blocked_actions": BLOCKED_ACTIONS,
    }

    lock_contract = {
        "contract": "internal_threshold_lock_contract.v0.1",
        "phase": "PROD-7661..7700",
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "active": decision_eval["internal_threshold_lock_active"],
        "scope": "INTERNAL_ONLY" if decision_eval["internal_threshold_lock_active"] else "NOT_ACTIVE",
        "decision_record": "product/reviews/human_decisions/prod7661_7700_human_decision_record.json",
        "approved_by": reviewer if decision_eval["internal_threshold_lock_active"] else None,
        "approved_decision": decision if decision_eval["internal_threshold_lock_active"] else None,
        "threshold": summary.get("proposed_threshold"),
        "evidence_requirements": {
            "calibrated_prompt_multirun_capture_required": True,
            "contextual_delta_zero_required": True,
            "vector_v2_calibrated_required": True,
            "graph_payload_binding_required": True,
            "human_decision_record_required": True,
        },
        "guardrails": {
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
            "automatic_merge_allowed": False,
            "production_neo4j_write_allowed": False,
            "external_side_effect_allowed": False,
        },
        "ready_for_internal_threshold_smoke_test": decision_eval["ready_for_internal_threshold_smoke_test"],
    }

    result = {
        "status": "PASS",
        "phase": "PROD-7661..7700",
        "decision": (
            "HUMAN_DECISION_APPROVED_INTERNAL_THRESHOLD_LOCK_CONTRACT_CREATED"
            if decision_eval["internal_threshold_lock_active"]
            else decision_eval["decision_status"]
        ),
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "human_decision_record": human_record,
        "internal_threshold_lock_contract": lock_contract,
        "calibration_decision": {
            "human_decision_recorded": True,
            "internal_threshold_lock_active": decision_eval["internal_threshold_lock_active"],
            "ready_for_internal_threshold_smoke_test": decision_eval["ready_for_internal_threshold_smoke_test"],
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required_for_scope_expansion": True,
        },
        "next": decision_eval["next"],
    }

    write_json("product/reviews/human_decisions/prod7661_7700_human_decision_record.json", human_record, wrote)
    write_json("product/calibration/thresholds/prod7661_7700_internal_threshold_lock_contract.json", lock_contract, wrote)
    write_json("outputs/prod7661_7700_human_decision_internal_threshold_lock_contract.json", result, wrote)

    md = [
        "# PROD-7661..7700 - Human Decision Record and Internal Threshold Lock Contract",
        "",
        "## Result",
        "",
        f"Status: {result['status']}",
        f"Decision: {result['decision']}",
        "",
        "## Human decision",
        "",
        f"- Reviewer: {reviewer}",
        f"- Decision: {decision}",
        f"- Decision status: {decision_eval['decision_status']}",
        f"- Internal threshold lock active: {decision_eval['internal_threshold_lock_active']}",
        "",
        "## Boundary",
        "",
        "- Scope: INTERNAL_ONLY" if decision_eval["internal_threshold_lock_active"] else "- Scope: NOT_ACTIVE",
        "- Client claim allowed: False",
        "- Production allowed: False",
        "- Commercial claim allowed: False",
        "- Scope expansion requires future human review: True",
        "",
        "## Next",
        "",
        decision_eval["next"],
        "",
    ]
    write_text("outputs/prod7661_7700_human_decision_internal_threshold_lock_contract.md", "\n".join(md), wrote)

    contract = {
        "contract": "human_decision_internal_threshold_lock_contract.contract.v0.1",
        "phase": "PROD-7661..7700",
        "requires": REQUIRED,
        "allowed_decisions": ALLOWED_DECISIONS,
        "decision_record_required": True,
        "decision_recorded": True,
        "internal_threshold_lock_active": decision_eval["internal_threshold_lock_active"],
        "threshold_lock_scope": "INTERNAL_ONLY" if decision_eval["internal_threshold_lock_active"] else "NOT_ACTIVE",
        "client_claim_allowed": False,
        "production_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/internal_threshold_lock_contract.contract.json", contract, wrote)

    docs = """# 766 - Human Decision Record and Internal Threshold Lock Contract

This phase records a human decision over the graph-backed threshold proposal.

Possible decisions:
- APPROVE_THRESHOLD_LOCK_INTERNAL_ONLY
- REQUEST_MORE_EVIDENCE
- REJECT_THRESHOLD_LOCK

Approval creates an internal-only threshold lock contract.

This does not allow:
- client-facing validation claims;
- production activation;
- commercial claims;
- validated hallucination reduction claims;
- production Neo4j writes.
"""
    write_text("docs/product/766_HUMAN_DECISION_INTERNAL_THRESHOLD_LOCK_CONTRACT.md", docs, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod7661_7700_human_decision_internal_threshold_lock_contract.py",
        "product/reviews/human_decisions/prod7661_7700_human_decision_record.json",
        "product/calibration/thresholds/prod7661_7700_internal_threshold_lock_contract.json",
        "outputs/prod7661_7700_human_decision_internal_threshold_lock_contract.json",
        "outputs/prod7661_7700_human_decision_internal_threshold_lock_contract.md",
        "product/contracts/internal_threshold_lock_contract.contract.json",
        "docs/product/766_HUMAN_DECISION_INTERNAL_THRESHOLD_LOCK_CONTRACT.md",
    ]
    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Record human decision and create internal threshold lock contract"',
        'git tag -a product-casulo-human-decision-internal-threshold-lock-v0.1 HEAD -m "CASULO human decision internal threshold lock v0.1"',
        "git push origin main",
        "git push origin product-casulo-human-decision-internal-threshold-lock-v0.1",
    ])

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--commit-plan", action="store_true")
    ap.add_argument("--decision", choices=ALLOWED_DECISIONS)
    ap.add_argument("--reviewer", default="Leonardo Serro")
    ap.add_argument("--note", default="Human reviewer approved internal-only threshold lock based on committed evidence packet.")
    args = ap.parse_args()

    if not any([args.check, args.apply, args.commit_plan]):
        args.check = True

    if args.check:
        print(json.dumps(check(), indent=2, ensure_ascii=False))

    if args.apply:
        c = check()
        if c["status"] != "PASS":
            print(json.dumps(c, indent=2, ensure_ascii=False))
            raise SystemExit("CHECK_FAILED")
        if not args.decision:
            raise SystemExit("DECISION_REQUIRED: pass --decision APPROVE_THRESHOLD_LOCK_INTERNAL_ONLY, REQUEST_MORE_EVIDENCE, or REJECT_THRESHOLD_LOCK")
        wrote = apply(args.decision, args.reviewer, args.note)
        print(json.dumps({"applied": True, "wrote_count": len(wrote), "wrote": wrote}, indent=2, ensure_ascii=False))

    if args.commit_plan:
        print(commit_plan())

    return 0

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
CASULO PROD-7861..7900 - Client/Production Claim Boundary Reassessment

Continues after:
  PROD-7821..7860 - Live Graph Retrieval Confirmation Gate

Purpose:
  - reassess client/production/commercial claim boundary after the live graph retrieval gate;
  - explicitly separate what can be stated internally from what remains blocked externally;
  - keep client-facing claims, production activation and commercial claims blocked when live retrieval is not confirmed.

This patcher does NOT:
  - call GPT;
  - dispatch GitHub Actions;
  - comment on GitHub issues/PRs;
  - write to production Neo4j;
  - activate production;
  - allow client/production/commercial claims.

Usage:
  python3 apply_prod7861_7900_client_production_claim_boundary_reassessment.py --check
  python3 apply_prod7861_7900_client_production_claim_boundary_reassessment.py --apply --commit-plan
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
    "outputs/prod7821_7860_live_graph_retrieval_confirmation_gate.json",
    "product/graph/retrieval_gates/prod7821_7860_live_graph_retrieval_confirmation_gate.json",
    "product/contracts/live_graph_retrieval_confirmation_gate.contract.json",
    "outputs/prod7781_7820_evidence_export_operator_review_packet.json",
    "outputs/prod7741_7780_internal_monitoring_snapshot_release_boundary_packet.json",
    "outputs/prod7701_7740_internal_threshold_lock_smoke_test_regression_guard.json",
    "outputs/prod7661_7700_human_decision_internal_threshold_lock_contract.json",
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
        "phase": "PROD-7861..7900",
        "missing_count": len(missing),
        "missing": missing,
        "will_create": [
            "product/claim_boundaries/prod7861_7900_client_production_claim_boundary_reassessment.json",
            "product/release_boundaries/prod7861_7900_client_production_release_boundary.json",
            "outputs/prod7861_7900_client_production_claim_boundary_reassessment.json",
            "outputs/prod7861_7900_client_production_claim_boundary_reassessment.md",
            "product/contracts/client_production_claim_boundary_reassessment.contract.json",
            "docs/product/786_CLIENT_PRODUCTION_CLAIM_BOUNDARY_REASSESSMENT.md",
        ],
        "will_call_gpt": False,
        "will_dispatch_workflow": False,
        "will_write_external_systems": False,
        "will_activate_production": False,
        "will_allow_client_claim": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def evaluate_claims() -> Dict[str, Any]:
    live_gate = read_json("outputs/prod7821_7860_live_graph_retrieval_confirmation_gate.json", {})
    operator = read_json("outputs/prod7781_7820_evidence_export_operator_review_packet.json", {})
    snapshot = read_json("outputs/prod7741_7780_internal_monitoring_snapshot_release_boundary_packet.json", {})
    smoke = read_json("outputs/prod7701_7740_internal_threshold_lock_smoke_test_regression_guard.json", {})
    lock = read_json("outputs/prod7661_7700_human_decision_internal_threshold_lock_contract.json", {})

    live_decision = live_gate.get("calibration_decision", {})
    operator_decision = operator.get("calibration_decision", {})
    snapshot_decision = snapshot.get("calibration_decision", {})
    smoke_decision = smoke.get("calibration_decision", {})
    lock_decision = lock.get("calibration_decision", {})

    internal_basis = {
        "internal_threshold_lock_active": lock_decision.get("internal_threshold_lock_active") is True,
        "regression_guard_active": smoke_decision.get("regression_guard_active") is True,
        "internal_threshold_smoke_test_pass": smoke_decision.get("internal_threshold_lock_smoke_test_pass") is True,
        "monitoring_snapshot_ready": snapshot_decision.get("internal_threshold_monitoring_snapshot_ready") is True,
        "operator_review_packet_ready": operator_decision.get("operator_review_packet_ready") is True,
        "offline_graph_payload_complete": live_decision.get("offline_graph_payload_complete") is True,
        "live_graph_retrieval_gate_executed": live_decision.get("live_graph_retrieval_confirmation_gate_executed") is True,
        "live_graph_retrieval_confirmed": live_decision.get("live_graph_retrieval_confirmed") is True,
    }

    external_claim_conditions = {
        "requires_internal_lock": internal_basis["internal_threshold_lock_active"],
        "requires_regression_guard": internal_basis["regression_guard_active"],
        "requires_operator_packet": internal_basis["operator_review_packet_ready"],
        "requires_live_graph_retrieval_confirmed": internal_basis["live_graph_retrieval_confirmed"],
        "requires_future_human_review": True,
        "requires_explicit_release_boundary_reassessment": True,
    }

    external_claim_allowed = (
        external_claim_conditions["requires_internal_lock"] and
        external_claim_conditions["requires_regression_guard"] and
        external_claim_conditions["requires_operator_packet"] and
        external_claim_conditions["requires_live_graph_retrieval_confirmed"] and
        False  # Explicit future release review remains required even if live retrieval is later confirmed.
    )

    return {
        "internal_basis": internal_basis,
        "external_claim_conditions": external_claim_conditions,
        "allowed_internal_statements": [
            "Internal threshold lock is active for REAL-CASE-001.",
            "Regression guard is active.",
            "Internal smoke test passed.",
            "Operator evidence packet is ready for internal audit.",
            "Offline committed graph payload is complete.",
            "Live graph retrieval gate was executed.",
            "Live graph retrieval is not confirmed unless a valid live evidence file is committed."
        ],
        "blocked_external_claims": [
            "client validated evidence",
            "production readiness",
            "commercial validation",
            "validated hallucination reduction",
            "validated model gain",
            "live Neo4j retrieval confirmation as a public/client claim",
        ],
        "client_claim_allowed": external_claim_allowed,
        "production_allowed": False,
        "commercial_claim_allowed": False,
        "validated_hallucination_reduction_claim_allowed": False,
        "validated_model_gain_claim_allowed": False,
        "ready_for_scope_expansion": False,
        "ready_for_live_graph_evidence_followup": True,
        "reason": (
            "Live graph retrieval was confirmed, but external scope expansion still requires future human review and release boundary reassessment."
            if internal_basis["live_graph_retrieval_confirmed"]
            else
            "Live graph retrieval is not confirmed; external client, production and commercial claims remain blocked."
        )
    }

def apply() -> List[str]:
    wrote: List[str] = []
    assessment = evaluate_claims()

    claim_boundary = {
        "version": "client_production_claim_boundary_reassessment.v0.1",
        "phase": "PROD-7861..7900",
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "assessment": assessment,
        "decision_matrix": {
            "internal_status_reporting": {
                "allowed": True,
                "scope": "INTERNAL_ONLY",
                "statements": assessment["allowed_internal_statements"],
            },
            "client_facing_claims": {
                "allowed": False,
                "reason": assessment["reason"],
            },
            "production_activation": {
                "allowed": False,
                "reason": "Production activation was not tested or authorized in this sequence.",
            },
            "commercial_claims": {
                "allowed": False,
                "reason": "Commercial validation is outside this evidence packet.",
            },
            "validated_hallucination_reduction": {
                "allowed": False,
                "reason": "This sequence calibrates internal Delta Zero boundaries; it does not validate public hallucination reduction claims.",
            },
        },
        "blocked_actions": BLOCKED_ACTIONS,
    }

    release_boundary = {
        "version": "client_production_release_boundary.v0.1",
        "phase": "PROD-7861..7900",
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "release_scope": "INTERNAL_ONLY_CONTINUE_LIVE_GRAPH_EVIDENCE_FOLLOWUP",
        "allowed": [
            "internal status reporting",
            "internal audit review",
            "live graph evidence follow-up",
            "controlled sandbox/read-only graph retrieval evidence capture",
            "future claim boundary reassessment after new evidence",
        ],
        "blocked": BLOCKED_ACTIONS,
        "requires_before_any_external_claim": [
            "live graph retrieval confirmation evidence",
            "future human review",
            "new release boundary reassessment",
            "explicit approval for client-facing scope",
            "explicit approval for production scope if production is ever considered",
        ],
    }

    result = {
        "status": "PASS",
        "phase": "PROD-7861..7900",
        "decision": "CLAIM_BOUNDARY_REASSESSED_CLIENT_PRODUCTION_REMAIN_BLOCKED_LIVE_GRAPH_NOT_CONFIRMED",
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "claim_boundary_reassessment": claim_boundary,
        "release_boundary": release_boundary,
        "calibration_decision": {
            "claim_boundary_reassessment_complete": True,
            "internal_status_reporting_allowed": True,
            "ready_for_live_graph_evidence_followup": True,
            "ready_for_scope_expansion": False,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "commercial_claim_allowed": False,
            "human_review_required_for_scope_expansion": True,
        },
        "next": "PROD-7901..7940 - Live Graph Evidence Follow-up and Controlled Sandbox Retrieval Run",
    }

    write_json("product/claim_boundaries/prod7861_7900_client_production_claim_boundary_reassessment.json", claim_boundary, wrote)
    write_json("product/release_boundaries/prod7861_7900_client_production_release_boundary.json", release_boundary, wrote)
    write_json("outputs/prod7861_7900_client_production_claim_boundary_reassessment.json", result, wrote)

    md = [
        "# PROD-7861..7900 - Client/Production Claim Boundary Reassessment",
        "",
        "## Result",
        "",
        f"Status: {result['status']}",
        f"Decision: {result['decision']}",
        "",
        "## Internal allowed",
        "",
        "- Internal status reporting: True",
        "- Internal threshold lock active: " + str(assessment["internal_basis"]["internal_threshold_lock_active"]),
        "- Regression guard active: " + str(assessment["internal_basis"]["regression_guard_active"]),
        "- Operator review packet ready: " + str(assessment["internal_basis"]["operator_review_packet_ready"]),
        "- Offline graph payload complete: " + str(assessment["internal_basis"]["offline_graph_payload_complete"]),
        "- Live graph retrieval gate executed: " + str(assessment["internal_basis"]["live_graph_retrieval_gate_executed"]),
        "- Live graph retrieval confirmed: " + str(assessment["internal_basis"]["live_graph_retrieval_confirmed"]),
        "",
        "## External blocked",
        "",
        "- Client claim allowed: False",
        "- Production allowed: False",
        "- Commercial claim allowed: False",
        "- Validated hallucination reduction claim allowed: False",
        "- Scope expansion requires future human review: True",
        "",
        "## Next",
        "",
        result["next"],
        "",
    ]
    write_text("outputs/prod7861_7900_client_production_claim_boundary_reassessment.md", "\n".join(md), wrote)

    contract = {
        "contract": "client_production_claim_boundary_reassessment.contract.v0.1",
        "phase": "PROD-7861..7900",
        "requires": REQUIRED,
        "claim_boundary_reassessment_complete": True,
        "internal_status_reporting_allowed": True,
        "ready_for_live_graph_evidence_followup": True,
        "ready_for_scope_expansion": False,
        "client_claim_allowed": False,
        "production_allowed": False,
        "commercial_claim_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/client_production_claim_boundary_reassessment.contract.json", contract, wrote)

    docs = """# 786 - Client/Production Claim Boundary Reassessment

This phase reassesses the claim boundary after the live graph retrieval gate.

Because live graph retrieval is not confirmed, client-facing claims, production activation and commercial claims remain blocked.

Allowed:
- internal status reporting;
- internal audit review;
- controlled live graph evidence follow-up;
- future reassessment after new evidence.

Blocked:
- client-facing validation claims;
- production activation;
- commercial claims;
- validated hallucination reduction claims;
- production Neo4j writes.
"""
    write_text("docs/product/786_CLIENT_PRODUCTION_CLAIM_BOUNDARY_REASSESSMENT.md", docs, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod7861_7900_client_production_claim_boundary_reassessment.py",
        "product/claim_boundaries/prod7861_7900_client_production_claim_boundary_reassessment.json",
        "product/release_boundaries/prod7861_7900_client_production_release_boundary.json",
        "outputs/prod7861_7900_client_production_claim_boundary_reassessment.json",
        "outputs/prod7861_7900_client_production_claim_boundary_reassessment.md",
        "product/contracts/client_production_claim_boundary_reassessment.contract.json",
        "docs/product/786_CLIENT_PRODUCTION_CLAIM_BOUNDARY_REASSESSMENT.md",
    ]
    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Reassess client and production claim boundary"',
        'git tag -a product-casulo-client-production-claim-boundary-reassessment-v0.1 HEAD -m "CASULO client production claim boundary reassessment v0.1"',
        "git push origin main",
        "git push origin product-casulo-client-production-claim-boundary-reassessment-v0.1",
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

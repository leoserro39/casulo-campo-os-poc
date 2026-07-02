#!/usr/bin/env python3
"""
CASULO PROD-7741..7780 - Internal Threshold Monitoring Snapshot and Release Boundary Packet

Continues after:
  PROD-7701..7740 - Internal Threshold Lock Smoke Test and Regression Guard

Purpose:
  - create an internal monitoring snapshot after the regression guard is active;
  - create a release boundary packet that states exactly what is allowed and blocked;
  - prepare the operator/evidence export phase.

This patcher does NOT:
  - call GPT;
  - dispatch GitHub Actions;
  - comment on GitHub issues/PRs;
  - write to production Neo4j;
  - activate production;
  - allow client/production/commercial claims.

Usage:
  python3 apply_prod7741_7780_internal_monitoring_snapshot_release_boundary_packet.py --check
  python3 apply_prod7741_7780_internal_monitoring_snapshot_release_boundary_packet.py --apply --commit-plan
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
    "outputs/prod7701_7740_internal_threshold_lock_smoke_test_regression_guard.json",
    "product/calibration/smoke_tests/prod7701_7740_internal_threshold_lock_smoke_test.json",
    "product/calibration/regression_guards/prod7701_7740_threshold_regression_guard.json",
    "product/contracts/internal_threshold_lock_smoke_test_regression_guard.contract.json",
    "outputs/prod7661_7700_human_decision_internal_threshold_lock_contract.json",
    "outputs/prod7621_7660_human_review_graph_threshold_lock_proposal.json",
    "outputs/prod7581_7620_calibrated_prompt_multirun_threshold_candidate_capture.json",
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
        "phase": "PROD-7741..7780",
        "missing_count": len(missing),
        "missing": missing,
        "will_create": [
            "product/monitoring/snapshots/prod7741_7780_internal_threshold_monitoring_snapshot.json",
            "product/release_boundaries/prod7741_7780_release_boundary_packet.json",
            "outputs/prod7741_7780_internal_monitoring_snapshot_release_boundary_packet.json",
            "outputs/prod7741_7780_internal_monitoring_snapshot_release_boundary_packet.md",
            "product/contracts/internal_monitoring_snapshot_release_boundary_packet.contract.json",
            "docs/product/774_INTERNAL_MONITORING_SNAPSHOT_RELEASE_BOUNDARY_PACKET.md",
        ],
        "will_call_gpt": False,
        "will_dispatch_workflow": False,
        "will_write_external_systems": False,
        "will_activate_production": False,
        "will_allow_client_claim": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def apply() -> List[str]:
    wrote: List[str] = []
    smoke = read_json("outputs/prod7701_7740_internal_threshold_lock_smoke_test_regression_guard.json", {})
    lock = read_json("outputs/prod7661_7700_human_decision_internal_threshold_lock_contract.json", {})
    proposal = read_json("outputs/prod7621_7660_human_review_graph_threshold_lock_proposal.json", {})
    candidate = read_json("outputs/prod7581_7620_calibrated_prompt_multirun_threshold_candidate_capture.json", {})

    smoke_decision = smoke.get("calibration_decision", {})
    lock_decision = lock.get("calibration_decision", {})
    candidate_metrics = candidate.get("aggregate", {}).get("metrics", {})
    graph_proposal = proposal.get("graph_backed_threshold_lock_proposal", {})

    monitoring_snapshot = {
        "version": "internal_threshold_monitoring_snapshot.v0.1",
        "phase": "PROD-7741..7780",
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "state": {
            "internal_threshold_lock_active": lock_decision.get("internal_threshold_lock_active") is True,
            "regression_guard_active": smoke_decision.get("regression_guard_active") is True,
            "internal_threshold_lock_smoke_test_pass": smoke_decision.get("internal_threshold_lock_smoke_test_pass") is True,
            "ready_for_internal_monitoring_snapshot": smoke_decision.get("ready_for_internal_monitoring_snapshot") is True,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required_for_scope_expansion": True,
        },
        "threshold": smoke.get("regression_guard", {}).get("guarded_threshold", {}),
        "latest_candidate_metrics": {
            "runs_captured": candidate_metrics.get("runs_captured"),
            "runs_total": candidate_metrics.get("runs_total"),
            "runs_llm_executed": candidate_metrics.get("runs_llm_executed"),
            "all_required_sections_present": candidate_metrics.get("all_required_sections_present"),
            "unsafe_forbidden_claim_count": candidate_metrics.get("unsafe_forbidden_claim_count"),
            "min_oqi_v2": candidate_metrics.get("min_oqi_v2"),
            "max_ohri_v2": candidate_metrics.get("max_ohri_v2"),
            "min_zpi_v2": candidate_metrics.get("min_zpi_v2"),
            "max_delta_estado": candidate_metrics.get("max_delta_estado"),
        },
        "graph_binding": {
            "mode": graph_proposal.get("graph_evidence", {}).get("graph_evidence_mode"),
            "node_count": graph_proposal.get("graph_evidence", {}).get("node_count"),
            "relationship_count": graph_proposal.get("graph_evidence", {}).get("relationship_count"),
            "neo4j_live_query_executed": graph_proposal.get("graph_evidence", {}).get("neo4j_live_query_executed"),
            "production_write_executed": graph_proposal.get("graph_evidence", {}).get("production_write_executed"),
        },
        "monitoring_signals": [
            "threshold contract remains internal-only",
            "regression guard remains active",
            "client claim remains blocked",
            "production activation remains blocked",
            "scope expansion requires future human review",
        ],
    }

    release_boundary = {
        "version": "release_boundary_packet.v0.1",
        "phase": "PROD-7741..7780",
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "release_scope": "INTERNAL_THRESHOLD_LOCK_MONITORING_ONLY",
        "allowed": [
            "internal threshold smoke/regression monitoring",
            "operator review packet generation",
            "evidence export for internal audit",
            "live graph retrieval confirmation planning",
        ],
        "blocked": BLOCKED_ACTIONS,
        "explicit_non_claims": {
            "client_validated_evidence": False,
            "production_ready": False,
            "commercially_validated": False,
            "validated_hallucination_reduction": False,
            "live_neo4j_retrieval_confirmed": False,
        },
        "required_before_scope_expansion": [
            "future human review",
            "live graph retrieval confirmation",
            "new evidence packet",
            "explicit release boundary reassessment",
        ],
    }

    ready = (
        monitoring_snapshot["state"]["internal_threshold_lock_active"] and
        monitoring_snapshot["state"]["regression_guard_active"] and
        monitoring_snapshot["state"]["internal_threshold_lock_smoke_test_pass"]
    )

    result = {
        "status": "PASS" if ready else "FAIL",
        "phase": "PROD-7741..7780",
        "decision": (
            "INTERNAL_THRESHOLD_MONITORING_SNAPSHOT_READY_RELEASE_BOUNDARY_PACKET_CREATED"
            if ready else
            "INTERNAL_THRESHOLD_MONITORING_SNAPSHOT_NOT_READY_REVIEW_REQUIRED"
        ),
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "monitoring_snapshot": monitoring_snapshot,
        "release_boundary_packet": release_boundary,
        "calibration_decision": {
            "internal_threshold_monitoring_snapshot_ready": ready,
            "release_boundary_packet_created": ready,
            "ready_for_operator_evidence_export_packet": ready,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required_for_scope_expansion": True,
        },
        "next": (
            "PROD-7781..7820 - Evidence Export and Operator Review Packet"
            if ready else
            "PROD-7781..7820 - Monitoring Snapshot Repair"
        ),
    }

    write_json("product/monitoring/snapshots/prod7741_7780_internal_threshold_monitoring_snapshot.json", monitoring_snapshot, wrote)
    write_json("product/release_boundaries/prod7741_7780_release_boundary_packet.json", release_boundary, wrote)
    write_json("outputs/prod7741_7780_internal_monitoring_snapshot_release_boundary_packet.json", result, wrote)

    md = [
        "# PROD-7741..7780 - Internal Monitoring Snapshot and Release Boundary Packet",
        "",
        "## Result",
        "",
        f"Status: {result['status']}",
        f"Decision: {result['decision']}",
        "",
        "## State",
        "",
        f"- Internal threshold lock active: {monitoring_snapshot['state']['internal_threshold_lock_active']}",
        f"- Regression guard active: {monitoring_snapshot['state']['regression_guard_active']}",
        f"- Smoke test pass: {monitoring_snapshot['state']['internal_threshold_lock_smoke_test_pass']}",
        f"- Ready for operator evidence export: {result['calibration_decision']['ready_for_operator_evidence_export_packet']}",
        "",
        "## Boundary",
        "",
        "- Release scope: INTERNAL_THRESHOLD_LOCK_MONITORING_ONLY",
        "- Client claim allowed: False",
        "- Production allowed: False",
        "- Commercial claim allowed: False",
        "- Scope expansion requires future human review: True",
        "",
        "## Next",
        "",
        result["next"],
        "",
    ]
    write_text("outputs/prod7741_7780_internal_monitoring_snapshot_release_boundary_packet.md", "\n".join(md), wrote)

    contract = {
        "contract": "internal_monitoring_snapshot_release_boundary_packet.contract.v0.1",
        "phase": "PROD-7741..7780",
        "requires": REQUIRED,
        "internal_threshold_monitoring_snapshot_ready": ready,
        "release_boundary_packet_created": ready,
        "release_scope": "INTERNAL_THRESHOLD_LOCK_MONITORING_ONLY",
        "client_claim_allowed": False,
        "production_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json("product/contracts/internal_monitoring_snapshot_release_boundary_packet.contract.json", contract, wrote)

    docs = """# 774 - Internal Monitoring Snapshot and Release Boundary Packet

This phase creates an internal monitoring snapshot after the internal threshold lock smoke test.

It also creates a release boundary packet.

Allowed:
- internal threshold monitoring;
- operator/evidence packet generation;
- internal audit preparation.

Blocked:
- client-facing validation claims;
- production activation;
- commercial claims;
- validated hallucination reduction claims;
- production Neo4j writes.
"""
    write_text("docs/product/774_INTERNAL_MONITORING_SNAPSHOT_RELEASE_BOUNDARY_PACKET.md", docs, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod7741_7780_internal_monitoring_snapshot_release_boundary_packet.py",
        "product/monitoring/snapshots/prod7741_7780_internal_threshold_monitoring_snapshot.json",
        "product/release_boundaries/prod7741_7780_release_boundary_packet.json",
        "outputs/prod7741_7780_internal_monitoring_snapshot_release_boundary_packet.json",
        "outputs/prod7741_7780_internal_monitoring_snapshot_release_boundary_packet.md",
        "product/contracts/internal_monitoring_snapshot_release_boundary_packet.contract.json",
        "docs/product/774_INTERNAL_MONITORING_SNAPSHOT_RELEASE_BOUNDARY_PACKET.md",
    ]
    return "\n".join([
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Add internal monitoring snapshot and release boundary packet"',
        'git tag -a product-casulo-internal-monitoring-release-boundary-v0.1 HEAD -m "CASULO internal monitoring release boundary v0.1"',
        "git push origin main",
        "git push origin product-casulo-internal-monitoring-release-boundary-v0.1",
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

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

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
]

def load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def classify_refreshed_item(case_id: str, fixed_decision: Dict[str, Any], prior_item: Dict[str, Any], resolution: Dict[str, Any]) -> Dict[str, Any]:
    fixed_gate = fixed_decision.get("gate")
    fixed_output = fixed_decision.get("output_mode")
    prior_issue = prior_item.get("candidate_issue")
    prior_status = prior_item.get("decision_status")
    risk_band = fixed_decision.get("risk_band")
    resolved_false_blocks = set(resolution.get("resolved_false_block_candidates", []))
    direct_blocks = set(resolution.get("direct_execution_blocks_preserved", []))

    if case_id in resolved_false_blocks:
        post_status = "APPROVE_FIXED_GATE_PENDING_FALSE_ALLOW_SCAN"
        priority = "HIGH"
        recommendation = "Accept the hotfix resolution at case level, then run false-allow scan before expanding pilot size."
        queue = "POST_HOTFIX_FALSE_ALLOW_SCAN"
    elif case_id in direct_blocks:
        post_status = "APPROVE_DIRECT_BLOCK"
        priority = "NORMAL"
        recommendation = "Keep direct execution block preserved."
        queue = "DIRECT_BLOCK_APPROVAL"
    elif prior_issue == "POSSIBLE_OVER_CONSERVATIVE_REVIEW":
        post_status = "RECLASSIFICATION_CANDIDATE"
        priority = "HIGH"
        recommendation = "Review whether this case should remain HUMAN_REVIEW_REQUIRED or become ALLOW_WITH_WARNING/EVIDENCE_REQUEST at case level only."
        queue = "OVER_CONSERVATIVE_REVIEW"
    elif fixed_gate in {"ANSWER_ALLOWED", "ALLOW_WITH_WARNING"}:
        post_status = "PENDING_FALSE_ALLOW_SCAN"
        priority = "NORMAL"
        recommendation = "Inspect allowed or warning output for false-allow risk before pilot expansion."
        queue = "FALSE_ALLOW_SCAN"
    elif fixed_gate == "EVIDENCE_REQUIRED":
        post_status = "KEEP_EVIDENCE_REQUEST"
        priority = "LOW"
        recommendation = "Keep evidence request and refine missing-evidence checklist."
        queue = "EVIDENCE_REQUEST_REVIEW"
    elif fixed_gate == "HUMAN_REVIEW_REQUIRED":
        post_status = "KEEP_HUMAN_REVIEW"
        priority = "NORMAL"
        recommendation = "Keep human review pending explicit reviewer decision."
        queue = "HUMAN_REVIEW_CONFIRMATION"
    else:
        post_status = "PENDING_REVIEW"
        priority = "NORMAL"
        recommendation = "Review manually."
        queue = "GENERAL_REVIEW"

    return {
        "case_id": case_id,
        "business_domain": prior_item.get("business_domain"),
        "problem_summary": prior_item.get("problem_summary"),
        "prior_candidate_issue": prior_issue,
        "prior_decision_status": prior_status,
        "fixed_gate": fixed_gate,
        "fixed_output_mode": fixed_output,
        "fixed_risk_band": risk_band,
        "fixed_adjusted_risk": fixed_decision.get("adjusted_risk"),
        "post_hotfix_review_status": post_status,
        "review_queue": queue,
        "review_priority": priority,
        "case_level_recommendation": recommendation,
        "allowed_human_decisions": [
            "APPROVE_FIXED_GATE",
            "KEEP_PRIOR_GATE",
            "MARK_FALSE_ALLOW",
            "MARK_FALSE_BLOCK_RESOLVED",
            "MARK_OVER_CONSERVATIVE",
            "REQUEST_MORE_EVIDENCE",
            "APPROVE_CASE_LEVEL_RECLASSIFICATION"
        ],
        "auto_apply": False,
    }

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    upstream = load_json(out / "prod801_820_execution_intent_readiness.json", {})
    upstream_ready = upstream.get("decision") == "READY_FOR_PILOT_BOARD_REFRESH_AFTER_INTENT_HOTFIX"

    prior_board_payload = load_json(out / "prod761_800_human_review_board.json", {})
    prior_items = prior_board_payload.get("board_items", [])
    prior_by_case = {item.get("case_id"): item for item in prior_items}

    fixed_decisions_payload = load_json(out / "prod801_820_business_pilot_fixed_decisions.json", {})
    fixed_decisions = fixed_decisions_payload.get("decisions", [])
    fixed_by_case = {item.get("case_id"): item for item in fixed_decisions}

    resolution_payload = load_json(out / "prod801_820_false_block_resolution.json", {})
    if len(fixed_decisions) != 20 or len(prior_items) != 20:
        raise SystemExit("Expected 20 prior board items and 20 fixed decisions.")

    refreshed_items = []
    for case_id in sorted(fixed_by_case.keys()):
        refreshed_items.append(classify_refreshed_item(case_id, fixed_by_case[case_id], prior_by_case.get(case_id, {}), resolution_payload))

    ledger = []
    for idx, item in enumerate(refreshed_items, start=1):
        ledger.append({
            "ledger_id": f"REFRESH-LEDGER-{idx:03d}",
            "case_id": item["case_id"],
            "prior_decision_status": item["prior_decision_status"],
            "post_hotfix_review_status": item["post_hotfix_review_status"],
            "review_queue": item["review_queue"],
            "human_review_status": "PENDING",
            "human_decision": None,
            "human_comment": None,
            "auto_apply": False,
            "created_at": generated_at,
        })

    queue_distribution: Dict[str, int] = defaultdict(int)
    status_distribution: Dict[str, int] = defaultdict(int)
    priority_distribution: Dict[str, int] = defaultdict(int)
    gate_distribution: Dict[str, int] = defaultdict(int)
    for item in refreshed_items:
        queue_distribution[item["review_queue"]] += 1
        status_distribution[item["post_hotfix_review_status"]] += 1
        priority_distribution[item["review_priority"]] += 1
        gate_distribution[item["fixed_gate"]] += 1

    resolved_false_blocks = resolution_payload.get("resolved_false_block_candidates", [])
    direct_blocks_preserved = resolution_payload.get("direct_execution_blocks_preserved", [])
    false_allow_scan_cases = [
        item["case_id"]
        for item in refreshed_items
        if item["review_queue"] in {"POST_HOTFIX_FALSE_ALLOW_SCAN", "FALSE_ALLOW_SCAN"}
    ]
    over_conservative_cases = [
        item["case_id"]
        for item in refreshed_items
        if item["review_queue"] == "OVER_CONSERVATIVE_REVIEW"
    ]

    status = {
        "status": "PASS" if upstream_ready else "WARN",
        "generated_at": generated_at,
        "phase": "Pilot Board Refresh and Case-Level Review Decisions",
        "mode": "case_level_review_no_global_threshold_mutation",
        "case_count": len(refreshed_items),
        "ledger_count": len(ledger),
        "queue_distribution": dict(sorted(queue_distribution.items())),
        "status_distribution": dict(sorted(status_distribution.items())),
        "priority_distribution": dict(sorted(priority_distribution.items())),
        "fixed_gate_distribution": dict(sorted(gate_distribution.items())),
        "resolved_false_block_count": len(resolved_false_blocks),
        "false_allow_scan_count": len(false_allow_scan_cases),
        "over_conservative_count": len(over_conservative_cases),
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "auto_apply": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    board = {
        "status": "PASS",
        "case_count": len(refreshed_items),
        "board_items": refreshed_items,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    ledger_payload = {
        "status": "PASS",
        "ledger_count": len(ledger),
        "ledger": ledger,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    findings = {
        "status": "PASS",
        "findings": [
            {
                "id": "REFRESH-FINDING-001",
                "name": "false_blocks_resolved_by_intent_hotfix",
                "cases": resolved_false_blocks,
                "meaning": "Negation-aware intent handling resolved prior false block candidates, but each newly allowed case still requires false-allow scan."
            },
            {
                "id": "REFRESH-FINDING-002",
                "name": "direct_execution_blocks_preserved",
                "cases": direct_blocks_preserved,
                "meaning": "Direct execution requests remain blocked after the hotfix."
            },
            {
                "id": "REFRESH-FINDING-003",
                "name": "over_conservative_review_candidates",
                "cases": over_conservative_cases,
                "meaning": "These cases should be reviewed for case-level reclassification, not global threshold mutation."
            },
            {
                "id": "REFRESH-FINDING-004",
                "name": "false_allow_scan_required",
                "cases": false_allow_scan_cases,
                "meaning": "Allowed or warning outputs must be reviewed before any 50-case expansion."
            },
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    recommendations = {
        "status": "PASS",
        "auto_apply": False,
        "automatic_threshold_mutation_allowed": False,
        "recommendations": [
            {
                "id": "REFRESH-CAL-001",
                "target": "case_level_false_block_resolution",
                "recommendation": "Approve resolved false block cases only at case level after false-allow scan confirms the allowed output is safe.",
                "cases": resolved_false_blocks,
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "REFRESH-CAL-002",
                "target": "direct_execution_block_policy",
                "recommendation": "Keep direct execution block policy unchanged.",
                "cases": direct_blocks_preserved,
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "REFRESH-CAL-003",
                "target": "over_conservative_review",
                "recommendation": "Inspect over-conservative candidates and approve only case-level reclassification if justified.",
                "cases": over_conservative_cases,
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "REFRESH-CAL-004",
                "target": "pilot_expansion_gate",
                "recommendation": "Do not expand to 50 cases until refreshed board queues are human-reviewed.",
                "cases": false_allow_scan_cases + over_conservative_cases,
                "auto_apply": False,
                "requires_human_approval": True,
            },
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness = {
        "status": "PASS" if upstream_ready else "WARN",
        "decision": "READY_FOR_CASE_LEVEL_HUMAN_DECISION_SESSION" if upstream_ready else "REVIEW_UPSTREAM_INTENT_HOTFIX_READINESS",
        "case_count": len(refreshed_items),
        "ledger_count": len(ledger),
        "ready_for": [
            "case-level human decision session",
            "false-allow scan on newly allowed cases",
            "over-conservative review inspection",
            "manual ledger update",
        ],
        "not_ready_for": [
            "automatic threshold mutation",
            "production activation",
            "autonomous external execution",
            "client-facing guarantees",
            "50-case expansion before refreshed board review",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS" if upstream_ready and len(refreshed_items) == 20 and recommendations["auto_apply"] is False else "WARN",
        "audit": "Pilot Board Refresh and Case-Level Review Decisions audit",
        "case_count": len(refreshed_items),
        "ledger_count": len(ledger),
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "auto_apply": False,
        "finding": "PASS: refreshed pilot board uses fixed decisions and case-level review queues without global threshold mutation.",
        "readiness": readiness["decision"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    outputs = {
        "prod821_860_pilot_board_refresh_status.json": status,
        "prod821_860_pilot_board_refresh.json": board,
        "prod821_860_case_level_decision_ledger.json": ledger_payload,
        "prod821_860_pilot_board_refresh_findings.json": findings,
        "prod821_860_case_level_recommendations.json": recommendations,
        "prod821_860_pilot_board_refresh_readiness.json": readiness,
        "prod821_860_pilot_board_refresh_audit_report.json": audit,
    }

    for name, obj in outputs.items():
        write_json(out / name, obj)

    report = [
        "# PROD-821..860 Pilot Board Refresh and Case-Level Review Decisions",
        "",
        f"- Status: `{audit['status']}`",
        f"- Case count: `{len(refreshed_items)}`",
        f"- Ledger count: `{len(ledger)}`",
        f"- Decision: `{readiness['decision']}`",
        f"- Auto apply: `{status['auto_apply']}`",
        f"- External execution allowed: `{status['external_execution_allowed']}`",
        f"- Automatic threshold mutation allowed: `{status['automatic_threshold_mutation_allowed']}`",
        "",
        "## Queue Distribution",
    ]
    for key, value in status["queue_distribution"].items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Status Distribution"]
    for key, value in status["status_distribution"].items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Critical Review Sets"]
    report.append(f"- Resolved false blocks: `{resolved_false_blocks}`")
    report.append(f"- Direct blocks preserved: `{direct_blocks_preserved}`")
    report.append(f"- False allow scan: `{false_allow_scan_cases}`")
    report.append(f"- Over-conservative review: `{over_conservative_cases}`")
    report += ["", "## Recommendations"]
    for rec in recommendations["recommendations"]:
        report.append(f"- `{rec['id']}` `{rec['target']}`: {rec['recommendation']} / auto_apply `{rec['auto_apply']}`")
    report += ["", "## Next Recommended Bundle", "- `PROD-861 Case-Level Human Decision Capture and Board Closure`"]
    write_text(out / "prod821_860_pilot_board_refresh_report.md", "\n".join(report) + "\n")

    result = {
        "task": "PROD-821..860",
        "status": audit["status"],
        "phase": "Pilot Board Refresh and Case-Level Review Decisions",
        "decision": readiness["decision"],
        "outputs": ["outputs/" + key for key in outputs.keys()],
        "next_recommended_bundle": "PROD-861 Case-Level Human Decision Capture and Board Closure",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod821_860_result.json", result)
    write_text(out / "prod821_860_report.md", "# PROD-821..860 Report\n\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    result = build(Path(args.repo))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

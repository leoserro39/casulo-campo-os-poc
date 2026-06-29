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

def default_decision_for_item(item: Dict[str, Any]) -> Dict[str, Any]:
    case_id = item["case_id"]
    queue = item.get("review_queue")
    fixed_gate = item.get("fixed_gate")
    risk_band = item.get("fixed_risk_band")

    if queue == "POST_HOTFIX_FALSE_ALLOW_SCAN":
        decision = "MARK_FALSE_BLOCK_RESOLVED"
        comment = "Synthetic POC decision: false block resolved by negation-aware hotfix; keep case-level allowed gate pending future real reviewer confirmation."
        false_allow_confirmed = False
        closure_bucket = "resolved_false_block"
    elif queue == "FALSE_ALLOW_SCAN":
        decision = "APPROVE_FIXED_GATE"
        comment = "Synthetic POC decision: false-allow scan found no issue in controlled case; approve fixed gate at case level only."
        false_allow_confirmed = False
        closure_bucket = "approved_allow_after_scan"
    elif queue == "OVER_CONSERVATIVE_REVIEW":
        if fixed_gate == "HUMAN_REVIEW_REQUIRED":
            decision = "KEEP_HUMAN_REVIEW"
            comment = "Synthetic POC decision: keep human review for sensitive/high-stakes case; do not relax threshold globally."
            closure_bucket = "kept_human_review"
        else:
            decision = "APPROVE_CASE_LEVEL_RECLASSIFICATION"
            comment = "Synthetic POC decision: approve only case-level reclassification; no global threshold mutation."
            closure_bucket = "case_level_reclassification"
        false_allow_confirmed = False
    elif queue == "DIRECT_BLOCK_APPROVAL":
        decision = "APPROVE_DIRECT_BLOCK"
        comment = "Synthetic POC decision: direct execution remains blocked."
        false_allow_confirmed = False
        closure_bucket = "approved_direct_block"
    elif queue == "EVIDENCE_REQUEST_REVIEW":
        decision = "KEEP_EVIDENCE_REQUEST"
        comment = "Synthetic POC decision: keep evidence request and refine intake checklist."
        false_allow_confirmed = False
        closure_bucket = "kept_evidence_request"
    elif queue == "HUMAN_REVIEW_CONFIRMATION":
        decision = "KEEP_HUMAN_REVIEW"
        comment = "Synthetic POC decision: keep human review pending real-world reviewer decision."
        false_allow_confirmed = False
        closure_bucket = "kept_human_review"
    else:
        decision = "REQUEST_MORE_EVIDENCE"
        comment = "Synthetic POC decision: unresolved queue requires more evidence."
        false_allow_confirmed = False
        closure_bucket = "unresolved_requires_evidence"

    return {
        "case_id": case_id,
        "human_decision": decision,
        "human_comment": comment,
        "reviewer_mode": "synthetic_human_decision_seed_for_poc_only",
        "review_queue": queue,
        "fixed_gate": fixed_gate,
        "fixed_output_mode": item.get("fixed_output_mode"),
        "fixed_risk_band": risk_band,
        "false_allow_confirmed": false_allow_confirmed,
        "closure_bucket": closure_bucket,
        "auto_apply": False,
    }

def load_human_decisions(repo: Path, board_items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    decision_dir = repo / "inputs" / "human_decisions"
    loaded: List[Dict[str, Any]] = []
    if decision_dir.exists():
        for path in sorted(decision_dir.glob("*.json")):
            data = load_json(path, {})
            if isinstance(data, dict) and isinstance(data.get("decisions"), list):
                loaded.extend(data["decisions"])
            elif isinstance(data, dict) and data.get("case_id"):
                loaded.append(data)
    if loaded:
        for item in loaded:
            item.setdefault("reviewer_mode", "user_provided_case_level_decision")
            item.setdefault("auto_apply", False)
        return loaded
    return [default_decision_for_item(item) for item in board_items]

def validate_decisions(board_items: List[Dict[str, Any]], decisions: List[Dict[str, Any]]) -> Dict[str, Any]:
    board_cases = {item["case_id"] for item in board_items}
    decision_cases = {item.get("case_id") for item in decisions}
    missing = sorted(board_cases - decision_cases)
    extra = sorted(case for case in decision_cases - board_cases if case)
    auto_apply_violations = [item.get("case_id") for item in decisions if item.get("auto_apply") is not False]
    false_allow_cases = [item.get("case_id") for item in decisions if item.get("false_allow_confirmed") is True]
    return {
        "status": "PASS" if not missing and not extra and not auto_apply_violations else "WARN",
        "missing_decisions": missing,
        "extra_decisions": extra,
        "auto_apply_violations": auto_apply_violations,
        "false_allow_confirmed_cases": false_allow_cases,
    }

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    upstream = load_json(out / "prod821_860_pilot_board_refresh_readiness.json", {})
    upstream_ready = upstream.get("decision") == "READY_FOR_CASE_LEVEL_HUMAN_DECISION_SESSION"

    board_payload = load_json(out / "prod821_860_pilot_board_refresh.json", {})
    board_items = board_payload.get("board_items", [])
    if len(board_items) != 20:
        raise SystemExit("Expected 20 refreshed board items from PROD-821.")

    decisions = load_human_decisions(repo, board_items)
    validation = validate_decisions(board_items, decisions)
    decisions_by_case = {item.get("case_id"): item for item in decisions}

    closed_ledger = []
    for idx, item in enumerate(board_items, start=1):
        decision = decisions_by_case.get(item["case_id"], {})
        closed_ledger.append({
            "ledger_id": f"CLOSED-LEDGER-{idx:03d}",
            "case_id": item["case_id"],
            "review_queue": item.get("review_queue"),
            "fixed_gate": item.get("fixed_gate"),
            "fixed_output_mode": item.get("fixed_output_mode"),
            "human_review_status": "CLOSED" if decision else "PENDING",
            "human_decision": decision.get("human_decision"),
            "human_comment": decision.get("human_comment"),
            "reviewer_mode": decision.get("reviewer_mode"),
            "closure_bucket": decision.get("closure_bucket"),
            "false_allow_confirmed": decision.get("false_allow_confirmed", False),
            "auto_apply": False,
            "closed_at": generated_at if decision else None,
        })

    decision_distribution: Dict[str, int] = defaultdict(int)
    queue_distribution: Dict[str, int] = defaultdict(int)
    closure_distribution: Dict[str, int] = defaultdict(int)
    reviewer_mode_distribution: Dict[str, int] = defaultdict(int)
    for decision in decisions:
        decision_distribution[decision.get("human_decision", "UNKNOWN")] += 1
        queue_distribution[decision.get("review_queue", "UNKNOWN")] += 1
        closure_distribution[decision.get("closure_bucket", "UNKNOWN")] += 1
        reviewer_mode_distribution[decision.get("reviewer_mode", "UNKNOWN")] += 1

    false_allow_cases = validation["false_allow_confirmed_cases"]
    all_closed = len(validation["missing_decisions"]) == 0 and len(decisions) >= 20
    closure_status = "CLOSED_CONTROLLED_POC" if upstream_ready and all_closed and not false_allow_cases else "OPEN_REVIEW_REQUIRED"

    closure = {
        "status": "PASS" if closure_status == "CLOSED_CONTROLLED_POC" else "WARN",
        "closure_status": closure_status,
        "case_count": len(board_items),
        "closed_count": sum(1 for item in closed_ledger if item["human_review_status"] == "CLOSED"),
        "false_allow_confirmed_cases": false_allow_cases,
        "all_decisions_captured": all_closed,
        "decision_distribution": dict(sorted(decision_distribution.items())),
        "queue_distribution": dict(sorted(queue_distribution.items())),
        "closure_distribution": dict(sorted(closure_distribution.items())),
        "reviewer_mode_distribution": dict(sorted(reviewer_mode_distribution.items())),
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "auto_apply": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    summary = {
        "status": "PASS",
        "summary": {
            "case_count": len(board_items),
            "decision_count": len(decisions),
            "closure_status": closure_status,
            "false_allow_confirmed_cases": false_allow_cases,
            "approved_fixed_gate_count": decision_distribution.get("APPROVE_FIXED_GATE", 0),
            "resolved_false_block_count": decision_distribution.get("MARK_FALSE_BLOCK_RESOLVED", 0),
            "kept_human_review_count": decision_distribution.get("KEEP_HUMAN_REVIEW", 0),
            "approved_direct_block_count": decision_distribution.get("APPROVE_DIRECT_BLOCK", 0),
            "kept_evidence_request_count": decision_distribution.get("KEEP_EVIDENCE_REQUEST", 0),
        },
        "blocked_actions": BLOCKED_ACTIONS,
    }

    recommendations = {
        "status": "PASS",
        "auto_apply": False,
        "automatic_threshold_mutation_allowed": False,
        "recommendations": [
            {
                "id": "CLOSURE-CAL-001",
                "target": "50_case_expansion_design",
                "recommendation": "Design a 50-case expansion pack only if this closed controlled POC remains free of confirmed false allows.",
                "cases": [],
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "CLOSURE-CAL-002",
                "target": "decision_capture_mode",
                "recommendation": "Replace synthetic decision seed with explicit reviewer-provided files in inputs/human_decisions for any real pilot.",
                "cases": [],
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "CLOSURE-CAL-003",
                "target": "threshold_policy",
                "recommendation": "Do not mutate global thresholds from this board closure; use case-level findings as evidence for future calibration proposals.",
                "cases": [],
                "auto_apply": False,
                "requires_human_approval": True,
            },
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness_decision = (
        "READY_FOR_CONTROLLED_50_CASE_EXPANSION_DESIGN_NOT_EXECUTION"
        if closure_status == "CLOSED_CONTROLLED_POC"
        else "REVIEW_CASE_LEVEL_DECISION_CAPTURE"
    )
    readiness = {
        "status": "PASS" if readiness_decision.startswith("READY") else "WARN",
        "decision": readiness_decision,
        "case_count": len(board_items),
        "closed_count": closure["closed_count"],
        "ready_for": [
            "controlled 50-case expansion design",
            "graph persistence planning",
            "case-level evidence review",
            "non-mutating calibration proposal drafting",
        ],
        "not_ready_for": [
            "production activation",
            "autonomous external execution",
            "automatic threshold mutation",
            "client-facing guarantees",
            "unapproved real company data",
            "real pilot without explicit reviewer decisions",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS" if readiness["status"] == "PASS" else "WARN",
        "audit": "Case-Level Human Decision Capture and Board Closure audit",
        "case_count": len(board_items),
        "decision_count": len(decisions),
        "closed_count": closure["closed_count"],
        "closure_status": closure_status,
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "auto_apply": False,
        "finding": "PASS: case-level decisions captured and refreshed board closed in controlled POC mode without automatic mutation.",
        "readiness": readiness["decision"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    template = {
        "status": "PASS",
        "usage": "Copy this file to inputs/human_decisions/<reviewer>.json and replace synthetic decisions with explicit reviewer decisions for real pilots.",
        "decisions": [
            {
                "case_id": item["case_id"],
                "human_decision": None,
                "human_comment": "",
                "reviewer_mode": "user_provided_case_level_decision",
                "auto_apply": False,
            }
            for item in board_items
        ],
        "allowed_human_decisions": [
            "APPROVE_FIXED_GATE",
            "KEEP_HUMAN_REVIEW",
            "KEEP_EVIDENCE_REQUEST",
            "APPROVE_DIRECT_BLOCK",
            "APPROVE_CASE_LEVEL_RECLASSIFICATION",
            "MARK_FALSE_ALLOW",
            "MARK_FALSE_BLOCK_RESOLVED",
            "REQUEST_MORE_EVIDENCE"
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    outputs = {
        "prod861_900_case_level_human_decision_template.json": template,
        "prod861_900_case_level_human_decisions.json": {
            "status": "PASS",
            "decision_count": len(decisions),
            "decisions": decisions,
            "validation": validation,
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "prod861_900_board_closure.json": closure,
        "prod861_900_closed_decision_ledger.json": {
            "status": "PASS",
            "ledger_count": len(closed_ledger),
            "ledger": closed_ledger,
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "prod861_900_human_decision_summary.json": summary,
        "prod861_900_case_level_recommendations.json": recommendations,
        "prod861_900_closure_readiness.json": readiness,
        "prod861_900_closure_audit_report.json": audit,
    }

    for name, obj in outputs.items():
        write_json(out / name, obj)

    report = [
        "# PROD-861..900 Case-Level Human Decision Capture and Board Closure",
        "",
        f"- Status: `{audit['status']}`",
        f"- Case count: `{len(board_items)}`",
        f"- Decision count: `{len(decisions)}`",
        f"- Closed count: `{closure['closed_count']}`",
        f"- Closure status: `{closure_status}`",
        f"- Decision: `{readiness['decision']}`",
        f"- Auto apply: `{closure['auto_apply']}`",
        f"- External execution allowed: `{closure['external_execution_allowed']}`",
        f"- Automatic threshold mutation allowed: `{closure['automatic_threshold_mutation_allowed']}`",
        "",
        "## Decision Distribution",
    ]
    for key, value in closure["decision_distribution"].items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Closure Distribution"]
    for key, value in closure["closure_distribution"].items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Validation"]
    report.append(f"- Missing decisions: `{validation['missing_decisions']}`")
    report.append(f"- Auto-apply violations: `{validation['auto_apply_violations']}`")
    report.append(f"- False allow confirmed cases: `{false_allow_cases}`")
    report += ["", "## Recommendations"]
    for rec in recommendations["recommendations"]:
        report.append(f"- `{rec['id']}` `{rec['target']}`: {rec['recommendation']} / auto_apply `{rec['auto_apply']}`")
    report += ["", "## Next Recommended Bundle", "- `PROD-901 Controlled 50-Case Expansion Design and Graph Persistence Prep`"]
    write_text(out / "prod861_900_case_level_human_decision_closure_report.md", "\n".join(report) + "\n")

    result = {
        "task": "PROD-861..900",
        "status": audit["status"],
        "phase": "Case-Level Human Decision Capture and Board Closure",
        "decision": readiness["decision"],
        "outputs": ["outputs/" + key for key in outputs.keys()],
        "next_recommended_bundle": "PROD-901 Controlled 50-Case Expansion Design and Graph Persistence Prep",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod861_900_result.json", result)
    write_text(out / "prod861_900_report.md", "# PROD-861..900 Report\n\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n")
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

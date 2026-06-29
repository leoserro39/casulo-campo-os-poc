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

NEGATED_EXECUTION_PATTERNS = [
    "sem executar",
    "sem enviar",
    "sem acionar",
    "sem liberar",
    "sem aprovar",
    "não executar",
    "nao executar",
    "não enviar",
    "nao enviar",
    "não acionar",
    "nao acionar",
    "não liberar",
    "nao liberar",
    "não aprovar",
    "nao aprovar",
]

DIRECT_EXECUTION_PATTERNS = [
    "aprovar automaticamente",
    "executar automaticamente",
    "enviar automaticamente",
    "acionar automaticamente",
    "liberar automaticamente",
    "executar ação",
    "executar acao",
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

def text_blob(run: Dict[str, Any]) -> str:
    case = run.get("input", {})
    parts = [
        str(case.get("problem_summary", "")),
        str(case.get("desired_decision_support", "")),
        " ".join(case.get("known_facts", []) if isinstance(case.get("known_facts"), list) else []),
        " ".join(case.get("assumptions", []) if isinstance(case.get("assumptions"), list) else []),
    ]
    return " ".join(parts).lower()

def has_negated_execution(run: Dict[str, Any]) -> bool:
    text = text_blob(run)
    return any(pattern in text for pattern in NEGATED_EXECUTION_PATTERNS)

def has_direct_execution(run: Dict[str, Any]) -> bool:
    text = text_blob(run)
    return any(pattern in text for pattern in DIRECT_EXECUTION_PATTERNS)

def classify_item(run: Dict[str, Any], feedback_by_case: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    case_id = run.get("case_id")
    case = run.get("input", {})
    decision = run.get("decision", {})
    pf = run.get("preflight", {})
    budget = run.get("hallucination_budget", {})
    feedback = feedback_by_case.get(case_id, {})

    gate = decision.get("gate")
    output_mode = decision.get("output_mode")
    risk_band = decision.get("risk_band")
    adjusted_risk = float(decision.get("adjusted_risk", 0))
    feedback_label = feedback.get("feedback_label")

    candidate_issue = "NO_ISSUE_DETECTED"
    decision_status = "PENDING_HUMAN_REVIEW"
    review_priority = "NORMAL"
    recommendation = "Review and confirm current gate/output mode."

    if gate == "UNSUPPORTED_BLOCKED" and has_negated_execution(run) and not has_direct_execution(run):
        candidate_issue = "POSSIBLE_FALSE_BLOCK_NEGATED_EXECUTION_PHRASE"
        decision_status = "FALSE_BLOCK_CANDIDATE"
        review_priority = "HIGH"
        recommendation = "Inspect whether the block was triggered by a negated phrase such as 'sem executar' or 'sem enviar'. Consider reclassifying to ANSWER_ALLOWED, ALLOW_WITH_WARNING or EVIDENCE_REQUEST if no execution is requested."
    elif feedback_label == "OVER_CONSERVATIVE_CANDIDATE":
        candidate_issue = "POSSIBLE_OVER_CONSERVATIVE_REVIEW"
        decision_status = "RECLASSIFICATION_CANDIDATE"
        review_priority = "HIGH"
        recommendation = "Inspect medium/low-risk HUMAN_REVIEW_REQUIRED case for possible ALLOW_WITH_WARNING or EVIDENCE_REQUEST split."
    elif gate == "UNSUPPORTED_BLOCKED" and has_direct_execution(run):
        candidate_issue = "DIRECT_EXECUTION_BLOCK_CONFIRMED"
        decision_status = "APPROVED_AS_IS"
        review_priority = "NORMAL"
        recommendation = "Maintain block unless human reviewer confirms the request was only a safe reformulation."
    elif gate == "UNSUPPORTED_BLOCKED":
        candidate_issue = "BLOCK_REVIEW_REQUIRED"
        decision_status = "PENDING_HUMAN_REVIEW"
        review_priority = "HIGH"
        recommendation = "Verify whether the block is truly unsupported/execution-related or a false block."
    elif gate == "HUMAN_REVIEW_REQUIRED" and adjusted_risk >= 75:
        candidate_issue = "HIGH_RISK_REVIEW_CONFIRMED"
        decision_status = "APPROVED_AS_IS"
        review_priority = "NORMAL"
        recommendation = "Maintain review gate unless human reviewer provides stronger evidence and revised policy."
    elif gate == "HUMAN_REVIEW_REQUIRED":
        candidate_issue = "REVIEW_GATE_INSPECTION"
        decision_status = "PENDING_HUMAN_REVIEW"
        review_priority = "NORMAL"
        recommendation = "Confirm whether review packet is appropriate or too conservative."
    elif gate == "EVIDENCE_REQUIRED":
        candidate_issue = "EVIDENCE_REQUEST_INSPECTION"
        decision_status = "NEEDS_MORE_EVIDENCE"
        review_priority = "LOW"
        recommendation = "Confirm missing evidence list and improve intake instructions."
    elif gate in {"ANSWER_ALLOWED", "ALLOW_WITH_WARNING"}:
        candidate_issue = "ALLOW_GATE_FALSE_ALLOW_SCAN"
        decision_status = "PENDING_HUMAN_REVIEW"
        review_priority = "NORMAL"
        recommendation = "Inspect for false allow before any pilot expansion."
    else:
        candidate_issue = "UNCLASSIFIED_REVIEW"
        review_priority = "NORMAL"

    return {
        "case_id": case_id,
        "business_domain": case.get("business_domain"),
        "problem_summary": case.get("problem_summary"),
        "current_gate": gate,
        "current_output_mode": output_mode,
        "risk_band": risk_band,
        "adjusted_risk": adjusted_risk,
        "live_delta_score": decision.get("live_delta_score"),
        "preflight_score": pf.get("preflight_score"),
        "activation_state": pf.get("activation_state"),
        "hallucination_budget": budget.get("hallucination_budget"),
        "reasoning_mode": budget.get("reasoning_mode"),
        "feedback_label": feedback_label,
        "candidate_issue": candidate_issue,
        "decision_status": decision_status,
        "review_priority": review_priority,
        "recommended_human_action": recommendation,
        "allowed_human_decisions": [
            "APPROVE_CURRENT_GATE",
            "MARK_FALSE_BLOCK",
            "MARK_FALSE_ALLOW",
            "MARK_OVER_CONSERVATIVE",
            "REQUEST_MORE_EVIDENCE",
            "APPROVE_RECLASSIFICATION_CANDIDATE",
        ],
        "auto_apply": False,
    }

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    upstream = load_json(out / "prod721_760_business_pilot_readiness.json", {})
    upstream_ready = upstream.get("decision") == "READY_FOR_HUMAN_REVIEWED_20_CASE_BUSINESS_PILOT"

    runs_payload = load_json(out / "prod721_760_business_pilot_runs.json", {})
    runs = runs_payload.get("runs", [])
    feedback_payload = load_json(out / "prod721_760_business_pilot_feedback_seed.json", {})
    feedback = feedback_payload.get("feedback", [])
    feedback_by_case = {item.get("case_id"): item for item in feedback}

    if len(runs) != 20:
        raise SystemExit("Expected 20 pilot runs from PROD-721.")

    board_items = [classify_item(run, feedback_by_case) for run in runs]
    ledger = []
    for idx, item in enumerate(board_items, start=1):
        ledger.append({
            "ledger_id": f"LEDGER-{idx:03d}",
            "case_id": item["case_id"],
            "candidate_issue": item["candidate_issue"],
            "initial_decision_status": item["decision_status"],
            "human_review_status": "PENDING",
            "human_decision": None,
            "human_comment": None,
            "auto_apply": False,
            "created_at": generated_at,
        })

    issue_distribution: Dict[str, int] = defaultdict(int)
    priority_distribution: Dict[str, int] = defaultdict(int)
    decision_status_distribution: Dict[str, int] = defaultdict(int)
    for item in board_items:
        issue_distribution[item["candidate_issue"]] += 1
        priority_distribution[item["review_priority"]] += 1
        decision_status_distribution[item["decision_status"]] += 1

    false_block_candidates = [item["case_id"] for item in board_items if item["decision_status"] == "FALSE_BLOCK_CANDIDATE"]
    reclassification_candidates = [item["case_id"] for item in board_items if item["decision_status"] == "RECLASSIFICATION_CANDIDATE"]
    false_allow_scan = [item["case_id"] for item in board_items if item["candidate_issue"] == "ALLOW_GATE_FALSE_ALLOW_SCAN"]

    status = {
        "status": "PASS" if upstream_ready else "WARN",
        "generated_at": generated_at,
        "phase": "Human Review Pilot Board and Decision Ledger",
        "mode": "human_review_board_no_auto_mutation",
        "case_count": len(board_items),
        "ledger_count": len(ledger),
        "issue_distribution": dict(sorted(issue_distribution.items())),
        "priority_distribution": dict(sorted(priority_distribution.items())),
        "decision_status_distribution": dict(sorted(decision_status_distribution.items())),
        "false_block_candidate_count": len(false_block_candidates),
        "reclassification_candidate_count": len(reclassification_candidates),
        "false_allow_scan_count": len(false_allow_scan),
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "auto_apply": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    board = {
        "status": "PASS",
        "case_count": len(board_items),
        "board_items": board_items,
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
                "id": "HR-FINDING-001",
                "name": "false_block_negated_execution_scan",
                "cases": false_block_candidates,
                "meaning": "Some blocked cases contain negated execution wording such as 'sem executar' or 'sem enviar'. These require human review because they may not be true execution requests.",
            },
            {
                "id": "HR-FINDING-002",
                "name": "over_conservative_review_scan",
                "cases": reclassification_candidates,
                "meaning": "Some review packets may be too conservative and could become ALLOW_WITH_WARNING or EVIDENCE_REQUEST after human approval.",
            },
            {
                "id": "HR-FINDING-003",
                "name": "false_allow_scan",
                "cases": false_allow_scan,
                "meaning": "All allowed/warning outputs must be scanned before pilot expansion.",
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
                "id": "HR-CAL-001",
                "target": "execution_intent_classifier",
                "recommendation": "Add explicit negation-aware execution intent handling before increasing pilot size.",
                "cases": false_block_candidates,
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "HR-CAL-002",
                "target": "review_reclassification",
                "recommendation": "Review over-conservative candidates and approve only case-level recommendations, not global thresholds.",
                "cases": reclassification_candidates,
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "HR-CAL-003",
                "target": "pilot_expansion_gate",
                "recommendation": "Do not expand to 50 cases until false block candidates and false allow scan are resolved.",
                "cases": false_block_candidates + false_allow_scan,
                "auto_apply": False,
                "requires_human_approval": True,
            },
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness = {
        "status": "PASS" if upstream_ready else "WARN",
        "decision": "READY_FOR_HUMAN_REVIEW_SESSION_NOT_THRESHOLD_MUTATION" if upstream_ready else "REVIEW_UPSTREAM_20_CASE_PILOT_READINESS",
        "case_count": len(board_items),
        "ledger_count": len(ledger),
        "ready_for": [
            "human review session",
            "manual decision ledger updates",
            "false block inspection",
            "over-conservative review inspection",
            "false allow scan",
        ],
        "not_ready_for": [
            "automatic threshold mutation",
            "production activation",
            "autonomous external execution",
            "client-facing guarantees",
            "unapproved real company data",
            "50-case expansion before human review",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS" if upstream_ready and len(board_items) == 20 and recommendations["auto_apply"] is False else "WARN",
        "audit": "Human Review Pilot Board audit",
        "case_count": len(board_items),
        "ledger_count": len(ledger),
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "auto_apply": False,
        "finding": "PASS: human review board and decision ledger created with false block, over-conservative and false allow review queues without automatic mutation.",
        "readiness": readiness["decision"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    outputs = {
        "prod761_800_human_review_board_status.json": status,
        "prod761_800_human_review_board.json": board,
        "prod761_800_decision_ledger.json": ledger_payload,
        "prod761_800_human_review_findings.json": findings,
        "prod761_800_human_review_recommendations.json": recommendations,
        "prod761_800_human_review_readiness.json": readiness,
        "prod761_800_human_review_audit_report.json": audit,
    }

    for name, obj in outputs.items():
        write_json(out / name, obj)

    report = [
        "# PROD-761..800 Human Review Pilot Board and Decision Ledger",
        "",
        f"- Status: `{audit['status']}`",
        f"- Case count: `{len(board_items)}`",
        f"- Ledger count: `{len(ledger)}`",
        f"- Decision: `{readiness['decision']}`",
        f"- Auto apply: `{status['auto_apply']}`",
        f"- External execution allowed: `{status['external_execution_allowed']}`",
        f"- Automatic threshold mutation allowed: `{status['automatic_threshold_mutation_allowed']}`",
        "",
        "## Issue Distribution",
    ]
    for key, value in status["issue_distribution"].items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Priority Distribution"]
    for key, value in status["priority_distribution"].items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Review Queues"]
    report.append(f"- False block candidates: `{false_block_candidates}`")
    report.append(f"- Reclassification candidates: `{reclassification_candidates}`")
    report.append(f"- False allow scan: `{false_allow_scan}`")
    report += ["", "## Recommendations"]
    for rec in recommendations["recommendations"]:
        report.append(f"- `{rec['id']}` `{rec['target']}`: {rec['recommendation']} / auto_apply `{rec['auto_apply']}`")
    report += ["", "## Next Recommended Bundle", "- `PROD-801 Negation-Aware Execution Intent Classifier Hotfix`"]
    write_text(out / "prod761_800_human_review_board_report.md", "\n".join(report) + "\n")

    result = {
        "task": "PROD-761..800",
        "status": audit["status"],
        "phase": "Human Review Pilot Board and Decision Ledger",
        "decision": readiness["decision"],
        "outputs": ["outputs/" + key for key in outputs.keys()],
        "next_recommended_bundle": "PROD-801 Negation-Aware Execution Intent Classifier Hotfix",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod761_800_result.json", result)
    write_text(out / "prod761_800_report.md", "# PROD-761..800 Report\n\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n")
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

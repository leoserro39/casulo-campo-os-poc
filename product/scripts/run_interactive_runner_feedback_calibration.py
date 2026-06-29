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

def pct(n: int, total: int) -> float:
    return round(n * 100 / total, 2) if total else 0.0

def default_feedback_for_run(run: Dict[str, Any], idx: int) -> Dict[str, Any]:
    decision = run.get("decision", {})
    pf = run.get("preflight", {})
    budget = run.get("hallucination_budget", {})
    risk = float(decision.get("adjusted_risk", 0))
    gate = decision.get("gate", "")
    mode = decision.get("output_mode", "")
    case_id = run.get("case_id", f"CASE-{idx:03d}")

    if gate == "UNSUPPORTED_BLOCKED":
        label = "BLOCK_APPROPRIATE"
        comment = "Blocking is appropriate because the case is unsupported or requests external execution."
        usefulness = "SAFE_BUT_NOT_ACTIONABLE"
    elif gate == "HUMAN_REVIEW_REQUIRED" and risk >= 75:
        label = "REVIEW_APPROPRIATE"
        comment = "Human review is appropriate due to high or critical risk."
        usefulness = "SAFE_REVIEW_PACKET"
    elif gate == "HUMAN_REVIEW_REQUIRED" and risk < 55 and pf.get("activation_state") == "CONTROLLED_ACTIVE_DOMAIN":
        label = "OVER_CONSERVATIVE_CANDIDATE"
        comment = "Potentially over-conservative: controlled active domain and medium risk still produced review packet."
        usefulness = "REVIEW_MAY_REDUCE_UTILITY"
    elif gate == "HUMAN_REVIEW_REQUIRED":
        label = "REVIEW_APPROPRIATE"
        comment = "Review appears appropriate based on preflight and sensitivity."
        usefulness = "SAFE_REVIEW_PACKET"
    elif gate == "EVIDENCE_REQUIRED":
        label = "NEEDS_MORE_EVIDENCE"
        comment = "Evidence request is appropriate."
        usefulness = "EVIDENCE_COLLECTION"
    else:
        label = "OUTPUT_USEFUL"
        comment = "Output appears useful under current constraints."
        usefulness = "USEFUL_CONTROLLED_OUTPUT"

    return {
        "feedback_id": f"FB-{case_id}",
        "case_id": case_id,
        "feedback_label": label,
        "human_comment": comment,
        "utility_signal": usefulness,
        "risk_band": decision.get("risk_band"),
        "gate": gate,
        "output_mode": mode,
        "preflight_score": pf.get("preflight_score"),
        "hallucination_budget": budget.get("hallucination_budget"),
        "adjusted_risk": decision.get("adjusted_risk"),
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": "synthetic_feedback_seed",
        "auto_apply": False,
    }

def load_feedback(repo: Path, runs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    feedback_dir = repo / "inputs" / "runner_feedback"
    feedback: List[Dict[str, Any]] = []
    if feedback_dir.exists():
        for path in sorted(feedback_dir.glob("*.json")):
            data = load_json(path, {})
            if isinstance(data, dict) and "feedback" in data and isinstance(data["feedback"], list):
                feedback.extend(data["feedback"])
            elif isinstance(data, dict):
                feedback.append(data)
    if feedback:
        for item in feedback:
            item.setdefault("auto_apply", False)
            item.setdefault("source", "user_feedback_file")
        return feedback
    return [default_feedback_for_run(run, idx) for idx, run in enumerate(runs, start=1)]

def analyze_feedback(feedback: List[Dict[str, Any]], runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    run_by_id = {run.get("case_id"): run for run in runs}
    label_distribution: Dict[str, int] = defaultdict(int)
    mode_distribution: Dict[str, int] = defaultdict(int)
    risk_band_distribution: Dict[str, int] = defaultdict(int)
    gate_distribution: Dict[str, int] = defaultdict(int)

    over_conservative = []
    false_block = []
    false_allow = []
    useful = []
    safe = []

    for item in feedback:
        label = item.get("feedback_label", "UNKNOWN")
        case_id = item.get("case_id")
        run = run_by_id.get(case_id, {})
        decision = run.get("decision", {})
        gate = item.get("gate") or decision.get("gate")
        mode = item.get("output_mode") or decision.get("output_mode")
        risk_band = item.get("risk_band") or decision.get("risk_band")

        label_distribution[label] += 1
        if mode:
            mode_distribution[mode] += 1
        if risk_band:
            risk_band_distribution[risk_band] += 1
        if gate:
            gate_distribution[gate] += 1

        if label == "OVER_CONSERVATIVE_CANDIDATE":
            over_conservative.append(case_id)
        if label == "FALSE_BLOCK_CANDIDATE":
            false_block.append(case_id)
        if label == "FALSE_ALLOW_CANDIDATE":
            false_allow.append(case_id)
        if label in {"OUTPUT_USEFUL", "REVIEW_APPROPRIATE", "BLOCK_APPROPRIATE", "NEEDS_MORE_EVIDENCE"}:
            safe.append(case_id)
        if label in {"OUTPUT_USEFUL", "REVIEW_APPROPRIATE", "NEEDS_MORE_EVIDENCE"}:
            useful.append(case_id)

    return {
        "feedback_count": len(feedback),
        "label_distribution": dict(sorted(label_distribution.items())),
        "gate_distribution": dict(sorted(gate_distribution.items())),
        "output_mode_distribution": dict(sorted(mode_distribution.items())),
        "risk_band_distribution": dict(sorted(risk_band_distribution.items())),
        "safe_feedback_rate_pct": pct(len(safe), len(feedback)),
        "useful_feedback_rate_pct": pct(len(useful), len(feedback)),
        "over_conservative_cases": over_conservative,
        "false_block_candidate_cases": false_block,
        "false_allow_candidate_cases": false_allow,
    }

def build_recommendations(analysis: Dict[str, Any], runs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    recommendations = []
    over_conservative = analysis.get("over_conservative_cases", [])
    false_block = analysis.get("false_block_candidate_cases", [])
    false_allow = analysis.get("false_allow_candidate_cases", [])

    if over_conservative:
        recommendations.append({
            "id": "CAL-001",
            "target": "review_threshold_or_output_mode",
            "recommendation": "Inspect medium-risk HUMAN_REVIEW_REQUIRED cases in controlled active domains for possible ALLOW_WITH_WARNING or EVIDENCE_REQUEST split.",
            "cases": over_conservative,
            "auto_apply": False,
            "requires_human_approval": True,
        })
    else:
        recommendations.append({
            "id": "CAL-001",
            "target": "review_threshold_or_output_mode",
            "recommendation": "No immediate threshold relaxation. Review behavior remains appropriate on current feedback seed.",
            "cases": [],
            "auto_apply": False,
            "requires_human_approval": True,
        })

    if false_block:
        recommendations.append({
            "id": "CAL-002",
            "target": "block_policy",
            "recommendation": "Investigate false block candidates before changing block policy.",
            "cases": false_block,
            "auto_apply": False,
            "requires_human_approval": True,
        })
    else:
        recommendations.append({
            "id": "CAL-002",
            "target": "block_policy",
            "recommendation": "No false block candidates detected. Maintain unsupported/execution block policy.",
            "cases": [],
            "auto_apply": False,
            "requires_human_approval": True,
        })

    if false_allow:
        recommendations.append({
            "id": "CAL-003",
            "target": "allow_policy",
            "recommendation": "Investigate false allow candidates and consider stricter evidence/budget gating.",
            "cases": false_allow,
            "auto_apply": False,
            "requires_human_approval": True,
        })
    else:
        recommendations.append({
            "id": "CAL-003",
            "target": "allow_policy",
            "recommendation": "No false allow candidates detected.",
            "cases": [],
            "auto_apply": False,
            "requires_human_approval": True,
        })

    recommendations.append({
        "id": "CAL-004",
        "target": "feedback_collection",
        "recommendation": "Collect at least 20 controlled anonymized cases before any threshold proposal can move from candidate to approved.",
        "cases": [],
        "auto_apply": False,
        "requires_human_approval": True,
    })

    return recommendations

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    upstream = load_json(out / "prod651a_680a_business_runner_readiness.json", {})
    upstream_ready = upstream.get("decision") == "READY_FOR_INTERACTIVE_FEEDBACK_CALIBRATION_LOOP"

    runs_payload = load_json(out / "prod651a_680a_business_runner_runs.json", {})
    runs = runs_payload.get("runs", [])
    if not runs:
        raise SystemExit("No PROD-651A runner runs found. Run PROD-651A first.")

    feedback = load_feedback(repo, runs)
    analysis = analyze_feedback(feedback, runs)
    recommendations = build_recommendations(analysis, runs)

    status = {
        "status": "PASS" if upstream_ready else "WARN",
        "generated_at": generated_at,
        "phase": "Interactive Runner Feedback Calibration Loop",
        "mode": "controlled_feedback_loop_no_auto_mutation",
        "case_count": len(runs),
        "feedback_count": len(feedback),
        "safe_feedback_rate_pct": analysis["safe_feedback_rate_pct"],
        "useful_feedback_rate_pct": analysis["useful_feedback_rate_pct"],
        "auto_apply": False,
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    taxonomy = {
        "status": "PASS",
        "feedback_labels": [
            {"label": "REVIEW_APPROPRIATE", "meaning": "Human review packet is a safe and useful output for the case."},
            {"label": "BLOCK_APPROPRIATE", "meaning": "Block is appropriate due to unsupported domain, external execution or unsafe request."},
            {"label": "NEEDS_MORE_EVIDENCE", "meaning": "System should ask for more evidence before answering."},
            {"label": "OVER_CONSERVATIVE_CANDIDATE", "meaning": "System may be too conservative; investigate before changing threshold."},
            {"label": "FALSE_ALLOW_CANDIDATE", "meaning": "System may have allowed too much; investigate urgently."},
            {"label": "FALSE_BLOCK_CANDIDATE", "meaning": "System may have blocked too much; investigate before changing block policy."},
            {"label": "OUTPUT_USEFUL", "meaning": "Output was useful under current safety constraints."},
            {"label": "OUTPUT_NOT_USEFUL", "meaning": "Output did not help enough; inspect output mode or evidence request."},
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    feedback_payload = {
        "status": "PASS",
        "feedback_count": len(feedback),
        "feedback": feedback,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    analysis_payload = {
        "status": "PASS",
        "feedback_count": len(feedback),
        "analysis": analysis,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    calibration_payload = {
        "status": "PASS",
        "auto_apply": False,
        "automatic_threshold_mutation_allowed": False,
        "recommendations": recommendations,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    telemetry = {
        "status": "PASS",
        "event_count": len(feedback) + len(recommendations),
        "events": (
            [
                {
                    "event_type": "RUNNER_FEEDBACK_RECEIVED",
                    "feedback_id": item.get("feedback_id"),
                    "case_id": item.get("case_id"),
                    "feedback_label": item.get("feedback_label"),
                    "auto_apply": False,
                }
                for item in feedback
            ]
            + [
                {
                    "event_type": "CALIBRATION_RECOMMENDATION_CREATED",
                    "recommendation_id": rec["id"],
                    "target": rec["target"],
                    "auto_apply": False,
                }
                for rec in recommendations
            ]
        ),
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness = {
        "status": "PASS" if upstream_ready else "WARN",
        "decision": "READY_FOR_CONTROLLED_20_CASE_FEEDBACK_PILOT" if upstream_ready else "REVIEW_UPSTREAM_RISK_HOTFIX_READINESS",
        "case_count": len(runs),
        "feedback_count": len(feedback),
        "ready_for": [
            "controlled 20-case feedback pilot",
            "human feedback capture",
            "non-mutating calibration recommendations",
            "false review/block/allow candidate discovery",
        ],
        "not_ready_for": [
            "production activation",
            "autonomous external execution",
            "automatic threshold mutation",
            "client-facing guarantees",
            "unapproved real company data",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS" if upstream_ready and calibration_payload["auto_apply"] is False else "WARN",
        "audit": "Interactive Runner Feedback Calibration Loop audit",
        "case_count": len(runs),
        "feedback_count": len(feedback),
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "auto_apply": False,
        "finding": "PASS: feedback loop captures human/user feedback and creates non-mutating calibration recommendations.",
        "readiness": readiness["decision"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    outputs = {
        "prod681_720_feedback_loop_status.json": status,
        "prod681_720_feedback_events.json": feedback_payload,
        "prod681_720_feedback_analysis.json": analysis_payload,
        "prod681_720_feedback_taxonomy.json": taxonomy,
        "prod681_720_calibration_recommendations.json": calibration_payload,
        "prod681_720_feedback_telemetry.json": telemetry,
        "prod681_720_feedback_readiness.json": readiness,
        "prod681_720_feedback_audit_report.json": audit,
    }

    for name, obj in outputs.items():
        write_json(out / name, obj)

    report = [
        "# PROD-681..720 Interactive Runner Feedback Calibration Loop",
        "",
        f"- Status: `{audit['status']}`",
        f"- Case count: `{len(runs)}`",
        f"- Feedback count: `{len(feedback)}`",
        f"- Decision: `{readiness['decision']}`",
        f"- Auto apply: `{status['auto_apply']}`",
        f"- External execution allowed: `{status['external_execution_allowed']}`",
        f"- Automatic threshold mutation allowed: `{status['automatic_threshold_mutation_allowed']}`",
        "",
        "## Feedback Distribution",
    ]
    for key, value in analysis["label_distribution"].items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Gate Distribution"]
    for key, value in analysis["gate_distribution"].items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Calibration Recommendations"]
    for rec in recommendations:
        report.append(f"- `{rec['id']}` `{rec['target']}`: {rec['recommendation']} / auto_apply `{rec['auto_apply']}`")
    report += ["", "## Next Recommended Bundle", "- `PROD-721 Controlled 20-Case Business Pilot Pack`"]
    write_text(out / "prod681_720_feedback_calibration_report.md", "\n".join(report) + "\n")

    result = {
        "task": "PROD-681..720",
        "status": audit["status"],
        "phase": "Interactive Runner Feedback Calibration Loop",
        "decision": readiness["decision"],
        "outputs": ["outputs/" + key for key in outputs.keys()],
        "next_recommended_bundle": "PROD-721 Controlled 20-Case Business Pilot Pack",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod681_720_result.json", result)
    write_text(out / "prod681_720_report.md", "# PROD-681..720 Report\n\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n")
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

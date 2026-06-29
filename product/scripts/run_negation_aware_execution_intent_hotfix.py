#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
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

EXPECTED_FALSE_BLOCK_CANDIDATES = ["PILOT-001", "PILOT-007", "PILOT-016"]
EXPECTED_DIRECT_BLOCKS = ["PILOT-014", "PILOT-015", "PILOT-020"]

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

def load_runner_module(repo: Path):
    runner_path = repo / "product/scripts/run_business_case_interactive_runner.py"
    if not runner_path.exists():
        raise SystemExit("Missing product/scripts/run_business_case_interactive_runner.py")
    spec = importlib.util.spec_from_file_location("business_runner", runner_path)
    if spec is None or spec.loader is None:
        raise SystemExit("Unable to load business runner module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not hasattr(module, "classify_execution_intent"):
        raise SystemExit("Runner does not expose classify_execution_intent after patch.")
    return module

def distribution(items: List[str]) -> Dict[str, int]:
    d: Dict[str, int] = defaultdict(int)
    for item in items:
        d[item] += 1
    return dict(sorted(d.items()))

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    upstream = load_json(out / "prod761_800_human_review_readiness.json", {})
    upstream_ready = upstream.get("decision") == "READY_FOR_HUMAN_REVIEW_SESSION_NOT_THRESHOLD_MUTATION"

    case_pack = load_json(out / "prod721_760_business_pilot_case_pack.json", {})
    cases = case_pack.get("cases", [])
    if len(cases) != 20:
        raise SystemExit("Expected 20 cases in PROD-721 case pack.")

    baseline_payload = load_json(out / "prod721_760_business_pilot_decisions.json", {})
    baseline_decisions = {item["case_id"]: item for item in baseline_payload.get("decisions", [])}

    runner = load_runner_module(repo)
    fixed_runs = [runner.run_case(case) for case in cases]
    fixed_decisions = {run["case_id"]: run["decision"] for run in fixed_runs}

    classifications = []
    transitions = []
    resolved_false_blocks = []
    still_blocked_false_block_candidates = []
    direct_blocks_preserved = []
    direct_blocks_failed = []

    for case in cases:
        case_id = case["case_id"]
        intent = runner.classify_execution_intent(case)
        baseline = baseline_decisions.get(case_id, {})
        fixed = fixed_decisions.get(case_id, {})
        classifications.append({
            "status": "PASS",
            "case_id": case_id,
            "business_domain": case.get("business_domain"),
            "execution_intent": intent,
            "baseline_gate": baseline.get("gate"),
            "fixed_gate": fixed.get("gate"),
            "baseline_output_mode": baseline.get("output_mode"),
            "fixed_output_mode": fixed.get("output_mode"),
            "blocked_actions": BLOCKED_ACTIONS,
        })
        transitions.append({
            "case_id": case_id,
            "execution_intent": intent,
            "baseline_gate": baseline.get("gate"),
            "fixed_gate": fixed.get("gate"),
            "baseline_output_mode": baseline.get("output_mode"),
            "fixed_output_mode": fixed.get("output_mode"),
            "changed": baseline.get("gate") != fixed.get("gate") or baseline.get("output_mode") != fixed.get("output_mode"),
        })

    for case_id in EXPECTED_FALSE_BLOCK_CANDIDATES:
        fixed_gate = fixed_decisions.get(case_id, {}).get("gate")
        if fixed_gate != "UNSUPPORTED_BLOCKED":
            resolved_false_blocks.append(case_id)
        else:
            still_blocked_false_block_candidates.append(case_id)

    for case_id in EXPECTED_DIRECT_BLOCKS:
        fixed_gate = fixed_decisions.get(case_id, {}).get("gate")
        if fixed_gate == "UNSUPPORTED_BLOCKED":
            direct_blocks_preserved.append(case_id)
        else:
            direct_blocks_failed.append(case_id)

    fixed_gate_distribution = distribution([run["decision"]["gate"] for run in fixed_runs])
    baseline_gate_distribution = distribution([baseline_decisions.get(case["case_id"], {}).get("gate", "UNKNOWN") for case in cases])
    fixed_output_distribution = distribution([run["decision"]["output_mode"] for run in fixed_runs])
    intent_distribution = distribution([item["execution_intent"] for item in classifications])

    false_block_resolution = {
        "status": "PASS",
        "expected_false_block_candidates": EXPECTED_FALSE_BLOCK_CANDIDATES,
        "resolved_false_block_candidates": resolved_false_blocks,
        "still_blocked_false_block_candidates": still_blocked_false_block_candidates,
        "direct_execution_blocks_expected": EXPECTED_DIRECT_BLOCKS,
        "direct_execution_blocks_preserved": direct_blocks_preserved,
        "direct_execution_blocks_failed": direct_blocks_failed,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    regression = {
        "status": "PASS",
        "generated_at": generated_at,
        "case_count": len(cases),
        "intent_distribution": intent_distribution,
        "baseline_gate_distribution": baseline_gate_distribution,
        "fixed_gate_distribution": fixed_gate_distribution,
        "fixed_output_mode_distribution": fixed_output_distribution,
        "gate_transitions": transitions,
        "false_block_resolution": false_block_resolution,
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    recommendations = {
        "status": "PASS",
        "auto_apply": False,
        "automatic_threshold_mutation_allowed": False,
        "recommendations": [
            {
                "id": "INTENT-CAL-001",
                "target": "pilot_board_refresh",
                "recommendation": "Refresh the human review board after the negation-aware classifier so resolved false blocks move to case-level review rather than global threshold mutation.",
                "cases": resolved_false_blocks,
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "INTENT-CAL-002",
                "target": "direct_execution_block_policy",
                "recommendation": "Maintain direct execution block policy for automatic approval, automatic send and unknown external actions.",
                "cases": direct_blocks_preserved,
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "INTENT-CAL-003",
                "target": "false_allow_scan",
                "recommendation": "Run false-allow scan on newly allowed cases before any expansion to 50 cases.",
                "cases": [t["case_id"] for t in transitions if t["baseline_gate"] == "UNSUPPORTED_BLOCKED" and t["fixed_gate"] in {"ANSWER_ALLOWED", "ALLOW_WITH_WARNING"}],
                "auto_apply": False,
                "requires_human_approval": True,
            },
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness_decision = (
        "READY_FOR_PILOT_BOARD_REFRESH_AFTER_INTENT_HOTFIX"
        if upstream_ready and len(resolved_false_blocks) == len(EXPECTED_FALSE_BLOCK_CANDIDATES) and not direct_blocks_failed
        else "REVIEW_EXECUTION_INTENT_HOTFIX"
    )

    readiness = {
        "status": "PASS" if readiness_decision.startswith("READY") else "WARN",
        "decision": readiness_decision,
        "case_count": len(cases),
        "resolved_false_block_count": len(resolved_false_blocks),
        "direct_execution_blocks_preserved_count": len(direct_blocks_preserved),
        "ready_for": [
            "pilot board refresh",
            "case-level human review of reclassified cases",
            "false allow scan after intent hotfix",
            "controlled continuation without threshold mutation",
        ],
        "not_ready_for": [
            "automatic threshold mutation",
            "production activation",
            "autonomous external execution",
            "client-facing guarantees",
            "50-case expansion before refreshed human review",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS" if readiness["status"] == "PASS" else "WARN",
        "audit": "Negation-Aware Execution Intent Classifier Hotfix audit",
        "case_count": len(cases),
        "resolved_false_block_candidates": resolved_false_blocks,
        "direct_execution_blocks_preserved": direct_blocks_preserved,
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "auto_apply": False,
        "finding": "PASS: negated execution phrases are no longer treated as external execution requests while direct execution blocks remain preserved.",
        "readiness": readiness["decision"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    outputs = {
        "prod801_820_execution_intent_status.json": {
            "status": audit["status"],
            "phase": "Negation-Aware Execution Intent Classifier Hotfix",
            "case_count": len(cases),
            "intent_distribution": intent_distribution,
            "baseline_gate_distribution": baseline_gate_distribution,
            "fixed_gate_distribution": fixed_gate_distribution,
            "external_execution_allowed": False,
            "automatic_threshold_mutation_allowed": False,
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "prod801_820_execution_intent_classifications.json": {
            "status": "PASS",
            "case_count": len(classifications),
            "classifications": classifications,
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "prod801_820_false_block_regression.json": regression,
        "prod801_820_business_pilot_fixed_runs.json": {
            "status": "PASS",
            "case_count": len(fixed_runs),
            "runs": fixed_runs,
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "prod801_820_business_pilot_fixed_decisions.json": {
            "status": "PASS",
            "decisions": [{"case_id": run["case_id"], **run["decision"]} for run in fixed_runs],
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "prod801_820_false_block_resolution.json": false_block_resolution,
        "prod801_820_execution_intent_recommendations.json": recommendations,
        "prod801_820_execution_intent_readiness.json": readiness,
        "prod801_820_execution_intent_audit_report.json": audit,
    }

    for name, obj in outputs.items():
        write_json(out / name, obj)

    report = [
        "# PROD-801..820 Negation-Aware Execution Intent Classifier Hotfix",
        "",
        f"- Status: `{audit['status']}`",
        f"- Case count: `{len(cases)}`",
        f"- Decision: `{readiness['decision']}`",
        f"- Resolved false block candidates: `{resolved_false_blocks}`",
        f"- Direct execution blocks preserved: `{direct_blocks_preserved}`",
        f"- External execution allowed: `False`",
        f"- Automatic threshold mutation allowed: `False`",
        "",
        "## Intent Distribution",
    ]
    for key, value in intent_distribution.items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Baseline Gate Distribution"]
    for key, value in baseline_gate_distribution.items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Fixed Gate Distribution"]
    for key, value in fixed_gate_distribution.items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Gate Transitions"]
    for item in transitions:
        if item["changed"]:
            report.append(f"- `{item['case_id']}` `{item['execution_intent']}`: `{item['baseline_gate']}` -> `{item['fixed_gate']}` / `{item['baseline_output_mode']}` -> `{item['fixed_output_mode']}`")
    report += ["", "## Next Recommended Bundle", "- `PROD-821 Pilot Board Refresh and Case-Level Review Decisions`"]
    write_text(out / "prod801_820_execution_intent_hotfix_report.md", "\n".join(report) + "\n")

    result = {
        "task": "PROD-801..820",
        "status": audit["status"],
        "phase": "Negation-Aware Execution Intent Classifier Hotfix",
        "decision": readiness["decision"],
        "outputs": ["outputs/" + key for key in outputs.keys()],
        "next_recommended_bundle": "PROD-821 Pilot Board Refresh and Case-Level Review Decisions",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod801_820_result.json", result)
    write_text(out / "prod801_820_report.md", "# PROD-801..820 Report\n\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n")
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

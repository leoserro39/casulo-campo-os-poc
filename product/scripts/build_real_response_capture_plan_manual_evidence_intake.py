#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GOV = ROOT / "outputs" / "prod1861_1900_calibration_governance_threshold_readiness_pack.json"
TEMPLATE = ROOT / "product/gpt/captures/manual_real_response_intake_template.json"
PROMPTS = ROOT / "product/gpt/captures/real_response_capture_prompt_pack.md"
OUT = ROOT / "outputs"

CAPTURE_MODES = [
    "MANUAL_PASTED_GPT_PURE",
    "MANUAL_PASTED_GPT_STACK_GROUNDED",
    "CUSTOM_GPT_ACTION_CAPTURED",
    "API_CAPTURED",
    "SIMULATED_FIXTURE",
    "UNKNOWN_OR_UNTRUSTED"
]

CALIBRATION_ELIGIBLE_MODES = [
    "MANUAL_PASTED_GPT_PURE",
    "MANUAL_PASTED_GPT_STACK_GROUNDED"
]

EXCLUDED_MODES = [
    "SIMULATED_FIXTURE",
    "UNKNOWN_OR_UNTRUSTED"
]

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
    "production_neo4j_connection",
    "production_graph_write",
    "final_answer_generation_without_boundary",
    "gpt_call",
    "codex_execution",
    "public_api_publication",
    "custom_gpt_connection_without_human_approval",
    "final_threshold_calibration",
    "final_weight_calibration"
]

def main():
    errors = []
    gov = {}

    if not GOV.exists():
        errors.append(f"Missing governance readiness pack: {GOV}")
    else:
        gov = json.loads(GOV.read_text(encoding="utf-8"))

    template = json.loads(TEMPLATE.read_text(encoding="utf-8")) if TEMPLATE.exists() else {}
    prompt_text = PROMPTS.read_text(encoding="utf-8") if PROMPTS.exists() else ""

    capture_plan = {
        "mode": "manual_real_response_capture_plan_no_automatic_gpt_call",
        "governance_source_decision": gov.get("decision"),
        "manual_capture_allowed": True,
        "automatic_gpt_call_allowed": False,
        "custom_gpt_connection_allowed": False,
        "api_capture_allowed": False,
        "capture_modes": CAPTURE_MODES,
        "calibration_eligible_modes_after_review": CALIBRATION_ELIGIBLE_MODES,
        "excluded_modes": EXCLUDED_MODES,
        "manual_intake_template": str(TEMPLATE.relative_to(ROOT)),
        "prompt_pack": str(PROMPTS.relative_to(ROOT)),
        "minimum_real_capture_set": {
            "pure_response_count": 4,
            "stack_grounded_response_count": 4,
            "total_minimum": 8,
            "requires_human_review": True,
            "requires_anonymization": True
        },
        "calibration_status": "NOT_CALIBRATED_REAL_CAPTURE_PLAN_ONLY"
    }

    intake_rules = {
        "must_label_capture_mode": True,
        "must_record_prompt": True,
        "must_record_raw_response": True,
        "must_record_context_packet_reference_when_used": True,
        "must_mark_client_or_sensitive_data": True,
        "must_anonymize_before_calibration": True,
        "must_human_review_before_calibration": True,
        "unknown_origin_excluded": True,
        "simulated_fixture_excluded_from_real_calibration": True
    }

    checks = {
        "governance_pack_exists": GOV.exists(),
        "governance_pack_status_pass": gov.get("status") == "PASS",
        "governance_threshold_go_false": gov.get("readiness", {}).get("go_no_go", {}).get("threshold_calibration_go") is False,
        "manual_template_exists": TEMPLATE.exists(),
        "prompt_pack_exists": PROMPTS.exists(),
        "capture_mode_count": len(CAPTURE_MODES),
        "has_manual_pure_mode": "MANUAL_PASTED_GPT_PURE" in CAPTURE_MODES,
        "has_manual_stack_grounded_mode": "MANUAL_PASTED_GPT_STACK_GROUNDED" in CAPTURE_MODES,
        "simulated_fixture_excluded": "SIMULATED_FIXTURE" in EXCLUDED_MODES,
        "unknown_untrusted_excluded": "UNKNOWN_OR_UNTRUSTED" in EXCLUDED_MODES,
        "automatic_gpt_call_blocked": capture_plan["automatic_gpt_call_allowed"] is False,
        "custom_gpt_connection_blocked": capture_plan["custom_gpt_connection_allowed"] is False,
        "api_capture_blocked": capture_plan["api_capture_allowed"] is False,
        "prompt_pack_has_four_pairs": prompt_text.count("## Prompt Pair") >= 4,
        "calibration_status": "NOT_CALIBRATED_REAL_CAPTURE_PLAN_ONLY"
    }

    if not checks["governance_pack_status_pass"]:
        errors.append("Governance readiness pack is not PASS")
    if not checks["governance_threshold_go_false"]:
        errors.append("Governance pack must keep threshold calibration as NO-GO")
    if not checks["manual_template_exists"]:
        errors.append("Manual intake template is missing")
    if not checks["prompt_pack_exists"]:
        errors.append("Prompt pack is missing")
    if not checks["automatic_gpt_call_blocked"]:
        errors.append("Automatic GPT call must remain blocked")
    if not checks["simulated_fixture_excluded"]:
        errors.append("Simulated fixture must be excluded from real calibration")

    status = "PASS" if not errors else "FAIL"
    decision = "REAL_RESPONSE_CAPTURE_PLAN_READY_MANUAL_INTAKE_ONLY" if status == "PASS" else "REAL_RESPONSE_CAPTURE_PLAN_NOT_READY"

    result = {
        "status": status,
        "phase": "PROD-1901..1940",
        "decision": decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "capture_plan": capture_plan,
        "intake_rules": intake_rules,
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED_ACTIONS
    }

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "prod1901_1940_real_response_capture_plan_manual_evidence_intake.json"
    md_path = OUT / "prod1901_1940_real_response_capture_plan_manual_evidence_intake.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PROD-1901..1940 Real Response Capture Plan and Manual Evidence Intake",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{decision}`",
        f"- Calibration: `{capture_plan['calibration_status']}`",
        f"- Manual capture allowed: `{capture_plan['manual_capture_allowed']}`",
        f"- Automatic GPT call allowed: `{capture_plan['automatic_gpt_call_allowed']}`",
        f"- Custom GPT connection allowed: `{capture_plan['custom_gpt_connection_allowed']}`",
        f"- Minimum pure responses: `{capture_plan['minimum_real_capture_set']['pure_response_count']}`",
        f"- Minimum stack-grounded responses: `{capture_plan['minimum_real_capture_set']['stack_grounded_response_count']}`",
        "",
        "## Capture Modes"
    ]

    for mode in CAPTURE_MODES:
        marker = "eligible after review" if mode in CALIBRATION_ELIGIBLE_MODES else "excluded or future-only"
        md.append(f"- {mode}: `{marker}`")

    md += ["", "## Intake Rules"]
    for key, value in intake_rules.items():
        md.append(f"- {key}: `{value}`")

    md += ["", "## Checks"]
    for key, value in checks.items():
        md.append(f"- {key}: `{value}`")

    md += ["", "## Errors"]
    if errors:
        for err in errors:
            md.append(f"- {err}")
    else:
        md.append("- None")

    md += [
        "",
        "## Boundary",
        "- Manual response capture plan only.",
        "- No automatic GPT call.",
        "- No Custom GPT connection approval.",
        "- No API capture approval.",
        "- No final thresholds.",
        "- No final weights.",
        "- No Codex execution.",
        "- No production connection.",
        "",
        "## Blocked Actions"
    ]
    for action in BLOCKED_ACTIONS:
        md.append(f"- {action}")

    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

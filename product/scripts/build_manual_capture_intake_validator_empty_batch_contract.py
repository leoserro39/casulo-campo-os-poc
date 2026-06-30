#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "outputs" / "prod1901_1940_real_response_capture_plan_manual_evidence_intake.json"
BATCH = ROOT / "product/gpt/captures/manual_real_response_intake_empty_batch.json"
VALIDATOR = ROOT / "product/scripts/validate_manual_real_response_intake_batch.py"
OUT = ROOT / "outputs"

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

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def run_validator():
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), str(BATCH)],
        cwd=str(ROOT),
        text=True,
        capture_output=True
    )
    stdout = proc.stdout.strip()
    try:
        parsed = json.loads(stdout)
    except Exception:
        parsed = {
            "status": "FAIL",
            "errors": ["validator output was not valid json"],
            "stdout": stdout,
            "stderr": proc.stderr
        }
    return proc.returncode, parsed

def main():
    errors = []

    if not SOURCE.exists():
        errors.append(f"Missing source capture plan: {SOURCE}")
        source = {}
    else:
        source = load(SOURCE)

    if not BATCH.exists():
        errors.append(f"Missing empty batch: {BATCH}")
        batch = {}
    else:
        batch = load(BATCH)

    if not VALIDATOR.exists():
        errors.append(f"Missing validator: {VALIDATOR}")

    returncode, validator_result = run_validator() if VALIDATOR.exists() and BATCH.exists() else (1, {"status": "FAIL", "errors": ["validator not run"]})

    validator = {
        "mode": "manual_real_response_intake_batch_validator",
        "validator_script": str(VALIDATOR.relative_to(ROOT)),
        "empty_batch": str(BATCH.relative_to(ROOT)),
        "empty_batch_allowed": True,
        "real_capture_required": False,
        "manual_capture_allowed": True,
        "automatic_gpt_call_allowed": False,
        "custom_gpt_connection_allowed": False,
        "api_capture_allowed": False,
        "validator_result": validator_result,
        "calibration_status": "NOT_CALIBRATED_VALIDATOR_AND_EMPTY_BATCH_ONLY"
    }

    checks = {
        "source_capture_plan_exists": SOURCE.exists(),
        "source_capture_plan_status_pass": source.get("status") == "PASS",
        "source_manual_capture_allowed": source.get("capture_plan", {}).get("manual_capture_allowed") is True,
        "source_automatic_gpt_call_blocked": source.get("capture_plan", {}).get("automatic_gpt_call_allowed") is False,
        "empty_batch_exists": BATCH.exists(),
        "empty_batch_record_count_zero": batch.get("record_count") == 0,
        "empty_batch_calibration_candidate_count_zero": batch.get("calibration_candidate_count") == 0,
        "empty_batch_not_calibrated": batch.get("calibration_status") == "NOT_CALIBRATED_EMPTY_BATCH_NO_REAL_RESPONSES",
        "validator_exists": VALIDATOR.exists(),
        "validator_passes_empty_batch": validator_result.get("status") == "PASS",
        "validator_returncode_zero": returncode == 0,
        "automatic_gpt_call_blocked": validator["automatic_gpt_call_allowed"] is False,
        "custom_gpt_connection_blocked": validator["custom_gpt_connection_allowed"] is False,
        "api_capture_blocked": validator["api_capture_allowed"] is False,
        "calibration_status": "NOT_CALIBRATED_VALIDATOR_AND_EMPTY_BATCH_ONLY"
    }

    if not checks["source_capture_plan_status_pass"]:
        errors.append("Source capture plan is not PASS")
    if not checks["source_manual_capture_allowed"]:
        errors.append("Source capture plan must allow manual capture")
    if not checks["source_automatic_gpt_call_blocked"]:
        errors.append("Source capture plan must block automatic GPT calls")
    if not checks["empty_batch_record_count_zero"]:
        errors.append("Empty batch must have zero records")
    if not checks["empty_batch_calibration_candidate_count_zero"]:
        errors.append("Empty batch must have zero calibration candidates")
    if not checks["validator_passes_empty_batch"]:
        errors.append("Validator must pass empty batch")

    status = "PASS" if not errors else "FAIL"
    decision = "MANUAL_CAPTURE_INTAKE_VALIDATOR_EMPTY_BATCH_READY" if status == "PASS" else "MANUAL_CAPTURE_INTAKE_VALIDATOR_EMPTY_BATCH_NOT_READY"

    result = {
        "status": status,
        "phase": "PROD-1941..1980",
        "decision": decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "validator": validator,
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED_ACTIONS
    }

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "prod1941_1980_manual_capture_intake_validator_empty_batch_contract.json"
    md_path = OUT / "prod1941_1980_manual_capture_intake_validator_empty_batch_contract.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PROD-1941..1980 Manual Capture Intake Validator and Empty Batch Contract",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{decision}`",
        f"- Calibration: `{validator['calibration_status']}`",
        f"- Real capture required: `{validator['real_capture_required']}`",
        f"- Empty batch allowed: `{validator['empty_batch_allowed']}`",
        f"- Manual capture allowed: `{validator['manual_capture_allowed']}`",
        f"- Automatic GPT call allowed: `{validator['automatic_gpt_call_allowed']}`",
        f"- Custom GPT connection allowed: `{validator['custom_gpt_connection_allowed']}`",
        f"- Empty batch record count: `{batch.get('record_count')}`",
        f"- Empty batch calibration candidates: `{batch.get('calibration_candidate_count')}`",
        "",
        "## Validator Result",
        f"- Status: `{validator_result.get('status')}`",
        f"- Errors: `{validator_result.get('errors')}`",
        f"- Warnings: `{validator_result.get('warnings')}`",
        "",
        "## Checks"
    ]

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
        "- Validator and empty batch only.",
        "- No real responses required yet.",
        "- No automatic GPT call.",
        "- No Custom GPT connection approval.",
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

#!/usr/bin/env python3
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "outputs" / "prod1941_1980_manual_capture_intake_validator_empty_batch_contract.json"
WORK_ORDER = ROOT / "product/gpt/captures/manual_real_response_batch_001_work_order.json"
RUNBOOK = ROOT / "product/gpt/captures/manual_real_response_batch_001_runbook.md"
EMPTY_BATCH = ROOT / "product/gpt/captures/manual_real_response_intake_empty_batch.json"
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

def validate_empty_batch():
    proc = subprocess.run(
        [sys.executable, str(VALIDATOR), str(EMPTY_BATCH)],
        cwd=str(ROOT),
        text=True,
        capture_output=True
    )
    try:
        payload = json.loads(proc.stdout)
    except Exception:
        payload = {"status": "FAIL", "errors": ["invalid validator output"], "stdout": proc.stdout, "stderr": proc.stderr}
    return proc.returncode, payload

def main():
    errors = []

    prior = load(PRIOR) if PRIOR.exists() else {}
    work_order = load(WORK_ORDER) if WORK_ORDER.exists() else {}

    rc, validator_result = validate_empty_batch() if VALIDATOR.exists() and EMPTY_BATCH.exists() else (1, {"status": "FAIL", "errors": ["validator or empty batch missing"]})

    prompt_pairs = work_order.get("prompt_pairs", [])
    expected_records = work_order.get("expected_records")
    derived_record_count = len(prompt_pairs) * 2

    batch_001 = {
        "batch_id": work_order.get("batch_id"),
        "batch_status": work_order.get("batch_status"),
        "capture_required_next": work_order.get("capture_required_next"),
        "expected_records": expected_records,
        "prompt_pair_count": len(prompt_pairs),
        "derived_record_count": derived_record_count,
        "runbook": str(RUNBOOK.relative_to(ROOT)),
        "work_order": str(WORK_ORDER.relative_to(ROOT)),
        "empty_batch_validator_result": validator_result,
        "manual_capture_allowed": True,
        "automatic_gpt_call_allowed": False,
        "custom_gpt_connection_allowed": False,
        "api_capture_allowed": False,
        "calibration_status": "NOT_CALIBRATED_BATCH_001_RUNBOOK_ONLY"
    }

    checks = {
        "prior_validator_phase_exists": PRIOR.exists(),
        "prior_validator_phase_pass": prior.get("status") == "PASS",
        "prior_decision_ready": prior.get("decision") == "MANUAL_CAPTURE_INTAKE_VALIDATOR_EMPTY_BATCH_READY",
        "work_order_exists": WORK_ORDER.exists(),
        "runbook_exists": RUNBOOK.exists(),
        "validator_exists": VALIDATOR.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "empty_batch_still_valid": validator_result.get("status") == "PASS" and rc == 0,
        "prompt_pair_count": len(prompt_pairs),
        "expected_prompt_pairs_four": len(prompt_pairs) == 4,
        "expected_records_eight": expected_records == 8,
        "derived_record_count_eight": derived_record_count == 8,
        "capture_required_next": work_order.get("capture_required_next") is True,
        "automatic_gpt_call_blocked": work_order.get("automatic_gpt_call_allowed") is False,
        "custom_gpt_connection_blocked": work_order.get("custom_gpt_connection_allowed") is False,
        "api_capture_blocked": work_order.get("api_capture_allowed") is False,
        "calibration_status": "NOT_CALIBRATED_BATCH_001_RUNBOOK_ONLY"
    }

    if not checks["prior_validator_phase_pass"]:
        errors.append("Prior validator phase is not PASS")
    if not checks["prior_decision_ready"]:
        errors.append("Prior validator decision is not ready")
    if not checks["work_order_exists"]:
        errors.append("Batch 001 work order is missing")
    if not checks["runbook_exists"]:
        errors.append("Batch 001 runbook is missing")
    if not checks["empty_batch_still_valid"]:
        errors.append("Empty intake batch must remain valid")
    if not checks["expected_prompt_pairs_four"]:
        errors.append("Batch 001 must define four prompt pairs")
    if not checks["expected_records_eight"]:
        errors.append("Batch 001 must expect eight records")
    if not checks["derived_record_count_eight"]:
        errors.append("Derived record count must be eight")
    if not checks["capture_required_next"]:
        errors.append("Batch 001 must require manual capture as next action")
    if not checks["automatic_gpt_call_blocked"]:
        errors.append("Automatic GPT call must remain blocked")

    status = "PASS" if not errors else "FAIL"
    decision = "MANUAL_REAL_RESPONSE_CAPTURE_BATCH_001_RUNBOOK_READY" if status == "PASS" else "MANUAL_REAL_RESPONSE_CAPTURE_BATCH_001_RUNBOOK_NOT_READY"

    result = {
        "status": status,
        "phase": "PROD-1981..2020",
        "decision": decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "batch_001": batch_001,
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED_ACTIONS
    }

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "prod1981_2020_manual_real_response_capture_batch_001_runbook.json"
    md_path = OUT / "prod1981_2020_manual_real_response_capture_batch_001_runbook.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PROD-1981..2020 Manual Real Response Capture Batch 001 Runbook",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{decision}`",
        f"- Batch ID: `{batch_001['batch_id']}`",
        f"- Batch status: `{batch_001['batch_status']}`",
        f"- Capture required next: `{batch_001['capture_required_next']}`",
        f"- Prompt pairs: `{batch_001['prompt_pair_count']}`",
        f"- Expected records: `{batch_001['expected_records']}`",
        f"- Derived record count: `{batch_001['derived_record_count']}`",
        f"- Calibration: `{batch_001['calibration_status']}`",
        f"- Automatic GPT call allowed: `{batch_001['automatic_gpt_call_allowed']}`",
        f"- Custom GPT connection allowed: `{batch_001['custom_gpt_connection_allowed']}`",
        "",
        "## Prompt Pairs"
    ]

    for pair in prompt_pairs:
        md += [
            f"### {pair['pair_id']}",
            f"- Boundary type: `{pair['boundary_type']}`",
            f"- Pure capture ID: `{pair['pure_capture_id']}`",
            f"- Stack capture ID: `{pair['stack_capture_id']}`",
            ""
        ]

    md += ["## Checks"]
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
        "- Runbook only.",
        "- No real responses included yet.",
        "- Manual capture is the next action.",
        "- No automatic GPT call.",
        "- No Custom GPT connection.",
        "- No API capture.",
        "- No final thresholds.",
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

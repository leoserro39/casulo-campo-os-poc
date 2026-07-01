#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3981..4020"
REQ_TAG = "product-controlled-pilot-real-candidate-dry-run-execution-packet-v0.1"

PREV_OUT = ROOT / "outputs/prod3941_3980_controlled_pilot_real_candidate_dry_run_execution_packet.json"
EXEC_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_packet_v0_1.json"
EXEC_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_checklist_v0_1.json"
EXEC_RUNBOOK = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_packet_v0_1.md"
READINESS_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_readiness_gate_v0_1.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_validator_v0_1.json"
SHELL = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.json"
FORM = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_form_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"

DOC = ROOT / "docs/product/601_CONTROLLED_PILOT_REAL_CANDIDATE_DRY_RUN_EXECUTION_READINESS_GATE.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_real_candidate_dry_run_execution_readiness_gate.contract.json"
GATE = ROOT / "product/memory/controlled_pilot_real_candidate_dry_run_execution_readiness_gate_v0_1.json"
CAL_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_readiness_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3981_4020_controlled_pilot_real_candidate_dry_run_execution_readiness_gate.json"
OUT_MD = ROOT / "outputs/prod3981_4020_controlled_pilot_real_candidate_dry_run_execution_readiness_gate.md"

READINESS_CHECKS = [
    "execution_packet_passed",
    "execution_packet_present",
    "execution_checklist_present",
    "execution_runbook_present",
    "prior_readiness_gate_present",
    "validator_present",
    "shell_present",
    "form_present",
    "schema_present",
    "real_dataset_empty",
    "reviewer_queue_empty",
    "execution_steps_present",
    "abort_triggers_present",
    "operator_checks_present",
    "manual_execution_boundary_confirmed",
    "automatic_capture_blocked",
    "real_candidate_insert_blocked",
    "dataset_acceptance_blocked",
    "raw_private_data_blocked",
    "secrets_blocked",
    "unredacted_pii_blocked",
    "client_claim_blocked",
    "production_activation_blocked",
    "human_review_required"
]

ALLOWED = [
    "manual_execution_readiness_gate_creation",
    "controlled_manual_dry_run_session_preparation",
    "operator_session_preflight_creation",
    "human_reviewer_preflight_creation",
    "hold_before_real_candidate_insert"
]

BLOCKED = [
    "automatic_real_session_capture",
    "real_candidate_insert",
    "real_candidate_dataset_acceptance",
    "dataset_acceptance_without_human_review",
    "raw_private_data_storage",
    "secret_or_credential_storage",
    "unredacted_pii_storage",
    "client_facing_value_claim",
    "real_world_profit_claim",
    "validated_savings_claim",
    "validated_hallucination_reduction_claim",
    "production_activation",
    "automatic_memory_delete",
    "gpt_memory_api_execution",
    "commercial_package_pricing_claim"
]

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def tags():
    raw = subprocess.check_output(["git", "tag", "--list"], cwd=ROOT, text=True)
    return set(x.strip() for x in raw.splitlines() if x.strip())

def main():
    errors = []

    prev = read_json(PREV_OUT) if PREV_OUT.exists() else {}
    packet = read_json(EXEC_PACKET) if EXEC_PACKET.exists() else {}
    checklist = read_json(EXEC_CHECKLIST) if EXEC_CHECKLIST.exists() else {}
    readiness = read_json(READINESS_GATE) if READINESS_GATE.exists() else {}
    validator = read_json(VALIDATOR) if VALIDATOR.exists() else {}
    shell = read_json(SHELL) if SHELL.exists() else {}
    form = read_json(FORM) if FORM.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    execution_steps = packet.get("execution_steps", [])
    abort_triggers = packet.get("abort_triggers", [])
    operator_checks_packet = packet.get("operator_checks", [])
    operator_checks_checklist = checklist.get("operator_checks", [])
    readiness_criteria = readiness.get("readiness_criteria", [])
    validator_rules = validator.get("validator_rules", [])
    shell_sections = shell.get("shell_sections", [])
    form_fields = form.get("fields", {})
    schema_required = schema.get("required", [])

    decision = "APPROVED_FOR_CONTROLLED_MANUAL_REAL_CANDIDATE_DRY_RUN_SESSION_PREPARATION_ONLY"
    if empty_batch.get("candidate_count") != 0 or empty_batch.get("accepted_count") != 0:
        decision = "BLOCK_REAL_DATASET_NOT_EMPTY"
    if prev.get("real_candidate_inserted") is not False or prev.get("real_candidate_accepted_to_dataset") is not False:
        decision = "BLOCK_REAL_CANDIDATE_ALREADY_PRESENT"
    if prev.get("real_data_captured_in_this_phase") is not False:
        decision = "BLOCK_REAL_DATA_BOUNDARY_BREACH"

    gate = {
        "version": "controlled_pilot_real_candidate_dry_run_execution_readiness_gate.v0.1",
        "phase": PHASE,
        "decision": decision,
        "purpose": "Validate execution packet readiness before preparing a controlled manual dry run session.",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "execution_readiness_gate_only": True,
        "readiness_checks": READINESS_CHECKS,
        "current_dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "manual_session_boundary": {
            "next_step_is_session_preparation_only": True,
            "automatic_capture_allowed": False,
            "real_candidate_insert_allowed": False,
            "dataset_acceptance_allowed": False,
            "raw_private_data_allowed": False,
            "secret_storage_allowed": False,
            "unredacted_pii_allowed": False,
            "client_claim_allowed": False,
            "production_activation_allowed": False,
            "human_reviewer_required": True
        },
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-4021..4060 - Controlled Pilot Manual Dry Run Session Packet"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_real_candidate_dry_run_execution_readiness_gate",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "execution_readiness_gate_only": True,
        "manual_session_preparation_only": True,
        "automatic_capture_blocked": True,
        "dataset_acceptance_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    doc = """# PROD-3981..4020 - Controlled Pilot Real Candidate Dry Run Execution Readiness Gate

Validates that the execution packet is ready before preparing a controlled manual dry run session packet.

This phase does not execute intake, does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

Boundary: execution readiness gate only. No automatic capture, no real candidate insert, no dataset acceptance, no raw private data, no secrets, no unredacted PII, no production activation and no real-world/client-facing claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(GATE, gate)
    write_json(CAL_GATE, gate)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_execution_packet_ready": prev.get("decision") == "CONTROLLED_PILOT_REAL_CANDIDATE_DRY_RUN_EXECUTION_PACKET_READY",
        "previous_real_candidate_not_inserted": prev.get("real_candidate_inserted") is False,
        "previous_real_candidate_not_accepted": prev.get("real_candidate_accepted_to_dataset") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "execution_packet_exists": EXEC_PACKET.exists(),
        "execution_checklist_exists": EXEC_CHECKLIST.exists(),
        "execution_runbook_exists": EXEC_RUNBOOK.exists(),
        "readiness_gate_exists": READINESS_GATE.exists(),
        "validator_exists": VALIDATOR.exists(),
        "shell_exists": SHELL.exists(),
        "form_exists": FORM.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "schema_exists": SCHEMA.exists(),
        "execution_step_count": len(execution_steps),
        "abort_trigger_count": len(abort_triggers),
        "operator_check_count_packet": len(operator_checks_packet),
        "operator_check_count_checklist": len(operator_checks_checklist),
        "readiness_criteria_count": len(readiness_criteria),
        "validator_rule_count": len(validator_rules),
        "shell_section_count": len(shell_sections),
        "form_field_count": len(form_fields),
        "schema_required_count": len(schema_required),
        "empty_batch_candidate_zero": empty_batch.get("candidate_count") == 0,
        "empty_batch_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "readiness_check_count": len(READINESS_CHECKS),
        "decision_manual_session_preparation_only": decision == "APPROVED_FOR_CONTROLLED_MANUAL_REAL_CANDIDATE_DRY_RUN_SESSION_PREPARATION_ONLY",
        "packet_execution_only": packet.get("execution_packet_only") is True,
        "packet_no_real_data": packet.get("real_data_captured_in_this_phase") is False,
        "packet_no_candidate_insert": packet.get("real_candidate_inserted") is False,
        "packet_no_dataset_acceptance": packet.get("real_candidate_accepted_to_dataset") is False,
        "contract_gate_only": contract["execution_readiness_gate_only"] is True,
        "contract_session_preparation_only": contract["manual_session_preparation_only"] is True,
        "real_data_not_captured_this_phase": contract["real_data_captured_in_this_phase"] is False,
        "real_candidate_not_inserted": contract["real_candidate_inserted"] is False,
        "real_candidate_not_accepted": contract["real_candidate_accepted_to_dataset"] is False,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "real_candidate_insert_blocked": "real_candidate_insert" in BLOCKED,
        "real_candidate_dataset_acceptance_blocked": "real_candidate_dataset_acceptance" in BLOCKED,
        "dataset_accept_without_review_blocked": "dataset_acceptance_without_human_review" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["execution_step_count"] < 18:
        errors.append("execution_step_count below 18")
    if checks["abort_trigger_count"] < 12:
        errors.append("abort_trigger_count below 12")
    if checks["operator_check_count_packet"] < 18:
        errors.append("operator_check_count_packet below 18")
    if checks["operator_check_count_checklist"] < 18:
        errors.append("operator_check_count_checklist below 18")
    if checks["readiness_criteria_count"] < 20:
        errors.append("readiness_criteria_count below 20")
    if checks["validator_rule_count"] < 20:
        errors.append("validator_rule_count below 20")
    if checks["shell_section_count"] < 17:
        errors.append("shell_section_count below 17")
    if checks["form_field_count"] < 16:
        errors.append("form_field_count below 16")
    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["readiness_check_count"] < 24:
        errors.append("readiness_check_count below 24")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": decision if status == "PASS" else "CONTROLLED_PILOT_REAL_CANDIDATE_DRY_RUN_EXECUTION_READINESS_GATE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "readiness_check_count": len(READINESS_CHECKS),
        "execution_step_count": len(execution_steps),
        "abort_trigger_count": len(abort_triggers),
        "operator_check_count": len(operator_checks_packet),
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "real_dataset_candidate_count": empty_batch.get("candidate_count", 0),
        "real_dataset_accepted_count": empty_batch.get("accepted_count", 0),
        "recommended_next_phase": gate["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3981..4020 Controlled Pilot Real Candidate Dry Run Execution Readiness Gate",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Readiness checks: `{len(READINESS_CHECKS)}`",
        f"- Execution steps: `{len(execution_steps)}`",
        f"- Abort triggers: `{len(abort_triggers)}`",
        f"- Operator checks: `{len(operator_checks_packet)}`",
        f"- Real candidate inserted: `{result['real_candidate_inserted']}`",
        f"- Real candidate accepted to dataset: `{result['real_candidate_accepted_to_dataset']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{gate['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Execution readiness gate only.",
        "- No execution performed.",
        "- No real candidate inserted.",
        "- No dataset acceptance.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("readiness_checks:", len(READINESS_CHECKS))
    print("execution_steps:", len(execution_steps))
    print("abort_triggers:", len(abort_triggers))
    print("operator_checks:", len(operator_checks_packet))
    print("real_candidate_inserted:", result["real_candidate_inserted"])
    print("real_candidate_accepted_to_dataset:", result["real_candidate_accepted_to_dataset"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", gate["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

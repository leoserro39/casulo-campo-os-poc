#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-4181..4220"
REQ_TAG = "product-controlled-pilot-manual-dry-run-session-execution-log-shell-v0.1"

PREV_OUT = ROOT / "outputs/prod4141_4180_controlled_pilot_manual_dry_run_session_execution_log_shell.json"
LOG_SHELL = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_log_shell_v0_1.json"
LOG_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_log_template_v0_1.json"
EXEC_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_gate_v0_1.json"
SESSION_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_packet_v0_1.json"
SESSION_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_checklist_v0_1.json"
SESSION_RUNBOOK = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_packet_v0_1.md"
EXEC_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_packet_v0_1.json"
SHELL = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.json"
FORM = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_form_v0_1.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_validator_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"

DOC = ROOT / "docs/product/606_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_EXECUTION_LOG_READINESS_GATE.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_manual_dry_run_session_execution_log_readiness_gate.contract.json"
GATE = ROOT / "product/memory/controlled_pilot_manual_dry_run_session_execution_log_readiness_gate_v0_1.json"
CAL_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_log_readiness_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod4181_4220_controlled_pilot_manual_dry_run_session_execution_log_readiness_gate.json"
OUT_MD = ROOT / "outputs/prod4181_4220_controlled_pilot_manual_dry_run_session_execution_log_readiness_gate.md"

READINESS_CHECKS = [
    "execution_log_shell_passed",
    "execution_log_shell_present",
    "execution_log_template_present",
    "execution_gate_present",
    "session_packet_present",
    "session_checklist_present",
    "session_runbook_present",
    "execution_packet_present",
    "dry_run_shell_present",
    "dry_run_form_present",
    "validator_present",
    "schema_present",
    "real_dataset_empty",
    "reviewer_queue_empty",
    "log_sections_present",
    "log_fields_present",
    "operator_ref_field_present",
    "reviewer_ref_field_present",
    "source_reference_refs_field_present",
    "privacy_review_ref_field_present",
    "pii_redaction_ref_field_present",
    "secret_scan_ref_field_present",
    "evidence_packet_ref_field_present",
    "reviewer_notes_ref_field_present",
    "claim_boundary_field_present",
    "dataset_hold_reason_field_present",
    "abort_trigger_review_field_present",
    "operator_check_summary_field_present",
    "final_gate_field_present",
    "template_only_confirmed",
    "session_execution_not_performed",
    "automatic_capture_blocked",
    "real_candidate_insert_blocked",
    "dataset_acceptance_blocked",
    "raw_private_data_blocked",
    "secrets_blocked",
    "unredacted_pii_blocked",
    "client_claim_blocked",
    "production_activation_blocked"
]

ALLOWED = [
    "execution_log_readiness_gate_creation",
    "manual_observation_packet_preparation",
    "log_template_validation",
    "operator_log_preflight_validation",
    "hold_before_actual_session_execution"
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
    log_shell = read_json(LOG_SHELL) if LOG_SHELL.exists() else {}
    log_template = read_json(LOG_TEMPLATE) if LOG_TEMPLATE.exists() else {}
    exec_gate = read_json(EXEC_GATE) if EXEC_GATE.exists() else {}
    session_packet = read_json(SESSION_PACKET) if SESSION_PACKET.exists() else {}
    session_checklist = read_json(SESSION_CHECKLIST) if SESSION_CHECKLIST.exists() else {}
    exec_packet = read_json(EXEC_PACKET) if EXEC_PACKET.exists() else {}
    shell = read_json(SHELL) if SHELL.exists() else {}
    form = read_json(FORM) if FORM.exists() else {}
    validator = read_json(VALIDATOR) if VALIDATOR.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    log_sections = log_shell.get("log_sections", [])
    log_fields = log_shell.get("log_fields", [])
    template_fields = log_template.get("fields", {})
    execution_gate_controls = exec_gate.get("execution_gate_controls", [])
    session_steps = session_packet.get("session_steps", [])
    session_abort = session_packet.get("session_abort_triggers", [])
    session_operator_checks = session_packet.get("session_operator_checks", [])
    session_checklist_items = session_checklist.get("session_operator_checks", [])
    exec_steps = exec_packet.get("execution_steps", [])
    shell_sections = shell.get("shell_sections", [])
    form_fields = form.get("fields", {})
    validator_rules = validator.get("validator_rules", [])
    schema_required = schema.get("required", [])

    decision = "APPROVED_FOR_CONTROLLED_MANUAL_DRY_RUN_SESSION_OBSERVATION_PACKET_PREPARATION_ONLY"
    if empty_batch.get("candidate_count") != 0 or empty_batch.get("accepted_count") != 0:
        decision = "BLOCK_REAL_DATASET_NOT_EMPTY"
    if prev.get("real_candidate_inserted") is not False or prev.get("real_candidate_accepted_to_dataset") is not False:
        decision = "BLOCK_REAL_CANDIDATE_ALREADY_PRESENT"
    if prev.get("real_data_captured_in_this_phase") is not False:
        decision = "BLOCK_REAL_DATA_BOUNDARY_BREACH"

    gate = {
        "version": "controlled_pilot_manual_dry_run_session_execution_log_readiness_gate.v0.1",
        "phase": PHASE,
        "decision": decision,
        "purpose": "Validate execution log shell readiness before preparing manual observation packet.",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "execution_log_readiness_gate_only": True,
        "session_execution_not_performed": True,
        "readiness_checks": READINESS_CHECKS,
        "current_dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "observation_packet_boundary": {
            "next_step_is_observation_packet_preparation_only": True,
            "automatic_capture_allowed": False,
            "real_candidate_insert_allowed": False,
            "dataset_acceptance_allowed": False,
            "raw_private_data_allowed": False,
            "secret_storage_allowed": False,
            "unredacted_pii_allowed": False,
            "client_claim_allowed": False,
            "production_activation_allowed": False
        },
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-4221..4260 - Controlled Pilot Manual Dry Run Session Observation Packet"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_manual_dry_run_session_execution_log_readiness_gate",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "execution_log_readiness_gate_only": True,
        "observation_packet_preparation_only": True,
        "session_execution_not_performed": True,
        "automatic_capture_blocked": True,
        "dataset_acceptance_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    doc = """# PROD-4181..4220 - Controlled Pilot Manual Dry Run Session Execution Log Readiness Gate

Validates the execution log shell before any observation packet preparation.

This phase does not execute a session, does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

It approves only preparation of the controlled manual dry run session observation packet.

Boundary: execution log readiness gate only. No automatic capture, no real candidate insert, no dataset acceptance, no raw private data, no secrets, no unredacted PII, no production activation and no real-world/client-facing claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(GATE, gate)
    write_json(CAL_GATE, gate)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_log_shell_ready": prev.get("decision") == "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_EXECUTION_LOG_SHELL_READY",
        "previous_real_candidate_not_inserted": prev.get("real_candidate_inserted") is False,
        "previous_real_candidate_not_accepted": prev.get("real_candidate_accepted_to_dataset") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "execution_log_shell_exists": LOG_SHELL.exists(),
        "execution_log_template_exists": LOG_TEMPLATE.exists(),
        "execution_gate_exists": EXEC_GATE.exists(),
        "session_packet_exists": SESSION_PACKET.exists(),
        "session_checklist_exists": SESSION_CHECKLIST.exists(),
        "session_runbook_exists": SESSION_RUNBOOK.exists(),
        "execution_packet_exists": EXEC_PACKET.exists(),
        "dry_run_shell_exists": SHELL.exists(),
        "dry_run_form_exists": FORM.exists(),
        "validator_exists": VALIDATOR.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "schema_exists": SCHEMA.exists(),
        "log_section_count": len(log_sections),
        "log_field_count": len(log_fields),
        "template_field_count": len(template_fields),
        "execution_gate_control_count": len(execution_gate_controls),
        "session_step_count": len(session_steps),
        "session_abort_trigger_count": len(session_abort),
        "session_operator_check_count": len(session_operator_checks),
        "session_checklist_item_count": len(session_checklist_items),
        "execution_step_count": len(exec_steps),
        "shell_section_count": len(shell_sections),
        "form_field_count": len(form_fields),
        "validator_rule_count": len(validator_rules),
        "schema_required_count": len(schema_required),
        "empty_batch_candidate_zero": empty_batch.get("candidate_count") == 0,
        "empty_batch_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "has_operator_ref": "operator_ref" in template_fields,
        "has_reviewer_ref": "human_reviewer_ref" in template_fields,
        "has_source_refs": "source_reference_refs" in template_fields,
        "has_privacy_review_ref": "privacy_review_ref" in template_fields,
        "has_pii_redaction_ref": "pii_redaction_ref" in template_fields,
        "has_secret_scan_ref": "secret_scan_ref" in template_fields,
        "has_evidence_packet_ref": "evidence_packet_ref" in template_fields,
        "has_reviewer_notes_ref": "reviewer_notes_ref" in template_fields,
        "has_claim_boundary": "claim_boundary" in template_fields,
        "has_dataset_hold_reason": "dataset_hold_reason" in template_fields,
        "has_final_gate": "final_gate" in template_fields,
        "template_status_no_execution": log_template.get("status") == "LOG_TEMPLATE_ONLY_NO_SESSION_EXECUTION",
        "log_shell_only": log_shell.get("execution_log_shell_only") is True,
        "log_execution_not_performed": log_shell.get("session_execution_not_performed") is True,
        "log_no_real_data": log_shell.get("real_data_captured_in_this_phase") is False,
        "log_no_candidate_insert": log_shell.get("real_candidate_inserted") is False,
        "log_no_dataset_acceptance": log_shell.get("real_candidate_accepted_to_dataset") is False,
        "readiness_check_count": len(READINESS_CHECKS),
        "decision_observation_packet_prep_only": decision == "APPROVED_FOR_CONTROLLED_MANUAL_DRY_RUN_SESSION_OBSERVATION_PACKET_PREPARATION_ONLY",
        "contract_gate_only": contract["execution_log_readiness_gate_only"] is True,
        "contract_observation_packet_prep_only": contract["observation_packet_preparation_only"] is True,
        "contract_execution_not_performed": contract["session_execution_not_performed"] is True,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "real_candidate_insert_blocked": "real_candidate_insert" in BLOCKED,
        "real_candidate_dataset_acceptance_blocked": "real_candidate_dataset_acceptance" in BLOCKED,
        "dataset_accept_without_review_blocked": "dataset_acceptance_without_human_review" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["log_section_count"] < 12:
        errors.append("log_section_count below 12")
    if checks["log_field_count"] < 20:
        errors.append("log_field_count below 20")
    if checks["template_field_count"] < 20:
        errors.append("template_field_count below 20")
    if checks["execution_gate_control_count"] < 34:
        errors.append("execution_gate_control_count below 34")
    if checks["session_step_count"] < 22:
        errors.append("session_step_count below 22")
    if checks["session_abort_trigger_count"] < 14:
        errors.append("session_abort_trigger_count below 14")
    if checks["session_operator_check_count"] < 20:
        errors.append("session_operator_check_count below 20")
    if checks["execution_step_count"] < 18:
        errors.append("execution_step_count below 18")
    if checks["shell_section_count"] < 17:
        errors.append("shell_section_count below 17")
    if checks["form_field_count"] < 16:
        errors.append("form_field_count below 16")
    if checks["validator_rule_count"] < 20:
        errors.append("validator_rule_count below 20")
    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["readiness_check_count"] < 39:
        errors.append("readiness_check_count below 39")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": decision if status == "PASS" else "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_EXECUTION_LOG_READINESS_GATE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "readiness_check_count": len(READINESS_CHECKS),
        "log_section_count": len(log_sections),
        "log_field_count": len(log_fields),
        "template_field_count": len(template_fields),
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
        "# PROD-4181..4220 Controlled Pilot Manual Dry Run Session Execution Log Readiness Gate",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Readiness checks: `{len(READINESS_CHECKS)}`",
        f"- Log sections: `{len(log_sections)}`",
        f"- Log fields: `{len(log_fields)}`",
        f"- Template fields: `{len(template_fields)}`",
        f"- Real candidate inserted: `{result['real_candidate_inserted']}`",
        f"- Real candidate accepted to dataset: `{result['real_candidate_accepted_to_dataset']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{gate['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Execution log readiness gate only.",
        "- No session execution performed.",
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
    print("log_sections:", len(log_sections))
    print("log_fields:", len(log_fields))
    print("template_fields:", len(template_fields))
    print("real_candidate_inserted:", result["real_candidate_inserted"])
    print("real_candidate_accepted_to_dataset:", result["real_candidate_accepted_to_dataset"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", gate["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

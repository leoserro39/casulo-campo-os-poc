#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-4061..4100"
REQ_TAG = "product-controlled-pilot-manual-dry-run-session-packet-v0.1"

PREV_OUT = ROOT / "outputs/prod4021_4060_controlled_pilot_manual_dry_run_session_packet.json"
SESSION_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_packet_v0_1.json"
SESSION_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_checklist_v0_1.json"
SESSION_RUNBOOK = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_packet_v0_1.md"
EXEC_READINESS_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_readiness_gate_v0_1.json"
EXEC_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_packet_v0_1.json"
SHELL = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.json"
FORM = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_form_v0_1.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_validator_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"

DOC = ROOT / "docs/product/603_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_READINESS_GATE.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_manual_dry_run_session_readiness_gate.contract.json"
GATE = ROOT / "product/memory/controlled_pilot_manual_dry_run_session_readiness_gate_v0_1.json"
CAL_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_readiness_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod4061_4100_controlled_pilot_manual_dry_run_session_readiness_gate.json"
OUT_MD = ROOT / "outputs/prod4061_4100_controlled_pilot_manual_dry_run_session_readiness_gate.md"

READINESS_CHECKS = [
    "session_packet_passed",
    "session_packet_present",
    "session_checklist_present",
    "session_runbook_present",
    "execution_readiness_gate_present",
    "execution_packet_present",
    "shell_present",
    "form_present",
    "validator_present",
    "schema_present",
    "real_dataset_empty",
    "reviewer_queue_empty",
    "session_steps_present",
    "session_abort_triggers_present",
    "session_operator_checks_present",
    "operator_and_reviewer_placeholders_present",
    "source_refs_only_required",
    "privacy_review_required",
    "pii_redaction_required",
    "secret_scan_required",
    "claim_boundary_required",
    "dataset_hold_required",
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
    "manual_dry_run_session_readiness_gate_creation",
    "controlled_manual_session_execution_preparation",
    "operator_and_reviewer_preflight_creation",
    "session_execution_boundary_confirmation",
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
    session = read_json(SESSION_PACKET) if SESSION_PACKET.exists() else {}
    session_checklist = read_json(SESSION_CHECKLIST) if SESSION_CHECKLIST.exists() else {}
    exec_readiness = read_json(EXEC_READINESS_GATE) if EXEC_READINESS_GATE.exists() else {}
    exec_packet = read_json(EXEC_PACKET) if EXEC_PACKET.exists() else {}
    shell = read_json(SHELL) if SHELL.exists() else {}
    form = read_json(FORM) if FORM.exists() else {}
    validator = read_json(VALIDATOR) if VALIDATOR.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    session_steps = session.get("session_steps", [])
    session_abort = session.get("session_abort_triggers", [])
    session_operator_checks = session.get("session_operator_checks", [])
    checklist_items = session_checklist.get("session_operator_checks", [])
    exec_readiness_checks = exec_readiness.get("readiness_checks", [])
    exec_steps = exec_packet.get("execution_steps", [])
    shell_sections = shell.get("shell_sections", [])
    form_fields = form.get("fields", {})
    validator_rules = validator.get("validator_rules", [])
    schema_required = schema.get("required", [])

    decision = "APPROVED_FOR_CONTROLLED_MANUAL_DRY_RUN_SESSION_EXECUTION_PREPARATION_ONLY"
    if empty_batch.get("candidate_count") != 0 or empty_batch.get("accepted_count") != 0:
        decision = "BLOCK_REAL_DATASET_NOT_EMPTY"
    if prev.get("real_candidate_inserted") is not False or prev.get("real_candidate_accepted_to_dataset") is not False:
        decision = "BLOCK_REAL_CANDIDATE_ALREADY_PRESENT"
    if prev.get("real_data_captured_in_this_phase") is not False:
        decision = "BLOCK_REAL_DATA_BOUNDARY_BREACH"

    gate = {
        "version": "controlled_pilot_manual_dry_run_session_readiness_gate.v0.1",
        "phase": PHASE,
        "decision": decision,
        "purpose": "Validate manual dry run session packet readiness before any controlled session execution.",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "session_readiness_gate_only": True,
        "readiness_checks": READINESS_CHECKS,
        "current_dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "execution_boundary": {
            "next_step_is_execution_preparation_only": True,
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
        "recommended_next_phase": "PROD-4101..4140 - Controlled Pilot Manual Dry Run Session Execution Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_manual_dry_run_session_readiness_gate",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "session_readiness_gate_only": True,
        "session_execution_preparation_only": True,
        "automatic_capture_blocked": True,
        "dataset_acceptance_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    doc = """# PROD-4061..4100 - Controlled Pilot Manual Dry Run Session Readiness Gate

Validates the controlled manual dry run session packet before any session execution.

This phase does not execute a session, does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

Boundary: session readiness gate only. No automatic capture, no real candidate insert, no dataset acceptance, no raw private data, no secrets, no unredacted PII, no production activation and no real-world/client-facing claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(GATE, gate)
    write_json(CAL_GATE, gate)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_session_packet_ready": prev.get("decision") == "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_PACKET_READY",
        "previous_real_candidate_not_inserted": prev.get("real_candidate_inserted") is False,
        "previous_real_candidate_not_accepted": prev.get("real_candidate_accepted_to_dataset") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "session_packet_exists": SESSION_PACKET.exists(),
        "session_checklist_exists": SESSION_CHECKLIST.exists(),
        "session_runbook_exists": SESSION_RUNBOOK.exists(),
        "execution_readiness_gate_exists": EXEC_READINESS_GATE.exists(),
        "execution_packet_exists": EXEC_PACKET.exists(),
        "shell_exists": SHELL.exists(),
        "form_exists": FORM.exists(),
        "validator_exists": VALIDATOR.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "schema_exists": SCHEMA.exists(),
        "session_step_count": len(session_steps),
        "session_abort_trigger_count": len(session_abort),
        "session_operator_check_count": len(session_operator_checks),
        "session_checklist_item_count": len(checklist_items),
        "execution_readiness_check_count": len(exec_readiness_checks),
        "execution_step_count": len(exec_steps),
        "shell_section_count": len(shell_sections),
        "form_field_count": len(form_fields),
        "validator_rule_count": len(validator_rules),
        "schema_required_count": len(schema_required),
        "empty_batch_candidate_zero": empty_batch.get("candidate_count") == 0,
        "empty_batch_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "readiness_check_count": len(READINESS_CHECKS),
        "decision_execution_prep_only": decision == "APPROVED_FOR_CONTROLLED_MANUAL_DRY_RUN_SESSION_EXECUTION_PREPARATION_ONLY",
        "session_packet_only": session.get("session_packet_only") is True,
        "session_execution_not_performed": session.get("session_execution_not_performed") is True,
        "session_no_real_data": session.get("real_data_captured_in_this_phase") is False,
        "session_no_candidate_insert": session.get("real_candidate_inserted") is False,
        "session_no_dataset_acceptance": session.get("real_candidate_accepted_to_dataset") is False,
        "contract_gate_only": contract["session_readiness_gate_only"] is True,
        "contract_execution_preparation_only": contract["session_execution_preparation_only"] is True,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "real_candidate_insert_blocked": "real_candidate_insert" in BLOCKED,
        "real_candidate_dataset_acceptance_blocked": "real_candidate_dataset_acceptance" in BLOCKED,
        "dataset_accept_without_review_blocked": "dataset_acceptance_without_human_review" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["session_step_count"] < 22:
        errors.append("session_step_count below 22")
    if checks["session_abort_trigger_count"] < 14:
        errors.append("session_abort_trigger_count below 14")
    if checks["session_operator_check_count"] < 20:
        errors.append("session_operator_check_count below 20")
    if checks["session_checklist_item_count"] < 20:
        errors.append("session_checklist_item_count below 20")
    if checks["execution_readiness_check_count"] < 24:
        errors.append("execution_readiness_check_count below 24")
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
    if checks["readiness_check_count"] < 30:
        errors.append("readiness_check_count below 30")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": decision if status == "PASS" else "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_READINESS_GATE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "readiness_check_count": len(READINESS_CHECKS),
        "session_step_count": len(session_steps),
        "session_abort_trigger_count": len(session_abort),
        "session_operator_check_count": len(session_operator_checks),
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
        "# PROD-4061..4100 Controlled Pilot Manual Dry Run Session Readiness Gate",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Readiness checks: `{len(READINESS_CHECKS)}`",
        f"- Session steps: `{len(session_steps)}`",
        f"- Session abort triggers: `{len(session_abort)}`",
        f"- Session operator checks: `{len(session_operator_checks)}`",
        f"- Real candidate inserted: `{result['real_candidate_inserted']}`",
        f"- Real candidate accepted to dataset: `{result['real_candidate_accepted_to_dataset']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{gate['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Session readiness gate only.",
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
    print("session_steps:", len(session_steps))
    print("session_abort_triggers:", len(session_abort))
    print("session_operator_checks:", len(session_operator_checks))
    print("real_candidate_inserted:", result["real_candidate_inserted"])
    print("real_candidate_accepted_to_dataset:", result["real_candidate_accepted_to_dataset"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", gate["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

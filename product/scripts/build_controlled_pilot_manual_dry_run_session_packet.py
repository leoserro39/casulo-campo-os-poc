#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-4021..4060"
REQ_TAG = "product-controlled-pilot-real-candidate-dry-run-execution-readiness-gate-v0.1"

PREV_OUT = ROOT / "outputs/prod3981_4020_controlled_pilot_real_candidate_dry_run_execution_readiness_gate.json"
EXEC_READINESS_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_readiness_gate_v0_1.json"
EXEC_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_packet_v0_1.json"
EXEC_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_checklist_v0_1.json"
EXEC_RUNBOOK = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_packet_v0_1.md"
SHELL = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.json"
FORM = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_form_v0_1.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_validator_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"

DOC = ROOT / "docs/product/602_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_PACKET.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_manual_dry_run_session_packet.contract.json"
SPEC = ROOT / "product/memory/controlled_pilot_manual_dry_run_session_packet_v0_1.json"
SESSION_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_packet_v0_1.json"
SESSION_RUNBOOK = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_packet_v0_1.md"
SESSION_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_checklist_v0_1.json"
OUT_JSON = ROOT / "outputs/prod4021_4060_controlled_pilot_manual_dry_run_session_packet.json"
OUT_MD = ROOT / "outputs/prod4021_4060_controlled_pilot_manual_dry_run_session_packet.md"

SESSION_STEPS = [
    "confirm_execution_readiness_gate",
    "confirm_human_reviewer_assignment",
    "confirm_operator_assignment",
    "open_execution_packet",
    "open_execution_checklist",
    "open_dry_run_shell",
    "open_dry_run_form",
    "prepare_manual_session_log_placeholder",
    "prepare_source_reference_placeholders",
    "prepare_privacy_review_placeholder",
    "prepare_pii_redaction_placeholder",
    "prepare_secret_scan_placeholder",
    "prepare_evidence_packet_placeholder",
    "prepare_boundary_checklist_placeholder",
    "prepare_reviewer_notes_placeholder",
    "confirm_no_raw_private_data",
    "confirm_no_secrets",
    "confirm_no_unredacted_pii",
    "confirm_no_client_claim",
    "confirm_no_production_activation",
    "confirm_dataset_acceptance_hold",
    "stop_before_real_candidate_insert"
]

SESSION_ABORT_TRIGGERS = [
    "automatic_capture_attempted",
    "real_candidate_insert_attempted",
    "dataset_acceptance_attempted",
    "raw_private_data_detected",
    "secret_or_credential_detected",
    "unredacted_pii_detected",
    "client_facing_claim_detected",
    "production_activation_attempted",
    "commercial_pricing_claim_attempted",
    "human_reviewer_missing",
    "privacy_review_missing",
    "pii_redaction_missing",
    "secret_scan_missing",
    "source_reference_missing"
]

SESSION_OPERATOR_CHECKS = [
    "readiness_gate_confirmed",
    "execution_packet_confirmed",
    "execution_checklist_confirmed",
    "runbook_confirmed",
    "operator_confirmed",
    "reviewer_confirmed",
    "shell_confirmed",
    "form_confirmed",
    "validator_confirmed",
    "schema_confirmed",
    "empty_dataset_confirmed",
    "empty_queue_confirmed",
    "source_refs_only_confirmed",
    "privacy_review_required_confirmed",
    "pii_redaction_required_confirmed",
    "secret_scan_required_confirmed",
    "claim_boundary_confirmed",
    "dataset_hold_confirmed",
    "abort_triggers_confirmed",
    "stop_before_insert_confirmed"
]

ALLOWED = [
    "manual_dry_run_session_packet_creation",
    "manual_session_runbook_creation",
    "manual_session_checklist_creation",
    "operator_session_preflight_creation",
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
    readiness = read_json(EXEC_READINESS_GATE) if EXEC_READINESS_GATE.exists() else {}
    exec_packet = read_json(EXEC_PACKET) if EXEC_PACKET.exists() else {}
    exec_checklist = read_json(EXEC_CHECKLIST) if EXEC_CHECKLIST.exists() else {}
    shell = read_json(SHELL) if SHELL.exists() else {}
    form = read_json(FORM) if FORM.exists() else {}
    validator = read_json(VALIDATOR) if VALIDATOR.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    readiness_checks = readiness.get("readiness_checks", [])
    exec_steps = exec_packet.get("execution_steps", [])
    exec_abort = exec_packet.get("abort_triggers", [])
    exec_operator_checks = exec_packet.get("operator_checks", [])
    exec_checklist_items = exec_checklist.get("operator_checks", [])
    shell_sections = shell.get("shell_sections", [])
    form_fields = form.get("fields", {})
    validator_rules = validator.get("validator_rules", [])
    schema_required = schema.get("required", [])

    session_packet = {
        "version": "controlled_pilot_manual_dry_run_session_packet.v0.1",
        "phase": PHASE,
        "purpose": "Prepare a controlled manual dry run session packet without executing real candidate intake.",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "session_packet_only": True,
        "session_execution_not_performed": True,
        "session_steps": SESSION_STEPS,
        "session_abort_triggers": SESSION_ABORT_TRIGGERS,
        "session_operator_checks": SESSION_OPERATOR_CHECKS,
        "current_dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "session_boundary": {
            "manual_session_preparation_only": True,
            "automatic_capture_allowed": False,
            "real_candidate_insert_allowed": False,
            "dataset_acceptance_allowed": False,
            "raw_private_data_allowed": False,
            "secret_storage_allowed": False,
            "unredacted_pii_allowed": False,
            "client_claim_allowed": False,
            "production_activation_allowed": False
        },
        "claim_boundary": "Manual dry run session packet only. No session execution, no real capture, no insert, no dataset acceptance.",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-4061..4100 - Controlled Pilot Manual Dry Run Session Readiness Gate"
    }

    checklist = {
        "version": "controlled_pilot_manual_dry_run_session_checklist.v0.1",
        "phase": PHASE,
        "status": "CHECKLIST_TEMPLATE_ONLY_NO_SESSION_EXECUTION",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "session_operator_checks": [
            {"id": f"SESSION-{i+1:03d}", "name": name, "required": True, "status": "PENDING"}
            for i, name in enumerate(SESSION_OPERATOR_CHECKS)
        ],
        "abort_triggers": SESSION_ABORT_TRIGGERS,
        "default_gate": "HOLD_SESSION_PACKET_NO_REAL_CANDIDATE"
    }

    spec = {
        "version": "controlled_pilot_manual_dry_run_session_packet.v0.1",
        "phase": PHASE,
        "purpose": session_packet["purpose"],
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "session_step_count": len(SESSION_STEPS),
        "session_abort_trigger_count": len(SESSION_ABORT_TRIGGERS),
        "session_operator_check_count": len(SESSION_OPERATOR_CHECKS),
        "session_packet": "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_packet_v0_1.json",
        "session_checklist": "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_checklist_v0_1.json",
        "session_runbook": "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_packet_v0_1.md",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": session_packet["recommended_next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_manual_dry_run_session_packet",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "session_packet_only": True,
        "session_execution_not_performed": True,
        "automatic_capture_blocked": True,
        "dataset_acceptance_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": session_packet["recommended_next_phase"]
    }

    runbook = """# Controlled Pilot Manual Dry Run Session Packet v0.1

Boundary: session packet only. Do not execute a real candidate intake session in this phase.

Manual session preparation order:
1. Confirm execution readiness gate.
2. Confirm human reviewer and operator assignment.
3. Open execution packet, checklist, shell and form.
4. Prepare manual session log placeholder.
5. Prepare source-reference placeholders only.
6. Prepare privacy, PII redaction and secret-scan placeholders.
7. Prepare evidence and reviewer note placeholders.
8. Confirm no raw private data, secrets or unredacted PII.
9. Confirm no client claim or production activation.
10. Confirm dataset acceptance hold.
11. Stop before any real candidate insert.

Abort if automatic capture, raw private data, secrets, unredacted PII, client-facing claim, production activation, real candidate insert or dataset acceptance is attempted.
"""

    doc = """# PROD-4021..4060 - Controlled Pilot Manual Dry Run Session Packet

Creates the controlled manual dry run session packet.

This phase does not execute a session, does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

Boundary: session packet only. No automatic capture, raw private data, secrets, unredacted PII, production activation, client-facing claim, commercial pricing claim or validated real-world claim.
"""

    write(DOC, doc)
    write(SESSION_RUNBOOK, runbook)
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(SESSION_PACKET, session_packet)
    write_json(SESSION_CHECKLIST, checklist)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_decision_session_prep_only": prev.get("decision") == "APPROVED_FOR_CONTROLLED_MANUAL_REAL_CANDIDATE_DRY_RUN_SESSION_PREPARATION_ONLY",
        "previous_real_candidate_not_inserted": prev.get("real_candidate_inserted") is False,
        "previous_real_candidate_not_accepted": prev.get("real_candidate_accepted_to_dataset") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "execution_readiness_gate_exists": EXEC_READINESS_GATE.exists(),
        "execution_packet_exists": EXEC_PACKET.exists(),
        "execution_checklist_exists": EXEC_CHECKLIST.exists(),
        "execution_runbook_exists": EXEC_RUNBOOK.exists(),
        "shell_exists": SHELL.exists(),
        "form_exists": FORM.exists(),
        "validator_exists": VALIDATOR.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "schema_exists": SCHEMA.exists(),
        "readiness_check_count": len(readiness_checks),
        "execution_step_count": len(exec_steps),
        "execution_abort_trigger_count": len(exec_abort),
        "execution_operator_check_count": len(exec_operator_checks),
        "execution_checklist_count": len(exec_checklist_items),
        "shell_section_count": len(shell_sections),
        "form_field_count": len(form_fields),
        "validator_rule_count": len(validator_rules),
        "schema_required_count": len(schema_required),
        "empty_batch_candidate_zero": empty_batch.get("candidate_count") == 0,
        "empty_batch_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "session_step_count": len(SESSION_STEPS),
        "session_abort_trigger_count": len(SESSION_ABORT_TRIGGERS),
        "session_operator_check_count": len(SESSION_OPERATOR_CHECKS),
        "session_packet_only": session_packet["session_packet_only"] is True,
        "session_execution_not_performed": session_packet["session_execution_not_performed"] is True,
        "session_no_real_data": session_packet["real_data_captured_in_this_phase"] is False,
        "session_no_candidate_insert": session_packet["real_candidate_inserted"] is False,
        "session_no_dataset_acceptance": session_packet["real_candidate_accepted_to_dataset"] is False,
        "contract_session_packet_only": contract["session_packet_only"] is True,
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

    if checks["readiness_check_count"] < 24:
        errors.append("readiness_check_count below 24")
    if checks["execution_step_count"] < 18:
        errors.append("execution_step_count below 18")
    if checks["execution_abort_trigger_count"] < 12:
        errors.append("execution_abort_trigger_count below 12")
    if checks["execution_operator_check_count"] < 18:
        errors.append("execution_operator_check_count below 18")
    if checks["shell_section_count"] < 17:
        errors.append("shell_section_count below 17")
    if checks["form_field_count"] < 16:
        errors.append("form_field_count below 16")
    if checks["validator_rule_count"] < 20:
        errors.append("validator_rule_count below 20")
    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["session_step_count"] < 22:
        errors.append("session_step_count below 22")
    if checks["session_abort_trigger_count"] < 14:
        errors.append("session_abort_trigger_count below 14")
    if checks["session_operator_check_count"] < 20:
        errors.append("session_operator_check_count below 20")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_PACKET_READY" if status == "PASS" else "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_PACKET_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "session_step_count": len(SESSION_STEPS),
        "session_abort_trigger_count": len(SESSION_ABORT_TRIGGERS),
        "session_operator_check_count": len(SESSION_OPERATOR_CHECKS),
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "real_dataset_candidate_count": empty_batch.get("candidate_count", 0),
        "real_dataset_accepted_count": empty_batch.get("accepted_count", 0),
        "recommended_next_phase": session_packet["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-4021..4060 Controlled Pilot Manual Dry Run Session Packet",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Session steps: `{len(SESSION_STEPS)}`",
        f"- Session abort triggers: `{len(SESSION_ABORT_TRIGGERS)}`",
        f"- Session operator checks: `{len(SESSION_OPERATOR_CHECKS)}`",
        f"- Real candidate inserted: `{result['real_candidate_inserted']}`",
        f"- Real candidate accepted to dataset: `{result['real_candidate_accepted_to_dataset']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{session_packet['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Session packet only.",
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
    print("session_steps:", len(SESSION_STEPS))
    print("session_abort_triggers:", len(SESSION_ABORT_TRIGGERS))
    print("session_operator_checks:", len(SESSION_OPERATOR_CHECKS))
    print("real_candidate_inserted:", result["real_candidate_inserted"])
    print("real_candidate_accepted_to_dataset:", result["real_candidate_accepted_to_dataset"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", session_packet["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3941..3980"
REQ_TAG = "product-controlled-pilot-real-candidate-dry-run-readiness-gate-v0.1"

PREV_OUT = ROOT / "outputs/prod3901_3940_controlled_pilot_real_candidate_dry_run_readiness_gate.json"
READINESS_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_readiness_gate_v0_1.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_validator_v0_1.json"
SHELL = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.json"
FORM = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_form_v0_1.json"
BOUNDARY_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_packet_v0_1.json"
BOUNDARY_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_checklist_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"

DOC = ROOT / "docs/product/600_CONTROLLED_PILOT_REAL_CANDIDATE_DRY_RUN_EXECUTION_PACKET.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_real_candidate_dry_run_execution_packet.contract.json"
SPEC = ROOT / "product/memory/controlled_pilot_real_candidate_dry_run_execution_packet_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_packet_v0_1.json"
RUNBOOK = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_packet_v0_1.md"
CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_checklist_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3941_3980_controlled_pilot_real_candidate_dry_run_execution_packet.json"
OUT_MD = ROOT / "outputs/prod3941_3980_controlled_pilot_real_candidate_dry_run_execution_packet.md"

EXECUTION_STEPS = [
    "confirm_readiness_gate",
    "assign_human_reviewer",
    "open_dry_run_shell",
    "open_dry_run_form",
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
    "confirm_claim_boundary",
    "confirm_dataset_acceptance_hold",
    "generate_manual_execution_log_placeholder",
    "hold_before_real_candidate_insert"
]

ABORT_TRIGGERS = [
    "automatic_capture_attempted",
    "raw_private_data_detected",
    "secret_or_credential_detected",
    "unredacted_pii_detected",
    "client_facing_claim_detected",
    "production_activation_attempted",
    "real_candidate_insert_attempted",
    "dataset_acceptance_attempted",
    "human_reviewer_missing",
    "privacy_review_missing",
    "pii_redaction_missing",
    "secret_scan_missing"
]

OPERATOR_CHECKS = [
    "readiness_gate_passed",
    "execution_packet_opened",
    "reviewer_assigned",
    "schema_confirmed",
    "validator_confirmed",
    "shell_confirmed",
    "form_confirmed",
    "boundary_packet_confirmed",
    "boundary_checklist_confirmed",
    "empty_dataset_confirmed",
    "empty_queue_confirmed",
    "source_refs_only_confirmed",
    "privacy_review_required_confirmed",
    "pii_redaction_required_confirmed",
    "secret_scan_required_confirmed",
    "claim_boundary_confirmed",
    "dataset_hold_confirmed",
    "abort_triggers_reviewed"
]

ALLOWED = [
    "manual_execution_packet_creation",
    "execution_runbook_creation",
    "operator_checklist_creation",
    "manual_dry_run_preparation",
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
    readiness = read_json(READINESS_GATE) if READINESS_GATE.exists() else {}
    validator = read_json(VALIDATOR) if VALIDATOR.exists() else {}
    shell = read_json(SHELL) if SHELL.exists() else {}
    form = read_json(FORM) if FORM.exists() else {}
    boundary_packet = read_json(BOUNDARY_PACKET) if BOUNDARY_PACKET.exists() else {}
    boundary_checklist = read_json(BOUNDARY_CHECKLIST) if BOUNDARY_CHECKLIST.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    readiness_criteria = readiness.get("readiness_criteria", [])
    validator_rules = validator.get("validator_rules", [])
    shell_sections = shell.get("shell_sections", [])
    form_fields = form.get("fields", {})
    boundary_controls = boundary_packet.get("boundary_controls", [])
    boundary_checks = boundary_checklist.get("checks", [])
    schema_required = schema.get("required", [])

    packet = {
        "version": "controlled_pilot_real_candidate_dry_run_execution_packet.v0.1",
        "phase": PHASE,
        "purpose": "Prepare the controlled manual real-candidate dry run execution packet without executing intake.",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "execution_packet_only": True,
        "execution_steps": EXECUTION_STEPS,
        "abort_triggers": ABORT_TRIGGERS,
        "operator_checks": OPERATOR_CHECKS,
        "current_dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "execution_boundary": {
            "manual_execution_preparation_only": True,
            "automatic_capture_allowed": False,
            "real_candidate_insert_allowed": False,
            "dataset_acceptance_allowed": False,
            "raw_private_data_allowed": False,
            "secret_storage_allowed": False,
            "unredacted_pii_allowed": False,
            "client_claim_allowed": False,
            "production_activation_allowed": False
        },
        "required_refs": {
            "readiness_gate": "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_readiness_gate_v0_1.json",
            "validator": "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_validator_v0_1.json",
            "shell": "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.json",
            "form": "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_form_v0_1.json",
            "boundary_packet": "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_packet_v0_1.json",
            "boundary_checklist": "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_checklist_v0_1.json"
        },
        "claim_boundary": "Execution packet only. No execution, capture, insertion or dataset acceptance in this phase.",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3981..4020 - Controlled Pilot Real Candidate Dry Run Execution Readiness Gate"
    }

    checklist = {
        "version": "controlled_pilot_real_candidate_dry_run_execution_checklist.v0.1",
        "phase": PHASE,
        "status": "CHECKLIST_TEMPLATE_ONLY_NO_EXECUTION",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "operator_checks": [
            {"id": f"EXEC-{i+1:03d}", "name": name, "required": True, "status": "PENDING"}
            for i, name in enumerate(OPERATOR_CHECKS)
        ],
        "abort_triggers": ABORT_TRIGGERS,
        "default_gate": "HOLD_EXECUTION_PACKET_NO_REAL_CANDIDATE"
    }

    spec = {
        "version": "controlled_pilot_real_candidate_dry_run_execution_packet.v0.1",
        "phase": PHASE,
        "purpose": packet["purpose"],
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "execution_step_count": len(EXECUTION_STEPS),
        "abort_trigger_count": len(ABORT_TRIGGERS),
        "operator_check_count": len(OPERATOR_CHECKS),
        "packet": "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_packet_v0_1.json",
        "checklist": "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_checklist_v0_1.json",
        "runbook": "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_packet_v0_1.md",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": packet["recommended_next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_real_candidate_dry_run_execution_packet",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "execution_packet_only": True,
        "execution_not_performed": True,
        "automatic_capture_blocked": True,
        "dataset_acceptance_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": packet["recommended_next_phase"]
    }

    runbook = """# Controlled Pilot Real Candidate Dry Run Execution Packet v0.1

Boundary: execution packet only. Do not execute real intake in this phase.

Manual execution preparation order:
1. Confirm readiness gate.
2. Assign human reviewer.
3. Open dry run shell and form.
4. Prepare source-reference placeholders only.
5. Prepare privacy, PII redaction and secret-scan placeholders.
6. Prepare evidence and boundary checklist placeholders.
7. Confirm no raw private data, secrets or unredacted PII.
8. Confirm claim boundary.
9. Confirm dataset acceptance hold.
10. Stop before any real candidate insert.

Abort if automatic capture, raw private data, secrets, unredacted PII, client-facing claim, production activation, real candidate insert or dataset acceptance is attempted.
"""

    doc = """# PROD-3941..3980 - Controlled Pilot Real Candidate Dry Run Execution Packet

Creates the controlled manual real-candidate dry run execution packet.

This phase does not execute intake, does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

Boundary: packet only. No automatic capture, raw private data, secrets, unredacted PII, production activation, client-facing claim, commercial pricing claim or validated real-world claim.
"""

    write(DOC, doc)
    write(RUNBOOK, runbook)
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(PACKET, packet)
    write_json(CHECKLIST, checklist)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_decision_packet_preparation_only": prev.get("decision") == "APPROVED_FOR_CONTROLLED_REAL_CANDIDATE_DRY_RUN_EXECUTION_PACKET_PREPARATION_ONLY",
        "previous_real_candidate_not_inserted": prev.get("real_candidate_inserted") is False,
        "previous_real_candidate_not_accepted": prev.get("real_candidate_accepted_to_dataset") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "readiness_gate_exists": READINESS_GATE.exists(),
        "validator_exists": VALIDATOR.exists(),
        "shell_exists": SHELL.exists(),
        "form_exists": FORM.exists(),
        "boundary_packet_exists": BOUNDARY_PACKET.exists(),
        "boundary_checklist_exists": BOUNDARY_CHECKLIST.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "schema_exists": SCHEMA.exists(),
        "readiness_criteria_count": len(readiness_criteria),
        "validator_rule_count": len(validator_rules),
        "shell_section_count": len(shell_sections),
        "form_field_count": len(form_fields),
        "boundary_control_count": len(boundary_controls),
        "boundary_check_count": len(boundary_checks),
        "schema_required_count": len(schema_required),
        "empty_batch_candidate_zero": empty_batch.get("candidate_count") == 0,
        "empty_batch_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "execution_step_count": len(EXECUTION_STEPS),
        "abort_trigger_count": len(ABORT_TRIGGERS),
        "operator_check_count": len(OPERATOR_CHECKS),
        "packet_execution_only": packet["execution_packet_only"] is True,
        "packet_no_real_data": packet["real_data_captured_in_this_phase"] is False,
        "packet_no_candidate_insert": packet["real_candidate_inserted"] is False,
        "packet_no_dataset_acceptance": packet["real_candidate_accepted_to_dataset"] is False,
        "contract_execution_not_performed": contract["execution_not_performed"] is True,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "real_candidate_insert_blocked": "real_candidate_insert" in BLOCKED,
        "real_candidate_dataset_acceptance_blocked": "real_candidate_dataset_acceptance" in BLOCKED,
        "dataset_accept_without_review_blocked": "dataset_acceptance_without_human_review" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["readiness_criteria_count"] < 20:
        errors.append("readiness_criteria_count below 20")
    if checks["validator_rule_count"] < 20:
        errors.append("validator_rule_count below 20")
    if checks["shell_section_count"] < 17:
        errors.append("shell_section_count below 17")
    if checks["form_field_count"] < 16:
        errors.append("form_field_count below 16")
    if checks["boundary_control_count"] < 16:
        errors.append("boundary_control_count below 16")
    if checks["boundary_check_count"] < 16:
        errors.append("boundary_check_count below 16")
    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["execution_step_count"] < 18:
        errors.append("execution_step_count below 18")
    if checks["abort_trigger_count"] < 12:
        errors.append("abort_trigger_count below 12")
    if checks["operator_check_count"] < 18:
        errors.append("operator_check_count below 18")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "CONTROLLED_PILOT_REAL_CANDIDATE_DRY_RUN_EXECUTION_PACKET_READY" if status == "PASS" else "CONTROLLED_PILOT_REAL_CANDIDATE_DRY_RUN_EXECUTION_PACKET_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "execution_step_count": len(EXECUTION_STEPS),
        "abort_trigger_count": len(ABORT_TRIGGERS),
        "operator_check_count": len(OPERATOR_CHECKS),
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "real_dataset_candidate_count": empty_batch.get("candidate_count", 0),
        "real_dataset_accepted_count": empty_batch.get("accepted_count", 0),
        "recommended_next_phase": packet["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3941..3980 Controlled Pilot Real Candidate Dry Run Execution Packet",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Execution steps: `{len(EXECUTION_STEPS)}`",
        f"- Abort triggers: `{len(ABORT_TRIGGERS)}`",
        f"- Operator checks: `{len(OPERATOR_CHECKS)}`",
        f"- Real candidate inserted: `{result['real_candidate_inserted']}`",
        f"- Real candidate accepted to dataset: `{result['real_candidate_accepted_to_dataset']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{packet['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Execution packet only.",
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
    print("execution_steps:", len(EXECUTION_STEPS))
    print("abort_triggers:", len(ABORT_TRIGGERS))
    print("operator_checks:", len(OPERATOR_CHECKS))
    print("real_candidate_inserted:", result["real_candidate_inserted"])
    print("real_candidate_accepted_to_dataset:", result["real_candidate_accepted_to_dataset"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", packet["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

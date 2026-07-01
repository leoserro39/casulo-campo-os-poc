#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-4461..4500"
REQ_TAG = "product-controlled-pilot-manual-dry-run-session-final-gate-readiness-gate-v0.1"

PREV_OUT = ROOT / "outputs/prod4421_4460_controlled_pilot_manual_dry_run_session_final_gate_readiness_gate.json"
FINAL_READINESS_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_gate_readiness_gate_v0_1.json"
FINAL_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_gate_packet_v0_1.json"
FINAL_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_gate_template_v0_1.json"
FINAL_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_gate_checklist_v0_1.json"
REVIEW_READINESS_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_review_readiness_gate_v0_1.json"
REVIEW_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_review_packet_v0_1.json"
REVIEW_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_review_template_v0_1.json"
REVIEW_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_review_checklist_v0_1.json"
OBS_READINESS_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_observation_readiness_gate_v0_1.json"
OBS_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_observation_packet_v0_1.json"
OBS_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_observation_template_v0_1.json"
OBS_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_observation_checklist_v0_1.json"
LOG_READINESS_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_log_readiness_gate_v0_1.json"
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

DOC = ROOT / "docs/product/613_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_EXECUTION_PRECHECK_PACKET.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_manual_dry_run_session_execution_precheck_packet.contract.json"
SPEC = ROOT / "product/memory/controlled_pilot_manual_dry_run_session_execution_precheck_packet_v0_1.json"
PRECHECK_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_precheck_packet_v0_1.json"
PRECHECK_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_precheck_template_v0_1.json"
PRECHECK_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_precheck_checklist_v0_1.json"
OUT_JSON = ROOT / "outputs/prod4461_4500_controlled_pilot_manual_dry_run_session_execution_precheck_packet.json"
OUT_MD = ROOT / "outputs/prod4461_4500_controlled_pilot_manual_dry_run_session_execution_precheck_packet.md"

PRECHECK_SECTIONS = [
    "precheck_context_refs",
    "prior_gate_chain_review",
    "final_gate_packet_review",
    "review_packet_review",
    "observation_packet_review",
    "execution_log_review",
    "session_packet_review",
    "operator_assignment_check",
    "human_reviewer_assignment_check",
    "source_reference_check",
    "privacy_review_check",
    "pii_redaction_check",
    "secret_scan_check",
    "evidence_packet_check",
    "manual_observation_boundary_check",
    "claim_boundary_check",
    "dataset_hold_check",
    "blocked_action_check",
    "abort_trigger_check",
    "pre_execution_hold"
]

PRECHECK_FIELDS = [
    "execution_precheck_packet_id",
    "phase",
    "final_gate_readiness_gate_ref",
    "final_gate_packet_ref",
    "final_gate_template_ref",
    "final_gate_checklist_ref",
    "review_packet_ref",
    "observation_packet_ref",
    "execution_log_shell_ref",
    "session_packet_ref",
    "dry_run_shell_ref",
    "dry_run_form_ref",
    "operator_ref",
    "human_reviewer_ref",
    "source_reference_refs",
    "privacy_review_ref",
    "pii_redaction_ref",
    "secret_scan_ref",
    "evidence_packet_ref",
    "manual_observation_refs",
    "reviewer_notes_ref",
    "claim_boundary_review",
    "dataset_hold_reason",
    "blocked_action_review",
    "abort_trigger_review",
    "precheck_decision",
    "precheck_reason",
    "next_allowed_phase"
]

PRECHECK_CHECKS = [
    "prior_final_gate_readiness_gate_passed",
    "final_gate_packet_present",
    "final_gate_template_present",
    "final_gate_checklist_present",
    "review_readiness_gate_present",
    "review_packet_present",
    "review_template_present",
    "review_checklist_present",
    "observation_readiness_gate_present",
    "observation_packet_present",
    "observation_template_present",
    "observation_checklist_present",
    "log_readiness_gate_present",
    "log_shell_present",
    "log_template_present",
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
    "precheck_sections_present",
    "precheck_fields_present",
    "precheck_template_fields_present",
    "precheck_checklist_items_present",
    "operator_ref_required",
    "human_reviewer_ref_required",
    "source_reference_refs_required",
    "privacy_review_ref_required",
    "pii_redaction_ref_required",
    "secret_scan_ref_required",
    "evidence_packet_ref_required",
    "manual_observation_refs_required",
    "reviewer_notes_ref_required",
    "claim_boundary_review_required",
    "dataset_hold_reason_required",
    "blocked_action_review_required",
    "abort_trigger_review_required",
    "precheck_decision_required",
    "precheck_reason_required",
    "next_allowed_phase_required",
    "reference_only_storage_required",
    "sanitized_precheck_only",
    "template_only_confirmed",
    "checklist_template_only_confirmed",
    "session_execution_not_performed",
    "precheck_packet_only_confirmed",
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
    "execution_precheck_packet_creation",
    "execution_precheck_template_creation",
    "execution_precheck_checklist_creation",
    "sanitized_execution_precheck_placeholder_creation",
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
    final_gate = read_json(FINAL_READINESS_GATE) if FINAL_READINESS_GATE.exists() else {}
    final_packet_src = read_json(FINAL_PACKET) if FINAL_PACKET.exists() else {}
    final_template_src = read_json(FINAL_TEMPLATE) if FINAL_TEMPLATE.exists() else {}
    final_checklist_src = read_json(FINAL_CHECKLIST) if FINAL_CHECKLIST.exists() else {}
    review_gate = read_json(REVIEW_READINESS_GATE) if REVIEW_READINESS_GATE.exists() else {}
    review_packet = read_json(REVIEW_PACKET) if REVIEW_PACKET.exists() else {}
    review_template = read_json(REVIEW_TEMPLATE) if REVIEW_TEMPLATE.exists() else {}
    review_checklist = read_json(REVIEW_CHECKLIST) if REVIEW_CHECKLIST.exists() else {}
    obs_gate = read_json(OBS_READINESS_GATE) if OBS_READINESS_GATE.exists() else {}
    obs_packet = read_json(OBS_PACKET) if OBS_PACKET.exists() else {}
    obs_template = read_json(OBS_TEMPLATE) if OBS_TEMPLATE.exists() else {}
    obs_checklist = read_json(OBS_CHECKLIST) if OBS_CHECKLIST.exists() else {}
    log_gate = read_json(LOG_READINESS_GATE) if LOG_READINESS_GATE.exists() else {}
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

    final_gate_readiness_checks = final_gate.get("readiness_checks", [])
    final_gate_sections = final_packet_src.get("final_gate_sections", [])
    final_gate_fields = final_packet_src.get("final_gate_fields", [])
    final_gate_checks = final_packet_src.get("final_gate_checks", [])
    final_template_fields = final_template_src.get("fields", {})
    final_checklist_items = final_checklist_src.get("checks", [])
    review_gate_checks = review_gate.get("readiness_checks", [])
    review_sections = review_packet.get("review_sections", [])
    review_fields = review_packet.get("review_fields", [])
    review_checks = review_packet.get("review_checks", [])
    review_template_fields = review_template.get("fields", {})
    review_checklist_items = review_checklist.get("checks", [])
    obs_gate_checks = obs_gate.get("readiness_checks", [])
    observation_sections = obs_packet.get("observation_sections", [])
    observation_fields = obs_packet.get("observation_fields", [])
    observation_checks = obs_packet.get("observation_checks", [])
    obs_template_fields = obs_template.get("fields", {})
    obs_checklist_items = obs_checklist.get("checks", [])
    log_gate_checks = log_gate.get("readiness_checks", [])
    log_sections = log_shell.get("log_sections", [])
    log_fields = log_shell.get("log_fields", [])
    log_template_fields = log_template.get("fields", {})
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

    precheck_packet = {
        "version": "controlled_pilot_manual_dry_run_session_execution_precheck_packet.v0.1",
        "phase": PHASE,
        "purpose": "Prepare controlled manual dry run session execution precheck packet without executing a session.",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "execution_precheck_packet_only": True,
        "session_execution_not_performed": True,
        "precheck_sections": PRECHECK_SECTIONS,
        "precheck_fields": PRECHECK_FIELDS,
        "precheck_checks": PRECHECK_CHECKS,
        "current_dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "precheck_boundary": {
            "template_only": True,
            "reference_only_storage_required": True,
            "sanitized_precheck_only": True,
            "automatic_capture_allowed": False,
            "real_candidate_insert_allowed": False,
            "dataset_acceptance_allowed": False,
            "raw_private_data_allowed": False,
            "secret_storage_allowed": False,
            "unredacted_pii_allowed": False,
            "client_claim_allowed": False,
            "production_activation_allowed": False
        },
        "claim_boundary": "Execution precheck packet only. No session execution, no capture, no insert, no dataset acceptance.",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-4501..4540 - Controlled Pilot Manual Dry Run Session Execution Precheck Readiness Gate"
    }

    precheck_template = {
        "version": "controlled_pilot_manual_dry_run_session_execution_precheck_template.v0.1",
        "phase": PHASE,
        "status": "EXECUTION_PRECHECK_TEMPLATE_ONLY_NO_SESSION_EXECUTION",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "fields": {
            field: {
                "value": None,
                "required": True,
                "storage_rule": "reference_only_or_sanitized_placeholder"
            }
            for field in PRECHECK_FIELDS
        },
        "default_gate": "HOLD_EXECUTION_PRECHECK_PACKET_NO_SESSION_EXECUTION",
        "blocked_actions": BLOCKED
    }

    precheck_checklist = {
        "version": "controlled_pilot_manual_dry_run_session_execution_precheck_checklist.v0.1",
        "phase": PHASE,
        "status": "CHECKLIST_TEMPLATE_ONLY_NO_SESSION_EXECUTION",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "checks": [
            {"id": f"PRECHECK-{i+1:03d}", "name": name, "required": True, "status": "PENDING"}
            for i, name in enumerate(PRECHECK_CHECKS)
        ],
        "default_gate": "HOLD_EXECUTION_PRECHECK_PACKET_NO_SESSION_EXECUTION",
        "blocked_actions": BLOCKED
    }

    spec = {
        "version": "controlled_pilot_manual_dry_run_session_execution_precheck_packet.v0.1",
        "phase": PHASE,
        "purpose": precheck_packet["purpose"],
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "precheck_section_count": len(PRECHECK_SECTIONS),
        "precheck_field_count": len(PRECHECK_FIELDS),
        "precheck_check_count": len(PRECHECK_CHECKS),
        "precheck_packet": "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_precheck_packet_v0_1.json",
        "precheck_template": "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_precheck_template_v0_1.json",
        "precheck_checklist": "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_precheck_checklist_v0_1.json",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": precheck_packet["recommended_next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_manual_dry_run_session_execution_precheck_packet",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "execution_precheck_packet_only": True,
        "session_execution_not_performed": True,
        "automatic_capture_blocked": True,
        "dataset_acceptance_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": precheck_packet["recommended_next_phase"]
    }

    doc = """# PROD-4461..4500 - Controlled Pilot Manual Dry Run Session Execution Precheck Packet

Creates the controlled manual dry run session execution precheck packet.

This phase does not execute a session, does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

Boundary: execution precheck packet only. Use reference-only or sanitized placeholders. No automatic capture, raw private data, secrets, unredacted PII, production activation, client-facing claim, commercial pricing claim or validated real-world claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(PRECHECK_PACKET, precheck_packet)
    write_json(PRECHECK_TEMPLATE, precheck_template)
    write_json(PRECHECK_CHECKLIST, precheck_checklist)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_decision_execution_precheck_prep_only": prev.get("decision") == "APPROVED_FOR_CONTROLLED_MANUAL_DRY_RUN_SESSION_EXECUTION_PRECHECK_PACKET_PREPARATION_ONLY",
        "previous_real_candidate_not_inserted": prev.get("real_candidate_inserted") is False,
        "previous_real_candidate_not_accepted": prev.get("real_candidate_accepted_to_dataset") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "final_readiness_gate_exists": FINAL_READINESS_GATE.exists(),
        "final_gate_packet_exists": FINAL_PACKET.exists(),
        "final_gate_template_exists": FINAL_TEMPLATE.exists(),
        "final_gate_checklist_exists": FINAL_CHECKLIST.exists(),
        "review_readiness_gate_exists": REVIEW_READINESS_GATE.exists(),
        "review_packet_exists": REVIEW_PACKET.exists(),
        "review_template_exists": REVIEW_TEMPLATE.exists(),
        "review_checklist_exists": REVIEW_CHECKLIST.exists(),
        "observation_readiness_gate_exists": OBS_READINESS_GATE.exists(),
        "observation_packet_exists": OBS_PACKET.exists(),
        "observation_template_exists": OBS_TEMPLATE.exists(),
        "observation_checklist_exists": OBS_CHECKLIST.exists(),
        "log_readiness_gate_exists": LOG_READINESS_GATE.exists(),
        "log_shell_exists": LOG_SHELL.exists(),
        "log_template_exists": LOG_TEMPLATE.exists(),
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
        "final_gate_readiness_check_count": len(final_gate_readiness_checks),
        "final_gate_section_count": len(final_gate_sections),
        "final_gate_field_count": len(final_gate_fields),
        "final_gate_check_count": len(final_gate_checks),
        "final_gate_template_field_count": len(final_template_fields),
        "final_gate_checklist_item_count": len(final_checklist_items),
        "review_readiness_check_count": len(review_gate_checks),
        "review_section_count": len(review_sections),
        "review_field_count": len(review_fields),
        "review_check_count": len(review_checks),
        "review_template_field_count": len(review_template_fields),
        "review_checklist_item_count": len(review_checklist_items),
        "observation_readiness_check_count": len(obs_gate_checks),
        "observation_section_count": len(observation_sections),
        "observation_field_count": len(observation_fields),
        "observation_check_count": len(observation_checks),
        "observation_template_field_count": len(obs_template_fields),
        "observation_checklist_item_count": len(obs_checklist_items),
        "log_gate_check_count": len(log_gate_checks),
        "log_section_count": len(log_sections),
        "log_field_count": len(log_fields),
        "log_template_field_count": len(log_template_fields),
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
        "precheck_section_count": len(PRECHECK_SECTIONS),
        "precheck_field_count": len(PRECHECK_FIELDS),
        "precheck_check_count": len(PRECHECK_CHECKS),
        "precheck_template_field_count": len(precheck_template["fields"]),
        "precheck_checklist_item_count": len(precheck_checklist["checks"]),
        "precheck_packet_only": precheck_packet["execution_precheck_packet_only"] is True,
        "session_execution_not_performed": precheck_packet["session_execution_not_performed"] is True,
        "precheck_no_real_data": precheck_packet["real_data_captured_in_this_phase"] is False,
        "precheck_no_candidate_insert": precheck_packet["real_candidate_inserted"] is False,
        "precheck_no_dataset_acceptance": precheck_packet["real_candidate_accepted_to_dataset"] is False,
        "contract_packet_only": contract["execution_precheck_packet_only"] is True,
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

    if checks["final_gate_readiness_check_count"] < 64:
        errors.append("final_gate_readiness_check_count below 64")
    if checks["final_gate_section_count"] < 18:
        errors.append("final_gate_section_count below 18")
    if checks["final_gate_field_count"] < 24:
        errors.append("final_gate_field_count below 24")
    if checks["final_gate_check_count"] < 53:
        errors.append("final_gate_check_count below 53")
    if checks["review_readiness_check_count"] < 55:
        errors.append("review_readiness_check_count below 55")
    if checks["review_section_count"] < 16:
        errors.append("review_section_count below 16")
    if checks["review_field_count"] < 22:
        errors.append("review_field_count below 22")
    if checks["review_check_count"] < 38:
        errors.append("review_check_count below 38")
    if checks["observation_readiness_check_count"] < 50:
        errors.append("observation_readiness_check_count below 50")
    if checks["observation_section_count"] < 15:
        errors.append("observation_section_count below 15")
    if checks["observation_field_count"] < 20:
        errors.append("observation_field_count below 20")
    if checks["log_gate_check_count"] < 39:
        errors.append("log_gate_check_count below 39")
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
    if checks["precheck_section_count"] < 20:
        errors.append("precheck_section_count below 20")
    if checks["precheck_field_count"] < 28:
        errors.append("precheck_field_count below 28")
    if checks["precheck_check_count"] < 60:
        errors.append("precheck_check_count below 60")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_EXECUTION_PRECHECK_PACKET_READY" if status == "PASS" else "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_EXECUTION_PRECHECK_PACKET_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "precheck_section_count": len(PRECHECK_SECTIONS),
        "precheck_field_count": len(PRECHECK_FIELDS),
        "precheck_check_count": len(PRECHECK_CHECKS),
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "real_dataset_candidate_count": empty_batch.get("candidate_count", 0),
        "real_dataset_accepted_count": empty_batch.get("accepted_count", 0),
        "recommended_next_phase": precheck_packet["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-4461..4500 Controlled Pilot Manual Dry Run Session Execution Precheck Packet",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Precheck sections: `{len(PRECHECK_SECTIONS)}`",
        f"- Precheck fields: `{len(PRECHECK_FIELDS)}`",
        f"- Precheck checks: `{len(PRECHECK_CHECKS)}`",
        f"- Real candidate inserted: `{result['real_candidate_inserted']}`",
        f"- Real candidate accepted to dataset: `{result['real_candidate_accepted_to_dataset']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{precheck_packet['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Execution precheck packet only.",
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
    print("precheck_sections:", len(PRECHECK_SECTIONS))
    print("precheck_fields:", len(PRECHECK_FIELDS))
    print("precheck_checks:", len(PRECHECK_CHECKS))
    print("real_candidate_inserted:", result["real_candidate_inserted"])
    print("real_candidate_accepted_to_dataset:", result["real_candidate_accepted_to_dataset"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", precheck_packet["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

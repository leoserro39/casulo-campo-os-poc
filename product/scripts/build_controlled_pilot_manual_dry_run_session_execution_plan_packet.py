#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-4621..4660"
REQ_TAG = "product-controlled-pilot-manual-dry-run-session-operator-start-readiness-gate-v0.1"

PREV_OUT = ROOT / "outputs/prod4581_4620_controlled_pilot_manual_dry_run_session_operator_start_readiness_gate.json"
OPERATOR_START_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_operator_start_readiness_gate_v0_1.json"
OPERATOR_START_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_operator_start_packet_v0_1.json"
OPERATOR_START_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_operator_start_template_v0_1.json"
OPERATOR_START_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_operator_start_checklist_v0_1.json"
PRECHECK_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_precheck_readiness_gate_v0_1.json"
PRECHECK_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_precheck_packet_v0_1.json"
PRECHECK_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_precheck_template_v0_1.json"
PRECHECK_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_precheck_checklist_v0_1.json"
FINAL_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_gate_readiness_gate_v0_1.json"
FINAL_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_gate_packet_v0_1.json"
FINAL_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_gate_template_v0_1.json"
FINAL_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_gate_checklist_v0_1.json"
REVIEW_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_review_readiness_gate_v0_1.json"
REVIEW_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_review_packet_v0_1.json"
OBS_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_observation_readiness_gate_v0_1.json"
OBS_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_observation_packet_v0_1.json"
LOG_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_log_readiness_gate_v0_1.json"
LOG_SHELL = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_log_shell_v0_1.json"
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

DOC = ROOT / "docs/product/617_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_EXECUTION_PLAN_PACKET.md"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_manual_dry_run_session_execution_plan_packet.contract.json"
SPEC = ROOT / "product/memory/controlled_pilot_manual_dry_run_session_execution_plan_packet_v0_1.json"
PLAN_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_plan_packet_v0_1.json"
PLAN_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_plan_template_v0_1.json"
PLAN_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_plan_checklist_v0_1.json"
OUT_JSON = ROOT / "outputs/prod4621_4660_controlled_pilot_manual_dry_run_session_execution_plan_packet.json"
OUT_MD = ROOT / "outputs/prod4621_4660_controlled_pilot_manual_dry_run_session_execution_plan_packet.md"
ROADMAP_JSON = ROOT / "outputs/prod4621_4660_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

EXECUTION_PLAN_SECTIONS = [
    "execution_plan_context_refs",
    "prior_gate_chain_review",
    "operator_start_readiness_review",
    "operator_start_packet_review",
    "execution_precheck_review",
    "final_gate_review",
    "review_packet_review",
    "observation_packet_review",
    "execution_log_review",
    "session_packet_review",
    "operator_identity_placeholder",
    "human_reviewer_confirmation_placeholder",
    "source_reference_confirmation",
    "privacy_review_confirmation",
    "pii_redaction_confirmation",
    "secret_scan_confirmation",
    "evidence_packet_confirmation",
    "manual_execution_steps_placeholder",
    "manual_stop_points",
    "abort_trigger_review",
    "blocked_action_review",
    "claim_boundary_confirmation",
    "dataset_hold_confirmation",
    "pre_execution_hold"
]

EXECUTION_PLAN_FIELDS = [
    "execution_plan_packet_id",
    "phase",
    "operator_start_readiness_gate_ref",
    "operator_start_packet_ref",
    "operator_start_template_ref",
    "operator_start_checklist_ref",
    "precheck_packet_ref",
    "precheck_template_ref",
    "precheck_checklist_ref",
    "final_gate_packet_ref",
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
    "start_hold_status_ref",
    "execution_plan_steps_ref",
    "manual_stop_points_ref",
    "execution_plan_decision",
    "execution_plan_reason",
    "next_allowed_phase",
    "stop_before_execution_confirmation"
]

EXECUTION_PLAN_CHECKS = [
    "prior_operator_start_readiness_gate_passed",
    "operator_start_packet_present",
    "operator_start_template_present",
    "operator_start_checklist_present",
    "precheck_readiness_gate_present",
    "precheck_packet_present",
    "precheck_template_present",
    "precheck_checklist_present",
    "final_gate_readiness_gate_present",
    "final_gate_packet_present",
    "final_gate_template_present",
    "final_gate_checklist_present",
    "review_readiness_gate_present",
    "review_packet_present",
    "observation_readiness_gate_present",
    "observation_packet_present",
    "log_readiness_gate_present",
    "log_shell_present",
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
    "execution_plan_sections_present",
    "execution_plan_fields_present",
    "execution_plan_checks_present",
    "execution_plan_template_fields_present",
    "execution_plan_checklist_items_present",
    "operator_start_refs_present",
    "precheck_refs_present",
    "final_gate_refs_present",
    "review_refs_present",
    "observation_refs_present",
    "log_refs_present",
    "session_refs_present",
    "dry_run_refs_present",
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
    "start_hold_status_ref_required",
    "execution_plan_steps_ref_required",
    "manual_stop_points_ref_required",
    "execution_plan_decision_required",
    "execution_plan_reason_required",
    "stop_before_execution_confirmation_required",
    "next_allowed_phase_required",
    "reference_only_storage_required",
    "sanitized_execution_plan_only",
    "template_only_confirmed",
    "checklist_template_only_confirmed",
    "session_execution_not_performed",
    "execution_plan_packet_only_confirmed",
    "start_command_blocked",
    "manual_session_execution_blocked",
    "automatic_capture_blocked",
    "real_candidate_insert_blocked",
    "dataset_acceptance_blocked",
    "raw_private_data_blocked",
    "secrets_blocked",
    "unredacted_pii_blocked",
    "client_claim_blocked",
    "production_activation_blocked",
    "human_review_required",
    "roadmap_updated",
    "execution_plan_readiness_gate_preparation_only",
    "no_real_value_claim",
    "no_validated_hallucination_claim",
    "no_commercial_pricing_claim",
    "no_gpt_memory_api_execution",
    "no_automatic_memory_delete",
    "dataset_hold_before_real_intake",
    "manual_only_path_confirmed",
    "controlled_pilot_boundary_confirmed",
    "execution_plan_review_before_session_required"
]

ALLOWED = [
    "execution_plan_packet_creation",
    "execution_plan_template_creation",
    "execution_plan_checklist_creation",
    "roadmap_update",
    "hold_before_actual_session_execution"
]

BLOCKED = [
    "start_command_execution",
    "manual_session_execution",
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

ROADMAP_ITEMS = [
    {"phase": "PROD-4101..4140", "name": "Manual Dry Run Session Execution Gate", "status": "DONE"},
    {"phase": "PROD-4141..4180", "name": "Execution Log Shell", "status": "DONE"},
    {"phase": "PROD-4181..4220", "name": "Execution Log Readiness Gate", "status": "DONE"},
    {"phase": "PROD-4221..4260", "name": "Observation Packet", "status": "DONE"},
    {"phase": "PROD-4261..4300", "name": "Observation Readiness Gate", "status": "DONE"},
    {"phase": "PROD-4301..4340", "name": "Review Packet", "status": "DONE"},
    {"phase": "PROD-4341..4380", "name": "Review Readiness Gate", "status": "DONE"},
    {"phase": "PROD-4381..4420", "name": "Final Gate Packet", "status": "DONE"},
    {"phase": "PROD-4421..4460", "name": "Final Gate Readiness Gate", "status": "DONE"},
    {"phase": "PROD-4461..4500", "name": "Execution Precheck Packet", "status": "DONE"},
    {"phase": "PROD-4501..4540", "name": "Execution Precheck Readiness Gate", "status": "DONE"},
    {"phase": "PROD-4541..4580", "name": "Operator Start Packet", "status": "DONE"},
    {"phase": "PROD-4581..4620", "name": "Operator Start Readiness Gate", "status": "DONE"},
    {"phase": "PROD-4621..4660", "name": "Execution Plan Packet", "status": "CURRENT"},
    {"phase": "PROD-4661..4700", "name": "Execution Plan Readiness Gate", "status": "NEXT"},
    {"phase": "PROD-4701..4740", "name": "Manual Session Execution Hold Packet", "status": "PLANNED"},
    {"phase": "PROD-4741..4780", "name": "Manual Session Execution Hold Readiness Gate", "status": "PLANNED"}
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
    start_gate = read_json(OPERATOR_START_GATE) if OPERATOR_START_GATE.exists() else {}
    start_packet = read_json(OPERATOR_START_PACKET) if OPERATOR_START_PACKET.exists() else {}
    start_template = read_json(OPERATOR_START_TEMPLATE) if OPERATOR_START_TEMPLATE.exists() else {}
    start_checklist = read_json(OPERATOR_START_CHECKLIST) if OPERATOR_START_CHECKLIST.exists() else {}
    precheck_gate = read_json(PRECHECK_GATE) if PRECHECK_GATE.exists() else {}
    precheck_packet = read_json(PRECHECK_PACKET) if PRECHECK_PACKET.exists() else {}
    precheck_template = read_json(PRECHECK_TEMPLATE) if PRECHECK_TEMPLATE.exists() else {}
    precheck_checklist = read_json(PRECHECK_CHECKLIST) if PRECHECK_CHECKLIST.exists() else {}
    final_gate = read_json(FINAL_GATE) if FINAL_GATE.exists() else {}
    final_packet = read_json(FINAL_PACKET) if FINAL_PACKET.exists() else {}
    final_template = read_json(FINAL_TEMPLATE) if FINAL_TEMPLATE.exists() else {}
    final_checklist = read_json(FINAL_CHECKLIST) if FINAL_CHECKLIST.exists() else {}
    review_gate = read_json(REVIEW_GATE) if REVIEW_GATE.exists() else {}
    review_packet = read_json(REVIEW_PACKET) if REVIEW_PACKET.exists() else {}
    obs_gate = read_json(OBS_GATE) if OBS_GATE.exists() else {}
    obs_packet = read_json(OBS_PACKET) if OBS_PACKET.exists() else {}
    log_gate = read_json(LOG_GATE) if LOG_GATE.exists() else {}
    log_shell = read_json(LOG_SHELL) if LOG_SHELL.exists() else {}
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

    operator_start_readiness_checks = start_gate.get("readiness_checks", [])
    operator_start_sections = start_packet.get("operator_start_sections", [])
    operator_start_fields = start_packet.get("operator_start_fields", [])
    operator_start_checks = start_packet.get("operator_start_checks", [])
    operator_start_template_fields = start_template.get("fields", {})
    operator_start_checklist_items = start_checklist.get("checks", [])

    precheck_readiness_checks = precheck_gate.get("readiness_checks", [])
    precheck_sections = precheck_packet.get("precheck_sections", [])
    precheck_fields = precheck_packet.get("precheck_fields", [])
    precheck_checks = precheck_packet.get("precheck_checks", [])
    precheck_template_fields = precheck_template.get("fields", {})
    precheck_checklist_items = precheck_checklist.get("checks", [])

    final_gate_readiness_checks = final_gate.get("readiness_checks", [])
    final_gate_sections = final_packet.get("final_gate_sections", [])
    final_gate_fields = final_packet.get("final_gate_fields", [])
    final_gate_checks = final_packet.get("final_gate_checks", [])
    final_template_fields = final_template.get("fields", {})
    final_checklist_items = final_checklist.get("checks", [])

    review_gate_checks = review_gate.get("readiness_checks", [])
    review_sections = review_packet.get("review_sections", [])
    review_fields = review_packet.get("review_fields", [])
    review_checks = review_packet.get("review_checks", [])
    obs_gate_checks = obs_gate.get("readiness_checks", [])
    observation_sections = obs_packet.get("observation_sections", [])
    observation_fields = obs_packet.get("observation_fields", [])
    log_gate_checks = log_gate.get("readiness_checks", [])
    log_sections = log_shell.get("log_sections", [])
    log_fields = log_shell.get("log_fields", [])
    execution_gate_controls = exec_gate.get("execution_gate_controls", [])
    session_steps = session_packet.get("session_steps", [])
    session_abort = session_packet.get("session_abort_triggers", [])
    session_operator_checks = session_packet.get("session_operator_checks", [])
    exec_steps = exec_packet.get("execution_steps", [])
    shell_sections = shell.get("shell_sections", [])
    form_fields = form.get("fields", {})
    validator_rules = validator.get("validator_rules", [])
    schema_required = schema.get("required", [])

    plan_packet = {
        "version": "controlled_pilot_manual_dry_run_session_execution_plan_packet.v0.1",
        "phase": PHASE,
        "purpose": "Prepare controlled manual dry run session execution plan packet without executing a session.",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "execution_plan_packet_only": True,
        "session_execution_not_performed": True,
        "execution_plan_sections": EXECUTION_PLAN_SECTIONS,
        "execution_plan_fields": EXECUTION_PLAN_FIELDS,
        "execution_plan_checks": EXECUTION_PLAN_CHECKS,
        "current_dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "execution_plan_boundary": {
            "template_only": True,
            "reference_only_storage_required": True,
            "sanitized_execution_plan_only": True,
            "start_command_allowed": False,
            "manual_session_execution_allowed": False,
            "automatic_capture_allowed": False,
            "real_candidate_insert_allowed": False,
            "dataset_acceptance_allowed": False,
            "raw_private_data_allowed": False,
            "secret_storage_allowed": False,
            "unredacted_pii_allowed": False,
            "client_claim_allowed": False,
            "production_activation_allowed": False
        },
        "claim_boundary": "Execution plan packet only. No session execution, no start command, no capture, no insert, no dataset acceptance.",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-4661..4700 - Controlled Pilot Manual Dry Run Session Execution Plan Readiness Gate"
    }

    plan_template = {
        "version": "controlled_pilot_manual_dry_run_session_execution_plan_template.v0.1",
        "phase": PHASE,
        "status": "EXECUTION_PLAN_TEMPLATE_ONLY_NO_SESSION_EXECUTION",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "fields": {
            field: {
                "value": None,
                "required": True,
                "storage_rule": "reference_only_or_sanitized_placeholder"
            }
            for field in EXECUTION_PLAN_FIELDS
        },
        "default_gate": "HOLD_EXECUTION_PLAN_PACKET_NO_SESSION_EXECUTION",
        "blocked_actions": BLOCKED
    }

    plan_checklist = {
        "version": "controlled_pilot_manual_dry_run_session_execution_plan_checklist.v0.1",
        "phase": PHASE,
        "status": "CHECKLIST_TEMPLATE_ONLY_NO_SESSION_EXECUTION",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "checks": [
            {"id": f"PLAN-{i+1:03d}", "name": name, "required": True, "status": "PENDING"}
            for i, name in enumerate(EXECUTION_PLAN_CHECKS)
        ],
        "default_gate": "HOLD_EXECUTION_PLAN_PACKET_NO_SESSION_EXECUTION",
        "blocked_actions": BLOCKED
    }

    roadmap_snapshot = {
        "version": "controlled_pilot_manual_dry_run_session_roadmap.v0.1",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": ROADMAP_ITEMS,
        "current_phase": "PROD-4621..4660 - Controlled Pilot Manual Dry Run Session Execution Plan Packet",
        "next_phase": plan_packet["recommended_next_phase"],
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "blocked_actions": BLOCKED
    }

    spec = {
        "version": "controlled_pilot_manual_dry_run_session_execution_plan_packet.v0.1",
        "phase": PHASE,
        "purpose": plan_packet["purpose"],
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "execution_plan_section_count": len(EXECUTION_PLAN_SECTIONS),
        "execution_plan_field_count": len(EXECUTION_PLAN_FIELDS),
        "execution_plan_check_count": len(EXECUTION_PLAN_CHECKS),
        "roadmap_updated": True,
        "execution_plan_packet": "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_plan_packet_v0_1.json",
        "execution_plan_template": "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_plan_template_v0_1.json",
        "execution_plan_checklist": "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_plan_checklist_v0_1.json",
        "roadmap": "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": plan_packet["recommended_next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_manual_dry_run_session_execution_plan_packet",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "execution_plan_packet_only": True,
        "session_execution_not_performed": True,
        "start_command_blocked": True,
        "manual_session_execution_blocked": True,
        "automatic_capture_blocked": True,
        "dataset_acceptance_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": plan_packet["recommended_next_phase"]
    }

    doc = """# PROD-4621..4660 - Controlled Pilot Manual Dry Run Session Execution Plan Packet

Creates the controlled manual dry run session execution plan packet.

This phase does not execute a session, does not run a start command, does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

Boundary: execution plan packet only. Use reference-only or sanitized placeholders. No start command, no manual execution, no automatic capture, no raw private data, no secrets, no unredacted PII, no production activation, no client-facing claim, no commercial pricing claim and no validated real-world claim.
"""

    roadmap_md = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in ROADMAP_ITEMS:
        roadmap_md.append(f"- `{item['phase']}` - {item['name']} - **{item['status']}**")
    roadmap_md += [
        "",
        "## Current boundary",
        "- Current phase prepares the execution plan packet only.",
        "- No session execution.",
        "- No start command.",
        "- No real candidate insert.",
        "- No dataset acceptance.",
        "- No real-world/client-facing claim."
    ]

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_md))
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(PLAN_PACKET, plan_packet)
    write_json(PLAN_TEMPLATE, plan_template)
    write_json(PLAN_CHECKLIST, plan_checklist)
    write_json(ROADMAP_JSON, roadmap_snapshot)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_decision_execution_plan_prep_only": prev.get("decision") == "APPROVED_FOR_CONTROLLED_MANUAL_DRY_RUN_SESSION_EXECUTION_PLAN_PACKET_PREPARATION_ONLY",
        "previous_real_candidate_not_inserted": prev.get("real_candidate_inserted") is False,
        "previous_real_candidate_not_accepted": prev.get("real_candidate_accepted_to_dataset") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "operator_start_readiness_gate_exists": OPERATOR_START_GATE.exists(),
        "operator_start_packet_exists": OPERATOR_START_PACKET.exists(),
        "operator_start_template_exists": OPERATOR_START_TEMPLATE.exists(),
        "operator_start_checklist_exists": OPERATOR_START_CHECKLIST.exists(),
        "precheck_readiness_gate_exists": PRECHECK_GATE.exists(),
        "precheck_packet_exists": PRECHECK_PACKET.exists(),
        "precheck_template_exists": PRECHECK_TEMPLATE.exists(),
        "precheck_checklist_exists": PRECHECK_CHECKLIST.exists(),
        "final_readiness_gate_exists": FINAL_GATE.exists(),
        "final_gate_packet_exists": FINAL_PACKET.exists(),
        "final_gate_template_exists": FINAL_TEMPLATE.exists(),
        "final_gate_checklist_exists": FINAL_CHECKLIST.exists(),
        "review_readiness_gate_exists": REVIEW_GATE.exists(),
        "review_packet_exists": REVIEW_PACKET.exists(),
        "observation_readiness_gate_exists": OBS_GATE.exists(),
        "observation_packet_exists": OBS_PACKET.exists(),
        "log_readiness_gate_exists": LOG_GATE.exists(),
        "log_shell_exists": LOG_SHELL.exists(),
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
        "operator_start_readiness_check_count": len(operator_start_readiness_checks),
        "operator_start_section_count": len(operator_start_sections),
        "operator_start_field_count": len(operator_start_fields),
        "operator_start_check_count": len(operator_start_checks),
        "operator_start_template_field_count": len(operator_start_template_fields),
        "operator_start_checklist_item_count": len(operator_start_checklist_items),
        "precheck_readiness_check_count": len(precheck_readiness_checks),
        "precheck_section_count": len(precheck_sections),
        "precheck_field_count": len(precheck_fields),
        "precheck_check_count": len(precheck_checks),
        "final_gate_readiness_check_count": len(final_gate_readiness_checks),
        "final_gate_section_count": len(final_gate_sections),
        "final_gate_field_count": len(final_gate_fields),
        "final_gate_check_count": len(final_gate_checks),
        "review_readiness_check_count": len(review_gate_checks),
        "review_section_count": len(review_sections),
        "review_field_count": len(review_fields),
        "review_check_count": len(review_checks),
        "observation_readiness_check_count": len(obs_gate_checks),
        "observation_section_count": len(observation_sections),
        "observation_field_count": len(observation_fields),
        "log_gate_check_count": len(log_gate_checks),
        "log_section_count": len(log_sections),
        "log_field_count": len(log_fields),
        "execution_gate_control_count": len(execution_gate_controls),
        "session_step_count": len(session_steps),
        "session_abort_trigger_count": len(session_abort),
        "session_operator_check_count": len(session_operator_checks),
        "execution_step_count": len(exec_steps),
        "shell_section_count": len(shell_sections),
        "form_field_count": len(form_fields),
        "validator_rule_count": len(validator_rules),
        "schema_required_count": len(schema_required),
        "empty_batch_candidate_zero": empty_batch.get("candidate_count") == 0,
        "empty_batch_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "execution_plan_section_count": len(EXECUTION_PLAN_SECTIONS),
        "execution_plan_field_count": len(EXECUTION_PLAN_FIELDS),
        "execution_plan_check_count": len(EXECUTION_PLAN_CHECKS),
        "execution_plan_template_field_count": len(plan_template["fields"]),
        "execution_plan_checklist_item_count": len(plan_checklist["checks"]),
        "execution_plan_packet_only": plan_packet["execution_plan_packet_only"] is True,
        "session_execution_not_performed": plan_packet["session_execution_not_performed"] is True,
        "execution_plan_no_real_data": plan_packet["real_data_captured_in_this_phase"] is False,
        "execution_plan_no_candidate_insert": plan_packet["real_candidate_inserted"] is False,
        "execution_plan_no_dataset_acceptance": plan_packet["real_candidate_accepted_to_dataset"] is False,
        "start_command_not_allowed": plan_packet["execution_plan_boundary"]["start_command_allowed"] is False,
        "manual_session_execution_not_allowed": plan_packet["execution_plan_boundary"]["manual_session_execution_allowed"] is False,
        "contract_packet_only": contract["execution_plan_packet_only"] is True,
        "contract_execution_not_performed": contract["session_execution_not_performed"] is True,
        "contract_start_command_blocked": contract["start_command_blocked"] is True,
        "contract_manual_session_execution_blocked": contract["manual_session_execution_blocked"] is True,
        "roadmap_doc_exists": ROADMAP_DOC.exists(),
        "roadmap_json_exists": ROADMAP_JSON.exists(),
        "roadmap_item_count": len(ROADMAP_ITEMS),
        "roadmap_current_phase_present": any(item["phase"] == PHASE and item["status"] == "CURRENT" for item in ROADMAP_ITEMS),
        "roadmap_next_phase_present": any(item["phase"] == "PROD-4661..4700" and item["status"] == "NEXT" for item in ROADMAP_ITEMS),
        "start_command_blocked": "start_command_execution" in BLOCKED,
        "manual_session_execution_blocked": "manual_session_execution" in BLOCKED,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "real_candidate_insert_blocked": "real_candidate_insert" in BLOCKED,
        "real_candidate_dataset_acceptance_blocked": "real_candidate_dataset_acceptance" in BLOCKED,
        "dataset_accept_without_review_blocked": "dataset_acceptance_without_human_review" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED
    }

    minimums = {
        "operator_start_readiness_check_count": 83,
        "operator_start_section_count": 22,
        "operator_start_field_count": 32,
        "operator_start_check_count": 78,
        "precheck_readiness_check_count": 73,
        "precheck_section_count": 20,
        "precheck_field_count": 28,
        "precheck_check_count": 60,
        "final_gate_readiness_check_count": 64,
        "final_gate_section_count": 18,
        "final_gate_field_count": 24,
        "final_gate_check_count": 53,
        "review_readiness_check_count": 55,
        "review_section_count": 16,
        "review_field_count": 22,
        "review_check_count": 38,
        "observation_readiness_check_count": 50,
        "observation_section_count": 15,
        "observation_field_count": 20,
        "log_gate_check_count": 39,
        "log_section_count": 12,
        "log_field_count": 20,
        "execution_gate_control_count": 34,
        "session_step_count": 22,
        "session_abort_trigger_count": 14,
        "session_operator_check_count": 20,
        "execution_step_count": 18,
        "shell_section_count": 17,
        "form_field_count": 16,
        "validator_rule_count": 20,
        "schema_required_count": 23,
        "execution_plan_section_count": 24,
        "execution_plan_field_count": 36,
        "execution_plan_check_count": 90,
        "roadmap_item_count": 17
    }

    for key, minimum in minimums.items():
        if checks.get(key, 0) < minimum:
            errors.append(f"{key} below {minimum}")

    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_EXECUTION_PLAN_PACKET_READY" if status == "PASS" else "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_EXECUTION_PLAN_PACKET_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "execution_plan_section_count": len(EXECUTION_PLAN_SECTIONS),
        "execution_plan_field_count": len(EXECUTION_PLAN_FIELDS),
        "execution_plan_check_count": len(EXECUTION_PLAN_CHECKS),
        "roadmap_updated": True,
        "roadmap_item_count": len(ROADMAP_ITEMS),
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "real_dataset_candidate_count": empty_batch.get("candidate_count", 0),
        "real_dataset_accepted_count": empty_batch.get("accepted_count", 0),
        "recommended_next_phase": plan_packet["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-4621..4660 Controlled Pilot Manual Dry Run Session Execution Plan Packet",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Execution plan sections: `{len(EXECUTION_PLAN_SECTIONS)}`",
        f"- Execution plan fields: `{len(EXECUTION_PLAN_FIELDS)}`",
        f"- Execution plan checks: `{len(EXECUTION_PLAN_CHECKS)}`",
        f"- Roadmap updated: `{result['roadmap_updated']}`",
        f"- Roadmap items: `{len(ROADMAP_ITEMS)}`",
        f"- Real candidate inserted: `{result['real_candidate_inserted']}`",
        f"- Real candidate accepted to dataset: `{result['real_candidate_accepted_to_dataset']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{plan_packet['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Execution plan packet only.",
        "- No start command executed.",
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
    print("execution_plan_sections:", len(EXECUTION_PLAN_SECTIONS))
    print("execution_plan_fields:", len(EXECUTION_PLAN_FIELDS))
    print("execution_plan_checks:", len(EXECUTION_PLAN_CHECKS))
    print("roadmap_updated:", result["roadmap_updated"])
    print("roadmap_items:", len(ROADMAP_ITEMS))
    print("real_candidate_inserted:", result["real_candidate_inserted"])
    print("real_candidate_accepted_to_dataset:", result["real_candidate_accepted_to_dataset"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", plan_packet["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

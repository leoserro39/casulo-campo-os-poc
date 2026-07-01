#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-4781..4820"
REQ_TAG = "product-controlled-pilot-manual-dry-run-session-manual-execution-hold-readiness-gate-v0.1"

PREV_OUT = ROOT / "outputs/prod4741_4780_controlled_pilot_manual_dry_run_session_manual_execution_hold_readiness_gate.json"
HOLD_READINESS_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_manual_execution_hold_readiness_gate_v0_1.json"
HOLD_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_manual_execution_hold_packet_v0_1.json"
HOLD_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_manual_execution_hold_template_v0_1.json"
HOLD_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_manual_execution_hold_checklist_v0_1.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"
ROADMAP_JSON = ROOT / "outputs/prod4741_4780_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

PLAN_READINESS_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_plan_readiness_gate_v0_1.json"
PLAN_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_plan_packet_v0_1.json"
OPERATOR_START_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_operator_start_readiness_gate_v0_1.json"
OPERATOR_START_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_operator_start_packet_v0_1.json"
PRECHECK_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_precheck_readiness_gate_v0_1.json"
PRECHECK_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_precheck_packet_v0_1.json"
FINAL_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_gate_readiness_gate_v0_1.json"
FINAL_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_gate_packet_v0_1.json"
REVIEW_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_review_readiness_gate_v0_1.json"
REVIEW_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_review_packet_v0_1.json"
OBS_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_observation_readiness_gate_v0_1.json"
OBS_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_observation_packet_v0_1.json"
LOG_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_log_readiness_gate_v0_1.json"
LOG_SHELL = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_log_shell_v0_1.json"
EXEC_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_execution_gate_v0_1.json"
SESSION_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_packet_v0_1.json"
SESSION_RUNBOOK = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_packet_v0_1.md"
EXEC_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_packet_v0_1.json"
SHELL = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.json"
FORM = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_form_v0_1.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_validator_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"

DOC = ROOT / "docs/product/621_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_HUMAN_RELEASE_PACKET.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_manual_dry_run_session_human_release_packet.contract.json"
SPEC = ROOT / "product/memory/controlled_pilot_manual_dry_run_session_human_release_packet_v0_1.json"
RELEASE_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_human_release_packet_v0_1.json"
RELEASE_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_human_release_template_v0_1.json"
RELEASE_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_human_release_checklist_v0_1.json"
OUT_JSON = ROOT / "outputs/prod4781_4820_controlled_pilot_manual_dry_run_session_human_release_packet.json"
OUT_MD = ROOT / "outputs/prod4781_4820_controlled_pilot_manual_dry_run_session_human_release_packet.md"
ROADMAP_OUT = ROOT / "outputs/prod4781_4820_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

RELEASE_SECTIONS = [
    "human_release_context_refs",
    "prior_hold_readiness_review",
    "manual_execution_hold_packet_review",
    "execution_plan_review",
    "operator_start_review",
    "precheck_review",
    "final_gate_review",
    "review_packet_review",
    "observation_packet_review",
    "execution_log_review",
    "session_packet_review",
    "operator_identity_confirmation",
    "human_reviewer_identity_confirmation",
    "scope_confirmation",
    "source_reference_confirmation",
    "privacy_review_confirmation",
    "pii_redaction_confirmation",
    "secret_scan_confirmation",
    "evidence_capture_confirmation",
    "abort_trigger_confirmation",
    "blocked_action_confirmation",
    "claim_boundary_confirmation",
    "dataset_hold_confirmation",
    "manual_execution_release_boundary",
    "start_command_release_boundary",
    "human_acknowledgement_required",
    "dual_review_required",
    "post_release_readiness_gate_required",
    "roadmap_update",
    "next_phase_boundary"
]

RELEASE_FIELDS = [
    "human_release_packet_id",
    "phase",
    "hold_readiness_gate_ref",
    "hold_packet_ref",
    "hold_template_ref",
    "hold_checklist_ref",
    "execution_plan_readiness_gate_ref",
    "execution_plan_packet_ref",
    "operator_start_readiness_gate_ref",
    "operator_start_packet_ref",
    "precheck_readiness_gate_ref",
    "precheck_packet_ref",
    "final_gate_ref",
    "review_packet_ref",
    "observation_packet_ref",
    "execution_log_shell_ref",
    "session_packet_ref",
    "session_runbook_ref",
    "dry_run_shell_ref",
    "dry_run_form_ref",
    "operator_ref",
    "human_reviewer_ref",
    "second_reviewer_ref",
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
    "start_command_release_scope",
    "manual_execution_release_scope",
    "human_acknowledgement",
    "dual_review_acknowledgement",
    "release_decision",
    "release_reason",
    "next_allowed_phase",
    "stop_before_execution_confirmation",
    "roadmap_ref"
]

RELEASE_CHECKS = [
    "prior_hold_readiness_gate_passed",
    "hold_readiness_gate_present",
    "hold_packet_present",
    "hold_template_present",
    "hold_checklist_present",
    "roadmap_doc_present",
    "roadmap_json_present",
    "execution_plan_readiness_gate_present",
    "execution_plan_packet_present",
    "operator_start_readiness_gate_present",
    "operator_start_packet_present",
    "precheck_readiness_gate_present",
    "precheck_packet_present",
    "final_gate_present",
    "final_packet_present",
    "review_gate_present",
    "review_packet_present",
    "observation_gate_present",
    "observation_packet_present",
    "log_gate_present",
    "log_shell_present",
    "execution_gate_present",
    "session_packet_present",
    "session_runbook_present",
    "execution_packet_present",
    "dry_run_shell_present",
    "dry_run_form_present",
    "validator_present",
    "schema_present",
    "real_dataset_empty",
    "reviewer_queue_empty",
    "release_sections_present",
    "release_fields_present",
    "release_checks_present",
    "release_template_fields_present",
    "release_checklist_items_present",
    "hold_sections_present",
    "hold_fields_present",
    "hold_checks_present",
    "roadmap_current_phase_done",
    "roadmap_next_phase_current",
    "roadmap_following_phase_next",
    "operator_ref_required",
    "human_reviewer_ref_required",
    "second_reviewer_ref_required",
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
    "start_command_release_scope_required",
    "manual_execution_release_scope_required",
    "human_acknowledgement_required",
    "dual_review_acknowledgement_required",
    "release_decision_required",
    "release_reason_required",
    "next_allowed_phase_required",
    "stop_before_execution_confirmation_required",
    "roadmap_ref_required",
    "human_release_packet_only_confirmed",
    "human_release_packet_is_not_execution",
    "post_release_readiness_gate_required",
    "start_command_still_blocked",
    "manual_session_execution_still_blocked",
    "automatic_capture_blocked",
    "real_candidate_insert_blocked",
    "dataset_acceptance_blocked",
    "raw_private_data_blocked",
    "secrets_blocked",
    "unredacted_pii_blocked",
    "client_claim_blocked",
    "production_activation_blocked",
    "human_review_required",
    "dual_review_required",
    "operator_acknowledgement_required",
    "reviewer_acknowledgement_required",
    "manual_release_is_conditional",
    "release_does_not_override_data_boundary",
    "release_does_not_override_claim_boundary",
    "release_does_not_override_dataset_hold",
    "release_does_not_override_privacy_hold",
    "release_does_not_override_secret_hold",
    "release_does_not_override_pii_hold",
    "no_real_value_claim",
    "no_validated_hallucination_claim",
    "no_commercial_pricing_claim",
    "no_gpt_memory_api_execution",
    "no_automatic_memory_delete",
    "controlled_pilot_boundary_confirmed",
    "roadmap_updated",
    "human_release_readiness_gate_preparation_only",
    "execution_still_requires_next_gate",
    "start_command_still_requires_next_gate",
    "real_candidate_intake_still_requires_future_gate",
    "dataset_acceptance_still_requires_future_gate",
    "manual_execution_window_not_set",
    "operator_identity_placeholder_only",
    "reviewer_identity_placeholder_only",
    "release_packet_sanitized_placeholders_only"
]

ALLOWED = [
    "human_release_packet_creation",
    "human_release_template_creation",
    "human_release_checklist_creation",
    "roadmap_update",
    "human_release_readiness_gate_preparation"
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

def count_list(obj, key):
    val = obj.get(key, [])
    return len(val) if isinstance(val, list) else 0

def main():
    prev = read_json(PREV_OUT) if PREV_OUT.exists() else {}
    hold_gate = read_json(HOLD_READINESS_GATE) if HOLD_READINESS_GATE.exists() else {}
    hold = read_json(HOLD_PACKET) if HOLD_PACKET.exists() else {}
    hold_template = read_json(HOLD_TEMPLATE) if HOLD_TEMPLATE.exists() else {}
    hold_checklist = read_json(HOLD_CHECKLIST) if HOLD_CHECKLIST.exists() else {}
    roadmap_prev = read_json(ROADMAP_JSON) if ROADMAP_JSON.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    roadmap_items = roadmap_prev.get("roadmap_items", [])
    updated_items = []
    for item in roadmap_items:
        item = dict(item)
        if item.get("phase") == "PROD-4741..4780":
            item["status"] = "DONE"
        elif item.get("phase") == PHASE:
            item["status"] = "CURRENT"
        elif item.get("phase") == "PROD-4821..4860":
            item["status"] = "NEXT"
        updated_items.append(item)

    if not any(item.get("phase") == PHASE for item in updated_items):
        updated_items.append({"phase": PHASE, "name": "Human Release Packet", "status": "CURRENT"})
    if not any(item.get("phase") == "PROD-4821..4860" for item in updated_items):
        updated_items.append({"phase": "PROD-4821..4860", "name": "Human Release Readiness Gate", "status": "NEXT"})

    release_packet = {
        "version": "controlled_pilot_manual_dry_run_session_human_release_packet.v0.1",
        "phase": PHASE,
        "purpose": "Prepare a human release packet after hard hold readiness, without executing a session.",
        "human_release_packet_only": True,
        "human_release_packet_is_not_execution": True,
        "session_execution_not_performed": True,
        "start_command_executed": False,
        "manual_session_execution_performed": False,
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "release_sections": RELEASE_SECTIONS,
        "release_fields": RELEASE_FIELDS,
        "release_checks": RELEASE_CHECKS,
        "current_dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "human_release_boundary": {
            "human_release_packet_is_not_execution": True,
            "next_step_is_human_release_readiness_gate_only": True,
            "start_command_allowed": False,
            "manual_session_execution_allowed": False,
            "automatic_capture_allowed": False,
            "real_candidate_insert_allowed": False,
            "dataset_acceptance_allowed": False,
            "raw_private_data_allowed": False,
            "secret_storage_allowed": False,
            "unredacted_pii_allowed": False,
            "client_claim_allowed": False,
            "production_activation_allowed": False,
            "post_release_readiness_gate_required_before_execution": True
        },
        "claim_boundary": "Human release packet only. No session execution, no start command, no capture, no insert, no dataset acceptance.",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-4821..4860 - Controlled Pilot Manual Dry Run Session Human Release Readiness Gate"
    }

    release_template = {
        "version": "controlled_pilot_manual_dry_run_session_human_release_template.v0.1",
        "phase": PHASE,
        "status": "HUMAN_RELEASE_TEMPLATE_ONLY_NO_SESSION_EXECUTION",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "fields": {
            field: {"value": None, "required": True, "storage_rule": "reference_only_or_sanitized_placeholder"}
            for field in RELEASE_FIELDS
        },
        "default_gate": "HOLD_HUMAN_RELEASE_NO_SESSION_EXECUTION",
        "blocked_actions": BLOCKED
    }

    release_checklist = {
        "version": "controlled_pilot_manual_dry_run_session_human_release_checklist.v0.1",
        "phase": PHASE,
        "status": "CHECKLIST_TEMPLATE_ONLY_NO_SESSION_EXECUTION",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "checks": [
            {"id": f"REL-{i+1:03d}", "name": name, "required": True, "status": "PENDING"}
            for i, name in enumerate(RELEASE_CHECKS)
        ],
        "default_gate": "HOLD_HUMAN_RELEASE_NO_SESSION_EXECUTION",
        "blocked_actions": BLOCKED
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_roadmap.v0.5",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": updated_items,
        "current_phase": "PROD-4781..4820 - Controlled Pilot Manual Dry Run Session Human Release Packet",
        "next_phase": release_packet["recommended_next_phase"],
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "blocked_actions": BLOCKED
    }

    spec = {
        "version": "controlled_pilot_manual_dry_run_session_human_release_packet.v0.1",
        "phase": PHASE,
        "purpose": release_packet["purpose"],
        "release_section_count": len(RELEASE_SECTIONS),
        "release_field_count": len(RELEASE_FIELDS),
        "release_check_count": len(RELEASE_CHECKS),
        "roadmap_updated": True,
        "human_release_packet_is_not_execution": True,
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": release_packet["recommended_next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_manual_dry_run_session_human_release_packet",
        "human_release_packet_only": True,
        "human_release_packet_is_not_execution": True,
        "session_execution_not_performed": True,
        "start_command_blocked": True,
        "manual_session_execution_blocked": True,
        "automatic_capture_blocked": True,
        "dataset_acceptance_blocked": True,
        "post_release_readiness_gate_required_before_execution": True,
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": release_packet["recommended_next_phase"]
    }

    doc = """# PROD-4781..4820 - Controlled Pilot Manual Dry Run Session Human Release Packet

Creates the human release packet after the manual execution hard hold readiness gate.

This phase does not execute a session, does not run a start command, does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

Boundary: human release packet only. This packet is not execution. Any real/manual execution remains blocked until at least one later explicit readiness gate.
"""

    roadmap_md = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in updated_items:
        roadmap_md.append(f"- `{item['phase']}` - {item['name']} - **{item['status']}**")
    roadmap_md += [
        "",
        "## Current boundary",
        "- Current phase creates the human release packet.",
        "- Human release packet is not execution.",
        "- No session execution.",
        "- No start command.",
        "- No real candidate insert.",
        "- No dataset acceptance.",
        "- Post-release readiness gate remains required before any actual execution."
    ]

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_md))
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(RELEASE_PACKET, release_packet)
    write_json(RELEASE_TEMPLATE, release_template)
    write_json(RELEASE_CHECKLIST, release_checklist)
    write_json(ROADMAP_OUT, roadmap_out)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_decision_human_release_packet_prep_only": prev.get("decision") == "APPROVED_FOR_CONTROLLED_MANUAL_DRY_RUN_SESSION_HUMAN_RELEASE_PACKET_PREPARATION_ONLY",
        "previous_real_candidate_not_inserted": prev.get("real_candidate_inserted") is False,
        "previous_real_candidate_not_accepted": prev.get("real_candidate_accepted_to_dataset") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "hold_readiness_gate_exists": HOLD_READINESS_GATE.exists(),
        "hold_packet_exists": HOLD_PACKET.exists(),
        "hold_template_exists": HOLD_TEMPLATE.exists(),
        "hold_checklist_exists": HOLD_CHECKLIST.exists(),
        "roadmap_doc_exists": ROADMAP_DOC.exists(),
        "roadmap_json_exists": ROADMAP_JSON.exists(),
        "plan_readiness_gate_exists": PLAN_READINESS_GATE.exists(),
        "plan_packet_exists": PLAN_PACKET.exists(),
        "operator_start_gate_exists": OPERATOR_START_GATE.exists(),
        "operator_start_packet_exists": OPERATOR_START_PACKET.exists(),
        "precheck_gate_exists": PRECHECK_GATE.exists(),
        "precheck_packet_exists": PRECHECK_PACKET.exists(),
        "final_gate_exists": FINAL_GATE.exists(),
        "final_packet_exists": FINAL_PACKET.exists(),
        "review_gate_exists": REVIEW_GATE.exists(),
        "review_packet_exists": REVIEW_PACKET.exists(),
        "observation_gate_exists": OBS_GATE.exists(),
        "observation_packet_exists": OBS_PACKET.exists(),
        "log_gate_exists": LOG_GATE.exists(),
        "log_shell_exists": LOG_SHELL.exists(),
        "execution_gate_exists": EXEC_GATE.exists(),
        "session_packet_exists": SESSION_PACKET.exists(),
        "session_runbook_exists": SESSION_RUNBOOK.exists(),
        "execution_packet_exists": EXEC_PACKET.exists(),
        "dry_run_shell_exists": SHELL.exists(),
        "dry_run_form_exists": FORM.exists(),
        "validator_exists": VALIDATOR.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "schema_exists": SCHEMA.exists(),
        "hold_readiness_check_count": count_list(hold_gate, "readiness_checks"),
        "hold_section_count": count_list(hold, "hold_sections"),
        "hold_field_count": count_list(hold, "hold_fields"),
        "hold_check_count": count_list(hold, "hold_checks"),
        "hold_template_field_count": len(hold_template.get("fields", {})),
        "hold_checklist_item_count": count_list(hold_checklist, "checks"),
        "schema_required_count": count_list(schema, "required"),
        "empty_batch_candidate_zero": empty_batch.get("candidate_count") == 0,
        "empty_batch_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "release_section_count": len(RELEASE_SECTIONS),
        "release_field_count": len(RELEASE_FIELDS),
        "release_check_count": len(RELEASE_CHECKS),
        "release_template_field_count": len(release_template["fields"]),
        "release_checklist_item_count": len(release_checklist["checks"]),
        "release_packet_only": release_packet["human_release_packet_only"] is True,
        "release_packet_is_not_execution": release_packet["human_release_packet_is_not_execution"] is True,
        "session_execution_not_performed": release_packet["session_execution_not_performed"] is True,
        "start_command_executed_false": release_packet["start_command_executed"] is False,
        "manual_session_execution_performed_false": release_packet["manual_session_execution_performed"] is False,
        "release_no_real_data": release_packet["real_data_captured_in_this_phase"] is False,
        "release_no_candidate_insert": release_packet["real_candidate_inserted"] is False,
        "release_no_dataset_acceptance": release_packet["real_candidate_accepted_to_dataset"] is False,
        "start_command_not_allowed": release_packet["human_release_boundary"]["start_command_allowed"] is False,
        "manual_session_execution_not_allowed": release_packet["human_release_boundary"]["manual_session_execution_allowed"] is False,
        "post_release_readiness_required": release_packet["human_release_boundary"]["post_release_readiness_gate_required_before_execution"] is True,
        "contract_release_only": contract["human_release_packet_only"] is True,
        "contract_release_not_execution": contract["human_release_packet_is_not_execution"] is True,
        "contract_execution_not_performed": contract["session_execution_not_performed"] is True,
        "contract_start_command_blocked": contract["start_command_blocked"] is True,
        "contract_manual_session_execution_blocked": contract["manual_session_execution_blocked"] is True,
        "roadmap_item_count": len(updated_items),
        "roadmap_current_phase_present": any(item.get("phase") == PHASE and item.get("status") == "CURRENT" for item in updated_items),
        "roadmap_next_phase_present": any(item.get("phase") == "PROD-4821..4860" and item.get("status") == "NEXT" for item in updated_items),
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
        "hold_readiness_check_count": 97,
        "hold_section_count": 26,
        "hold_field_count": 36,
        "hold_check_count": 90,
        "hold_template_field_count": 36,
        "hold_checklist_item_count": 90,
        "schema_required_count": 23,
        "release_section_count": 30,
        "release_field_count": 43,
        "release_check_count": 105,
        "release_template_field_count": 43,
        "release_checklist_item_count": 105,
        "roadmap_item_count": 17
    }

    errors = []
    for key, minimum in minimums.items():
        if checks.get(key, 0) < minimum:
            errors.append(f"{key} below {minimum}")

    for key, value in checks.items():
        if isinstance(value, bool) and not value:
            errors.append("check failed: " + key)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_HUMAN_RELEASE_PACKET_READY" if status == "PASS" else "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_HUMAN_RELEASE_PACKET_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "release_section_count": len(RELEASE_SECTIONS),
        "release_field_count": len(RELEASE_FIELDS),
        "release_check_count": len(RELEASE_CHECKS),
        "roadmap_updated": True,
        "roadmap_item_count": len(updated_items),
        "human_release_packet_is_not_execution": True,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "real_dataset_candidate_count": empty_batch.get("candidate_count", 0),
        "real_dataset_accepted_count": empty_batch.get("accepted_count", 0),
        "recommended_next_phase": release_packet["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-4781..4820 Controlled Pilot Manual Dry Run Session Human Release Packet",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Release sections: `{len(RELEASE_SECTIONS)}`",
        f"- Release fields: `{len(RELEASE_FIELDS)}`",
        f"- Release checks: `{len(RELEASE_CHECKS)}`",
        f"- Roadmap updated: `{result['roadmap_updated']}`",
        f"- Human release packet is not execution: `{result['human_release_packet_is_not_execution']}`",
        f"- Real candidate inserted: `{result['real_candidate_inserted']}`",
        f"- Real candidate accepted to dataset: `{result['real_candidate_accepted_to_dataset']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{release_packet['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Human release packet only.",
        "- Human release packet is not execution.",
        "- No start command executed.",
        "- No session execution performed.",
        "- No real candidate inserted.",
        "- No dataset acceptance.",
        "- Post-release readiness gate remains required.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("release_sections:", len(RELEASE_SECTIONS))
    print("release_fields:", len(RELEASE_FIELDS))
    print("release_checks:", len(RELEASE_CHECKS))
    print("roadmap_updated:", result["roadmap_updated"])
    print("human_release_packet_is_not_execution:", result["human_release_packet_is_not_execution"])
    print("real_candidate_inserted:", result["real_candidate_inserted"])
    print("real_candidate_accepted_to_dataset:", result["real_candidate_accepted_to_dataset"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", release_packet["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-4861..4900"
REQ_TAG = "product-controlled-pilot-manual-dry-run-session-human-release-readiness-gate-v0.1"

PREV_OUT = ROOT / "outputs/prod4821_4860_controlled_pilot_manual_dry_run_session_human_release_readiness_gate.json"
RELEASE_READINESS_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_human_release_readiness_gate_v0_1.json"
RELEASE_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_human_release_packet_v0_1.json"
RELEASE_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_human_release_template_v0_1.json"
RELEASE_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_human_release_checklist_v0_1.json"

HOLD_READINESS_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_manual_execution_hold_readiness_gate_v0_1.json"
HOLD_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_manual_execution_hold_packet_v0_1.json"
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
SHELL = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.json"
FORM = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_form_v0_1.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_validator_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"
ROADMAP_JSON = ROOT / "outputs/prod4821_4860_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/623_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_FINAL_HUMAN_GO_NO_GO_PACKET.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_manual_dry_run_session_final_human_go_no_go_packet.contract.json"
SPEC = ROOT / "product/memory/controlled_pilot_manual_dry_run_session_final_human_go_no_go_packet_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_human_go_no_go_packet_v0_1.json"
TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_human_go_no_go_template_v0_1.json"
CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_human_go_no_go_checklist_v0_1.json"
OUT_JSON = ROOT / "outputs/prod4861_4900_controlled_pilot_manual_dry_run_session_final_human_go_no_go_packet.json"
OUT_MD = ROOT / "outputs/prod4861_4900_controlled_pilot_manual_dry_run_session_final_human_go_no_go_packet.md"
ROADMAP_OUT = ROOT / "outputs/prod4861_4900_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

GO_NO_GO_SECTIONS = [
    "go_no_go_context_refs",
    "prior_human_release_readiness_review",
    "human_release_packet_review",
    "manual_execution_hold_review",
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
    "second_reviewer_identity_confirmation",
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
    "manual_execution_boundary",
    "start_command_boundary",
    "go_decision_placeholder",
    "no_go_decision_placeholder",
    "conditional_go_decision_placeholder",
    "post_go_no_go_readiness_gate_required",
    "roadmap_update"
]

GO_NO_GO_FIELDS = [
    "final_go_no_go_packet_id",
    "phase",
    "human_release_readiness_gate_ref",
    "human_release_packet_ref",
    "human_release_template_ref",
    "human_release_checklist_ref",
    "hold_readiness_gate_ref",
    "hold_packet_ref",
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
    "start_command_scope",
    "manual_execution_scope",
    "go_no_go_decision",
    "go_no_go_reason",
    "conditional_release_constraints",
    "post_go_no_go_readiness_gate_required",
    "next_allowed_phase",
    "stop_before_execution_confirmation",
    "roadmap_ref",
    "signature_placeholder"
]

GO_NO_GO_CHECKS = [
    "prior_human_release_readiness_gate_passed",
    "human_release_readiness_gate_present",
    "human_release_packet_present",
    "human_release_template_present",
    "human_release_checklist_present",
    "roadmap_doc_present",
    "roadmap_json_present",
    "hold_readiness_gate_present",
    "hold_packet_present",
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
    "dry_run_shell_present",
    "dry_run_form_present",
    "validator_present",
    "schema_present",
    "real_dataset_empty",
    "reviewer_queue_empty",
    "go_no_go_sections_present",
    "go_no_go_fields_present",
    "go_no_go_checks_present",
    "go_no_go_template_fields_present",
    "go_no_go_checklist_items_present",
    "release_sections_present",
    "release_fields_present",
    "release_checks_present",
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
    "start_command_scope_required",
    "manual_execution_scope_required",
    "go_no_go_decision_required",
    "go_no_go_reason_required",
    "conditional_release_constraints_required",
    "post_go_no_go_readiness_gate_required",
    "next_allowed_phase_required",
    "stop_before_execution_confirmation_required",
    "roadmap_ref_required",
    "signature_placeholder_required",
    "final_go_no_go_packet_only_confirmed",
    "final_go_no_go_packet_is_not_execution",
    "post_go_no_go_readiness_gate_required_before_execution",
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
    "go_decision_is_placeholder_only",
    "no_go_decision_is_placeholder_only",
    "conditional_go_is_placeholder_only",
    "go_no_go_does_not_override_data_boundary",
    "go_no_go_does_not_override_claim_boundary",
    "go_no_go_does_not_override_dataset_hold",
    "go_no_go_does_not_override_privacy_hold",
    "go_no_go_does_not_override_secret_hold",
    "go_no_go_does_not_override_pii_hold",
    "no_real_value_claim",
    "no_validated_hallucination_claim",
    "no_commercial_pricing_claim",
    "no_gpt_memory_api_execution",
    "no_automatic_memory_delete",
    "controlled_pilot_boundary_confirmed",
    "roadmap_updated",
    "go_no_go_readiness_gate_preparation_only",
    "execution_still_requires_future_gate",
    "start_command_still_requires_future_gate",
    "real_candidate_intake_still_requires_future_gate",
    "dataset_acceptance_still_requires_future_gate",
    "manual_execution_window_not_set",
    "operator_identity_placeholder_only",
    "reviewer_identity_placeholder_only",
    "go_no_go_packet_sanitized_placeholders_only",
    "final_decision_packet_does_not_capture_data",
    "final_decision_packet_does_not_insert_candidate",
    "final_decision_packet_does_not_accept_dataset",
    "final_decision_packet_does_not_start_session",
    "final_decision_packet_does_not_execute_command",
    "final_decision_packet_requires_next_readiness_gate",
    "go_no_go_packet_has_explicit_blocked_actions",
    "go_no_go_packet_has_allowed_actions",
    "go_no_go_packet_has_boundary_claim",
    "go_no_go_packet_has_dataset_state",
    "go_no_go_packet_has_next_phase",
    "go_no_go_packet_has_stop_before_execution",
    "go_no_go_packet_has_signature_placeholder",
    "go_no_go_packet_has_dual_reviewer_requirement",
    "go_no_go_packet_has_abort_trigger_review",
    "go_no_go_packet_has_privacy_review",
    "go_no_go_packet_has_secret_scan",
    "go_no_go_packet_has_pii_redaction",
    "go_no_go_packet_has_source_reference",
    "go_no_go_packet_has_evidence_reference",
    "go_no_go_packet_has_claim_boundary_review",
    "go_no_go_packet_has_conditional_constraints"
]

ALLOWED = [
    "final_human_go_no_go_packet_creation",
    "final_human_go_no_go_template_creation",
    "final_human_go_no_go_checklist_creation",
    "roadmap_update",
    "final_human_go_no_go_readiness_gate_preparation"
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
    release_gate = read_json(RELEASE_READINESS_GATE) if RELEASE_READINESS_GATE.exists() else {}
    release = read_json(RELEASE_PACKET) if RELEASE_PACKET.exists() else {}
    release_template = read_json(RELEASE_TEMPLATE) if RELEASE_TEMPLATE.exists() else {}
    release_checklist = read_json(RELEASE_CHECKLIST) if RELEASE_CHECKLIST.exists() else {}
    roadmap_prev = read_json(ROADMAP_JSON) if ROADMAP_JSON.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    roadmap_items = roadmap_prev.get("roadmap_items", [])
    updated_items = []
    for item in roadmap_items:
        item = dict(item)
        if item.get("phase") == "PROD-4821..4860":
            item["status"] = "DONE"
        elif item.get("phase") == PHASE:
            item["status"] = "CURRENT"
        elif item.get("phase") == "PROD-4901..4940":
            item["status"] = "NEXT"
        updated_items.append(item)

    if not any(item.get("phase") == PHASE for item in updated_items):
        updated_items.append({"phase": PHASE, "name": "Final Human Go No-Go Packet", "status": "CURRENT"})
    if not any(item.get("phase") == "PROD-4901..4940" for item in updated_items):
        updated_items.append({"phase": "PROD-4901..4940", "name": "Final Human Go No-Go Readiness Gate", "status": "NEXT"})

    packet = {
        "version": "controlled_pilot_manual_dry_run_session_final_human_go_no_go_packet.v0.1",
        "phase": PHASE,
        "purpose": "Prepare final human go/no-go packet without executing a session.",
        "final_go_no_go_packet_only": True,
        "final_go_no_go_packet_is_not_execution": True,
        "post_go_no_go_readiness_gate_required_before_execution": True,
        "session_execution_not_performed": True,
        "start_command_executed": False,
        "manual_session_execution_performed": False,
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "go_no_go_sections": GO_NO_GO_SECTIONS,
        "go_no_go_fields": GO_NO_GO_FIELDS,
        "go_no_go_checks": GO_NO_GO_CHECKS,
        "current_dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "go_no_go_boundary": {
            "packet_is_not_execution": True,
            "next_step_is_go_no_go_readiness_gate_only": True,
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
        "claim_boundary": "Final human go/no-go packet only. No session execution, no start command, no capture, no insert, no dataset acceptance.",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-4901..4940 - Controlled Pilot Manual Dry Run Session Final Human Go No-Go Readiness Gate"
    }

    template = {
        "version": "controlled_pilot_manual_dry_run_session_final_human_go_no_go_template.v0.1",
        "phase": PHASE,
        "status": "FINAL_HUMAN_GO_NO_GO_TEMPLATE_ONLY_NO_SESSION_EXECUTION",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "fields": {
            field: {"value": None, "required": True, "storage_rule": "reference_only_or_sanitized_placeholder"}
            for field in GO_NO_GO_FIELDS
        },
        "default_gate": "HOLD_FINAL_HUMAN_GO_NO_GO_NO_SESSION_EXECUTION",
        "blocked_actions": BLOCKED
    }

    checklist = {
        "version": "controlled_pilot_manual_dry_run_session_final_human_go_no_go_checklist.v0.1",
        "phase": PHASE,
        "status": "CHECKLIST_TEMPLATE_ONLY_NO_SESSION_EXECUTION",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "checks": [
            {"id": f"GNG-{i+1:03d}", "name": name, "required": True, "status": "PENDING"}
            for i, name in enumerate(GO_NO_GO_CHECKS)
        ],
        "default_gate": "HOLD_FINAL_HUMAN_GO_NO_GO_NO_SESSION_EXECUTION",
        "blocked_actions": BLOCKED
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_roadmap.v0.7",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": updated_items,
        "current_phase": "PROD-4861..4900 - Controlled Pilot Manual Dry Run Session Final Human Go No-Go Packet",
        "next_phase": packet["recommended_next_phase"],
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "blocked_actions": BLOCKED
    }

    spec = {
        "version": "controlled_pilot_manual_dry_run_session_final_human_go_no_go_packet.v0.1",
        "phase": PHASE,
        "purpose": packet["purpose"],
        "go_no_go_section_count": len(GO_NO_GO_SECTIONS),
        "go_no_go_field_count": len(GO_NO_GO_FIELDS),
        "go_no_go_check_count": len(GO_NO_GO_CHECKS),
        "roadmap_updated": True,
        "final_go_no_go_packet_is_not_execution": True,
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": packet["recommended_next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_manual_dry_run_session_final_human_go_no_go_packet",
        "final_go_no_go_packet_only": True,
        "final_go_no_go_packet_is_not_execution": True,
        "session_execution_not_performed": True,
        "start_command_blocked": True,
        "manual_session_execution_blocked": True,
        "automatic_capture_blocked": True,
        "dataset_acceptance_blocked": True,
        "post_go_no_go_readiness_gate_required_before_execution": True,
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": packet["recommended_next_phase"]
    }

    doc = """# PROD-4861..4900 - Controlled Pilot Manual Dry Run Session Final Human Go/No-Go Packet

Creates the final human go/no-go packet after human release readiness.

This phase does not execute a session, does not run a start command, does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

Boundary: final human go/no-go packet only. This packet is not execution. Any real/manual execution remains blocked until a later explicit readiness gate.
"""

    roadmap_md = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in updated_items:
        roadmap_md.append(f"- `{item['phase']}` - {item['name']} - **{item['status']}**")
    roadmap_md += [
        "",
        "## Current boundary",
        "- Current phase creates the final human go/no-go packet.",
        "- The packet is not execution.",
        "- No session execution.",
        "- No start command.",
        "- No real candidate insert.",
        "- No dataset acceptance.",
        "- Final go/no-go readiness gate remains required before any actual execution."
    ]

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_md))
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(PACKET, packet)
    write_json(TEMPLATE, template)
    write_json(CHECKLIST, checklist)
    write_json(ROADMAP_OUT, roadmap_out)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_decision_final_go_no_go_packet_prep_only": prev.get("decision") == "APPROVED_FOR_CONTROLLED_MANUAL_DRY_RUN_SESSION_FINAL_GO_NO_GO_PACKET_PREPARATION_ONLY",
        "previous_final_go_no_go_prep_only": prev.get("final_go_no_go_packet_preparation_only") is True,
        "previous_final_go_no_go_not_execution": prev.get("final_go_no_go_packet_is_not_execution") is True,
        "previous_real_candidate_not_inserted": prev.get("real_candidate_inserted") is False,
        "previous_real_candidate_not_accepted": prev.get("real_candidate_accepted_to_dataset") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "release_readiness_gate_exists": RELEASE_READINESS_GATE.exists(),
        "release_packet_exists": RELEASE_PACKET.exists(),
        "release_template_exists": RELEASE_TEMPLATE.exists(),
        "release_checklist_exists": RELEASE_CHECKLIST.exists(),
        "roadmap_doc_exists": ROADMAP_DOC.exists(),
        "roadmap_json_exists": ROADMAP_JSON.exists(),
        "schema_exists": SCHEMA.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "release_readiness_check_count": count_list(release_gate, "readiness_checks"),
        "release_section_count": count_list(release, "release_sections"),
        "release_field_count": count_list(release, "release_fields"),
        "release_check_count": count_list(release, "release_checks"),
        "release_template_field_count": len(release_template.get("fields", {})),
        "release_checklist_item_count": count_list(release_checklist, "checks"),
        "schema_required_count": count_list(schema, "required"),
        "empty_batch_candidate_zero": empty_batch.get("candidate_count") == 0,
        "empty_batch_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "go_no_go_section_count": len(GO_NO_GO_SECTIONS),
        "go_no_go_field_count": len(GO_NO_GO_FIELDS),
        "go_no_go_check_count": len(GO_NO_GO_CHECKS),
        "go_no_go_template_field_count": len(template["fields"]),
        "go_no_go_checklist_item_count": len(checklist["checks"]),
        "go_no_go_packet_only": packet["final_go_no_go_packet_only"] is True,
        "go_no_go_packet_is_not_execution": packet["final_go_no_go_packet_is_not_execution"] is True,
        "session_execution_not_performed": packet["session_execution_not_performed"] is True,
        "start_command_executed_false": packet["start_command_executed"] is False,
        "manual_session_execution_performed_false": packet["manual_session_execution_performed"] is False,
        "go_no_go_no_real_data": packet["real_data_captured_in_this_phase"] is False,
        "go_no_go_no_candidate_insert": packet["real_candidate_inserted"] is False,
        "go_no_go_no_dataset_acceptance": packet["real_candidate_accepted_to_dataset"] is False,
        "start_command_not_allowed": packet["go_no_go_boundary"]["start_command_allowed"] is False,
        "manual_session_execution_not_allowed": packet["go_no_go_boundary"]["manual_session_execution_allowed"] is False,
        "roadmap_item_count": len(updated_items),
        "roadmap_current_phase_present": any(item.get("phase") == PHASE and item.get("status") == "CURRENT" for item in updated_items),
        "roadmap_next_phase_present": any(item.get("phase") == "PROD-4901..4940" and item.get("status") == "NEXT" for item in updated_items),
        "contract_packet_only": contract["final_go_no_go_packet_only"] is True,
        "contract_not_execution": contract["final_go_no_go_packet_is_not_execution"] is True,
        "contract_execution_not_performed": contract["session_execution_not_performed"] is True,
        "contract_start_command_blocked": contract["start_command_blocked"] is True,
        "contract_manual_session_execution_blocked": contract["manual_session_execution_blocked"] is True,
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
        "release_readiness_check_count": 122,
        "release_section_count": 30,
        "release_field_count": 43,
        "release_check_count": 105,
        "release_template_field_count": 43,
        "release_checklist_item_count": 105,
        "schema_required_count": 23,
        "go_no_go_section_count": 32,
        "go_no_go_field_count": 46,
        "go_no_go_check_count": 130,
        "go_no_go_template_field_count": 46,
        "go_no_go_checklist_item_count": 130,
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
        "decision": "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_FINAL_HUMAN_GO_NO_GO_PACKET_READY" if status == "PASS" else "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_FINAL_HUMAN_GO_NO_GO_PACKET_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "go_no_go_section_count": len(GO_NO_GO_SECTIONS),
        "go_no_go_field_count": len(GO_NO_GO_FIELDS),
        "go_no_go_check_count": len(GO_NO_GO_CHECKS),
        "roadmap_updated": True,
        "roadmap_item_count": len(updated_items),
        "final_go_no_go_packet_is_not_execution": True,
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
        "# PROD-4861..4900 Controlled Pilot Manual Dry Run Session Final Human Go/No-Go Packet",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Go/no-go sections: `{len(GO_NO_GO_SECTIONS)}`",
        f"- Go/no-go fields: `{len(GO_NO_GO_FIELDS)}`",
        f"- Go/no-go checks: `{len(GO_NO_GO_CHECKS)}`",
        f"- Roadmap updated: `{result['roadmap_updated']}`",
        f"- Final go/no-go packet is not execution: `{result['final_go_no_go_packet_is_not_execution']}`",
        f"- Real candidate inserted: `{result['real_candidate_inserted']}`",
        f"- Real candidate accepted to dataset: `{result['real_candidate_accepted_to_dataset']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{packet['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Final human go/no-go packet only.",
        "- Packet is not execution.",
        "- No start command executed.",
        "- No session execution performed.",
        "- No real candidate inserted.",
        "- No dataset acceptance.",
        "- Final go/no-go readiness gate remains required.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("go_no_go_sections:", len(GO_NO_GO_SECTIONS))
    print("go_no_go_fields:", len(GO_NO_GO_FIELDS))
    print("go_no_go_checks:", len(GO_NO_GO_CHECKS))
    print("roadmap_updated:", result["roadmap_updated"])
    print("final_go_no_go_packet_is_not_execution:", result["final_go_no_go_packet_is_not_execution"])
    print("real_candidate_inserted:", result["real_candidate_inserted"])
    print("real_candidate_accepted_to_dataset:", result["real_candidate_accepted_to_dataset"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", packet["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

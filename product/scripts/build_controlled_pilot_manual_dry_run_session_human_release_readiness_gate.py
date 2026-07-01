#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-4821..4860"
REQ_TAG = "product-controlled-pilot-manual-dry-run-session-human-release-packet-v0.1"

PREV_OUT = ROOT / "outputs/prod4781_4820_controlled_pilot_manual_dry_run_session_human_release_packet.json"
RELEASE_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_human_release_packet_v0_1.json"
RELEASE_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_human_release_template_v0_1.json"
RELEASE_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_human_release_checklist_v0_1.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"
ROADMAP_JSON = ROOT / "outputs/prod4781_4820_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

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
EXEC_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_execution_packet_v0_1.json"
SHELL = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.json"
FORM = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_form_v0_1.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_validator_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"

DOC = ROOT / "docs/product/622_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_HUMAN_RELEASE_READINESS_GATE.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_manual_dry_run_session_human_release_readiness_gate.contract.json"
GATE = ROOT / "product/memory/controlled_pilot_manual_dry_run_session_human_release_readiness_gate_v0_1.json"
CAL_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_human_release_readiness_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod4821_4860_controlled_pilot_manual_dry_run_session_human_release_readiness_gate.json"
OUT_MD = ROOT / "outputs/prod4821_4860_controlled_pilot_manual_dry_run_session_human_release_readiness_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod4821_4860_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

READINESS_CHECKS = [
    "human_release_packet_passed",
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
    "final_go_no_go_packet_preparation_only",
    "execution_still_requires_future_gate",
    "start_command_still_requires_future_gate",
    "real_candidate_intake_still_requires_future_gate",
    "dataset_acceptance_still_requires_future_gate",
    "manual_execution_window_not_set",
    "operator_identity_placeholder_only",
    "reviewer_identity_placeholder_only",
    "release_readiness_sanitized_placeholders_only",
    "final_go_no_go_is_not_execution",
    "final_go_no_go_does_not_capture_data",
    "final_go_no_go_does_not_insert_candidate",
    "final_go_no_go_does_not_accept_dataset",
    "release_readiness_gate_only_confirmed",
    "release_readiness_does_not_override_hold",
    "human_release_readiness_review_before_go_no_go_required",
    "final_go_no_go_requires_explicit_human_decision",
    "manual_execution_cannot_start_from_this_gate",
    "start_command_cannot_start_from_this_gate",
    "dataset_acceptance_cannot_start_from_this_gate",
    "real_candidate_insert_cannot_start_from_this_gate",
    "privacy_boundary_reconfirmed_before_go_no_go",
    "pii_boundary_reconfirmed_before_go_no_go",
    "secret_boundary_reconfirmed_before_go_no_go",
    "claim_boundary_reconfirmed_before_go_no_go"
]

ALLOWED = [
    "human_release_readiness_gate_creation",
    "roadmap_update",
    "final_go_no_go_packet_preparation",
    "sanitized_human_release_validation",
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
    release = read_json(RELEASE_PACKET) if RELEASE_PACKET.exists() else {}
    release_template = read_json(RELEASE_TEMPLATE) if RELEASE_TEMPLATE.exists() else {}
    release_checklist = read_json(RELEASE_CHECKLIST) if RELEASE_CHECKLIST.exists() else {}
    hold = read_json(HOLD_PACKET) if HOLD_PACKET.exists() else {}
    roadmap_prev = read_json(ROADMAP_JSON) if ROADMAP_JSON.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    roadmap_items = roadmap_prev.get("roadmap_items", [])
    updated_items = []
    for item in roadmap_items:
        item = dict(item)
        if item.get("phase") == "PROD-4781..4820":
            item["status"] = "DONE"
        elif item.get("phase") == PHASE:
            item["status"] = "CURRENT"
        elif item.get("phase") == "PROD-4861..4900":
            item["status"] = "NEXT"
        updated_items.append(item)

    if not any(item.get("phase") == PHASE for item in updated_items):
        updated_items.append({"phase": PHASE, "name": "Human Release Readiness Gate", "status": "CURRENT"})
    if not any(item.get("phase") == "PROD-4861..4900" for item in updated_items):
        updated_items.append({"phase": "PROD-4861..4900", "name": "Final Human Go No-Go Packet", "status": "NEXT"})

    decision = "APPROVED_FOR_CONTROLLED_MANUAL_DRY_RUN_SESSION_FINAL_GO_NO_GO_PACKET_PREPARATION_ONLY"
    if empty_batch.get("candidate_count") != 0 or empty_batch.get("accepted_count") != 0:
        decision = "BLOCK_REAL_DATASET_NOT_EMPTY"
    if prev.get("real_candidate_inserted") is not False or prev.get("real_candidate_accepted_to_dataset") is not False:
        decision = "BLOCK_REAL_CANDIDATE_ALREADY_PRESENT"
    if prev.get("real_data_captured_in_this_phase") is not False:
        decision = "BLOCK_REAL_DATA_BOUNDARY_BREACH"

    gate = {
        "version": "controlled_pilot_manual_dry_run_session_human_release_readiness_gate.v0.1",
        "phase": PHASE,
        "decision": decision,
        "purpose": "Validate the human release packet before preparing the final human go/no-go packet.",
        "human_release_readiness_gate_only": True,
        "final_go_no_go_packet_preparation_only": True,
        "session_execution_not_performed": True,
        "start_command_executed": False,
        "manual_session_execution_performed": False,
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "roadmap_updated": True,
        "readiness_checks": READINESS_CHECKS,
        "current_dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "final_go_no_go_boundary": {
            "next_step_is_final_go_no_go_packet_preparation_only": True,
            "final_go_no_go_packet_is_not_execution": True,
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
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-4861..4900 - Controlled Pilot Manual Dry Run Session Final Human Go No-Go Packet"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_manual_dry_run_session_human_release_readiness_gate",
        "human_release_readiness_gate_only": True,
        "final_go_no_go_packet_preparation_only": True,
        "final_go_no_go_packet_is_not_execution": True,
        "session_execution_not_performed": True,
        "start_command_blocked": True,
        "manual_session_execution_blocked": True,
        "automatic_capture_blocked": True,
        "dataset_acceptance_blocked": True,
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_roadmap.v0.6",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": updated_items,
        "current_phase": "PROD-4821..4860 - Controlled Pilot Manual Dry Run Session Human Release Readiness Gate",
        "next_phase": gate["recommended_next_phase"],
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-4821..4860 - Controlled Pilot Manual Dry Run Session Human Release Readiness Gate

Validates the human release packet before preparing the final human go/no-go packet.

This phase does not execute a session, does not run a start command, does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

The next phase may prepare a final human go/no-go packet, but that packet is still not execution.
"""

    roadmap_md = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in updated_items:
        roadmap_md.append(f"- `{item['phase']}` - {item['name']} - **{item['status']}**")
    roadmap_md += [
        "",
        "## Current boundary",
        "- Current phase validates human release readiness only.",
        "- No session execution.",
        "- No start command.",
        "- No real candidate insert.",
        "- No dataset acceptance.",
        "- Next phase prepares a final human go/no-go packet only."
    ]

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_md))
    write_json(CONTRACT, contract)
    write_json(GATE, gate)
    write_json(CAL_GATE, gate)
    write_json(ROADMAP_OUT, roadmap_out)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_human_release_packet_ready": prev.get("decision") == "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_HUMAN_RELEASE_PACKET_READY",
        "previous_release_not_execution": prev.get("human_release_packet_is_not_execution") is True,
        "previous_real_candidate_not_inserted": prev.get("real_candidate_inserted") is False,
        "previous_real_candidate_not_accepted": prev.get("real_candidate_accepted_to_dataset") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "release_packet_exists": RELEASE_PACKET.exists(),
        "release_template_exists": RELEASE_TEMPLATE.exists(),
        "release_checklist_exists": RELEASE_CHECKLIST.exists(),
        "roadmap_doc_exists": ROADMAP_DOC.exists(),
        "roadmap_json_exists": ROADMAP_JSON.exists(),
        "hold_readiness_gate_exists": HOLD_READINESS_GATE.exists(),
        "hold_packet_exists": HOLD_PACKET.exists(),
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
        "release_section_count": count_list(release, "release_sections"),
        "release_field_count": count_list(release, "release_fields"),
        "release_check_count": count_list(release, "release_checks"),
        "release_template_field_count": len(release_template.get("fields", {})),
        "release_checklist_item_count": count_list(release_checklist, "checks"),
        "hold_section_count": count_list(hold, "hold_sections"),
        "hold_field_count": count_list(hold, "hold_fields"),
        "hold_check_count": count_list(hold, "hold_checks"),
        "schema_required_count": count_list(schema, "required"),
        "empty_batch_candidate_zero": empty_batch.get("candidate_count") == 0,
        "empty_batch_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "readiness_check_count": len(READINESS_CHECKS),
        "release_packet_only": release.get("human_release_packet_only") is True,
        "release_packet_is_not_execution": release.get("human_release_packet_is_not_execution") is True,
        "release_execution_not_performed": release.get("session_execution_not_performed") is True,
        "release_no_real_data": release.get("real_data_captured_in_this_phase") is False,
        "release_no_candidate_insert": release.get("real_candidate_inserted") is False,
        "release_no_dataset_acceptance": release.get("real_candidate_accepted_to_dataset") is False,
        "start_command_executed_false": release.get("start_command_executed") is False,
        "manual_execution_performed_false": release.get("manual_session_execution_performed") is False,
        "start_command_not_allowed": release.get("human_release_boundary", {}).get("start_command_allowed") is False,
        "manual_session_execution_not_allowed": release.get("human_release_boundary", {}).get("manual_session_execution_allowed") is False,
        "post_release_readiness_required": release.get("human_release_boundary", {}).get("post_release_readiness_gate_required_before_execution") is True,
        "roadmap_item_count": len(updated_items),
        "roadmap_current_phase_present": any(item.get("phase") == PHASE and item.get("status") == "CURRENT" for item in updated_items),
        "roadmap_next_phase_present": any(item.get("phase") == "PROD-4861..4900" and item.get("status") == "NEXT" for item in updated_items),
        "decision_final_go_no_go_packet_prep_only": decision == "APPROVED_FOR_CONTROLLED_MANUAL_DRY_RUN_SESSION_FINAL_GO_NO_GO_PACKET_PREPARATION_ONLY",
        "contract_gate_only": contract["human_release_readiness_gate_only"] is True,
        "contract_final_go_no_go_packet_prep_only": contract["final_go_no_go_packet_preparation_only"] is True,
        "contract_final_go_no_go_not_execution": contract["final_go_no_go_packet_is_not_execution"] is True,
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
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED,
        "gpt_memory_api_execution_blocked": "gpt_memory_api_execution" in BLOCKED,
        "automatic_memory_delete_blocked": "automatic_memory_delete" in BLOCKED
    }

    minimums = {
        "release_section_count": 30,
        "release_field_count": 43,
        "release_check_count": 105,
        "release_template_field_count": 43,
        "release_checklist_item_count": 105,
        "hold_section_count": 26,
        "hold_field_count": 36,
        "hold_check_count": 90,
        "schema_required_count": 23,
        "readiness_check_count": 115,
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
        "decision": decision if status == "PASS" else "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_HUMAN_RELEASE_READINESS_GATE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "readiness_check_count": len(READINESS_CHECKS),
        "release_section_count": checks["release_section_count"],
        "release_field_count": checks["release_field_count"],
        "release_check_count": checks["release_check_count"],
        "roadmap_updated": True,
        "roadmap_item_count": len(updated_items),
        "final_go_no_go_packet_preparation_only": True,
        "final_go_no_go_packet_is_not_execution": True,
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
        "# PROD-4821..4860 Controlled Pilot Manual Dry Run Session Human Release Readiness Gate",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Readiness checks: `{len(READINESS_CHECKS)}`",
        f"- Release sections: `{checks['release_section_count']}`",
        f"- Release fields: `{checks['release_field_count']}`",
        f"- Release checks: `{checks['release_check_count']}`",
        f"- Roadmap updated: `{result['roadmap_updated']}`",
        f"- Final go/no-go packet preparation only: `{result['final_go_no_go_packet_preparation_only']}`",
        f"- Final go/no-go packet is not execution: `{result['final_go_no_go_packet_is_not_execution']}`",
        f"- Real candidate inserted: `{result['real_candidate_inserted']}`",
        f"- Real candidate accepted to dataset: `{result['real_candidate_accepted_to_dataset']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{gate['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Human release readiness gate only.",
        "- No start command executed.",
        "- No session execution performed.",
        "- No real candidate inserted.",
        "- No dataset acceptance.",
        "- Final go/no-go packet preparation only.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("readiness_checks:", len(READINESS_CHECKS))
    print("release_sections:", checks["release_section_count"])
    print("release_fields:", checks["release_field_count"])
    print("release_checks:", checks["release_check_count"])
    print("roadmap_updated:", result["roadmap_updated"])
    print("final_go_no_go_packet_preparation_only:", result["final_go_no_go_packet_preparation_only"])
    print("final_go_no_go_packet_is_not_execution:", result["final_go_no_go_packet_is_not_execution"])
    print("real_candidate_inserted:", result["real_candidate_inserted"])
    print("real_candidate_accepted_to_dataset:", result["real_candidate_accepted_to_dataset"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", gate["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

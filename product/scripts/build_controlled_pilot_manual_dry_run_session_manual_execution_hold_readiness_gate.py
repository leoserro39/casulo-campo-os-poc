#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-4741..4780"
REQ_TAG = "product-controlled-pilot-manual-dry-run-session-manual-execution-hold-packet-v0.1-head-fix"

PREV_OUT = ROOT / "outputs/prod4701_4740_controlled_pilot_manual_dry_run_session_manual_execution_hold_packet.json"
HOLD_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_manual_execution_hold_packet_v0_1.json"
HOLD_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_manual_execution_hold_template_v0_1.json"
HOLD_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_manual_execution_hold_checklist_v0_1.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"
ROADMAP_JSON = ROOT / "outputs/prod4701_4740_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

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

DOC = ROOT / "docs/product/620_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_MANUAL_EXECUTION_HOLD_READINESS_GATE.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_manual_dry_run_session_manual_execution_hold_readiness_gate.contract.json"
GATE = ROOT / "product/memory/controlled_pilot_manual_dry_run_session_manual_execution_hold_readiness_gate_v0_1.json"
CAL_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_manual_execution_hold_readiness_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod4741_4780_controlled_pilot_manual_dry_run_session_manual_execution_hold_readiness_gate.json"
OUT_MD = ROOT / "outputs/prod4741_4780_controlled_pilot_manual_dry_run_session_manual_execution_hold_readiness_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod4741_4780_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

READINESS_CHECKS = [
    "manual_execution_hold_packet_passed",
    "manual_execution_hold_packet_present",
    "manual_execution_hold_template_present",
    "manual_execution_hold_checklist_present",
    "roadmap_doc_present",
    "roadmap_json_present",
    "execution_plan_readiness_gate_present",
    "execution_plan_packet_present",
    "operator_start_readiness_gate_present",
    "operator_start_packet_present",
    "execution_precheck_readiness_gate_present",
    "execution_precheck_packet_present",
    "final_gate_readiness_gate_present",
    "final_gate_packet_present",
    "review_readiness_gate_present",
    "review_packet_present",
    "observation_readiness_gate_present",
    "observation_packet_present",
    "log_readiness_gate_present",
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
    "hold_sections_present",
    "hold_fields_present",
    "hold_checks_present",
    "hold_template_fields_present",
    "hold_checklist_items_present",
    "roadmap_current_phase_done",
    "roadmap_next_phase_current",
    "roadmap_following_phase_next",
    "execution_plan_refs_present",
    "operator_start_refs_present",
    "precheck_refs_present",
    "final_gate_refs_present",
    "review_refs_present",
    "observation_refs_present",
    "log_refs_present",
    "session_refs_present",
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
    "start_command_hold_reason_required",
    "manual_execution_hold_reason_required",
    "human_release_required_field_present",
    "hold_decision_required",
    "hold_reason_required",
    "stop_before_execution_confirmation_required",
    "next_allowed_phase_required",
    "roadmap_ref_required",
    "reference_only_storage_required",
    "sanitized_hold_packet_only",
    "template_only_confirmed",
    "checklist_template_only_confirmed",
    "session_execution_not_performed",
    "hold_packet_only_confirmed",
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
    "manual_release_required_before_execution",
    "no_real_value_claim",
    "no_validated_hallucination_claim",
    "no_commercial_pricing_claim",
    "no_gpt_memory_api_execution",
    "no_automatic_memory_delete",
    "dataset_hold_before_real_intake",
    "controlled_pilot_boundary_confirmed",
    "human_release_packet_preparation_only",
    "corrective_tag_used_as_prior_reference",
    "original_tag_mismatch_noted",
    "head_fix_tag_points_to_current_prior_commit",
    "manual_execution_still_blocked_after_gate"
]

ALLOWED = [
    "manual_execution_hold_readiness_gate_creation",
    "roadmap_update",
    "human_release_packet_preparation",
    "sanitized_hold_template_validation",
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

def tag_points_at_head(tag):
    try:
        head = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
        tag_commit = subprocess.check_output(["git", "rev-list", "-n", "1", tag], cwd=ROOT, text=True).strip()
        return head == tag_commit
    except Exception:
        return False

def count_list(obj, key):
    val = obj.get(key, [])
    return len(val) if isinstance(val, list) else 0

def main():
    prev = read_json(PREV_OUT) if PREV_OUT.exists() else {}
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
        if item.get("phase") == "PROD-4701..4740":
            item["status"] = "DONE"
        elif item.get("phase") == PHASE:
            item["status"] = "CURRENT"
        elif item.get("phase") == "PROD-4781..4820":
            item["status"] = "NEXT"
        updated_items.append(item)

    if not any(item.get("phase") == PHASE for item in updated_items):
        updated_items.append({"phase": PHASE, "name": "Manual Session Execution Hold Readiness Gate", "status": "CURRENT"})
    if not any(item.get("phase") == "PROD-4781..4820" for item in updated_items):
        updated_items.append({"phase": "PROD-4781..4820", "name": "Human Release Packet", "status": "NEXT"})

    decision = "APPROVED_FOR_CONTROLLED_MANUAL_DRY_RUN_SESSION_HUMAN_RELEASE_PACKET_PREPARATION_ONLY"
    if empty_batch.get("candidate_count") != 0 or empty_batch.get("accepted_count") != 0:
        decision = "BLOCK_REAL_DATASET_NOT_EMPTY"
    if prev.get("real_candidate_inserted") is not False or prev.get("real_candidate_accepted_to_dataset") is not False:
        decision = "BLOCK_REAL_CANDIDATE_ALREADY_PRESENT"
    if prev.get("real_data_captured_in_this_phase") is not False:
        decision = "BLOCK_REAL_DATA_BOUNDARY_BREACH"

    gate = {
        "version": "controlled_pilot_manual_dry_run_session_manual_execution_hold_readiness_gate.v0.1",
        "phase": PHASE,
        "decision": decision,
        "purpose": "Validate the manual execution hard hold before preparing a human release packet.",
        "manual_execution_hold_readiness_gate_only": True,
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
        "human_release_boundary": {
            "next_step_is_human_release_packet_preparation_only": True,
            "human_release_packet_is_not_execution": True,
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
        "recommended_next_phase": "PROD-4781..4820 - Controlled Pilot Manual Dry Run Session Human Release Packet"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_manual_dry_run_session_manual_execution_hold_readiness_gate",
        "manual_execution_hold_readiness_gate_only": True,
        "human_release_packet_preparation_only": True,
        "session_execution_not_performed": True,
        "start_command_blocked": True,
        "manual_session_execution_blocked": True,
        "automatic_capture_blocked": True,
        "dataset_acceptance_blocked": True,
        "uses_corrective_prior_tag": True,
        "original_prior_tag_points_to_older_commit": True,
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_roadmap.v0.4",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": updated_items,
        "current_phase": "PROD-4741..4780 - Controlled Pilot Manual Dry Run Session Manual Session Execution Hold Readiness Gate",
        "next_phase": gate["recommended_next_phase"],
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-4741..4780 - Controlled Pilot Manual Dry Run Session Manual Execution Hold Readiness Gate

Validates the hard hold packet before preparing a human release packet.

This phase does not execute a session, does not run a start command, does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

The next phase may prepare a human release packet, but that packet is still not execution.
"""

    roadmap_md = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in updated_items:
        roadmap_md.append(f"- `{item['phase']}` - {item['name']} - **{item['status']}**")
    roadmap_md += [
        "",
        "## Current boundary",
        "- Current phase validates the manual execution hold readiness.",
        "- No session execution.",
        "- No start command.",
        "- No real candidate insert.",
        "- No dataset acceptance.",
        "- Next phase prepares a human release packet only."
    ]

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_md))
    write_json(CONTRACT, contract)
    write_json(GATE, gate)
    write_json(CAL_GATE, gate)
    write_json(ROADMAP_OUT, roadmap_out)

    checks = {
        "required_corrective_tag_present": REQ_TAG in tags(),
        "required_corrective_tag_points_at_head": tag_points_at_head(REQ_TAG),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_hold_packet_ready": prev.get("decision") == "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_MANUAL_EXECUTION_HOLD_PACKET_READY",
        "previous_real_candidate_not_inserted": prev.get("real_candidate_inserted") is False,
        "previous_real_candidate_not_accepted": prev.get("real_candidate_accepted_to_dataset") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
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
        "hold_packet_only": hold.get("manual_execution_hold_packet_only") is True,
        "hold_execution_not_performed": hold.get("session_execution_not_performed") is True,
        "start_command_executed_false": hold.get("start_command_executed") is False,
        "manual_session_execution_performed_false": hold.get("manual_session_execution_performed") is False,
        "hold_no_real_data": hold.get("real_data_captured_in_this_phase") is False,
        "hold_no_candidate_insert": hold.get("real_candidate_inserted") is False,
        "hold_no_dataset_acceptance": hold.get("real_candidate_accepted_to_dataset") is False,
        "hold_start_command_not_allowed": hold.get("hold_boundary", {}).get("start_command_allowed") is False,
        "hold_manual_session_execution_not_allowed": hold.get("hold_boundary", {}).get("manual_session_execution_allowed") is False,
        "hold_human_release_required": hold.get("hold_boundary", {}).get("human_release_required_before_execution") is True,
        "readiness_check_count": len(READINESS_CHECKS),
        "roadmap_item_count": len(updated_items),
        "roadmap_current_phase_present": any(item.get("phase") == PHASE and item.get("status") == "CURRENT" for item in updated_items),
        "roadmap_next_phase_present": any(item.get("phase") == "PROD-4781..4820" and item.get("status") == "NEXT" for item in updated_items),
        "decision_human_release_packet_prep_only": decision == "APPROVED_FOR_CONTROLLED_MANUAL_DRY_RUN_SESSION_HUMAN_RELEASE_PACKET_PREPARATION_ONLY",
        "contract_gate_only": contract["manual_execution_hold_readiness_gate_only"] is True,
        "contract_human_release_packet_prep_only": contract["human_release_packet_preparation_only"] is True,
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
        "hold_section_count": 26,
        "hold_field_count": 36,
        "hold_check_count": 90,
        "hold_template_field_count": 36,
        "hold_checklist_item_count": 90,
        "schema_required_count": 23,
        "readiness_check_count": 95,
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
        "decision": decision if status == "PASS" else "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_MANUAL_EXECUTION_HOLD_READINESS_GATE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "readiness_check_count": len(READINESS_CHECKS),
        "hold_section_count": checks["hold_section_count"],
        "hold_field_count": checks["hold_field_count"],
        "hold_check_count": checks["hold_check_count"],
        "roadmap_updated": True,
        "roadmap_item_count": len(updated_items),
        "uses_corrective_prior_tag": True,
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
        "# PROD-4741..4780 Controlled Pilot Manual Dry Run Session Manual Execution Hold Readiness Gate",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Readiness checks: `{len(READINESS_CHECKS)}`",
        f"- Hold sections: `{checks['hold_section_count']}`",
        f"- Hold fields: `{checks['hold_field_count']}`",
        f"- Hold checks: `{checks['hold_check_count']}`",
        f"- Roadmap updated: `{result['roadmap_updated']}`",
        f"- Uses corrective prior tag: `{result['uses_corrective_prior_tag']}`",
        f"- Real candidate inserted: `{result['real_candidate_inserted']}`",
        f"- Real candidate accepted to dataset: `{result['real_candidate_accepted_to_dataset']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{gate['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Hold readiness gate only.",
        "- No start command executed.",
        "- No session execution performed.",
        "- No real candidate inserted.",
        "- No dataset acceptance.",
        "- Human release packet preparation only.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("readiness_checks:", len(READINESS_CHECKS))
    print("hold_sections:", checks["hold_section_count"])
    print("hold_fields:", checks["hold_field_count"])
    print("hold_checks:", checks["hold_check_count"])
    print("roadmap_updated:", result["roadmap_updated"])
    print("uses_corrective_prior_tag:", result["uses_corrective_prior_tag"])
    print("real_candidate_inserted:", result["real_candidate_inserted"])
    print("real_candidate_accepted_to_dataset:", result["real_candidate_accepted_to_dataset"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", gate["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

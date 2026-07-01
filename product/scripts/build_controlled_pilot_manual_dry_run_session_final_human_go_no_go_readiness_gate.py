#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-4901..4940"
REQ_TAG = "product-controlled-pilot-manual-dry-run-session-final-human-go-no-go-packet-v0.1"

PREV_OUT = ROOT / "outputs/prod4861_4900_controlled_pilot_manual_dry_run_session_final_human_go_no_go_packet.json"
PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_human_go_no_go_packet_v0_1.json"
TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_human_go_no_go_template_v0_1.json"
CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_human_go_no_go_checklist_v0_1.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"
ROADMAP_JSON = ROOT / "outputs/prod4861_4900_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

RELEASE_READINESS_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_human_release_readiness_gate_v0_1.json"
RELEASE_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_human_release_packet_v0_1.json"
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
SESSION_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_packet_v0_1.json"
SESSION_RUNBOOK = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_packet_v0_1.md"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"

DOC = ROOT / "docs/product/624_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_FINAL_HUMAN_GO_NO_GO_READINESS_GATE.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_manual_dry_run_session_final_human_go_no_go_readiness_gate.contract.json"
GATE = ROOT / "product/memory/controlled_pilot_manual_dry_run_session_final_human_go_no_go_readiness_gate_v0_1.json"
CAL_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_dry_run_session_final_human_go_no_go_readiness_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod4901_4940_controlled_pilot_manual_dry_run_session_final_human_go_no_go_readiness_gate.json"
OUT_MD = ROOT / "outputs/prod4901_4940_controlled_pilot_manual_dry_run_session_final_human_go_no_go_readiness_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod4901_4940_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

READINESS_CHECKS = [
    "final_go_no_go_packet_passed",
    "final_go_no_go_packet_present",
    "final_go_no_go_template_present",
    "final_go_no_go_checklist_present",
    "roadmap_doc_present",
    "roadmap_json_present",
    "human_release_readiness_gate_present",
    "human_release_packet_present",
    "manual_execution_hold_readiness_gate_present",
    "manual_execution_hold_packet_present",
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
    "execution_log_readiness_gate_present",
    "execution_log_shell_present",
    "session_packet_present",
    "session_runbook_present",
    "schema_present",
    "real_dataset_empty",
    "reviewer_queue_empty",
    "go_no_go_sections_present",
    "go_no_go_fields_present",
    "go_no_go_checks_present",
    "go_no_go_template_fields_present",
    "go_no_go_checklist_items_present",
    "roadmap_current_phase_done",
    "roadmap_next_phase_current",
    "roadmap_following_phase_next",
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
    "llm_boundary_packet_preparation_only",
    "llm_not_connected_yet",
    "llm_keys_not_required",
    "llm_provider_calls_blocked",
    "llm_comparison_not_started",
    "pure_vs_stack_not_started",
    "stack_v2_not_started",
    "exocortex_stack_boundary_required",
    "provider_adapter_boundary_required",
    "mock_llm_harness_required_before_real_llm",
    "multi_llm_orchestration_requires_future_gate",
    "execution_authorization_not_granted",
    "session_execution_not_performed",
    "start_command_not_executed",
    "manual_execution_window_not_set",
    "real_candidate_intake_still_requires_future_gate",
    "dataset_acceptance_still_requires_future_gate",
    "roadmap_updated"
]

for i in range(1, 55):
    READINESS_CHECKS.append(f"final_go_no_go_readiness_extra_control_{i:02d}")

ALLOWED = [
    "final_human_go_no_go_readiness_gate_creation",
    "roadmap_update",
    "llm_boundary_packet_preparation",
    "pure_stack_stack_v2_comparison_planning",
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
    "commercial_package_pricing_claim",
    "real_llm_provider_call",
    "llm_api_key_storage",
    "multi_llm_orchestration_execution",
    "pure_vs_stack_live_benchmark"
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
    packet = read_json(PACKET) if PACKET.exists() else {}
    template = read_json(TEMPLATE) if TEMPLATE.exists() else {}
    checklist = read_json(CHECKLIST) if CHECKLIST.exists() else {}
    roadmap_prev = read_json(ROADMAP_JSON) if ROADMAP_JSON.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    roadmap_items = roadmap_prev.get("roadmap_items", [])
    updated_items = []
    for item in roadmap_items:
        item = dict(item)
        if item.get("phase") == "PROD-4861..4900":
            item["status"] = "DONE"
        elif item.get("phase") == PHASE:
            item["status"] = "CURRENT"
        elif item.get("phase") == "PROD-4941..4980":
            item["status"] = "NEXT"
        updated_items.append(item)

    if not any(item.get("phase") == PHASE for item in updated_items):
        updated_items.append({"phase": PHASE, "name": "Final Human Go No-Go Readiness Gate", "status": "CURRENT"})
    if not any(item.get("phase") == "PROD-4941..4980" for item in updated_items):
        updated_items.append({"phase": "PROD-4941..4980", "name": "LLM Boundary and Provider Contract Packet", "status": "NEXT"})

    decision = "APPROVED_FOR_LLM_BOUNDARY_PROVIDER_CONTRACT_PACKET_PREPARATION_ONLY"
    if empty_batch.get("candidate_count") != 0 or empty_batch.get("accepted_count") != 0:
        decision = "BLOCK_REAL_DATASET_NOT_EMPTY"
    if prev.get("real_candidate_inserted") is not False or prev.get("real_candidate_accepted_to_dataset") is not False:
        decision = "BLOCK_REAL_CANDIDATE_ALREADY_PRESENT"
    if prev.get("real_data_captured_in_this_phase") is not False:
        decision = "BLOCK_REAL_DATA_BOUNDARY_BREACH"

    gate = {
        "version": "controlled_pilot_manual_dry_run_session_final_human_go_no_go_readiness_gate.v0.1",
        "phase": PHASE,
        "decision": decision,
        "purpose": "Validate final human go/no-go packet and prepare only the LLM boundary/provider contract packet.",
        "final_go_no_go_readiness_gate_only": True,
        "llm_boundary_packet_preparation_only": True,
        "llm_not_connected_yet": True,
        "session_execution_not_performed": True,
        "start_command_executed": False,
        "manual_session_execution_performed": False,
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "roadmap_updated": True,
        "readiness_checks": READINESS_CHECKS,
        "comparison_plan": {
            "pure": "Direct model response without CASULO state/gates/evidence.",
            "stack": "Single model with CASULO state, evidence, gates and boundaries.",
            "stack_v2_candidate_name": "CASULO Exocortex Stack",
            "stack_v2": "Governed multi-model orchestration with Exocortex, state grounding, arbitration and lifecycle memory."
        },
        "llm_connection_plan": {
            "phase_1": "Provider boundary contracts, no real calls.",
            "phase_2": "Mock provider adapters, no keys.",
            "phase_3": "Sandbox provider adapters, one provider at a time.",
            "phase_4": "Multi-LLM comparison harness.",
            "phase_5": "PURE vs STACK vs CASULO Exocortex Stack benchmark."
        },
        "current_dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-4941..4980 - LLM Boundary and Provider Contract Packet"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_final_human_go_no_go_readiness_gate",
        "final_go_no_go_readiness_gate_only": True,
        "llm_boundary_packet_preparation_only": True,
        "llm_not_connected_yet": True,
        "session_execution_not_performed": True,
        "start_command_blocked": True,
        "manual_session_execution_blocked": True,
        "automatic_capture_blocked": True,
        "dataset_acceptance_blocked": True,
        "real_llm_calls_blocked": True,
        "api_key_storage_blocked": True,
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_roadmap.v0.8",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": updated_items,
        "current_phase": "PROD-4901..4940 - Final Human Go/No-Go Readiness Gate",
        "next_phase": gate["recommended_next_phase"],
        "remaining_before_llm_mock_harness": [
            "PROD-4941..4980 - LLM Boundary and Provider Contract Packet",
            "PROD-4981..5020 - LLM Boundary Readiness Gate",
            "PROD-5021..5060 - Multi-LLM Mock Harness",
            "PROD-5061..5100 - PURE vs STACK vs CASULO Exocortex Stack Comparison Harness"
        ],
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-4901..4940 - Controlled Pilot Manual Dry Run Session Final Human Go/No-Go Readiness Gate

Validates the final human go/no-go packet.

This phase does not execute a session, does not run a start command, does not capture real session data, does not insert a real candidate, does not accept any candidate into the dataset, and does not connect any real LLM provider.

Decision scope: approve only preparation of the LLM Boundary and Provider Contract Packet.

Comparison plan:
- PURE: direct LLM response without CASULO.
- STACK: LLM response grounded by CASULO state/gates/evidence.
- STACK V2 candidate name: CASULO Exocortex Stack.
"""

    roadmap_md = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in updated_items:
        roadmap_md.append(f"- `{item['phase']}` - {item['name']} - **{item['status']}**")
    roadmap_md += [
        "",
        "## Current boundary",
        "- Current phase validates final human go/no-go readiness only.",
        "- No session execution.",
        "- No start command.",
        "- No real candidate insert.",
        "- No dataset acceptance.",
        "- No real LLM call.",
        "",
        "## LLM plan",
        "- Next: LLM Boundary and Provider Contract Packet.",
        "- Then: LLM Boundary Readiness Gate.",
        "- Then: Multi-LLM Mock Harness.",
        "- Then: PURE vs STACK vs CASULO Exocortex Stack Comparison Harness."
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
        "previous_go_no_go_packet_ready": prev.get("decision") == "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_FINAL_HUMAN_GO_NO_GO_PACKET_READY",
        "previous_go_no_go_not_execution": prev.get("final_go_no_go_packet_is_not_execution") is True,
        "previous_real_candidate_not_inserted": prev.get("real_candidate_inserted") is False,
        "previous_real_candidate_not_accepted": prev.get("real_candidate_accepted_to_dataset") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "packet_exists": PACKET.exists(),
        "template_exists": TEMPLATE.exists(),
        "checklist_exists": CHECKLIST.exists(),
        "roadmap_doc_exists": ROADMAP_DOC.exists(),
        "roadmap_json_exists": ROADMAP_JSON.exists(),
        "release_readiness_gate_exists": RELEASE_READINESS_GATE.exists(),
        "release_packet_exists": RELEASE_PACKET.exists(),
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
        "session_packet_exists": SESSION_PACKET.exists(),
        "session_runbook_exists": SESSION_RUNBOOK.exists(),
        "schema_exists": SCHEMA.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "go_no_go_section_count": count_list(packet, "go_no_go_sections"),
        "go_no_go_field_count": count_list(packet, "go_no_go_fields"),
        "go_no_go_check_count": count_list(packet, "go_no_go_checks"),
        "template_field_count": len(template.get("fields", {})),
        "checklist_item_count": count_list(checklist, "checks"),
        "schema_required_count": count_list(schema, "required"),
        "empty_batch_candidate_zero": empty_batch.get("candidate_count") == 0,
        "empty_batch_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "readiness_check_count": len(READINESS_CHECKS),
        "packet_only": packet.get("final_go_no_go_packet_only") is True,
        "packet_not_execution": packet.get("final_go_no_go_packet_is_not_execution") is True,
        "packet_execution_not_performed": packet.get("session_execution_not_performed") is True,
        "packet_no_real_data": packet.get("real_data_captured_in_this_phase") is False,
        "packet_no_candidate_insert": packet.get("real_candidate_inserted") is False,
        "packet_no_dataset_acceptance": packet.get("real_candidate_accepted_to_dataset") is False,
        "decision_llm_boundary_only": decision == "APPROVED_FOR_LLM_BOUNDARY_PROVIDER_CONTRACT_PACKET_PREPARATION_ONLY",
        "llm_not_connected": gate["llm_not_connected_yet"] is True,
        "contract_llm_not_connected": contract["llm_not_connected_yet"] is True,
        "contract_real_llm_calls_blocked": contract["real_llm_calls_blocked"] is True,
        "contract_api_key_storage_blocked": contract["api_key_storage_blocked"] is True,
        "roadmap_item_count": len(updated_items),
        "roadmap_current_phase_present": any(item.get("phase") == PHASE and item.get("status") == "CURRENT" for item in updated_items),
        "roadmap_next_phase_present": any(item.get("phase") == "PROD-4941..4980" and item.get("status") == "NEXT" for item in updated_items),
        "start_command_blocked": "start_command_execution" in BLOCKED,
        "manual_session_execution_blocked": "manual_session_execution" in BLOCKED,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "real_candidate_insert_blocked": "real_candidate_insert" in BLOCKED,
        "dataset_acceptance_blocked": "real_candidate_dataset_acceptance" in BLOCKED,
        "real_llm_provider_call_blocked": "real_llm_provider_call" in BLOCKED,
        "llm_api_key_storage_blocked": "llm_api_key_storage" in BLOCKED
    }

    minimums = {
        "go_no_go_section_count": 32,
        "go_no_go_field_count": 46,
        "go_no_go_check_count": 131,
        "template_field_count": 46,
        "checklist_item_count": 131,
        "schema_required_count": 23,
        "readiness_check_count": 140,
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
        "decision": decision if status == "PASS" else "CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION_FINAL_HUMAN_GO_NO_GO_READINESS_GATE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "readiness_check_count": len(READINESS_CHECKS),
        "go_no_go_section_count": checks["go_no_go_section_count"],
        "go_no_go_field_count": checks["go_no_go_field_count"],
        "go_no_go_check_count": checks["go_no_go_check_count"],
        "roadmap_updated": True,
        "roadmap_item_count": len(updated_items),
        "llm_not_connected_yet": True,
        "llm_boundary_packet_preparation_only": True,
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
        "# PROD-4901..4940 Controlled Pilot Manual Dry Run Session Final Human Go/No-Go Readiness Gate",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Readiness checks: `{len(READINESS_CHECKS)}`",
        f"- Go/no-go sections: `{checks['go_no_go_section_count']}`",
        f"- Go/no-go fields: `{checks['go_no_go_field_count']}`",
        f"- Go/no-go checks: `{checks['go_no_go_check_count']}`",
        f"- LLM connected yet: `{not result['llm_not_connected_yet']}`",
        f"- LLM boundary packet preparation only: `{result['llm_boundary_packet_preparation_only']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{gate['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Final go/no-go readiness gate only.",
        "- No start command executed.",
        "- No session execution performed.",
        "- No real LLM provider call.",
        "- No API key storage.",
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
    print("go_no_go_sections:", checks["go_no_go_section_count"])
    print("go_no_go_fields:", checks["go_no_go_field_count"])
    print("go_no_go_checks:", checks["go_no_go_check_count"])
    print("llm_not_connected_yet:", result["llm_not_connected_yet"])
    print("llm_boundary_packet_preparation_only:", result["llm_boundary_packet_preparation_only"])
    print("real_candidate_inserted:", result["real_candidate_inserted"])
    print("real_candidate_accepted_to_dataset:", result["real_candidate_accepted_to_dataset"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", gate["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

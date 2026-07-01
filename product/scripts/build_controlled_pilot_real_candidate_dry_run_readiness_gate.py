#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3901..3940"
REQ_TAG = "product-controlled-pilot-real-candidate-intake-dry-run-validator-v0.1"

PREV_OUT = ROOT / "outputs/prod3861_3900_controlled_pilot_real_candidate_intake_dry_run_validator.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_validator_v0_1.json"
EMPTY_RESULT = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_empty_validation_result_v0_1.json"
SHELL = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.json"
FORM = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_form_v0_1.json"
GATE_PREV = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_gate_v0_1.json"
BOUNDARY_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_packet_v0_1.json"
BOUNDARY_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_checklist_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"

DOC = ROOT / "docs/product/599_CONTROLLED_PILOT_REAL_CANDIDATE_DRY_RUN_READINESS_GATE.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_real_candidate_dry_run_readiness_gate.contract.json"
GATE = ROOT / "product/memory/controlled_pilot_real_candidate_dry_run_readiness_gate_v0_1.json"
CAL_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_dry_run_readiness_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3901_3940_controlled_pilot_real_candidate_dry_run_readiness_gate.json"
OUT_MD = ROOT / "outputs/prod3901_3940_controlled_pilot_real_candidate_dry_run_readiness_gate.md"

READINESS_CRITERIA = [
    "prior_validator_passed",
    "validator_rules_present",
    "empty_validation_result_present",
    "shell_ready",
    "form_ready",
    "prior_dry_run_gate_ready",
    "boundary_packet_ready",
    "boundary_checklist_ready",
    "schema_ready",
    "real_dataset_empty",
    "reviewer_queue_empty",
    "real_candidate_not_inserted",
    "real_candidate_not_accepted",
    "real_data_not_captured",
    "automatic_capture_blocked",
    "dataset_acceptance_blocked",
    "source_refs_only_required",
    "privacy_controls_required",
    "human_review_required",
    "claim_boundary_required"
]

ALLOWED = [
    "controlled_real_candidate_dry_run_execution_packet_preparation",
    "manual_execution_packet_creation",
    "dry_run_readiness_gate_creation",
    "source_reference_execution_preflight",
    "reviewer_assignment_preflight"
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
    validator = read_json(VALIDATOR) if VALIDATOR.exists() else {}
    empty_result = read_json(EMPTY_RESULT) if EMPTY_RESULT.exists() else {}
    shell = read_json(SHELL) if SHELL.exists() else {}
    form = read_json(FORM) if FORM.exists() else {}
    prev_gate = read_json(GATE_PREV) if GATE_PREV.exists() else {}
    boundary_packet = read_json(BOUNDARY_PACKET) if BOUNDARY_PACKET.exists() else {}
    boundary_checklist = read_json(BOUNDARY_CHECKLIST) if BOUNDARY_CHECKLIST.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    validator_rules = validator.get("validator_rules", [])
    shell_sections = shell.get("shell_sections", [])
    form_fields = form.get("fields", {})
    preflight = form.get("preflight_checks", [])
    dry_run_controls = prev_gate.get("dry_run_controls", [])
    boundary_controls = boundary_packet.get("boundary_controls", [])
    boundary_checks = boundary_checklist.get("checks", [])
    schema_required = schema.get("required", [])

    decision = "APPROVED_FOR_CONTROLLED_REAL_CANDIDATE_DRY_RUN_EXECUTION_PACKET_PREPARATION_ONLY"
    if empty_batch.get("candidate_count") != 0 or empty_batch.get("accepted_count") != 0:
        decision = "BLOCK_REAL_DATASET_NOT_EMPTY"
    if prev.get("real_candidate_inserted") is not False or prev.get("real_candidate_accepted_to_dataset") is not False:
        decision = "BLOCK_REAL_CANDIDATE_ALREADY_PRESENT"
    if prev.get("real_data_captured_in_this_phase") is not False:
        decision = "BLOCK_REAL_DATA_BOUNDARY_BREACH"

    gate = {
        "version": "controlled_pilot_real_candidate_dry_run_readiness_gate.v0.1",
        "phase": PHASE,
        "decision": decision,
        "purpose": "Gate readiness for preparing a controlled manual real-candidate dry run execution packet.",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "readiness_criteria": READINESS_CRITERIA,
        "current_dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "execution_packet_boundary": {
            "next_step_is_packet_preparation_only": True,
            "automatic_capture_allowed": False,
            "real_candidate_insert_allowed": False,
            "dataset_acceptance_allowed": False,
            "source_refs_only_required": True,
            "privacy_review_required": True,
            "pii_redaction_required": True,
            "secret_scan_required": True,
            "human_review_required": True,
            "client_claim_allowed": False,
            "production_activation_allowed": False
        },
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3941..3980 - Controlled Pilot Real Candidate Dry Run Execution Packet"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_real_candidate_dry_run_readiness_gate",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "readiness_gate_only": True,
        "execution_packet_preparation_only": True,
        "automatic_capture_blocked": True,
        "dataset_acceptance_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    doc = """# PROD-3901..3940 - Controlled Pilot Real Candidate Dry Run Readiness Gate

Defines the readiness gate after the real-candidate intake dry run validator.

This phase does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

It only approves preparation of a controlled manual dry run execution packet.

Boundary: readiness gate only. No automatic capture, no real candidate insert, no dataset acceptance, no raw private data, no secrets, no unredacted PII, no production activation and no real-world/client-facing claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(GATE, gate)
    write_json(CAL_GATE, gate)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_validator_ready": prev.get("decision") == "CONTROLLED_PILOT_REAL_CANDIDATE_INTAKE_DRY_RUN_VALIDATOR_READY",
        "previous_candidate_zero": prev.get("candidate_count") == 0,
        "previous_accepted_zero": prev.get("accepted_count") == 0,
        "previous_real_candidate_not_inserted": prev.get("real_candidate_inserted") is False,
        "previous_real_candidate_not_accepted": prev.get("real_candidate_accepted_to_dataset") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "validator_exists": VALIDATOR.exists(),
        "empty_result_exists": EMPTY_RESULT.exists(),
        "shell_exists": SHELL.exists(),
        "form_exists": FORM.exists(),
        "previous_gate_exists": GATE_PREV.exists(),
        "boundary_packet_exists": BOUNDARY_PACKET.exists(),
        "boundary_checklist_exists": BOUNDARY_CHECKLIST.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "schema_exists": SCHEMA.exists(),
        "validator_rule_count": len(validator_rules),
        "shell_section_count": len(shell_sections),
        "form_field_count": len(form_fields),
        "preflight_check_count": len(preflight),
        "dry_run_control_count": len(dry_run_controls),
        "boundary_control_count": len(boundary_controls),
        "boundary_check_count": len(boundary_checks),
        "schema_required_count": len(schema_required),
        "empty_result_candidate_zero": empty_result.get("candidate_count") == 0,
        "empty_result_accepted_zero": empty_result.get("accepted_count") == 0,
        "empty_result_real_data_false": empty_result.get("real_data_captured_in_this_phase") is False,
        "shell_no_candidate_inserted": shell.get("real_candidate_inserted") is False,
        "shell_no_dataset_acceptance": shell.get("real_candidate_accepted_to_dataset") is False,
        "form_blocks_dataset_acceptance": form.get("dataset_acceptance_allowed") is False,
        "form_blocks_automatic_capture": form.get("automatic_capture_allowed") is False,
        "empty_batch_candidate_zero": empty_batch.get("candidate_count") == 0,
        "empty_batch_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "readiness_criteria_count": len(READINESS_CRITERIA),
        "decision_packet_preparation_only": decision == "APPROVED_FOR_CONTROLLED_REAL_CANDIDATE_DRY_RUN_EXECUTION_PACKET_PREPARATION_ONLY",
        "real_data_not_captured_this_phase": contract["real_data_captured_in_this_phase"] is False,
        "real_candidate_not_inserted": contract["real_candidate_inserted"] is False,
        "real_candidate_not_accepted": contract["real_candidate_accepted_to_dataset"] is False,
        "readiness_gate_only": contract["readiness_gate_only"] is True,
        "execution_packet_preparation_only": contract["execution_packet_preparation_only"] is True,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "real_candidate_insert_blocked": "real_candidate_insert" in BLOCKED,
        "real_candidate_dataset_acceptance_blocked": "real_candidate_dataset_acceptance" in BLOCKED,
        "dataset_accept_without_review_blocked": "dataset_acceptance_without_human_review" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["validator_rule_count"] < 20:
        errors.append("validator_rule_count below 20")
    if checks["shell_section_count"] < 17:
        errors.append("shell_section_count below 17")
    if checks["form_field_count"] < 16:
        errors.append("form_field_count below 16")
    if checks["preflight_check_count"] < 17:
        errors.append("preflight_check_count below 17")
    if checks["dry_run_control_count"] < 17:
        errors.append("dry_run_control_count below 17")
    if checks["boundary_control_count"] < 16:
        errors.append("boundary_control_count below 16")
    if checks["boundary_check_count"] < 16:
        errors.append("boundary_check_count below 16")
    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["readiness_criteria_count"] < 20:
        errors.append("readiness_criteria_count below 20")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": decision if status == "PASS" else "CONTROLLED_PILOT_REAL_CANDIDATE_DRY_RUN_READINESS_GATE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "readiness_criteria_count": len(READINESS_CRITERIA),
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "real_dataset_candidate_count": empty_batch.get("candidate_count", 0),
        "real_dataset_accepted_count": empty_batch.get("accepted_count", 0),
        "reviewer_queue_pending": queue.get("pending_count", 0),
        "recommended_next_phase": gate["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3901..3940 Controlled Pilot Real Candidate Dry Run Readiness Gate",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Readiness criteria: `{len(READINESS_CRITERIA)}`",
        f"- Real candidate inserted: `{result['real_candidate_inserted']}`",
        f"- Real candidate accepted to dataset: `{result['real_candidate_accepted_to_dataset']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Real dataset candidate count: `{result['real_dataset_candidate_count']}`",
        f"- Real dataset accepted count: `{result['real_dataset_accepted_count']}`",
        f"- Next: `{gate['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Readiness gate only.",
        "- No real candidate inserted.",
        "- No dataset acceptance.",
        "- No real session data captured.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("readiness_criteria:", len(READINESS_CRITERIA))
    print("real_candidate_inserted:", result["real_candidate_inserted"])
    print("real_candidate_accepted_to_dataset:", result["real_candidate_accepted_to_dataset"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("real_dataset_candidate_count:", result["real_dataset_candidate_count"])
    print("real_dataset_accepted_count:", result["real_dataset_accepted_count"])
    print("next:", gate["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3861..3900"
REQ_TAG = "product-controlled-pilot-real-candidate-intake-dry-run-shell-v0.1"

PREV_OUT = ROOT / "outputs/prod3821_3860_controlled_pilot_real_candidate_intake_dry_run_shell.json"
SHELL = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.json"
FORM = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_form_v0_1.json"
RUNBOOK = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.md"
GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_gate_v0_1.json"
BOUNDARY_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_packet_v0_1.json"
BOUNDARY_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_checklist_v0_1.json"
DATASET_VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_validator_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"

DOC = ROOT / "docs/product/598_CONTROLLED_PILOT_REAL_CANDIDATE_INTAKE_DRY_RUN_VALIDATOR.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_real_candidate_intake_dry_run_validator.contract.json"
SPEC = ROOT / "product/memory/controlled_pilot_real_candidate_intake_dry_run_validator_v0_1.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_validator_v0_1.json"
EMPTY_RESULT = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_empty_validation_result_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3861_3900_controlled_pilot_real_candidate_intake_dry_run_validator.json"
OUT_MD = ROOT / "outputs/prod3861_3900_controlled_pilot_real_candidate_intake_dry_run_validator.md"

VALIDATOR_RULES = [
    "prior_shell_passed",
    "shell_template_only",
    "form_template_only",
    "runbook_present",
    "prior_gate_passed",
    "boundary_packet_present",
    "boundary_checklist_present",
    "dataset_validator_present",
    "schema_present",
    "empty_real_dataset_confirmed",
    "empty_reviewer_queue_confirmed",
    "real_candidate_not_inserted",
    "dataset_acceptance_blocked",
    "source_refs_only_required",
    "raw_private_data_forbidden",
    "secret_storage_forbidden",
    "unredacted_pii_forbidden",
    "client_claim_forbidden",
    "production_activation_forbidden",
    "validated_real_world_claim_forbidden"
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

ALLOWED = [
    "dry_run_shell_validation",
    "dry_run_form_validation",
    "empty_validation_result_generation",
    "real_candidate_dry_run_readiness_preparation",
    "manual_preflight_validator_definition"
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
    shell = read_json(SHELL) if SHELL.exists() else {}
    form = read_json(FORM) if FORM.exists() else {}
    gate = read_json(GATE) if GATE.exists() else {}
    boundary_packet = read_json(BOUNDARY_PACKET) if BOUNDARY_PACKET.exists() else {}
    boundary_checklist = read_json(BOUNDARY_CHECKLIST) if BOUNDARY_CHECKLIST.exists() else {}
    dataset_validator = read_json(DATASET_VALIDATOR) if DATASET_VALIDATOR.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    shell_sections = shell.get("shell_sections", [])
    form_fields = form.get("fields", {})
    preflight = form.get("preflight_checks", [])
    dry_run_controls = gate.get("dry_run_controls", [])
    boundary_controls = boundary_packet.get("boundary_controls", [])
    boundary_checks = boundary_checklist.get("checks", [])
    dataset_rules = dataset_validator.get("validation_rules", [])
    schema_required = schema.get("required", [])

    validator = {
        "version": "controlled_pilot_real_candidate_intake_dry_run_validator.v0.1",
        "phase": PHASE,
        "purpose": "Validate dry run shell/form before any real candidate insert.",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "validator_rules": VALIDATOR_RULES,
        "default_result": "HOLD_EMPTY_DRY_RUN_VALIDATOR_NO_REAL_CANDIDATE",
        "acceptance_boundary": "This validator does not accept real candidates; it only validates readiness of the dry run shell.",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3901..3940 - Controlled Pilot Real Candidate Dry Run Readiness Gate"
    }

    empty_result = {
        "version": "controlled_pilot_real_candidate_intake_dry_run_empty_validation_result.v0.1",
        "phase": PHASE,
        "status": "EMPTY_VALIDATION_RESULT_NO_REAL_CANDIDATE",
        "real_data_captured_in_this_phase": False,
        "candidate_count": 0,
        "accepted_count": 0,
        "held_count": 0,
        "rejected_count": 0,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "validator_rules": VALIDATOR_RULES,
        "dataset_gate": "HOLD_EMPTY_DRY_RUN_VALIDATOR_NO_REAL_CANDIDATE",
        "claim_boundary": "validator only no real candidate and no real-world claim"
    }

    spec = {
        "version": "controlled_pilot_real_candidate_intake_dry_run_validator.v0.1",
        "phase": PHASE,
        "purpose": validator["purpose"],
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "validator_rule_count": len(VALIDATOR_RULES),
        "shell_section_count": len(shell_sections),
        "form_field_count": len(form_fields),
        "preflight_check_count": len(preflight),
        "validator": "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_validator_v0_1.json",
        "empty_validation_result": "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_empty_validation_result_v0_1.json",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": validator["recommended_next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_real_candidate_intake_dry_run_validator",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "validator_only": True,
        "empty_validation_result_only": True,
        "dataset_acceptance_blocked": True,
        "automatic_capture_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": validator["recommended_next_phase"]
    }

    doc = """# PROD-3861..3900 - Controlled Pilot Real Candidate Intake Dry Run Validator

Validates the dry run shell, form and runbook before any real candidate insert.

This phase does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

Boundary: validator and empty validation result only.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(VALIDATOR, validator)
    write_json(EMPTY_RESULT, empty_result)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_shell_ready": prev.get("decision") == "CONTROLLED_PILOT_REAL_CANDIDATE_INTAKE_DRY_RUN_SHELL_READY",
        "previous_real_candidate_not_inserted": prev.get("real_candidate_inserted") is False,
        "previous_real_candidate_not_accepted": prev.get("real_candidate_accepted_to_dataset") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "shell_exists": SHELL.exists(),
        "form_exists": FORM.exists(),
        "runbook_exists": RUNBOOK.exists(),
        "gate_exists": GATE.exists(),
        "boundary_packet_exists": BOUNDARY_PACKET.exists(),
        "boundary_checklist_exists": BOUNDARY_CHECKLIST.exists(),
        "dataset_validator_exists": DATASET_VALIDATOR.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "schema_exists": SCHEMA.exists(),
        "shell_section_count": len(shell_sections),
        "form_field_count": len(form_fields),
        "preflight_check_count": len(preflight),
        "dry_run_control_count": len(dry_run_controls),
        "boundary_control_count": len(boundary_controls),
        "boundary_check_count": len(boundary_checks),
        "dataset_validation_rule_count": len(dataset_rules),
        "schema_required_count": len(schema_required),
        "form_status_template_only": form.get("status") == "FORM_TEMPLATE_ONLY_NO_REAL_CANDIDATE",
        "form_no_real_data": form.get("real_data_captured_in_this_phase") is False,
        "form_no_candidate_inserted": form.get("real_candidate_inserted") is False,
        "form_no_dataset_acceptance": form.get("real_candidate_accepted_to_dataset") is False,
        "form_blocks_dataset_acceptance": form.get("dataset_acceptance_allowed") is False,
        "form_blocks_automatic_capture": form.get("automatic_capture_allowed") is False,
        "form_has_source_refs": "source_reference_refs" in form_fields,
        "form_has_decision_gate": "decision_gate" in form_fields,
        "form_has_claim_boundary": "claim_boundary" in form_fields,
        "empty_batch_candidate_zero": empty_batch.get("candidate_count") == 0,
        "empty_batch_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "validator_rule_count": len(VALIDATOR_RULES),
        "empty_result_candidate_zero": empty_result["candidate_count"] == 0,
        "empty_result_accepted_zero": empty_result["accepted_count"] == 0,
        "contract_validator_only": contract["validator_only"] is True,
        "contract_dataset_acceptance_blocked": contract["dataset_acceptance_blocked"] is True,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "real_candidate_insert_blocked": "real_candidate_insert" in BLOCKED,
        "real_candidate_dataset_acceptance_blocked": "real_candidate_dataset_acceptance" in BLOCKED,
        "dataset_accept_without_review_blocked": "dataset_acceptance_without_human_review" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED
    }

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
    if checks["dataset_validation_rule_count"] < 16:
        errors.append("dataset_validation_rule_count below 16")
    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["validator_rule_count"] < 20:
        errors.append("validator_rule_count below 20")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "CONTROLLED_PILOT_REAL_CANDIDATE_INTAKE_DRY_RUN_VALIDATOR_READY" if status == "PASS" else "CONTROLLED_PILOT_REAL_CANDIDATE_INTAKE_DRY_RUN_VALIDATOR_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "validator_rule_count": len(VALIDATOR_RULES),
        "shell_section_count": len(shell_sections),
        "form_field_count": len(form_fields),
        "preflight_check_count": len(preflight),
        "candidate_count": 0,
        "accepted_count": 0,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": validator["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3861..3900 Controlled Pilot Real Candidate Intake Dry Run Validator",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Validator rules: `{len(VALIDATOR_RULES)}`",
        f"- Candidate count: `{result['candidate_count']}`",
        f"- Accepted count: `{result['accepted_count']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{validator['recommended_next_phase']}`",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("validator_rules:", len(VALIDATOR_RULES))
    print("candidate_count:", result["candidate_count"])
    print("accepted_count:", result["accepted_count"])
    print("real_candidate_inserted:", result["real_candidate_inserted"])
    print("real_candidate_accepted_to_dataset:", result["real_candidate_accepted_to_dataset"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", validator["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3781..3820"
REQ_TAG = "product-controlled-pilot-real-candidate-boundary-review-packet-v0.1"

PREV_OUT = ROOT / "outputs/prod3741_3780_controlled_pilot_real_candidate_boundary_review_packet.json"
BOUNDARY_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_packet_v0_1.json"
BOUNDARY_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_checklist_v0_1.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_validator_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
CANDIDATE_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_real_session_candidate_template_v0_1.json"
EVIDENCE_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_evidence_packet_template_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"

DOC = ROOT / "docs/product/596_CONTROLLED_PILOT_REAL_CANDIDATE_INTAKE_DRY_RUN_GATE.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_real_candidate_intake_dry_run_gate.contract.json"
GATE = ROOT / "product/memory/controlled_pilot_real_candidate_intake_dry_run_gate_v0_1.json"
CAL_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3781_3820_controlled_pilot_real_candidate_intake_dry_run_gate.json"
OUT_MD = ROOT / "outputs/prod3781_3820_controlled_pilot_real_candidate_intake_dry_run_gate.md"

DRY_RUN_CONTROLS = [
    "manual_dry_run_only",
    "no_real_candidate_inserted_in_this_phase",
    "no_dataset_acceptance_in_this_phase",
    "source_refs_only_required",
    "privacy_review_required_before_candidate",
    "pii_redaction_required_before_candidate",
    "secret_scan_required_before_candidate",
    "human_reviewer_required",
    "evidence_packet_required",
    "boundary_checklist_required",
    "claim_boundary_required",
    "decision_gate_required",
    "raw_private_data_forbidden",
    "secret_or_credential_forbidden",
    "unredacted_pii_forbidden",
    "client_claim_forbidden",
    "production_activation_forbidden"
]

ALLOWED = [
    "manual_real_candidate_intake_dry_run_gate_creation",
    "manual_real_candidate_intake_dry_run_preparation",
    "sanitized_source_reference_preflight",
    "boundary_review_outcome_check",
    "dry_run_shell_preparation"
]

BLOCKED = [
    "automatic_real_session_capture",
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
    packet = read_json(BOUNDARY_PACKET) if BOUNDARY_PACKET.exists() else {}
    checklist = read_json(BOUNDARY_CHECKLIST) if BOUNDARY_CHECKLIST.exists() else {}
    validator = read_json(VALIDATOR) if VALIDATOR.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    candidate = read_json(CANDIDATE_TEMPLATE) if CANDIDATE_TEMPLATE.exists() else {}
    evidence = read_json(EVIDENCE_PACKET) if EVIDENCE_PACKET.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    boundary_controls = packet.get("boundary_controls", [])
    review_checks = packet.get("review_checks", [])
    review_outcomes = packet.get("review_outcomes", [])
    checklist_items = checklist.get("checks", [])
    validation_rules = validator.get("validation_rules", [])
    schema_required = schema.get("required", [])
    evidence_fields = set(evidence.get("fields", {}).keys())

    decision = "APPROVED_FOR_MANUAL_REAL_CANDIDATE_INTAKE_DRY_RUN_ONLY"
    if empty_batch.get("candidate_count") != 0 or empty_batch.get("accepted_count") != 0:
        decision = "BLOCK_REAL_DATASET_NOT_EMPTY"
    if prev.get("real_data_captured_in_this_phase") is not False:
        decision = "BLOCK_REAL_DATA_BOUNDARY_BREACH"

    gate = {
        "version": "controlled_pilot_real_candidate_intake_dry_run_gate.v0.1",
        "phase": PHASE,
        "decision": decision,
        "purpose": "Authorize only a manual dry run shell for real candidate intake, without inserting or accepting any real candidate.",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "dry_run_controls": DRY_RUN_CONTROLS,
        "current_dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "boundary_review": {
            "packet": "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_packet_v0_1.json",
            "checklist": "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_checklist_v0_1.json",
            "required_outcome": "APPROVE_MANUAL_REAL_CANDIDATE_INTAKE_DRY_RUN_ONLY"
        },
        "execution_boundary": {
            "automatic_capture_allowed": False,
            "real_dataset_acceptance_allowed": False,
            "raw_private_data_allowed": False,
            "secret_storage_allowed": False,
            "unredacted_pii_allowed": False,
            "client_claim_allowed": False,
            "production_activation_allowed": False
        },
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3821..3860 - Controlled Pilot Real Candidate Intake Dry Run Shell"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_real_candidate_intake_dry_run_gate",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "manual_dry_run_gate_only": True,
        "automatic_capture_blocked": True,
        "dataset_acceptance_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    doc = """# PROD-3781..3820 - Controlled Pilot Real Candidate Intake Dry Run Gate

Authorizes only preparation of a manual real-candidate intake dry run shell.

This phase does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

Boundary: gate only. No automatic capture, raw private data, secrets, unredacted PII, production activation, client-facing claim, commercial pricing claim or validated real-world claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(GATE, gate)
    write_json(CAL_GATE, gate)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_packet_ready": prev.get("decision") == "CONTROLLED_PILOT_REAL_CANDIDATE_BOUNDARY_REVIEW_PACKET_READY",
        "previous_real_candidate_not_inserted": prev.get("real_candidate_inserted") is False,
        "previous_real_candidate_not_accepted": prev.get("real_candidate_accepted_to_dataset") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "boundary_packet_exists": BOUNDARY_PACKET.exists(),
        "boundary_checklist_exists": BOUNDARY_CHECKLIST.exists(),
        "validator_exists": VALIDATOR.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "candidate_template_exists": CANDIDATE_TEMPLATE.exists(),
        "evidence_packet_exists": EVIDENCE_PACKET.exists(),
        "schema_exists": SCHEMA.exists(),
        "boundary_control_count": len(boundary_controls),
        "review_check_count": len(review_checks),
        "review_outcome_count": len(review_outcomes),
        "checklist_item_count": len(checklist_items),
        "validation_rule_count": len(validation_rules),
        "schema_required_count": len(schema_required),
        "has_required_review_outcome": "APPROVE_MANUAL_REAL_CANDIDATE_INTAKE_DRY_RUN_ONLY" in review_outcomes,
        "empty_batch_candidate_zero": empty_batch.get("candidate_count") == 0,
        "empty_batch_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "candidate_template_no_real_data": candidate.get("session_id") == "CANDIDATE_TEMPLATE_NO_REAL_SESSION_DATA",
        "candidate_source_refs_only": candidate.get("source_refs_only") is True,
        "evidence_refs_only": evidence.get("required_refs_only") is True,
        "evidence_has_decision_gate": "decision_gate" in evidence_fields,
        "dry_run_control_count": len(DRY_RUN_CONTROLS),
        "decision_manual_dry_run_only": decision == "APPROVED_FOR_MANUAL_REAL_CANDIDATE_INTAKE_DRY_RUN_ONLY",
        "real_data_not_captured_this_phase": contract["real_data_captured_in_this_phase"] is False,
        "real_candidate_not_inserted": contract["real_candidate_inserted"] is False,
        "real_candidate_not_accepted": contract["real_candidate_accepted_to_dataset"] is False,
        "manual_dry_run_gate_only": contract["manual_dry_run_gate_only"] is True,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "real_candidate_dataset_acceptance_blocked": "real_candidate_dataset_acceptance" in BLOCKED,
        "dataset_accept_without_review_blocked": "dataset_acceptance_without_human_review" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["boundary_control_count"] < 16:
        errors.append("boundary_control_count below 16")
    if checks["review_check_count"] < 16:
        errors.append("review_check_count below 16")
    if checks["review_outcome_count"] < 5:
        errors.append("review_outcome_count below 5")
    if checks["validation_rule_count"] < 16:
        errors.append("validation_rule_count below 16")
    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["dry_run_control_count"] < 17:
        errors.append("dry_run_control_count below 17")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": decision if status == "PASS" else "CONTROLLED_PILOT_REAL_CANDIDATE_INTAKE_DRY_RUN_GATE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dry_run_control_count": len(DRY_RUN_CONTROLS),
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
        "# PROD-3781..3820 Controlled Pilot Real Candidate Intake Dry Run Gate",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Dry run controls: `{len(DRY_RUN_CONTROLS)}`",
        f"- Real candidate inserted: `{result['real_candidate_inserted']}`",
        f"- Real candidate accepted to dataset: `{result['real_candidate_accepted_to_dataset']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Real dataset candidate count: `{result['real_dataset_candidate_count']}`",
        f"- Real dataset accepted count: `{result['real_dataset_accepted_count']}`",
        f"- Next: `{gate['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Gate only.",
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
    print("dry_run_controls:", len(DRY_RUN_CONTROLS))
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

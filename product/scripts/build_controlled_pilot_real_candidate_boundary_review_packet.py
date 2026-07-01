#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3741..3780"
REQ_TAG = "product-controlled-pilot-mock-dataset-gate-v0.1"

PREV_OUT = ROOT / "outputs/prod3701_3740_controlled_pilot_mock_dataset_gate.json"
MOCK_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_mock_dataset_gate_v0_1.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_validator_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
EVIDENCE_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_evidence_packet_template_v0_1.json"
CANDIDATE_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_real_session_candidate_template_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"

DOC = ROOT / "docs/product/595_CONTROLLED_PILOT_REAL_CANDIDATE_BOUNDARY_REVIEW_PACKET.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_real_candidate_boundary_review_packet.contract.json"
SPEC = ROOT / "product/memory/controlled_pilot_real_candidate_boundary_review_packet_v0_1.json"
PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_packet_v0_1.json"
CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_checklist_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3741_3780_controlled_pilot_real_candidate_boundary_review_packet.json"
OUT_MD = ROOT / "outputs/prod3741_3780_controlled_pilot_real_candidate_boundary_review_packet.md"

BOUNDARY_CONTROLS = [
    "manual_candidate_only",
    "source_refs_only_required",
    "raw_private_data_forbidden",
    "secret_or_credential_forbidden",
    "unredacted_pii_forbidden",
    "privacy_review_required",
    "pii_redaction_required",
    "secret_scan_required",
    "human_reviewer_required",
    "evidence_packet_refs_required",
    "operator_checklist_required",
    "claim_boundary_required",
    "decision_gate_required",
    "dataset_acceptance_without_review_forbidden",
    "client_facing_claim_forbidden",
    "production_activation_forbidden"
]

REVIEW_CHECKS = [
    "reviewer_identity_confirmed",
    "candidate_source_refs_only_confirmed",
    "no_raw_private_data_confirmed",
    "no_secret_or_credential_confirmed",
    "no_unredacted_pii_confirmed",
    "privacy_review_ref_present",
    "pii_redaction_ref_present",
    "secret_scan_ref_present",
    "evidence_packet_ref_present",
    "operator_checklist_ref_present",
    "human_reviewer_notes_ref_present",
    "claim_boundary_confirmed",
    "decision_gate_confirmed",
    "dataset_acceptance_decision_confirmed",
    "client_claim_absent_confirmed",
    "production_activation_absent_confirmed"
]

REVIEW_OUTCOMES = [
    "APPROVE_MANUAL_REAL_CANDIDATE_INTAKE_DRY_RUN_ONLY",
    "HOLD_FOR_MISSING_BOUNDARY_EVIDENCE",
    "HOLD_FOR_PRIVACY_OR_PII_REVIEW",
    "REJECT_SECRET_OR_RAW_PRIVATE_DATA_RISK",
    "REJECT_CLIENT_OR_PRODUCTION_CLAIM_RISK"
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

ALLOWED = [
    "real_candidate_boundary_review_packet_creation",
    "manual_boundary_review_preparation",
    "review_checklist_creation",
    "manual_real_candidate_intake_dry_run_preparation",
    "source_reference_boundary_preparation"
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
    mock_gate = read_json(MOCK_GATE) if MOCK_GATE.exists() else {}
    validator = read_json(VALIDATOR) if VALIDATOR.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    evidence = read_json(EVIDENCE_PACKET) if EVIDENCE_PACKET.exists() else {}
    candidate = read_json(CANDIDATE_TEMPLATE) if CANDIDATE_TEMPLATE.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    validation_rules = validator.get("validation_rules", [])
    decisions = validator.get("acceptance_decisions", [])
    schema_required = schema.get("required", [])
    evidence_fields = set(evidence.get("fields", {}).keys())

    boundary_packet = {
        "version": "controlled_pilot_real_candidate_boundary_review_packet.v0.1",
        "phase": PHASE,
        "purpose": "Prepare boundary review before any real controlled pilot candidate intake.",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "decision": "BOUNDARY_REVIEW_PACKET_READY_NO_REAL_CANDIDATE",
        "boundary_controls": BOUNDARY_CONTROLS,
        "review_checks": REVIEW_CHECKS,
        "review_outcomes": REVIEW_OUTCOMES,
        "current_dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "entry_boundary": {
            "next_allowed_step": "manual real candidate intake dry run preparation only",
            "automatic_capture_allowed": False,
            "raw_private_data_allowed": False,
            "secret_storage_allowed": False,
            "unredacted_pii_allowed": False,
            "dataset_acceptance_allowed_in_this_phase": False,
            "client_claim_allowed": False,
            "production_activation_allowed": False
        },
        "required_references": {
            "schema": "product/schemas/real_session_capture.schema.json",
            "validator": "product/calibration/real_sessions/controlled_pilot_dataset_candidate_validator_v0_1.json",
            "evidence_packet_template": "product/calibration/real_sessions/controlled_pilot_evidence_packet_template_v0_1.json",
            "candidate_template": "product/calibration/real_sessions/controlled_real_session_candidate_template_v0_1.json",
            "reviewer_queue": "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
        },
        "claim_boundary": "Boundary review packet only. No real candidate captured or accepted.",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3781..3820 - Controlled Pilot Real Candidate Intake Dry Run Gate"
    }

    checklist = {
        "version": "controlled_pilot_real_candidate_boundary_review_checklist.v0.1",
        "phase": PHASE,
        "status": "CHECKLIST_TEMPLATE_ONLY_NO_REAL_CANDIDATE",
        "real_data_captured_in_this_phase": False,
        "checks": [
            {"id": f"BR-{i+1:03d}", "name": name, "required": True, "status": "PENDING"}
            for i, name in enumerate(REVIEW_CHECKS)
        ],
        "review_outcomes": REVIEW_OUTCOMES,
        "default_outcome": "HOLD_FOR_MISSING_BOUNDARY_EVIDENCE",
        "blocked_actions": BLOCKED
    }

    spec = {
        "version": "controlled_pilot_real_candidate_boundary_review_packet.v0.1",
        "phase": PHASE,
        "purpose": boundary_packet["purpose"],
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "boundary_control_count": len(BOUNDARY_CONTROLS),
        "review_check_count": len(REVIEW_CHECKS),
        "review_outcome_count": len(REVIEW_OUTCOMES),
        "packet": "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_packet_v0_1.json",
        "checklist": "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_checklist_v0_1.json",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": boundary_packet["recommended_next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_real_candidate_boundary_review_packet",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "boundary_review_only": True,
        "dataset_acceptance_blocked": True,
        "automatic_capture_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": boundary_packet["recommended_next_phase"]
    }

    doc = """# PROD-3741..3780 - Controlled Pilot Real Candidate Boundary Review Packet

Prepares the boundary review packet before any real controlled pilot candidate intake.

This phase does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

It prepares boundary controls, review checklist and review outcomes for the future manual real candidate intake dry run.

Boundary: review packet only. No automatic capture, raw private data, secrets, unredacted PII, production activation, client-facing claim or validated real-world claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(PACKET, boundary_packet)
    write_json(CHECKLIST, checklist)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_decision_boundary_review_prep": prev.get("decision") == "APPROVED_FOR_REAL_CANDIDATE_BOUNDARY_REVIEW_PREPARATION_ONLY",
        "previous_real_dataset_zero": prev.get("real_dataset_candidate_count") == 0,
        "previous_real_accepted_zero": prev.get("real_dataset_accepted_count") == 0,
        "previous_queue_pending_zero": prev.get("reviewer_queue_pending") == 0,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "mock_gate_exists": MOCK_GATE.exists(),
        "validator_exists": VALIDATOR.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "evidence_packet_exists": EVIDENCE_PACKET.exists(),
        "candidate_template_exists": CANDIDATE_TEMPLATE.exists(),
        "schema_exists": SCHEMA.exists(),
        "validation_rule_count": len(validation_rules),
        "acceptance_decision_count": len(decisions),
        "schema_required_count": len(schema_required),
        "empty_batch_candidate_zero": empty_batch.get("candidate_count") == 0,
        "empty_batch_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "evidence_refs_only": evidence.get("required_refs_only") is True,
        "evidence_has_dataset_decision": "dataset_acceptance_decision" in evidence_fields,
        "candidate_template_no_real_data": candidate.get("session_id") == "CANDIDATE_TEMPLATE_NO_REAL_SESSION_DATA",
        "candidate_source_refs_only": candidate.get("source_refs_only") is True,
        "mock_gate_real_dataset_empty": mock_gate.get("real_dataset_state", {}).get("candidate_count") == 0,
        "boundary_control_count": len(BOUNDARY_CONTROLS),
        "review_check_count": len(REVIEW_CHECKS),
        "review_outcome_count": len(REVIEW_OUTCOMES),
        "has_approve_dry_run_outcome": "APPROVE_MANUAL_REAL_CANDIDATE_INTAKE_DRY_RUN_ONLY" in REVIEW_OUTCOMES,
        "real_data_not_captured_this_phase": contract["real_data_captured_in_this_phase"] is False,
        "real_candidate_not_inserted": contract["real_candidate_inserted"] is False,
        "real_candidate_not_accepted": contract["real_candidate_accepted_to_dataset"] is False,
        "boundary_review_only": contract["boundary_review_only"] is True,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "real_candidate_dataset_acceptance_blocked": "real_candidate_dataset_acceptance" in BLOCKED,
        "dataset_accept_without_review_blocked": "dataset_acceptance_without_human_review" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["validation_rule_count"] < 16:
        errors.append("validation_rule_count below 16")
    if checks["acceptance_decision_count"] < 5:
        errors.append("acceptance_decision_count below 5")
    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["boundary_control_count"] < 16:
        errors.append("boundary_control_count below 16")
    if checks["review_check_count"] < 16:
        errors.append("review_check_count below 16")
    if checks["review_outcome_count"] < 5:
        errors.append("review_outcome_count below 5")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "CONTROLLED_PILOT_REAL_CANDIDATE_BOUNDARY_REVIEW_PACKET_READY" if status == "PASS" else "CONTROLLED_PILOT_REAL_CANDIDATE_BOUNDARY_REVIEW_PACKET_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "boundary_control_count": len(BOUNDARY_CONTROLS),
        "review_check_count": len(REVIEW_CHECKS),
        "review_outcome_count": len(REVIEW_OUTCOMES),
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": boundary_packet["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3741..3780 Controlled Pilot Real Candidate Boundary Review Packet",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Boundary controls: `{len(BOUNDARY_CONTROLS)}`",
        f"- Review checks: `{len(REVIEW_CHECKS)}`",
        f"- Review outcomes: `{len(REVIEW_OUTCOMES)}`",
        f"- Real candidate inserted: `{result['real_candidate_inserted']}`",
        f"- Real candidate accepted to dataset: `{result['real_candidate_accepted_to_dataset']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{boundary_packet['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Boundary review packet only.",
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
    print("boundary_controls:", len(BOUNDARY_CONTROLS))
    print("review_checks:", len(REVIEW_CHECKS))
    print("review_outcomes:", len(REVIEW_OUTCOMES))
    print("real_candidate_inserted:", result["real_candidate_inserted"])
    print("real_candidate_accepted_to_dataset:", result["real_candidate_accepted_to_dataset"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", boundary_packet["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

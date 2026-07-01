#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3541..3580"
REQ_TAG = "product-controlled-pilot-evidence-packet-reviewer-queue-v0.1"

PREV_OUT = ROOT / "outputs/prod3501_3540_controlled_pilot_evidence_packet_reviewer_queue.json"
EVIDENCE_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_evidence_packet_template_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
CANDIDATE_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_real_session_candidate_template_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"
OPERATOR_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_real_session_operator_checklist_v0_1.json"

DOC = ROOT / "docs/product/590_CONTROLLED_PILOT_DATASET_CANDIDATE_VALIDATOR.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_dataset_candidate_validator.contract.json"
SPEC = ROOT / "product/memory/controlled_pilot_dataset_candidate_validator_v0_1.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_validator_v0_1.json"
EMPTY_VALIDATION_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3541_3580_controlled_pilot_dataset_candidate_validator.json"
OUT_MD = ROOT / "outputs/prod3541_3580_controlled_pilot_dataset_candidate_validator.md"

VALIDATION_RULES = [
    "schema_required_fields_present",
    "source_refs_only_true",
    "no_raw_private_data",
    "no_secret_or_credential",
    "no_unredacted_pii",
    "privacy_review_passed",
    "pii_redaction_passed",
    "secret_scan_passed",
    "human_reviewer_notes_present",
    "evidence_packet_refs_present",
    "operator_checklist_passed",
    "claim_boundary_confirmed",
    "decision_gate_present",
    "dataset_acceptance_decision_valid",
    "client_claim_absent",
    "production_activation_absent"
]

ACCEPTANCE_DECISIONS = [
    "ACCEPT_AS_CALIBRATION_CANDIDATE",
    "REJECT_PRIVACY_OR_SECRET_RISK",
    "HOLD_FOR_MISSING_EVIDENCE",
    "HOLD_FOR_CLAIM_BOUNDARY_REVIEW",
    "HOLD_FOR_SCHEMA_REPAIR"
]

BLOCKED = [
    "automatic_real_session_capture",
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
    "dataset_candidate_validator_creation",
    "empty_validation_batch_creation",
    "candidate_acceptance_rule_definition",
    "manual_candidate_validation_preparation",
    "review_gate_taxonomy_definition"
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

    prev_out = read_json(PREV_OUT) if PREV_OUT.exists() else {}
    evidence = read_json(EVIDENCE_PACKET) if EVIDENCE_PACKET.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    candidate = read_json(CANDIDATE_TEMPLATE) if CANDIDATE_TEMPLATE.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}
    operator = read_json(OPERATOR_CHECKLIST) if OPERATOR_CHECKLIST.exists() else {}

    schema_required = schema.get("required", [])
    evidence_fields = set(evidence.get("fields", {}).keys())
    queue_items = queue.get("items", [])
    candidate_fields = set(candidate.keys())
    operator_checks = {c.get("name") for c in operator.get("checks", [])}
    review_decisions = set(evidence.get("review_decisions", []))

    validator = {
        "version": "controlled_pilot_dataset_candidate_validator.v0.1",
        "phase": PHASE,
        "purpose": "Define validation rules before any controlled pilot candidate enters calibration dataset.",
        "real_data_captured_in_this_phase": False,
        "validation_rules": VALIDATION_RULES,
        "acceptance_decisions": ACCEPTANCE_DECISIONS,
        "acceptance_rule": "A candidate can enter the calibration dataset only when all validation rules pass and the reviewer decision is ACCEPT_AS_CALIBRATION_CANDIDATE.",
        "default_result": "HOLD_EMPTY_VALIDATION_BATCH_NO_REAL_CANDIDATES",
        "candidate_template": "product/calibration/real_sessions/controlled_real_session_candidate_template_v0_1.json",
        "evidence_packet_template": "product/calibration/real_sessions/controlled_pilot_evidence_packet_template_v0_1.json",
        "reviewer_queue": "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json",
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": "PROD-3581..3620 - Controlled Pilot Empty Dataset Acceptance Gate"
    }

    empty_validation_batch = {
        "version": "controlled_pilot_dataset_candidate_empty_validation_batch.v0.1",
        "phase": PHASE,
        "batch_id": "CONTROLLED-PILOT-CANDIDATE-VALIDATION-EMPTY-V0-1",
        "batch_status": "EMPTY_VALIDATOR_READY_NO_REAL_CANDIDATES",
        "real_data_captured_in_this_phase": False,
        "candidate_count": 0,
        "accepted_count": 0,
        "rejected_count": 0,
        "held_count": 0,
        "candidates": [],
        "validation_rules": VALIDATION_RULES,
        "acceptance_decisions": ACCEPTANCE_DECISIONS,
        "dataset_gate": "HOLD_EMPTY_VALIDATION_BATCH_NO_REAL_CANDIDATES",
        "claim_boundary": "validator and empty validation batch only no real-world claim"
    }

    spec = {
        "version": "controlled_pilot_dataset_candidate_validator.v0.1",
        "phase": PHASE,
        "purpose": validator["purpose"],
        "real_data_captured_in_this_phase": False,
        "validator": "product/calibration/real_sessions/controlled_pilot_dataset_candidate_validator_v0_1.json",
        "empty_validation_batch": "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json",
        "validation_rule_count": len(VALIDATION_RULES),
        "acceptance_decision_count": len(ACCEPTANCE_DECISIONS),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": validator["recommended_next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_dataset_candidate_validator",
        "real_data_captured_in_this_phase": False,
        "validator_only": True,
        "empty_validation_batch_only": True,
        "manual_review_required": True,
        "all_rules_required_for_acceptance": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": validator["recommended_next_phase"]
    }

    doc = """# PROD-3541..3580 - Controlled Pilot Dataset Candidate Validator

Creates the validator for controlled pilot dataset candidates.

This phase does not capture real session data and does not accept candidates into the dataset.

A future candidate can enter calibration only when schema, source-ref-only capture, privacy review, PII redaction, secret scan, human reviewer notes, evidence packet refs, operator checklist, claim boundary and decision gate all pass.

Boundary: validator and empty validation batch only. No raw private data, secrets, unredacted PII, production activation or real-world/client-facing claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(VALIDATOR, validator)
    write_json(EMPTY_VALIDATION_BATCH, empty_validation_batch)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev_out.get("status") == "PASS",
        "previous_real_data_false": prev_out.get("real_data_captured_in_this_phase") is False,
        "evidence_packet_exists": EVIDENCE_PACKET.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "candidate_template_exists": CANDIDATE_TEMPLATE.exists(),
        "schema_exists": SCHEMA.exists(),
        "operator_checklist_exists": OPERATOR_CHECKLIST.exists(),
        "schema_required_count": len(schema_required),
        "candidate_has_all_schema_required": set(schema_required).issubset(candidate_fields),
        "evidence_has_dataset_decision": "dataset_acceptance_decision" in evidence_fields,
        "evidence_has_decision_gate": "decision_gate" in evidence_fields,
        "evidence_refs_only": evidence.get("required_refs_only") is True,
        "reviewer_queue_empty": queue_items == [],
        "queue_pending_zero": queue.get("pending_count") == 0,
        "candidate_source_refs_only": candidate.get("source_refs_only") is True,
        "operator_has_dataset_gate": "dataset_gate_applied" in operator_checks,
        "validation_rule_count": len(VALIDATION_RULES),
        "acceptance_decision_count": len(ACCEPTANCE_DECISIONS),
        "has_accept_decision": "ACCEPT_AS_CALIBRATION_CANDIDATE" in ACCEPTANCE_DECISIONS,
        "has_reject_privacy_decision": "REJECT_PRIVACY_OR_SECRET_RISK" in ACCEPTANCE_DECISIONS,
        "prior_review_decisions_preserved": review_decisions.issubset(set(ACCEPTANCE_DECISIONS)),
        "empty_validation_candidate_count_zero": empty_validation_batch["candidate_count"] == 0,
        "empty_validation_accept_zero": empty_validation_batch["accepted_count"] == 0,
        "real_data_not_captured_this_phase": contract["real_data_captured_in_this_phase"] is False,
        "validator_only": contract["validator_only"] is True,
        "empty_batch_only": contract["empty_validation_batch_only"] is True,
        "manual_review_required": contract["manual_review_required"] is True,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
        "client_claim_blocked": "client_facing_value_claim" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["validation_rule_count"] < 16:
        errors.append("validation_rule_count below 16")
    if checks["acceptance_decision_count"] < 5:
        errors.append("acceptance_decision_count below 5")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "CONTROLLED_PILOT_DATASET_CANDIDATE_VALIDATOR_READY" if status == "PASS" else "CONTROLLED_PILOT_DATASET_CANDIDATE_VALIDATOR_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "validator": "product/calibration/real_sessions/controlled_pilot_dataset_candidate_validator_v0_1.json",
        "empty_validation_batch": "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json",
        "validation_rule_count": len(VALIDATION_RULES),
        "acceptance_decision_count": len(ACCEPTANCE_DECISIONS),
        "candidate_count": empty_validation_batch["candidate_count"],
        "accepted_count": empty_validation_batch["accepted_count"],
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": validator["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3541..3580 Controlled Pilot Dataset Candidate Validator",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Validation rules: `{len(VALIDATION_RULES)}`",
        f"- Acceptance decisions: `{len(ACCEPTANCE_DECISIONS)}`",
        f"- Candidate count: `{empty_validation_batch['candidate_count']}`",
        f"- Accepted count: `{empty_validation_batch['accepted_count']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{validator['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Validator and empty validation batch only.",
        "- No real session data captured.",
        "- No candidate accepted yet.",
        "- No validated real-world claim.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("validation_rules:", len(VALIDATION_RULES))
    print("acceptance_decisions:", len(ACCEPTANCE_DECISIONS))
    print("candidate_count:", empty_validation_batch["candidate_count"])
    print("accepted_count:", empty_validation_batch["accepted_count"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", validator["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3581..3620"
REQ_TAG = "product-controlled-pilot-dataset-candidate-validator-v0.1"

PREV_OUT = ROOT / "outputs/prod3541_3580_controlled_pilot_dataset_candidate_validator.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_validator_v0_1.json"
EMPTY_VALIDATION_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
EVIDENCE_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_evidence_packet_template_v0_1.json"
CANDIDATE_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_real_session_candidate_template_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"

DOC = ROOT / "docs/product/591_CONTROLLED_PILOT_EMPTY_DATASET_ACCEPTANCE_GATE.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_empty_dataset_acceptance_gate.contract.json"
GATE = ROOT / "product/memory/controlled_pilot_empty_dataset_acceptance_gate_v0_1.json"
CAL_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_empty_dataset_acceptance_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3581_3620_controlled_pilot_empty_dataset_acceptance_gate.json"
OUT_MD = ROOT / "outputs/prod3581_3620_controlled_pilot_empty_dataset_acceptance_gate.md"

REQUIRED_PRECONDITIONS = [
    "validator_ready",
    "empty_validation_batch_present",
    "candidate_count_zero",
    "accepted_count_zero",
    "reviewer_queue_empty",
    "evidence_packet_template_present",
    "candidate_template_present",
    "schema_present",
    "real_data_captured_false",
    "claim_boundary_present"
]

ALLOWED = [
    "manual_candidate_intake_preparation",
    "empty_dataset_acceptance_gate_definition",
    "reviewer_queue_preflight",
    "candidate_template_preflight",
    "evidence_packet_preflight"
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
    "commercial_package_pricing_claim",
    "dataset_acceptance_without_human_review"
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
    validator = read_json(VALIDATOR) if VALIDATOR.exists() else {}
    empty_batch = read_json(EMPTY_VALIDATION_BATCH) if EMPTY_VALIDATION_BATCH.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    evidence = read_json(EVIDENCE_PACKET) if EVIDENCE_PACKET.exists() else {}
    candidate = read_json(CANDIDATE_TEMPLATE) if CANDIDATE_TEMPLATE.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    validator_rules = validator.get("validation_rules", [])
    decisions = validator.get("acceptance_decisions", [])
    schema_required = schema.get("required", [])

    decision = "APPROVED_FOR_MANUAL_CANDIDATE_INTAKE_PREPARATION_ONLY"
    if empty_batch.get("candidate_count") != 0 or empty_batch.get("accepted_count") != 0:
        decision = "BLOCK_NON_EMPTY_DATASET_GATE"
    if prev_out.get("real_data_captured_in_this_phase") is not False:
        decision = "BLOCK_REAL_DATA_BOUNDARY_BREACH"

    gate = {
        "version": "controlled_pilot_empty_dataset_acceptance_gate.v0.1",
        "phase": PHASE,
        "decision": decision,
        "purpose": "Confirm empty dataset boundary before any manual controlled pilot candidate intake.",
        "real_data_captured_in_this_phase": False,
        "dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "rejected_count": empty_batch.get("rejected_count", 0),
            "held_count": empty_batch.get("held_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "required_preconditions": REQUIRED_PRECONDITIONS,
        "acceptance_boundary": "No candidate is accepted in this phase. This gate only prepares manual candidate intake.",
        "next_candidate_rule": "Any future candidate must pass validator rules, evidence packet refs, source refs only, privacy review, PII redaction, secret scan, human reviewer notes, claim boundary and decision gate.",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3621..3660 - Controlled Pilot Manual Candidate Intake Shell"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_empty_dataset_acceptance_gate",
        "real_data_captured_in_this_phase": False,
        "empty_dataset_gate_only": True,
        "manual_candidate_intake_preparation_only": True,
        "dataset_acceptance_without_human_review_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    doc = """# PROD-3581..3620 - Controlled Pilot Empty Dataset Acceptance Gate

Confirms the empty dataset boundary before any controlled pilot candidate intake.

This phase does not capture real session data and does not accept candidates.

It only allows preparation of a manual candidate intake shell.

Boundary: empty dataset gate only. No automatic capture, raw private data, secrets, unredacted PII, production activation, client-facing claim or validated real-world claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(GATE, gate)
    write_json(CAL_GATE, gate)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev_out.get("status") == "PASS",
        "previous_real_data_false": prev_out.get("real_data_captured_in_this_phase") is False,
        "validator_exists": VALIDATOR.exists(),
        "empty_validation_batch_exists": EMPTY_VALIDATION_BATCH.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "evidence_packet_exists": EVIDENCE_PACKET.exists(),
        "candidate_template_exists": CANDIDATE_TEMPLATE.exists(),
        "schema_exists": SCHEMA.exists(),
        "validator_rule_count": len(validator_rules),
        "acceptance_decision_count": len(decisions),
        "schema_required_count": len(schema_required),
        "candidate_count_zero": empty_batch.get("candidate_count") == 0,
        "accepted_count_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "evidence_refs_only": evidence.get("required_refs_only") is True,
        "candidate_source_refs_only": candidate.get("source_refs_only") is True,
        "candidate_template_no_real_data": candidate.get("session_id") == "CANDIDATE_TEMPLATE_NO_REAL_SESSION_DATA",
        "precondition_count": len(REQUIRED_PRECONDITIONS),
        "decision_preparation_only": decision == "APPROVED_FOR_MANUAL_CANDIDATE_INTAKE_PREPARATION_ONLY",
        "real_data_not_captured_this_phase": contract["real_data_captured_in_this_phase"] is False,
        "empty_dataset_gate_only": contract["empty_dataset_gate_only"] is True,
        "manual_candidate_intake_preparation_only": contract["manual_candidate_intake_preparation_only"] is True,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
        "dataset_accept_without_review_blocked": "dataset_acceptance_without_human_review" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["validator_rule_count"] < 16:
        errors.append("validator_rule_count below 16")
    if checks["acceptance_decision_count"] < 5:
        errors.append("acceptance_decision_count below 5")
    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["precondition_count"] < 10:
        errors.append("precondition_count below 10")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": decision if status == "PASS" else "CONTROLLED_PILOT_EMPTY_DATASET_ACCEPTANCE_GATE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gate": "product/memory/controlled_pilot_empty_dataset_acceptance_gate_v0_1.json",
        "candidate_count": empty_batch.get("candidate_count", 0),
        "accepted_count": empty_batch.get("accepted_count", 0),
        "reviewer_queue_pending": queue.get("pending_count", 0),
        "real_data_captured_in_this_phase": False,
        "precondition_count": len(REQUIRED_PRECONDITIONS),
        "recommended_next_phase": gate["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3581..3620 Controlled Pilot Empty Dataset Acceptance Gate",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Candidate count: `{result['candidate_count']}`",
        f"- Accepted count: `{result['accepted_count']}`",
        f"- Reviewer queue pending: `{result['reviewer_queue_pending']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{gate['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Empty dataset gate only.",
        "- No candidate accepted.",
        "- No real session data captured.",
        "- Manual intake preparation only.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("candidate_count:", result["candidate_count"])
    print("accepted_count:", result["accepted_count"])
    print("reviewer_queue_pending:", result["reviewer_queue_pending"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", gate["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

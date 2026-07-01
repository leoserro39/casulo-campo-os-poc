#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3701..3740"
REQ_TAG = "product-controlled-pilot-mock-candidate-intake-dry-run-v0.1"

PREV_OUT = ROOT / "outputs/prod3661_3700_controlled_pilot_mock_candidate_intake_dry_run.json"
MOCK_CANDIDATE = ROOT / "product/calibration/real_sessions/controlled_pilot_mock_candidate_dry_run_v0_1.json"
MOCK_EVIDENCE = ROOT / "product/calibration/real_sessions/controlled_pilot_mock_evidence_packet_dry_run_v0_1.json"
MOCK_RESULT = ROOT / "product/calibration/real_sessions/controlled_pilot_mock_candidate_validation_result_v0_1.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_validator_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"

DOC = ROOT / "docs/product/594_CONTROLLED_PILOT_MOCK_DATASET_GATE.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_mock_dataset_gate.contract.json"
GATE = ROOT / "product/memory/controlled_pilot_mock_dataset_gate_v0_1.json"
MOCK_DATASET = ROOT / "product/calibration/real_sessions/controlled_pilot_mock_dataset_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3701_3740_controlled_pilot_mock_dataset_gate.json"
OUT_MD = ROOT / "outputs/prod3701_3740_controlled_pilot_mock_dataset_gate.md"

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
    "mock_dataset_gate_creation",
    "mock_candidate_path_confirmation",
    "mock_dataset_summary_generation",
    "manual_real_candidate_readiness_preparation",
    "real_candidate_boundary_review_preparation"
]

REQUIRED_GATE_CONTROLS = [
    "mock_candidate_present",
    "mock_validation_result_pass",
    "mock_evidence_refs_only",
    "real_dataset_empty",
    "reviewer_queue_empty",
    "real_candidate_acceptance_blocked",
    "raw_private_data_blocked",
    "secrets_blocked",
    "unredacted_pii_blocked",
    "real_claims_blocked",
    "human_review_required_for_future_real_candidate"
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
    mock_candidate = read_json(MOCK_CANDIDATE) if MOCK_CANDIDATE.exists() else {}
    mock_evidence = read_json(MOCK_EVIDENCE) if MOCK_EVIDENCE.exists() else {}
    mock_result = read_json(MOCK_RESULT) if MOCK_RESULT.exists() else {}
    validator = read_json(VALIDATOR) if VALIDATOR.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}

    validation_rules = validator.get("validation_rules", [])
    decisions = validator.get("acceptance_decisions", [])

    decision = "APPROVED_FOR_REAL_CANDIDATE_BOUNDARY_REVIEW_PREPARATION_ONLY"
    if mock_result.get("result") != "MOCK_DRY_RUN_PASS_NOT_REAL_ACCEPTANCE":
        decision = "HOLD_MOCK_DATASET_GATE_REVIEW"
    if empty_batch.get("candidate_count") != 0 or empty_batch.get("accepted_count") != 0:
        decision = "BLOCK_REAL_DATASET_NOT_EMPTY"

    mock_dataset = {
        "version": "controlled_pilot_mock_dataset_gate.v0.1",
        "phase": PHASE,
        "decision": decision,
        "purpose": "Confirm mock candidate path while preserving empty real dataset boundary.",
        "mock_only": True,
        "real_data_captured_in_this_phase": False,
        "mock_candidate_count": 1,
        "mock_candidate_accepted_to_real_dataset": False,
        "real_dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "rejected_count": empty_batch.get("rejected_count", 0),
            "held_count": empty_batch.get("held_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "gate_controls": REQUIRED_GATE_CONTROLS,
        "mock_path_result": {
            "candidate": "product/calibration/real_sessions/controlled_pilot_mock_candidate_dry_run_v0_1.json",
            "evidence": "product/calibration/real_sessions/controlled_pilot_mock_evidence_packet_dry_run_v0_1.json",
            "validation_result": "product/calibration/real_sessions/controlled_pilot_mock_candidate_validation_result_v0_1.json",
            "result": mock_result.get("result")
        },
        "future_real_candidate_boundary": {
            "manual_only": True,
            "source_refs_only": True,
            "privacy_review_required": True,
            "pii_redaction_required": True,
            "secret_scan_required": True,
            "human_reviewer_required": True,
            "dataset_acceptance_gate_required": True,
            "client_claim_forbidden": True,
            "production_activation_forbidden": True
        },
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3741..3780 - Controlled Pilot Real Candidate Boundary Review Packet"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_mock_dataset_gate",
        "mock_only": True,
        "real_data_captured_in_this_phase": False,
        "mock_candidate_accepted_to_real_dataset": False,
        "real_dataset_must_remain_empty": True,
        "real_candidate_acceptance_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": mock_dataset["recommended_next_phase"]
    }

    doc = """# PROD-3701..3740 - Controlled Pilot Mock Dataset Gate

Confirms the mock candidate intake path while preserving the empty real dataset boundary.

This phase does not capture real session data and does not accept any candidate into the real calibration dataset.

The mock path can pass, but real candidate acceptance remains blocked until a boundary review packet is prepared and approved.

Boundary: mock dataset gate only. No automatic capture, raw private data, secrets, unredacted PII, production activation, client-facing claim or validated real-world claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(GATE, mock_dataset)
    write_json(MOCK_DATASET, mock_dataset)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_decision_ready": prev.get("decision") == "CONTROLLED_PILOT_MOCK_CANDIDATE_INTAKE_DRY_RUN_READY",
        "previous_mock_candidate_count_one": prev.get("mock_candidate_count") == 1,
        "previous_dataset_not_accepted": prev.get("dataset_candidate_accepted") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "mock_candidate_exists": MOCK_CANDIDATE.exists(),
        "mock_evidence_exists": MOCK_EVIDENCE.exists(),
        "mock_result_exists": MOCK_RESULT.exists(),
        "validator_exists": VALIDATOR.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "validation_rule_count": len(validation_rules),
        "acceptance_decision_count": len(decisions),
        "mock_candidate_mock_only": mock_candidate.get("mock_only") is True,
        "mock_candidate_real_data_false": mock_candidate.get("real_data_captured") is False,
        "mock_candidate_not_accepted": mock_candidate.get("dataset_candidate_accepted") is False,
        "mock_evidence_refs_only": mock_evidence.get("required_refs_only") is True,
        "mock_evidence_real_data_false": mock_evidence.get("real_data_captured") is False,
        "mock_validation_result_pass": mock_result.get("result") == "MOCK_DRY_RUN_PASS_NOT_REAL_ACCEPTANCE",
        "mock_validation_not_accepted": mock_result.get("dataset_candidate_accepted") is False,
        "real_dataset_candidate_zero": empty_batch.get("candidate_count") == 0,
        "real_dataset_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "gate_control_count": len(REQUIRED_GATE_CONTROLS),
        "decision_boundary_review_only": decision == "APPROVED_FOR_REAL_CANDIDATE_BOUNDARY_REVIEW_PREPARATION_ONLY",
        "contract_mock_only": contract["mock_only"] is True,
        "contract_real_data_false": contract["real_data_captured_in_this_phase"] is False,
        "contract_real_dataset_empty": contract["real_dataset_must_remain_empty"] is True,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "real_candidate_acceptance_blocked": "real_candidate_dataset_acceptance" in BLOCKED,
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
    if checks["gate_control_count"] < 11:
        errors.append("gate_control_count below 11")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": decision if status == "PASS" else "CONTROLLED_PILOT_MOCK_DATASET_GATE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mock_candidate_count": 1,
        "mock_candidate_accepted_to_real_dataset": False,
        "real_dataset_candidate_count": empty_batch.get("candidate_count", 0),
        "real_dataset_accepted_count": empty_batch.get("accepted_count", 0),
        "reviewer_queue_pending": queue.get("pending_count", 0),
        "real_data_captured_in_this_phase": False,
        "gate_control_count": len(REQUIRED_GATE_CONTROLS),
        "recommended_next_phase": mock_dataset["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3701..3740 Controlled Pilot Mock Dataset Gate",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Mock candidate count: `{result['mock_candidate_count']}`",
        f"- Mock accepted to real dataset: `{result['mock_candidate_accepted_to_real_dataset']}`",
        f"- Real dataset candidate count: `{result['real_dataset_candidate_count']}`",
        f"- Real dataset accepted count: `{result['real_dataset_accepted_count']}`",
        f"- Reviewer queue pending: `{result['reviewer_queue_pending']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{mock_dataset['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Mock dataset gate only.",
        "- Real dataset remains empty.",
        "- No real candidate accepted.",
        "- No validated real-world claim.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("mock_candidate_count:", result["mock_candidate_count"])
    print("mock_accepted_to_real_dataset:", result["mock_candidate_accepted_to_real_dataset"])
    print("real_dataset_candidate_count:", result["real_dataset_candidate_count"])
    print("real_dataset_accepted_count:", result["real_dataset_accepted_count"])
    print("reviewer_queue_pending:", result["reviewer_queue_pending"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", mock_dataset["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

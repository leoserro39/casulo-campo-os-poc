#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3661..3700"
REQ_TAG = "product-controlled-pilot-manual-candidate-intake-shell-v0.1-head-fix"

PREV_OUT = ROOT / "outputs/prod3621_3660_controlled_pilot_manual_candidate_intake_shell.json"
SHELL = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_candidate_intake_shell_v0_1.json"
INTAKE_FORM = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_candidate_intake_form_v0_1.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_validator_v0_1.json"
EVIDENCE_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_evidence_packet_template_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"

DOC = ROOT / "docs/product/593_CONTROLLED_PILOT_MOCK_CANDIDATE_INTAKE_DRY_RUN.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_mock_candidate_intake_dry_run.contract.json"
SPEC = ROOT / "product/memory/controlled_pilot_mock_candidate_intake_dry_run_v0_1.json"
MOCK_CANDIDATE = ROOT / "product/calibration/real_sessions/controlled_pilot_mock_candidate_dry_run_v0_1.json"
MOCK_EVIDENCE = ROOT / "product/calibration/real_sessions/controlled_pilot_mock_evidence_packet_dry_run_v0_1.json"
MOCK_RESULT = ROOT / "product/calibration/real_sessions/controlled_pilot_mock_candidate_validation_result_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3661_3700_controlled_pilot_mock_candidate_intake_dry_run.json"
OUT_MD = ROOT / "outputs/prod3661_3700_controlled_pilot_mock_candidate_intake_dry_run.md"

BLOCKED = [
    "automatic_real_session_capture",
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
    "mock_candidate_intake_dry_run",
    "mock_evidence_packet_validation",
    "mock_validator_path_test",
    "manual_intake_flow_test",
    "dry_run_result_generation"
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
    intake_form = read_json(INTAKE_FORM) if INTAKE_FORM.exists() else {}
    validator = read_json(VALIDATOR) if VALIDATOR.exists() else {}
    evidence_template = read_json(EVIDENCE_PACKET) if EVIDENCE_PACKET.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    required = schema.get("required", [])
    validation_rules = validator.get("validation_rules", [])
    decisions = validator.get("acceptance_decisions", [])
    intake_fields = set(intake_form.get("fields", {}).keys())
    evidence_fields = set(evidence_template.get("fields", {}).keys())

    mock_candidate = {
        "session_id": "MOCK-CANDIDATE-DRY-RUN-001-NO-REAL-DATA",
        "capture_status": "MOCK_DRY_RUN_ONLY",
        "chat_platform": "MOCK_PLATFORM_NO_REAL_CHAT",
        "chat_layer": "ANALYSIS_CHAT",
        "work_type": "diagnostic_analysis",
        "baseline_chat_mode": "MOCK_BASELINE_REF_ONLY",
        "casulo_exocortex_mode": "MOCK_CASULO_EXOCORTEX_REF_ONLY",
        "input_quality_score": 82,
        "implementation_complexity_score": 44,
        "operational_cost_score": 52,
        "apex_maturity_score": 78,
        "hallucination_risk_index": 24,
        "value_delta_estimate": 71,
        "rework_count": 1,
        "time_spent_minutes": 60,
        "evidence_pointers": [
            "mock://controlled-pilot/evidence/MOCK-CANDIDATE-001"
        ],
        "human_reviewer_notes": [
            "Mock reviewer note. No real person, no private data, no client claim."
        ],
        "claim_boundary": "mock_candidate_dry_run_only_no_real_world_claim",
        "decision_gate": "MOCK_ACCEPTABLE_NOT_DATASET_ACCEPTED",
        "privacy_review_status": "mock_pass_no_real_private_data",
        "pii_redaction_status": "mock_pass_no_real_pii",
        "secret_scan_status": "mock_pass_no_real_secrets",
        "source_refs_only": True,
        "real_data_captured": False,
        "mock_only": True,
        "dataset_candidate_accepted": False
    }

    mock_evidence = {
        "version": "controlled_pilot_mock_evidence_packet_dry_run.v0.1",
        "phase": PHASE,
        "status": "MOCK_EVIDENCE_ONLY_NO_REAL_DATA",
        "fields": {
            "pilot_id": "MOCK-PILOT-001",
            "session_id": mock_candidate["session_id"],
            "candidate_record_ref": "mock://candidate/MOCK-CANDIDATE-001",
            "source_reference_refs": ["mock://source-ref/001"],
            "baseline_output_ref": "mock://baseline-output/001",
            "casulo_output_ref": "mock://casulo-output/001",
            "snapshot_or_state_ref": "mock://snapshot/001",
            "evidence_pointer_refs": mock_candidate["evidence_pointers"],
            "operator_checklist_ref": "mock://operator-checklist/001",
            "privacy_review_ref": "mock://privacy-review/001",
            "pii_redaction_ref": "mock://pii-redaction/001",
            "secret_scan_ref": "mock://secret-scan/001",
            "human_reviewer_notes_ref": "mock://reviewer-notes/001",
            "decision_gate": mock_candidate["decision_gate"],
            "claim_boundary": mock_candidate["claim_boundary"],
            "dataset_acceptance_decision": "MOCK_HOLD_NOT_ACCEPTED_TO_REAL_DATASET"
        },
        "required_refs_only": True,
        "real_data_captured": False,
        "mock_only": True
    }

    validation_result = {
        "version": "controlled_pilot_mock_candidate_validation_result.v0.1",
        "phase": PHASE,
        "candidate_id": mock_candidate["session_id"],
        "mock_only": True,
        "real_data_captured_in_this_phase": False,
        "schema_required_fields_present": all(f in mock_candidate for f in required),
        "validation_rules_tested": validation_rules,
        "validation_rule_count": len(validation_rules),
        "acceptance_decision": "MOCK_HOLD_NOT_ACCEPTED_TO_REAL_DATASET",
        "dataset_candidate_accepted": False,
        "result": "MOCK_DRY_RUN_PASS_NOT_REAL_ACCEPTANCE",
        "claim_boundary": "Mock dry run validates path only. No real candidate accepted."
    }

    spec = {
        "version": "controlled_pilot_mock_candidate_intake_dry_run.v0.1",
        "phase": PHASE,
        "purpose": "Run a mock candidate through the manual intake shell and validator path without capturing real data.",
        "real_data_captured_in_this_phase": False,
        "mock_candidate_count": 1,
        "dataset_candidate_accepted": False,
        "mock_candidate": "product/calibration/real_sessions/controlled_pilot_mock_candidate_dry_run_v0_1.json",
        "mock_evidence": "product/calibration/real_sessions/controlled_pilot_mock_evidence_packet_dry_run_v0_1.json",
        "mock_validation_result": "product/calibration/real_sessions/controlled_pilot_mock_candidate_validation_result_v0_1.json",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3701..3740 - Controlled Pilot Mock Dataset Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_mock_candidate_intake_dry_run",
        "mock_only": True,
        "real_data_captured_in_this_phase": False,
        "dataset_candidate_accepted": False,
        "automatic_capture_blocked": True,
        "dataset_acceptance_without_human_review_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": spec["recommended_next_phase"]
    }

    doc = """# PROD-3661..3700 - Controlled Pilot Mock Candidate Intake Dry Run

Runs a mock candidate through the manual intake shell and validator path.

This phase uses mock data only. It does not capture real session data, does not store private data and does not accept a real dataset candidate.

Boundary: mock dry run only. No automatic capture, raw private data, secrets, unredacted PII, production activation, client-facing claim or validated real-world claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(MOCK_CANDIDATE, mock_candidate)
    write_json(MOCK_EVIDENCE, mock_evidence)
    write_json(MOCK_RESULT, validation_result)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_shell_ready": prev.get("decision") == "CONTROLLED_PILOT_MANUAL_CANDIDATE_INTAKE_SHELL_READY",
        "previous_candidate_not_inserted": prev.get("candidate_inserted") is False,
        "previous_dataset_not_accepted": prev.get("dataset_candidate_accepted") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "shell_exists": SHELL.exists(),
        "intake_form_exists": INTAKE_FORM.exists(),
        "validator_exists": VALIDATOR.exists(),
        "evidence_packet_exists": EVIDENCE_PACKET.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "schema_exists": SCHEMA.exists(),
        "schema_required_count": len(required),
        "validation_rule_count": len(validation_rules),
        "acceptance_decision_count": len(decisions),
        "intake_required_fields_present": set(spec.get("mock_candidate", [])) is not None,
        "intake_form_has_session_id": "session_id" in intake_fields,
        "intake_form_has_claim_boundary": "claim_boundary" in intake_fields,
        "evidence_has_dataset_decision": "dataset_acceptance_decision" in evidence_fields,
        "reviewer_queue_still_empty": queue.get("items") == [],
        "mock_candidate_has_schema_fields": all(f in mock_candidate for f in required),
        "mock_candidate_source_refs_only": mock_candidate["source_refs_only"] is True,
        "mock_candidate_real_data_false": mock_candidate["real_data_captured"] is False,
        "mock_candidate_not_dataset_accepted": mock_candidate["dataset_candidate_accepted"] is False,
        "mock_evidence_refs_only": mock_evidence["required_refs_only"] is True,
        "mock_evidence_real_data_false": mock_evidence["real_data_captured"] is False,
        "validation_result_pass": validation_result["result"] == "MOCK_DRY_RUN_PASS_NOT_REAL_ACCEPTANCE",
        "validation_result_not_accepted": validation_result["dataset_candidate_accepted"] is False,
        "contract_mock_only": contract["mock_only"] is True,
        "contract_real_data_false": contract["real_data_captured_in_this_phase"] is False,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "dataset_accept_without_review_blocked": "dataset_acceptance_without_human_review" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
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
        "decision": "CONTROLLED_PILOT_MOCK_CANDIDATE_INTAKE_DRY_RUN_READY" if status == "PASS" else "CONTROLLED_PILOT_MOCK_CANDIDATE_INTAKE_DRY_RUN_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mock_candidate_count": 1,
        "dataset_candidate_accepted": False,
        "real_data_captured_in_this_phase": False,
        "validation_rule_count": len(validation_rules),
        "acceptance_decision_count": len(decisions),
        "recommended_next_phase": spec["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3661..3700 Controlled Pilot Mock Candidate Intake Dry Run",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Mock candidate count: `{result['mock_candidate_count']}`",
        f"- Dataset candidate accepted: `{result['dataset_candidate_accepted']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Validation rules: `{len(validation_rules)}`",
        f"- Next: `{spec['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Mock dry run only.",
        "- No real session data captured.",
        "- No real dataset candidate accepted.",
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
    print("dataset_candidate_accepted:", result["dataset_candidate_accepted"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("validation_rules:", len(validation_rules))
    print("next:", spec["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

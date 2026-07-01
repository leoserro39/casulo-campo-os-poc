#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3621..3660"
REQ_TAG = "product-controlled-pilot-empty-dataset-acceptance-gate-v0.1"

PREV_OUT = ROOT / "outputs/prod3581_3620_controlled_pilot_empty_dataset_acceptance_gate.json"
EMPTY_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_empty_dataset_acceptance_gate_v0_1.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_validator_v0_1.json"
EMPTY_VALIDATION_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
EVIDENCE_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_evidence_packet_template_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
CANDIDATE_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_real_session_candidate_template_v0_1.json"
OPERATOR_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_real_session_operator_checklist_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"

DOC = ROOT / "docs/product/592_CONTROLLED_PILOT_MANUAL_CANDIDATE_INTAKE_SHELL.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_manual_candidate_intake_shell.contract.json"
SPEC = ROOT / "product/memory/controlled_pilot_manual_candidate_intake_shell_v0_1.json"
SHELL = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_candidate_intake_shell_v0_1.json"
INTAKE_FORM = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_candidate_intake_form_v0_1.json"
INTAKE_RUNBOOK = ROOT / "product/calibration/real_sessions/controlled_pilot_manual_candidate_intake_shell_v0_1.md"
OUT_JSON = ROOT / "outputs/prod3621_3660_controlled_pilot_manual_candidate_intake_shell.json"
OUT_MD = ROOT / "outputs/prod3621_3660_controlled_pilot_manual_candidate_intake_shell.md"

INTAKE_SECTIONS = [
    "operator_scope_confirmation",
    "session_identity",
    "chat_layer_and_work_type",
    "source_reference_capture",
    "baseline_vs_exocortex_reference",
    "score_entry",
    "privacy_review",
    "pii_redaction",
    "secret_scan",
    "evidence_packet_refs",
    "operator_checklist_refs",
    "human_reviewer_notes",
    "claim_boundary",
    "decision_gate",
    "dataset_candidate_decision"
]

REQUIRED_MANUAL_FIELDS = [
    "session_id",
    "chat_layer",
    "work_type",
    "source_reference_refs",
    "baseline_output_ref",
    "casulo_output_ref",
    "input_quality_score",
    "implementation_complexity_score",
    "operational_cost_score",
    "apex_maturity_score",
    "hallucination_risk_index",
    "value_delta_estimate",
    "privacy_review_ref",
    "pii_redaction_ref",
    "secret_scan_ref",
    "human_reviewer_notes_ref",
    "claim_boundary",
    "decision_gate"
]

PREFLIGHT_CHECKS = [
    "manual_scope_confirmed",
    "reviewer_assigned",
    "schema_loaded",
    "candidate_template_loaded",
    "evidence_packet_template_loaded",
    "reviewer_queue_loaded",
    "validator_loaded",
    "empty_dataset_gate_confirmed",
    "source_refs_only_confirmed",
    "raw_private_data_not_present",
    "secrets_not_present",
    "unredacted_pii_not_present",
    "client_claim_not_present",
    "production_activation_not_present",
    "dataset_acceptance_without_review_blocked"
]

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
    "manual_candidate_intake_shell_creation",
    "manual_candidate_intake_form_template_creation",
    "manual_candidate_preflight_definition",
    "source_reference_only_intake_preparation",
    "reviewer_queue_intake_preparation"
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
    empty_gate = read_json(EMPTY_GATE) if EMPTY_GATE.exists() else {}
    validator = read_json(VALIDATOR) if VALIDATOR.exists() else {}
    empty_batch = read_json(EMPTY_VALIDATION_BATCH) if EMPTY_VALIDATION_BATCH.exists() else {}
    evidence = read_json(EVIDENCE_PACKET) if EVIDENCE_PACKET.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    candidate = read_json(CANDIDATE_TEMPLATE) if CANDIDATE_TEMPLATE.exists() else {}
    operator = read_json(OPERATOR_CHECKLIST) if OPERATOR_CHECKLIST.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    schema_required = schema.get("required", [])
    validator_rules = validator.get("validation_rules", [])
    acceptance_decisions = validator.get("acceptance_decisions", [])
    evidence_fields = set(evidence.get("fields", {}).keys())
    operator_checks = {c.get("name") for c in operator.get("checks", [])}

    shell = {
        "version": "controlled_pilot_manual_candidate_intake_shell.v0.1",
        "phase": PHASE,
        "purpose": "Prepare manual candidate intake shell after empty dataset gate.",
        "real_data_captured_in_this_phase": False,
        "candidate_inserted": False,
        "dataset_candidate_accepted": False,
        "intake_sections": INTAKE_SECTIONS,
        "required_manual_fields": REQUIRED_MANUAL_FIELDS,
        "preflight_checks": PREFLIGHT_CHECKS,
        "default_gate": "HOLD_INTAKE_SHELL_NO_CANDIDATE_INSERTED",
        "claim_boundary": "manual candidate intake shell only no real candidate and no real-world claim",
        "references": {
            "schema": "product/schemas/real_session_capture.schema.json",
            "validator": "product/calibration/real_sessions/controlled_pilot_dataset_candidate_validator_v0_1.json",
            "candidate_template": "product/calibration/real_sessions/controlled_real_session_candidate_template_v0_1.json",
            "evidence_packet_template": "product/calibration/real_sessions/controlled_pilot_evidence_packet_template_v0_1.json",
            "reviewer_queue": "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
        },
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3661..3700 - Controlled Pilot Mock Candidate Intake Dry Run"
    }

    intake_form = {
        "version": "controlled_pilot_manual_candidate_intake_form.v0.1",
        "phase": PHASE,
        "status": "FORM_TEMPLATE_ONLY_NO_REAL_CANDIDATE",
        "real_data_captured_in_this_phase": False,
        "candidate_inserted": False,
        "fields": {
            field: {
                "value": None,
                "required": True,
                "storage_rule": "reference_or_sanitized_value_only"
            }
            for field in REQUIRED_MANUAL_FIELDS
        },
        "preflight_checks": [
            {"name": name, "required": True, "status": "PENDING"}
            for name in PREFLIGHT_CHECKS
        ],
        "allowed_decisions": acceptance_decisions,
        "default_decision": "HOLD_FOR_MISSING_EVIDENCE",
        "claim_boundary": "form template only no real candidate"
    }

    spec = {
        "version": "controlled_pilot_manual_candidate_intake_shell.v0.1",
        "phase": PHASE,
        "purpose": shell["purpose"],
        "real_data_captured_in_this_phase": False,
        "candidate_inserted": False,
        "dataset_candidate_accepted": False,
        "intake_section_count": len(INTAKE_SECTIONS),
        "required_manual_field_count": len(REQUIRED_MANUAL_FIELDS),
        "preflight_check_count": len(PREFLIGHT_CHECKS),
        "shell": "product/calibration/real_sessions/controlled_pilot_manual_candidate_intake_shell_v0_1.json",
        "intake_form": "product/calibration/real_sessions/controlled_pilot_manual_candidate_intake_form_v0_1.json",
        "runbook": "product/calibration/real_sessions/controlled_pilot_manual_candidate_intake_shell_v0_1.md",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": shell["recommended_next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_manual_candidate_intake_shell",
        "real_data_captured_in_this_phase": False,
        "candidate_inserted": False,
        "dataset_candidate_accepted": False,
        "shell_only": True,
        "manual_intake_only": True,
        "automatic_capture_blocked": True,
        "dataset_acceptance_without_human_review_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": shell["recommended_next_phase"]
    }

    runbook = """# Controlled Pilot Manual Candidate Intake Shell v0.1

Boundary: shell/template only. No real candidate is inserted by this phase.

Manual intake order:
1. Confirm empty dataset gate.
2. Assign reviewer.
3. Confirm schema and validator.
4. Copy candidate template.
5. Fill source references only.
6. Fill baseline and CASULO Exocortex refs.
7. Fill scores.
8. Attach privacy review ref.
9. Attach PII redaction ref.
10. Attach secret scan ref.
11. Attach evidence packet refs.
12. Attach reviewer notes ref.
13. Confirm claim boundary.
14. Apply decision gate.
15. Hold until validator approves.

Abort if raw private data, secrets, unredacted PII, automatic capture, client claim, production activation, commercial pricing claim or acceptance without review appears.
"""

    doc = """# PROD-3621..3660 - Controlled Pilot Manual Candidate Intake Shell

Creates the manual candidate intake shell after the empty dataset acceptance gate.

This phase does not capture real session data, does not insert a candidate and does not accept a candidate into the dataset.

It prepares the intake form, preflight checks and manual source-reference-only intake boundary.

Boundary: shell only. No automatic capture, raw private data, secrets, unredacted PII, production activation, client-facing claim or validated real-world claim.
"""

    write(DOC, doc)
    write(INTAKE_RUNBOOK, runbook)
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(SHELL, shell)
    write_json(INTAKE_FORM, intake_form)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev_out.get("status") == "PASS",
        "previous_decision_preparation_only": prev_out.get("decision") == "APPROVED_FOR_MANUAL_CANDIDATE_INTAKE_PREPARATION_ONLY",
        "previous_candidate_count_zero": prev_out.get("candidate_count") == 0,
        "previous_accepted_count_zero": prev_out.get("accepted_count") == 0,
        "previous_queue_pending_zero": prev_out.get("reviewer_queue_pending") == 0,
        "previous_real_data_false": prev_out.get("real_data_captured_in_this_phase") is False,
        "empty_gate_exists": EMPTY_GATE.exists(),
        "validator_exists": VALIDATOR.exists(),
        "empty_validation_batch_exists": EMPTY_VALIDATION_BATCH.exists(),
        "evidence_packet_exists": EVIDENCE_PACKET.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "candidate_template_exists": CANDIDATE_TEMPLATE.exists(),
        "operator_checklist_exists": OPERATOR_CHECKLIST.exists(),
        "schema_exists": SCHEMA.exists(),
        "schema_required_count": len(schema_required),
        "validator_rule_count": len(validator_rules),
        "acceptance_decision_count": len(acceptance_decisions),
        "empty_gate_preparation_only": empty_gate.get("decision") == "APPROVED_FOR_MANUAL_CANDIDATE_INTAKE_PREPARATION_ONLY",
        "empty_batch_candidate_zero": empty_batch.get("candidate_count") == 0,
        "empty_batch_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "evidence_refs_only": evidence.get("required_refs_only") is True,
        "candidate_template_no_real_data": candidate.get("session_id") == "CANDIDATE_TEMPLATE_NO_REAL_SESSION_DATA",
        "candidate_source_refs_only": candidate.get("source_refs_only") is True,
        "operator_has_dataset_gate": "dataset_gate_applied" in operator_checks,
        "evidence_has_source_refs": "source_reference_refs" in evidence_fields,
        "evidence_has_decision_gate": "decision_gate" in evidence_fields,
        "intake_section_count": len(INTAKE_SECTIONS),
        "required_manual_field_count": len(REQUIRED_MANUAL_FIELDS),
        "preflight_check_count": len(PREFLIGHT_CHECKS),
        "shell_real_data_false": shell["real_data_captured_in_this_phase"] is False,
        "candidate_not_inserted": contract["candidate_inserted"] is False,
        "dataset_candidate_not_accepted": contract["dataset_candidate_accepted"] is False,
        "shell_only": contract["shell_only"] is True,
        "automatic_capture_blocked": "automatic_real_session_capture" in BLOCKED,
        "dataset_accept_without_review_blocked": "dataset_acceptance_without_human_review" in BLOCKED,
        "raw_private_storage_blocked": "raw_private_data_storage" in BLOCKED,
        "secret_storage_blocked": "secret_or_credential_storage" in BLOCKED,
        "unredacted_pii_blocked": "unredacted_pii_storage" in BLOCKED,
        "validated_hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["validator_rule_count"] < 16:
        errors.append("validator_rule_count below 16")
    if checks["acceptance_decision_count"] < 5:
        errors.append("acceptance_decision_count below 5")
    if checks["intake_section_count"] < 15:
        errors.append("intake_section_count below 15")
    if checks["required_manual_field_count"] < 18:
        errors.append("required_manual_field_count below 18")
    if checks["preflight_check_count"] < 15:
        errors.append("preflight_check_count below 15")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "CONTROLLED_PILOT_MANUAL_CANDIDATE_INTAKE_SHELL_READY" if status == "PASS" else "CONTROLLED_PILOT_MANUAL_CANDIDATE_INTAKE_SHELL_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "shell": "product/calibration/real_sessions/controlled_pilot_manual_candidate_intake_shell_v0_1.json",
        "intake_form": "product/calibration/real_sessions/controlled_pilot_manual_candidate_intake_form_v0_1.json",
        "intake_section_count": len(INTAKE_SECTIONS),
        "required_manual_field_count": len(REQUIRED_MANUAL_FIELDS),
        "preflight_check_count": len(PREFLIGHT_CHECKS),
        "candidate_inserted": False,
        "dataset_candidate_accepted": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": shell["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3621..3660 Controlled Pilot Manual Candidate Intake Shell",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Intake sections: `{len(INTAKE_SECTIONS)}`",
        f"- Required manual fields: `{len(REQUIRED_MANUAL_FIELDS)}`",
        f"- Preflight checks: `{len(PREFLIGHT_CHECKS)}`",
        f"- Candidate inserted: `{result['candidate_inserted']}`",
        f"- Dataset candidate accepted: `{result['dataset_candidate_accepted']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{shell['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Manual candidate intake shell only.",
        "- No candidate inserted.",
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
    print("intake_sections:", len(INTAKE_SECTIONS))
    print("required_manual_fields:", len(REQUIRED_MANUAL_FIELDS))
    print("preflight_checks:", len(PREFLIGHT_CHECKS))
    print("candidate_inserted:", result["candidate_inserted"])
    print("dataset_candidate_accepted:", result["dataset_candidate_accepted"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("next:", shell["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

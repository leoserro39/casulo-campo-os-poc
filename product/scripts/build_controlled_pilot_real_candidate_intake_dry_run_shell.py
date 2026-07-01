#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3821..3860"
REQ_TAG = "product-controlled-pilot-real-candidate-intake-dry-run-gate-v0.1"

PREV_OUT = ROOT / "outputs/prod3781_3820_controlled_pilot_real_candidate_intake_dry_run_gate.json"
DRY_RUN_GATE = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_gate_v0_1.json"
BOUNDARY_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_packet_v0_1.json"
BOUNDARY_CHECKLIST = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_boundary_review_checklist_v0_1.json"
VALIDATOR = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_validator_v0_1.json"
CANDIDATE_TEMPLATE = ROOT / "product/calibration/real_sessions/controlled_real_session_candidate_template_v0_1.json"
EVIDENCE_PACKET = ROOT / "product/calibration/real_sessions/controlled_pilot_evidence_packet_template_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/controlled_pilot_dataset_candidate_empty_validation_batch_v0_1.json"
REVIEWER_QUEUE = ROOT / "product/calibration/real_sessions/controlled_pilot_reviewer_queue_empty_v0_1.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"

DOC = ROOT / "docs/product/597_CONTROLLED_PILOT_REAL_CANDIDATE_INTAKE_DRY_RUN_SHELL.md"
CONTRACT = ROOT / "product/contracts/controlled_pilot_real_candidate_intake_dry_run_shell.contract.json"
SPEC = ROOT / "product/memory/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.json"
SHELL = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.json"
FORM = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_form_v0_1.json"
RUNBOOK = ROOT / "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.md"
OUT_JSON = ROOT / "outputs/prod3821_3860_controlled_pilot_real_candidate_intake_dry_run_shell.json"
OUT_MD = ROOT / "outputs/prod3821_3860_controlled_pilot_real_candidate_intake_dry_run_shell.md"

SHELL_SECTIONS = [
    "gate_confirmation",
    "boundary_review_confirmation",
    "reviewer_assignment_placeholder",
    "real_candidate_identity_placeholder",
    "source_reference_placeholder",
    "baseline_reference_placeholder",
    "casulo_exocortex_reference_placeholder",
    "score_placeholder",
    "privacy_review_placeholder",
    "pii_redaction_placeholder",
    "secret_scan_placeholder",
    "evidence_packet_placeholder",
    "boundary_checklist_placeholder",
    "human_reviewer_notes_placeholder",
    "claim_boundary_placeholder",
    "decision_gate_placeholder",
    "dataset_acceptance_hold"
]

FORM_FIELDS = [
    "dry_run_id",
    "real_candidate_placeholder_id",
    "operator_id_ref",
    "human_reviewer_ref",
    "source_reference_refs",
    "baseline_output_ref",
    "casulo_output_ref",
    "privacy_review_ref",
    "pii_redaction_ref",
    "secret_scan_ref",
    "evidence_packet_ref",
    "boundary_checklist_ref",
    "human_reviewer_notes_ref",
    "claim_boundary",
    "decision_gate",
    "dataset_acceptance_hold_reason"
]

PREFLIGHT_CHECKS = [
    "prior_gate_passed",
    "boundary_packet_present",
    "boundary_checklist_present",
    "validator_present",
    "schema_present",
    "candidate_template_present",
    "evidence_packet_template_present",
    "empty_real_dataset_confirmed",
    "empty_reviewer_queue_confirmed",
    "manual_dry_run_only_confirmed",
    "source_refs_only_confirmed",
    "raw_private_data_absent_confirmed",
    "secrets_absent_confirmed",
    "unredacted_pii_absent_confirmed",
    "client_claim_absent_confirmed",
    "production_activation_absent_confirmed",
    "dataset_acceptance_blocked_confirmed"
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
    "real_candidate_intake_dry_run_shell_creation",
    "real_candidate_dry_run_form_template_creation",
    "manual_preflight_shell_creation",
    "source_reference_placeholder_preparation",
    "dataset_acceptance_hold_preparation"
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
    gate = read_json(DRY_RUN_GATE) if DRY_RUN_GATE.exists() else {}
    boundary_packet = read_json(BOUNDARY_PACKET) if BOUNDARY_PACKET.exists() else {}
    boundary_checklist = read_json(BOUNDARY_CHECKLIST) if BOUNDARY_CHECKLIST.exists() else {}
    validator = read_json(VALIDATOR) if VALIDATOR.exists() else {}
    candidate_template = read_json(CANDIDATE_TEMPLATE) if CANDIDATE_TEMPLATE.exists() else {}
    evidence_packet = read_json(EVIDENCE_PACKET) if EVIDENCE_PACKET.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}
    queue = read_json(REVIEWER_QUEUE) if REVIEWER_QUEUE.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}

    dry_run_controls = gate.get("dry_run_controls", [])
    boundary_controls = boundary_packet.get("boundary_controls", [])
    boundary_checks = boundary_checklist.get("checks", [])
    validation_rules = validator.get("validation_rules", [])
    schema_required = schema.get("required", [])
    evidence_fields = set(evidence_packet.get("fields", {}).keys())

    shell = {
        "version": "controlled_pilot_real_candidate_intake_dry_run_shell.v0.1",
        "phase": PHASE,
        "purpose": "Prepare a manual dry run shell for real candidate intake without inserting a real candidate.",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "shell_only": True,
        "shell_sections": SHELL_SECTIONS,
        "preflight_checks": PREFLIGHT_CHECKS,
        "default_gate": "HOLD_DRY_RUN_SHELL_NO_REAL_CANDIDATE_INSERTED",
        "dataset_acceptance_state": "BLOCKED_IN_THIS_PHASE",
        "current_dataset_state": {
            "candidate_count": empty_batch.get("candidate_count", 0),
            "accepted_count": empty_batch.get("accepted_count", 0),
            "reviewer_queue_pending": queue.get("pending_count", 0)
        },
        "claim_boundary": "Real candidate intake dry run shell only. No real candidate inserted or accepted.",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3861..3900 - Controlled Pilot Real Candidate Intake Dry Run Validator"
    }

    form = {
        "version": "controlled_pilot_real_candidate_intake_dry_run_form.v0.1",
        "phase": PHASE,
        "status": "FORM_TEMPLATE_ONLY_NO_REAL_CANDIDATE",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "fields": {
            field: {
                "value": None,
                "required": True,
                "storage_rule": "reference_only_or_sanitized_placeholder"
            }
            for field in FORM_FIELDS
        },
        "preflight_checks": [
            {"name": name, "required": True, "status": "PENDING"}
            for name in PREFLIGHT_CHECKS
        ],
        "dataset_acceptance_allowed": False,
        "automatic_capture_allowed": False,
        "claim_boundary": "form template only no real candidate"
    }

    spec = {
        "version": "controlled_pilot_real_candidate_intake_dry_run_shell.v0.1",
        "phase": PHASE,
        "purpose": shell["purpose"],
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "shell_section_count": len(SHELL_SECTIONS),
        "form_field_count": len(FORM_FIELDS),
        "preflight_check_count": len(PREFLIGHT_CHECKS),
        "shell": "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.json",
        "form": "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_form_v0_1.json",
        "runbook": "product/calibration/real_sessions/controlled_pilot_real_candidate_intake_dry_run_shell_v0_1.md",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": shell["recommended_next_phase"]
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "controlled_pilot_real_candidate_intake_dry_run_shell",
        "real_data_captured_in_this_phase": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "shell_only": True,
        "dataset_acceptance_blocked": True,
        "automatic_capture_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": shell["recommended_next_phase"]
    }

    runbook = """# Controlled Pilot Real Candidate Intake Dry Run Shell v0.1

Boundary: dry run shell/template only.

This phase does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

Manual shell order:
1. Confirm prior dry run gate.
2. Confirm boundary review packet and checklist.
3. Confirm validator and schema.
4. Confirm real dataset remains empty.
5. Confirm reviewer queue remains empty.
6. Prepare source-reference placeholders only.
7. Prepare privacy, PII and secret-scan placeholders.
8. Prepare evidence packet placeholders.
9. Prepare reviewer notes placeholder.
10. Confirm claim boundary.
11. Hold dataset acceptance.

Abort if automatic capture, raw private data, secrets, unredacted PII, client-facing claim, production activation, commercial pricing claim or dataset acceptance is attempted.
"""

    doc = """# PROD-3821..3860 - Controlled Pilot Real Candidate Intake Dry Run Shell

Creates the real-candidate intake dry run shell.

This phase does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

It prepares a form template, preflight checks and runbook for a future manual dry run validator.

Boundary: shell only. No automatic capture, raw private data, secrets, unredacted PII, production activation, client-facing claim, commercial pricing claim or validated real-world claim.
"""

    write(DOC, doc)
    write(RUNBOOK, runbook)
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(SHELL, shell)
    write_json(FORM, form)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev.get("status") == "PASS",
        "previous_decision_manual_dry_run_only": prev.get("decision") == "APPROVED_FOR_MANUAL_REAL_CANDIDATE_INTAKE_DRY_RUN_ONLY",
        "previous_real_candidate_not_inserted": prev.get("real_candidate_inserted") is False,
        "previous_real_candidate_not_accepted": prev.get("real_candidate_accepted_to_dataset") is False,
        "previous_real_data_false": prev.get("real_data_captured_in_this_phase") is False,
        "dry_run_gate_exists": DRY_RUN_GATE.exists(),
        "boundary_packet_exists": BOUNDARY_PACKET.exists(),
        "boundary_checklist_exists": BOUNDARY_CHECKLIST.exists(),
        "validator_exists": VALIDATOR.exists(),
        "candidate_template_exists": CANDIDATE_TEMPLATE.exists(),
        "evidence_packet_exists": EVIDENCE_PACKET.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "reviewer_queue_exists": REVIEWER_QUEUE.exists(),
        "schema_exists": SCHEMA.exists(),
        "dry_run_control_count": len(dry_run_controls),
        "boundary_control_count": len(boundary_controls),
        "boundary_check_count": len(boundary_checks),
        "validation_rule_count": len(validation_rules),
        "schema_required_count": len(schema_required),
        "empty_batch_candidate_zero": empty_batch.get("candidate_count") == 0,
        "empty_batch_accepted_zero": empty_batch.get("accepted_count") == 0,
        "reviewer_queue_empty": queue.get("items") == [],
        "reviewer_queue_pending_zero": queue.get("pending_count") == 0,
        "candidate_template_no_real_data": candidate_template.get("session_id") == "CANDIDATE_TEMPLATE_NO_REAL_SESSION_DATA",
        "candidate_source_refs_only": candidate_template.get("source_refs_only") is True,
        "evidence_refs_only": evidence_packet.get("required_refs_only") is True,
        "evidence_has_source_refs": "source_reference_refs" in evidence_fields,
        "shell_section_count": len(SHELL_SECTIONS),
        "form_field_count": len(FORM_FIELDS),
        "preflight_check_count": len(PREFLIGHT_CHECKS),
        "shell_real_data_false": shell["real_data_captured_in_this_phase"] is False,
        "shell_real_candidate_not_inserted": shell["real_candidate_inserted"] is False,
        "shell_real_candidate_not_accepted": shell["real_candidate_accepted_to_dataset"] is False,
        "contract_shell_only": contract["shell_only"] is True,
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

    if checks["dry_run_control_count"] < 17:
        errors.append("dry_run_control_count below 17")
    if checks["boundary_control_count"] < 16:
        errors.append("boundary_control_count below 16")
    if checks["boundary_check_count"] < 16:
        errors.append("boundary_check_count below 16")
    if checks["validation_rule_count"] < 16:
        errors.append("validation_rule_count below 16")
    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["shell_section_count"] < 17:
        errors.append("shell_section_count below 17")
    if checks["form_field_count"] < 16:
        errors.append("form_field_count below 16")
    if checks["preflight_check_count"] < 17:
        errors.append("preflight_check_count below 17")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "CONTROLLED_PILOT_REAL_CANDIDATE_INTAKE_DRY_RUN_SHELL_READY" if status == "PASS" else "CONTROLLED_PILOT_REAL_CANDIDATE_INTAKE_DRY_RUN_SHELL_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "shell_section_count": len(SHELL_SECTIONS),
        "form_field_count": len(FORM_FIELDS),
        "preflight_check_count": len(PREFLIGHT_CHECKS),
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "real_dataset_candidate_count": empty_batch.get("candidate_count", 0),
        "real_dataset_accepted_count": empty_batch.get("accepted_count", 0),
        "recommended_next_phase": shell["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3821..3860 Controlled Pilot Real Candidate Intake Dry Run Shell",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Shell sections: `{len(SHELL_SECTIONS)}`",
        f"- Form fields: `{len(FORM_FIELDS)}`",
        f"- Preflight checks: `{len(PREFLIGHT_CHECKS)}`",
        f"- Real candidate inserted: `{result['real_candidate_inserted']}`",
        f"- Real candidate accepted to dataset: `{result['real_candidate_accepted_to_dataset']}`",
        f"- Real data captured in this phase: `{result['real_data_captured_in_this_phase']}`",
        f"- Next: `{shell['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Dry run shell only.",
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
    print("shell_sections:", len(SHELL_SECTIONS))
    print("form_fields:", len(FORM_FIELDS))
    print("preflight_checks:", len(PREFLIGHT_CHECKS))
    print("real_candidate_inserted:", result["real_candidate_inserted"])
    print("real_candidate_accepted_to_dataset:", result["real_candidate_accepted_to_dataset"])
    print("real_data_captured_in_this_phase:", result["real_data_captured_in_this_phase"])
    print("real_dataset_candidate_count:", result["real_dataset_candidate_count"])
    print("real_dataset_accepted_count:", result["real_dataset_accepted_count"])
    print("next:", shell["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

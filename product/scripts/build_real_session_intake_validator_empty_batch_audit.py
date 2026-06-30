#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3221..3260"
REQ_TAG = "product-real-session-manual-capture-runbook-v0.1"

PREV_OUT = ROOT / "outputs/prod3181_3220_real_session_manual_capture_runbook.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"
EMPTY_INTAKE = ROOT / "product/calibration/real_sessions/real_session_empty_intake_v0_1.json"
RUNBOOK = ROOT / "product/calibration/real_sessions/manual_capture_runbook_v0_1.md"
CHECKLIST = ROOT / "product/calibration/real_sessions/manual_capture_privacy_review_checklist_v0_1.json"

DOC = ROOT / "docs/product/582_REAL_SESSION_INTAKE_VALIDATOR_EMPTY_BATCH_AUDIT.md"
CONTRACT = ROOT / "product/contracts/real_session_intake_validator_empty_batch_audit.contract.json"
SPEC = ROOT / "product/memory/real_session_intake_validator_empty_batch_audit_v0_1.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/real_session_empty_batch_manifest_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3221_3260_real_session_intake_validator_empty_batch_audit.json"
OUT_MD = ROOT / "outputs/prod3221_3260_real_session_intake_validator_empty_batch_audit.md"

BLOCKED = [
    "real_session_data_capture_without_review",
    "raw_private_data_storage",
    "secret_or_credential_storage",
    "unredacted_pii_storage",
    "client_facing_value_claim",
    "real_world_profit_claim",
    "validated_savings_claim",
    "validated_hallucination_reduction_claim",
    "production_activation",
    "automatic_memory_delete",
    "gpt_memory_api_execution"
]

ALLOWED = [
    "empty_batch_manifest_creation",
    "intake_validator_definition",
    "empty_template_audit",
    "privacy_control_audit",
    "calibration_batch_structure_preparation"
]

REQUIRED_EMPTY_FIELDS = [
    "session_id",
    "capture_status",
    "claim_boundary",
    "decision_gate",
    "privacy_review_status",
    "pii_redaction_status",
    "secret_scan_status",
    "source_refs_only"
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

def validate_empty_intake(empty, schema_required):
    errors = []
    for f in schema_required:
        if f not in empty:
            errors.append("missing schema field: " + f)
    for f in REQUIRED_EMPTY_FIELDS:
        if f not in empty:
            errors.append("missing empty control field: " + f)
    if empty.get("capture_status") != "EMPTY_TEMPLATE":
        errors.append("capture_status must be EMPTY_TEMPLATE")
    if empty.get("source_refs_only") is not True:
        errors.append("source_refs_only must be true")
    if empty.get("evidence_pointers") != []:
        errors.append("evidence_pointers must be empty")
    if empty.get("human_reviewer_notes") != []:
        errors.append("human_reviewer_notes must be empty")
    if empty.get("decision_gate") != "HOLD_EMPTY_INTAKE_NOT_REAL_DATA":
        errors.append("decision_gate must hold empty intake")
    return errors

def main():
    errors = []
    prev_out = read_json(PREV_OUT) if PREV_OUT.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}
    empty = read_json(EMPTY_INTAKE) if EMPTY_INTAKE.exists() else {}
    checklist = read_json(CHECKLIST) if CHECKLIST.exists() else {}

    schema_required = schema.get("required", [])
    empty_errors = validate_empty_intake(empty, schema_required)

    empty_batch = {
        "version": "real_session_empty_batch_manifest.v0.1",
        "phase": PHASE,
        "batch_id": "BATCH-000-EMPTY-NO-REAL-DATA",
        "batch_status": "EMPTY_AUDITED",
        "real_data_captured": False,
        "record_count": 0,
        "records": [],
        "schema": "product/schemas/real_session_capture.schema.json",
        "empty_intake_template": "product/calibration/real_sessions/real_session_empty_intake_v0_1.json",
        "runbook": "product/calibration/real_sessions/manual_capture_runbook_v0_1.md",
        "privacy_review_checklist": "product/calibration/real_sessions/manual_capture_privacy_review_checklist_v0_1.json",
        "dataset_acceptance_gate": "HOLD_EMPTY_BATCH_NO_REAL_DATA",
        "claim_boundary": "empty batch audit only no real session data",
        "blocked_actions": BLOCKED
    }

    spec = {
        "version": "real_session_intake_validator_empty_batch_audit.v0.1",
        "phase": PHASE,
        "purpose": "Validate empty real-session intake template and create an audited empty batch manifest.",
        "real_data_captured": False,
        "validator_rules": [
            "All schema-required fields must exist in empty intake.",
            "capture_status must be EMPTY_TEMPLATE.",
            "source_refs_only must be true.",
            "evidence_pointers and reviewer notes must be empty.",
            "empty batch record_count must be zero.",
            "dataset acceptance must remain held."
        ],
        "empty_intake_errors": empty_errors,
        "empty_batch_manifest": "product/calibration/real_sessions/real_session_empty_batch_manifest_v0_1.json",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3261..3300 - Synthetic Calibration Capture Dry Run"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "intake_validator_empty_batch_audit",
        "real_data_captured": False,
        "record_count": 0,
        "empty_batch_only": True,
        "human_review_required_before_real_capture": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": spec["recommended_next_phase"]
    }

    doc = """# PROD-3221..3260 - Real Session Intake Validator and Empty Batch Audit

Validates the empty real-session intake template and creates an audited empty batch manifest.

No real session data is captured in this phase.

The batch is intentionally empty, with record_count zero and dataset acceptance held.

Boundary: empty batch audit only. No real-world profit, savings, ROI, client-facing value or validated hallucination-reduction claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(EMPTY_BATCH, empty_batch)

    checklist_items = checklist.get("checks", [])
    checklist_names = {c.get("name") for c in checklist_items}

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev_out.get("status") == "PASS",
        "previous_real_data_false": prev_out.get("real_data_captured") is False,
        "schema_exists": SCHEMA.exists(),
        "empty_intake_exists": EMPTY_INTAKE.exists(),
        "runbook_exists": RUNBOOK.exists(),
        "checklist_exists": CHECKLIST.exists(),
        "schema_required_count": len(schema_required),
        "empty_intake_valid": len(empty_errors) == 0,
        "empty_batch_record_count_zero": empty_batch["record_count"] == 0,
        "empty_batch_records_empty": empty_batch["records"] == [],
        "real_data_not_captured": contract["real_data_captured"] is False,
        "empty_batch_only": contract["empty_batch_only"] is True,
        "source_refs_only": empty.get("source_refs_only") is True,
        "has_privacy_check": "source_refs_only" in checklist_names,
        "has_pii_check": "pii_redacted" in checklist_names,
        "has_secret_check": "secret_scan_completed" in checklist_names,
        "blocked_unreviewed_capture": "real_session_data_capture_without_review" in BLOCKED,
        "blocked_raw_private_storage": "raw_private_data_storage" in BLOCKED,
        "blocked_secret_storage": "secret_or_credential_storage" in BLOCKED,
        "blocked_unredacted_pii": "unredacted_pii_storage" in BLOCKED,
        "allowed_empty_batch_manifest": "empty_batch_manifest_creation" in ALLOWED
    }

    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if empty_errors:
        errors.extend(["empty_intake: " + e for e in empty_errors])
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "REAL_SESSION_INTAKE_VALIDATOR_EMPTY_BATCH_AUDIT_READY" if status == "PASS" else "REAL_SESSION_INTAKE_VALIDATOR_EMPTY_BATCH_AUDIT_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "validator": "product/memory/real_session_intake_validator_empty_batch_audit_v0_1.json",
        "empty_batch": "product/calibration/real_sessions/real_session_empty_batch_manifest_v0_1.json",
        "schema_required_count": len(schema_required),
        "record_count": empty_batch["record_count"],
        "real_data_captured": False,
        "recommended_next_phase": spec["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3221..3260 Real Session Intake Validator and Empty Batch Audit",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Schema required fields: `{len(schema_required)}`",
        f"- Record count: `{empty_batch['record_count']}`",
        f"- Real data captured: `{result['real_data_captured']}`",
        f"- Next: `{spec['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Empty batch audit only.",
        "- No real session data captured.",
        "- Dataset acceptance remains held.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("schema_required:", len(schema_required))
    print("record_count:", empty_batch["record_count"])
    print("real_data_captured:", result["real_data_captured"])
    print("next:", spec["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

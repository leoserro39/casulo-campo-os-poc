#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3181..3220"
REQ_TAG = "product-real-session-capture-schema-empty-intake-v0.1"

PREV_OUT = ROOT / "outputs/prod3141_3180_real_session_capture_schema_empty_intake.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"
EMPTY_INTAKE = ROOT / "product/calibration/real_sessions/real_session_empty_intake_v0_1.json"
SPEC_PREV = ROOT / "product/memory/real_session_capture_schema_empty_intake_v0_1.json"

DOC = ROOT / "docs/product/581_REAL_SESSION_MANUAL_CAPTURE_RUNBOOK.md"
CONTRACT = ROOT / "product/contracts/real_session_manual_capture_runbook.contract.json"
SPEC = ROOT / "product/memory/real_session_manual_capture_runbook_v0_1.json"
RUNBOOK = ROOT / "product/calibration/real_sessions/manual_capture_runbook_v0_1.md"
CHECKLIST = ROOT / "product/calibration/real_sessions/manual_capture_privacy_review_checklist_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3181_3220_real_session_manual_capture_runbook.json"
OUT_MD = ROOT / "outputs/prod3181_3220_real_session_manual_capture_runbook.md"

STEPS = [
    "select_controlled_session",
    "copy_empty_intake_template",
    "assign_session_id",
    "classify_chat_layer_and_work_type",
    "record_source_references_only",
    "redact_pii_before_storage",
    "run_secret_scan_before_storage",
    "capture_baseline_vs_exocortex_scores",
    "score_value_delta_apex_cost_and_hallucination",
    "attach_evidence_pointers",
    "human_reviewer_decision",
    "accept_or_reject_into_calibration_dataset"
]

REVIEW_GATES = [
    "PRIVACY_REVIEW_REQUIRED",
    "PII_REDACTION_REQUIRED",
    "SECRET_SCAN_REQUIRED",
    "HUMAN_REVIEW_REQUIRED",
    "CLAIM_BOUNDARY_REVIEW_REQUIRED",
    "DATASET_ACCEPTANCE_REVIEW_REQUIRED"
]

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
    "manual_capture_runbook_creation",
    "privacy_review_checklist_creation",
    "controlled_capture_preparation",
    "sanitized_source_reference_capture",
    "human_review_protocol_preparation"
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
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}
    empty = read_json(EMPTY_INTAKE) if EMPTY_INTAKE.exists() else {}
    prev_spec = read_json(SPEC_PREV) if SPEC_PREV.exists() else {}

    checklist = {
        "version": "manual_capture_privacy_review_checklist.v0.1",
        "phase": PHASE,
        "checks": [
            {"id": "CHK-001", "name": "source_refs_only", "required": True},
            {"id": "CHK-002", "name": "no_raw_private_chat_storage", "required": True},
            {"id": "CHK-003", "name": "pii_redacted", "required": True},
            {"id": "CHK-004", "name": "secret_scan_completed", "required": True},
            {"id": "CHK-005", "name": "claim_boundary_confirmed", "required": True},
            {"id": "CHK-006", "name": "human_reviewer_notes_present", "required": True},
            {"id": "CHK-007", "name": "decision_gate_present", "required": True},
            {"id": "CHK-008", "name": "dataset_acceptance_decision_present", "required": True}
        ]
    }

    spec = {
        "version": "real_session_manual_capture_runbook.v0.1",
        "phase": PHASE,
        "purpose": "Define manual capture runbook for future sanitized real-session calibration.",
        "steps": STEPS,
        "review_gates": REVIEW_GATES,
        "privacy_review_checklist": "product/calibration/real_sessions/manual_capture_privacy_review_checklist_v0_1.json",
        "schema": "product/schemas/real_session_capture.schema.json",
        "empty_intake": "product/calibration/real_sessions/real_session_empty_intake_v0_1.json",
        "real_data_captured": False,
        "runbook_boundary": "Preparation only. No real session data captured in this phase.",
        "dataset_acceptance_rule": "A session can enter calibration dataset only after privacy review, PII redaction, secret scan, source-ref-only capture and human reviewer acceptance.",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3221..3260 - Real Session Intake Validator and Empty Batch Audit"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "manual_capture_runbook_only",
        "real_data_captured": False,
        "source_refs_only_required": True,
        "human_review_required": True,
        "privacy_review_required": True,
        "secret_scan_required": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": spec["recommended_next_phase"]
    }

    doc = """# PROD-3181..3220 - Real Session Manual Capture Runbook

Defines the manual runbook for future sanitized real-session calibration.

This phase prepares the process only. It does not capture real session data.

Any future real session must use source references only, PII redaction, secret scan, privacy review and human reviewer acceptance before entering the calibration dataset.

Boundary: runbook only. No real-world profit, savings, ROI, client-facing value or validated hallucination-reduction claim.
"""

    runbook_text = """# Manual Capture Runbook v0.1

1. Select a controlled session.
2. Copy the empty intake template.
3. Assign a session_id.
4. Classify chat_layer and work_type.
5. Store source references only.
6. Redact PII before storage.
7. Run secret scan before storage.
8. Score baseline and CASULO Exocortex modes.
9. Score Value Delta, Apex Maturity, operational cost and hallucination risk.
10. Attach evidence pointers.
11. Add human reviewer notes.
12. Accept or reject the session for calibration dataset.

Blocked: raw private data, secrets, unreviewed capture, client claims, production claims and validated savings or hallucination-reduction claims.
"""

    write(DOC, doc)
    write(RUNBOOK, runbook_text)
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(CHECKLIST, checklist)

    required = schema.get("required", [])
    checklist_names = {c["name"] for c in checklist["checks"]}

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev_out.get("status") == "PASS",
        "schema_exists": SCHEMA.exists(),
        "empty_intake_exists": EMPTY_INTAKE.exists(),
        "previous_spec_exists": SPEC_PREV.exists(),
        "previous_real_data_false": prev_out.get("real_data_captured") is False,
        "empty_template_status": empty.get("capture_status") == "EMPTY_TEMPLATE",
        "schema_required_count": len(required),
        "step_count": len(STEPS),
        "review_gate_count": len(REVIEW_GATES),
        "checklist_count": len(checklist["checks"]),
        "has_source_refs_check": "source_refs_only" in checklist_names,
        "has_no_raw_private_check": "no_raw_private_chat_storage" in checklist_names,
        "has_pii_check": "pii_redacted" in checklist_names,
        "has_secret_scan_check": "secret_scan_completed" in checklist_names,
        "has_human_review_gate": "HUMAN_REVIEW_REQUIRED" in REVIEW_GATES,
        "has_privacy_gate": "PRIVACY_REVIEW_REQUIRED" in REVIEW_GATES,
        "real_data_not_captured": contract["real_data_captured"] is False,
        "source_refs_only_required": contract["source_refs_only_required"] is True,
        "human_review_required": contract["human_review_required"] is True,
        "privacy_review_required": contract["privacy_review_required"] is True,
        "secret_scan_required": contract["secret_scan_required"] is True,
        "blocked_unreviewed_capture": "real_session_data_capture_without_review" in BLOCKED,
        "blocked_raw_private_storage": "raw_private_data_storage" in BLOCKED,
        "blocked_secret_storage": "secret_or_credential_storage" in BLOCKED,
        "blocked_unredacted_pii": "unredacted_pii_storage" in BLOCKED
    }

    if checks["schema_required_count"] < 23:
        errors.append("schema_required_count below 23")
    if checks["step_count"] < 12:
        errors.append("step_count below 12")
    if checks["review_gate_count"] < 6:
        errors.append("review_gate_count below 6")
    if checks["checklist_count"] < 8:
        errors.append("checklist_count below 8")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "REAL_SESSION_MANUAL_CAPTURE_RUNBOOK_READY" if status == "PASS" else "REAL_SESSION_MANUAL_CAPTURE_RUNBOOK_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runbook": "product/calibration/real_sessions/manual_capture_runbook_v0_1.md",
        "checklist": "product/calibration/real_sessions/manual_capture_privacy_review_checklist_v0_1.json",
        "step_count": len(STEPS),
        "review_gate_count": len(REVIEW_GATES),
        "checklist_count": len(checklist["checks"]),
        "real_data_captured": False,
        "recommended_next_phase": spec["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3181..3220 Real Session Manual Capture Runbook",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Steps: `{len(STEPS)}`",
        f"- Review gates: `{len(REVIEW_GATES)}`",
        f"- Checklist items: `{len(checklist['checks'])}`",
        f"- Real data captured: `{result['real_data_captured']}`",
        f"- Next: `{spec['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Runbook only.",
        "- No real session data captured.",
        "- No raw private data or secret storage.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("steps:", len(STEPS))
    print("review_gates:", len(REVIEW_GATES))
    print("checklist:", len(checklist["checks"]))
    print("real_data_captured:", result["real_data_captured"])
    print("next:", spec["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

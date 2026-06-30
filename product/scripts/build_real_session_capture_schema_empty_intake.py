#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3141..3180"
REQ_TAG = "product-calibration-plan-real-sessions-v0.1"

PLAN_OUT = ROOT / "outputs/prod3101_3140_calibration_plan_real_sessions.json"
PLAN = ROOT / "product/memory/calibration_plan_real_sessions_v0_1.json"

DOC = ROOT / "docs/product/580_REAL_SESSION_CAPTURE_SCHEMA_EMPTY_INTAKE.md"
CONTRACT = ROOT / "product/contracts/real_session_capture_schema_empty_intake.contract.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"
SPEC = ROOT / "product/memory/real_session_capture_schema_empty_intake_v0_1.json"
EMPTY_INTAKE = ROOT / "product/calibration/real_sessions/real_session_empty_intake_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3141_3180_real_session_capture_schema_empty_intake.json"
OUT_MD = ROOT / "outputs/prod3141_3180_real_session_capture_schema_empty_intake.md"

BLOCKED = [
    "real_session_data_capture_without_review",
    "raw_private_data_storage",
    "secret_or_credential_storage",
    "client_facing_value_claim",
    "real_world_profit_claim",
    "validated_savings_claim",
    "validated_hallucination_reduction_claim",
    "production_activation",
    "automatic_memory_delete",
    "gpt_memory_api_execution"
]

ALLOWED = [
    "empty_intake_creation",
    "schema_definition",
    "sanitized_manual_capture_preparation",
    "human_review_protocol_preparation",
    "calibration_dataset_structure_preparation"
]

REQUIRED_FIELDS = [
    "session_id",
    "capture_status",
    "chat_platform",
    "chat_layer",
    "work_type",
    "baseline_chat_mode",
    "casulo_exocortex_mode",
    "input_quality_score",
    "implementation_complexity_score",
    "operational_cost_score",
    "apex_maturity_score",
    "hallucination_risk_index",
    "value_delta_estimate",
    "rework_count",
    "time_spent_minutes",
    "evidence_pointers",
    "human_reviewer_notes",
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

def main():
    errors = []
    plan_out = read_json(PLAN_OUT) if PLAN_OUT.exists() else {}
    plan = read_json(PLAN) if PLAN.exists() else {}

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Real Session Capture",
        "type": "object",
        "required": REQUIRED_FIELDS,
        "properties": {
            "session_id": {"type": "string"},
            "capture_status": {"type": "string", "enum": ["EMPTY_TEMPLATE", "SANITIZED_DRAFT", "HUMAN_REVIEWED", "REJECTED"]},
            "chat_platform": {"type": "string"},
            "chat_layer": {"type": "string"},
            "work_type": {"type": "string"},
            "baseline_chat_mode": {"type": "string"},
            "casulo_exocortex_mode": {"type": "string"},
            "input_quality_score": {"type": ["number", "null"]},
            "implementation_complexity_score": {"type": ["number", "null"]},
            "operational_cost_score": {"type": ["number", "null"]},
            "apex_maturity_score": {"type": ["number", "null"]},
            "hallucination_risk_index": {"type": ["number", "null"]},
            "value_delta_estimate": {"type": ["number", "null"]},
            "rework_count": {"type": ["integer", "null"]},
            "time_spent_minutes": {"type": ["number", "null"]},
            "evidence_pointers": {"type": "array", "items": {"type": "string"}},
            "human_reviewer_notes": {"type": "array", "items": {"type": "string"}},
            "claim_boundary": {"type": "string"},
            "decision_gate": {"type": "string"},
            "privacy_review_status": {"type": "string"},
            "pii_redaction_status": {"type": "string"},
            "secret_scan_status": {"type": "string"},
            "source_refs_only": {"type": "boolean"}
        }
    }

    empty_intake = {
        "session_id": "EMPTY_TEMPLATE_NO_REAL_SESSION_DATA",
        "capture_status": "EMPTY_TEMPLATE",
        "chat_platform": "",
        "chat_layer": "",
        "work_type": "",
        "baseline_chat_mode": "",
        "casulo_exocortex_mode": "",
        "input_quality_score": None,
        "implementation_complexity_score": None,
        "operational_cost_score": None,
        "apex_maturity_score": None,
        "hallucination_risk_index": None,
        "value_delta_estimate": None,
        "rework_count": None,
        "time_spent_minutes": None,
        "evidence_pointers": [],
        "human_reviewer_notes": [],
        "claim_boundary": "no_claim_empty_template",
        "decision_gate": "HOLD_EMPTY_INTAKE_NOT_REAL_DATA",
        "privacy_review_status": "not_started",
        "pii_redaction_status": "not_applicable_empty_template",
        "secret_scan_status": "not_applicable_empty_template",
        "source_refs_only": True
    }

    spec = {
        "version": "real_session_capture_schema_empty_intake.v0.1",
        "phase": PHASE,
        "purpose": "Create the schema and empty intake template for future sanitized real-session calibration.",
        "required_fields": REQUIRED_FIELDS,
        "empty_intake": "product/calibration/real_sessions/real_session_empty_intake_v0_1.json",
        "privacy_controls": [
            "source_refs_only",
            "pii_redaction_required_before_capture",
            "secret_scan_required_before_capture",
            "human_review_required_before_dataset_acceptance"
        ],
        "calibration_relations": [
            "value_delta_calibration",
            "operational_hallucination_index_calibration",
            "apex_maturity_calibration",
            "cost_decision_metric_calibration",
            "work_type_package_fit_calibration"
        ],
        "claim_boundary": "Schema and empty intake only. No real session data captured in this phase.",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3181..3220 - Real Session Manual Capture Runbook"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "real_session_capture_schema_empty_intake",
        "real_data_captured": False,
        "empty_intake_only": True,
        "human_review_required_before_real_capture": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": spec["recommended_next_phase"]
    }

    doc = """# PROD-3141..3180 - Real Session Capture Schema and Empty Intake

Creates the schema and empty intake template for future sanitized real-session calibration.

No real session data is captured in this phase.

Real captures must be manually reviewed, privacy-checked, PII-redacted and secret-scanned before acceptance.

Boundary: schema and empty intake only. No real-world profit, savings, ROI, client-facing value or validated hallucination-reduction claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(SPEC, spec)
    write_json(EMPTY_INTAKE, empty_intake)

    plan_fields = set(plan.get("session_capture_schema", []))
    required_set = set(REQUIRED_FIELDS)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "plan_output_exists": PLAN_OUT.exists(),
        "plan_output_pass": plan_out.get("status") == "PASS",
        "plan_exists": PLAN.exists(),
        "plan_fields_covered": plan_fields.issubset(required_set),
        "required_field_count": len(REQUIRED_FIELDS),
        "empty_intake_exists": EMPTY_INTAKE.exists(),
        "schema_exists": SCHEMA.exists(),
        "empty_intake_only": contract["empty_intake_only"] is True,
        "real_data_not_captured": contract["real_data_captured"] is False,
        "source_refs_only": empty_intake["source_refs_only"] is True,
        "has_privacy_review": "privacy_review_status" in REQUIRED_FIELDS,
        "has_pii_redaction": "pii_redaction_status" in REQUIRED_FIELDS,
        "has_secret_scan": "secret_scan_status" in REQUIRED_FIELDS,
        "has_value_delta": "value_delta_estimate" in REQUIRED_FIELDS,
        "has_hallucination_index": "hallucination_risk_index" in REQUIRED_FIELDS,
        "has_apex": "apex_maturity_score" in REQUIRED_FIELDS,
        "has_cost": "operational_cost_score" in REQUIRED_FIELDS,
        "blocked_raw_private_data": "raw_private_data_storage" in BLOCKED,
        "blocked_secret_storage": "secret_or_credential_storage" in BLOCKED,
        "blocked_real_capture_without_review": "real_session_data_capture_without_review" in BLOCKED,
        "allowed_empty_intake_creation": "empty_intake_creation" in ALLOWED
    }

    if checks["required_field_count"] < 23:
        errors.append("required_field_count below 23")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "REAL_SESSION_CAPTURE_SCHEMA_EMPTY_INTAKE_READY" if status == "PASS" else "REAL_SESSION_CAPTURE_SCHEMA_EMPTY_INTAKE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "schema": "product/schemas/real_session_capture.schema.json",
        "empty_intake": "product/calibration/real_sessions/real_session_empty_intake_v0_1.json",
        "required_field_count": len(REQUIRED_FIELDS),
        "real_data_captured": False,
        "recommended_next_phase": spec["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3141..3180 Real Session Capture Schema and Empty Intake",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Required fields: `{len(REQUIRED_FIELDS)}`",
        f"- Real data captured: `{result['real_data_captured']}`",
        f"- Next: `{spec['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Empty intake only.",
        "- No real session data captured.",
        "- Privacy review, PII redaction and secret scan required before real capture.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("required_fields:", len(REQUIRED_FIELDS))
    print("real_data_captured:", result["real_data_captured"])
    print("next:", spec["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

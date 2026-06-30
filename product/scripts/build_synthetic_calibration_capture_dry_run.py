#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3261..3300"
REQ_TAG = "product-real-session-intake-validator-empty-batch-audit-v0.1"

PREV_OUT = ROOT / "outputs/prod3221_3260_real_session_intake_validator_empty_batch_audit.json"
SCHEMA = ROOT / "product/schemas/real_session_capture.schema.json"
EMPTY_BATCH = ROOT / "product/calibration/real_sessions/real_session_empty_batch_manifest_v0_1.json"
PLAN = ROOT / "product/memory/calibration_plan_real_sessions_v0_1.json"
MATRIX = ROOT / "product/memory/expanded_test_matrix_pack_v0_1.json"

DOC = ROOT / "docs/product/583_SYNTHETIC_CALIBRATION_CAPTURE_DRY_RUN.md"
CONTRACT = ROOT / "product/contracts/synthetic_calibration_capture_dry_run.contract.json"
SPEC = ROOT / "product/memory/synthetic_calibration_capture_dry_run_v0_1.json"
BATCH = ROOT / "product/calibration/synthetic_sessions/synthetic_calibration_dry_run_batch_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3261_3300_synthetic_calibration_capture_dry_run.json"
OUT_MD = ROOT / "outputs/prod3261_3300_synthetic_calibration_capture_dry_run.md"

BLOCKED = [
    "real_session_data_capture",
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
    "synthetic_dry_run_capture",
    "schema_field_validation",
    "synthetic_batch_scoring",
    "calibration_pipeline_dry_run",
    "human_review_simulation"
]

SYNTHETIC_CASES = [
    {
        "id": "SYN-CAL-001",
        "chat_layer": "ANALYSIS_CHAT",
        "work_type": "diagnostic_analysis",
        "input_quality": 88,
        "complexity": 28,
        "cost": 35,
        "apex": 82,
        "hallucination": 18,
        "value_delta": 62,
        "rework": 1,
        "minutes": 42,
        "gate": "ACCEPT_SYNTHETIC_DRY_RUN"
    },
    {
        "id": "SYN-CAL-002",
        "chat_layer": "PROJECT_CHAT",
        "work_type": "project_design",
        "input_quality": 72,
        "complexity": 56,
        "cost": 54,
        "apex": 68,
        "hallucination": 36,
        "value_delta": 70,
        "rework": 2,
        "minutes": 85,
        "gate": "ACCEPT_SYNTHETIC_DRY_RUN"
    },
    {
        "id": "SYN-CAL-003",
        "chat_layer": "IMPLEMENTATION_CHAT",
        "work_type": "repo_implementation",
        "input_quality": 64,
        "complexity": 82,
        "cost": 77,
        "apex": 55,
        "hallucination": 61,
        "value_delta": 78,
        "rework": 4,
        "minutes": 130,
        "gate": "HOLD_SYNTHETIC_COMPLEXITY_REVIEW"
    },
    {
        "id": "SYN-CAL-004",
        "chat_layer": "GOVERNANCE_CHAT",
        "work_type": "governance_review",
        "input_quality": 76,
        "complexity": 62,
        "cost": 69,
        "apex": 66,
        "hallucination": 42,
        "value_delta": 73,
        "rework": 2,
        "minutes": 95,
        "gate": "HOLD_SYNTHETIC_EVIDENCE_REVIEW"
    },
    {
        "id": "SYN-CAL-005",
        "chat_layer": "CALIBRATION_CHAT",
        "work_type": "calibration_benchmark",
        "input_quality": 58,
        "complexity": 78,
        "cost": 74,
        "apex": 52,
        "hallucination": 68,
        "value_delta": 84,
        "rework": 5,
        "minutes": 150,
        "gate": "HOLD_SYNTHETIC_CALIBRATION_REVIEW"
    },
    {
        "id": "SYN-CAL-006",
        "chat_layer": "OPERATIONS_CHAT",
        "work_type": "operational_cockpit",
        "input_quality": 80,
        "complexity": 70,
        "cost": 71,
        "apex": 72,
        "hallucination": 34,
        "value_delta": 88,
        "rework": 2,
        "minutes": 110,
        "gate": "ACCEPT_SYNTHETIC_DRY_RUN"
    },
    {
        "id": "SYN-CAL-007",
        "chat_layer": "INTEGRATION_CHAT",
        "work_type": "system_integration",
        "input_quality": 52,
        "complexity": 90,
        "cost": 86,
        "apex": 45,
        "hallucination": 76,
        "value_delta": 91,
        "rework": 6,
        "minutes": 180,
        "gate": "BLOCK_SYNTHETIC_RISK_TOO_HIGH"
    },
    {
        "id": "SYN-CAL-008",
        "chat_layer": "EVIDENCE_AUDIT_CHAT",
        "work_type": "evidence_audit",
        "input_quality": 84,
        "complexity": 58,
        "cost": 66,
        "apex": 74,
        "hallucination": 28,
        "value_delta": 79,
        "rework": 1,
        "minutes": 100,
        "gate": "ACCEPT_SYNTHETIC_DRY_RUN"
    }
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

def to_record(c):
    return {
        "session_id": c["id"],
        "capture_status": "HUMAN_REVIEWED",
        "chat_platform": "SYNTHETIC_NO_REAL_PLATFORM",
        "chat_layer": c["chat_layer"],
        "work_type": c["work_type"],
        "baseline_chat_mode": "PURE_CHAT_BASELINE_SYNTHETIC",
        "casulo_exocortex_mode": "CASULO_EXOCORTEX_ASSISTED_SYNTHETIC",
        "input_quality_score": c["input_quality"],
        "implementation_complexity_score": c["complexity"],
        "operational_cost_score": c["cost"],
        "apex_maturity_score": c["apex"],
        "hallucination_risk_index": c["hallucination"],
        "value_delta_estimate": c["value_delta"],
        "rework_count": c["rework"],
        "time_spent_minutes": c["minutes"],
        "evidence_pointers": [
            "synthetic://calibration_dry_run/" + c["id"]
        ],
        "human_reviewer_notes": [
            "Synthetic reviewer simulation only. No real data."
        ],
        "claim_boundary": "synthetic_dry_run_only_no_real_claim",
        "decision_gate": c["gate"],
        "privacy_review_status": "not_applicable_synthetic",
        "pii_redaction_status": "not_applicable_synthetic_no_pii",
        "secret_scan_status": "not_applicable_synthetic_no_secrets",
        "source_refs_only": True
    }

def validate_record(record, required_fields):
    errors = []
    for field in required_fields:
        if field not in record:
            errors.append(record.get("session_id", "unknown") + " missing " + field)
    if record.get("source_refs_only") is not True:
        errors.append(record["session_id"] + " source_refs_only false")
    if not str(record.get("claim_boundary", "")).startswith("synthetic_dry_run_only"):
        errors.append(record["session_id"] + " invalid claim boundary")
    if record.get("privacy_review_status") != "not_applicable_synthetic":
        errors.append(record["session_id"] + " invalid privacy review status")
    return errors

def main():
    errors = []
    prev_out = read_json(PREV_OUT) if PREV_OUT.exists() else {}
    schema = read_json(SCHEMA) if SCHEMA.exists() else {}
    empty_batch = read_json(EMPTY_BATCH) if EMPTY_BATCH.exists() else {}
    plan = read_json(PLAN) if PLAN.exists() else {}
    matrix = read_json(MATRIX) if MATRIX.exists() else {}

    required_fields = schema.get("required", [])
    records = [to_record(c) for c in SYNTHETIC_CASES]

    record_errors = []
    for r in records:
        record_errors.extend(validate_record(r, required_fields))

    accepted = [r for r in records if r["decision_gate"] == "ACCEPT_SYNTHETIC_DRY_RUN"]
    held = [r for r in records if r["decision_gate"].startswith("HOLD_")]
    blocked = [r for r in records if r["decision_gate"].startswith("BLOCK_")]

    avg_apex = round(sum(r["apex_maturity_score"] for r in records) / len(records), 2)
    avg_hallucination = round(sum(r["hallucination_risk_index"] for r in records) / len(records), 2)
    avg_cost = round(sum(r["operational_cost_score"] for r in records) / len(records), 2)
    avg_value_delta = round(sum(r["value_delta_estimate"] for r in records) / len(records), 2)

    batch = {
        "version": "synthetic_calibration_dry_run_batch.v0.1",
        "phase": PHASE,
        "batch_id": "SYNTHETIC-CALIBRATION-DRY-RUN-001",
        "batch_status": "SYNTHETIC_DRY_RUN_REVIEWED",
        "real_data_captured": False,
        "record_count": len(records),
        "records": records,
        "summary": {
            "accepted_count": len(accepted),
            "held_count": len(held),
            "blocked_count": len(blocked),
            "average_apex_maturity_score": avg_apex,
            "average_hallucination_risk_index": avg_hallucination,
            "average_operational_cost_score": avg_cost,
            "average_value_delta_estimate": avg_value_delta
        },
        "claim_boundary": "synthetic calibration dry run only no real-world claim",
        "blocked_actions": BLOCKED
    }

    spec = {
        "version": "synthetic_calibration_capture_dry_run.v0.1",
        "phase": PHASE,
        "purpose": "Run a synthetic dry run through the real-session capture schema without capturing real data.",
        "real_data_captured": False,
        "synthetic_record_count": len(records),
        "dry_run_batch": "product/calibration/synthetic_sessions/synthetic_calibration_dry_run_batch_v0_1.json",
        "calibration_axes_tested": [
            "value_delta_calibration",
            "operational_hallucination_index_calibration",
            "apex_maturity_calibration",
            "input_quality_calibration",
            "implementation_complexity_calibration",
            "cost_decision_metric_calibration",
            "work_type_package_fit_calibration"
        ],
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3301..3340 - Synthetic Calibration Dry Run Evaluator"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "synthetic_calibration_capture_dry_run",
        "real_data_captured": False,
        "synthetic_only": True,
        "schema_validation_required": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": spec["recommended_next_phase"]
    }

    doc = """# PROD-3261..3300 - Synthetic Calibration Capture Dry Run

Runs a synthetic dry run through the real-session capture schema.

This phase uses synthetic records only. No real session data is captured.

The dry run tests schema compatibility, scoring fields, gates, batch structure and calibration pipeline readiness.

Boundary: synthetic dry run only. No real-world profit, savings, ROI, client-facing value or validated hallucination-reduction claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SPEC, spec)
    write_json(BATCH, batch)

    gates = {r["decision_gate"] for r in records}
    layers = {r["chat_layer"] for r in records}
    work_types = {r["work_type"] for r in records}

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev_out.get("status") == "PASS",
        "previous_record_count_zero": prev_out.get("record_count") == 0,
        "schema_exists": SCHEMA.exists(),
        "empty_batch_exists": EMPTY_BATCH.exists(),
        "plan_exists": PLAN.exists(),
        "matrix_exists": MATRIX.exists(),
        "empty_batch_no_real_data": empty_batch.get("real_data_captured") is False,
        "plan_minimum_sessions_present": plan.get("minimum_viable_calibration_sessions", 0) >= 30,
        "matrix_case_count_present": matrix.get("case_count", 0) >= 48,
        "required_field_count": len(required_fields),
        "record_count": len(records),
        "record_errors_empty": len(record_errors) == 0,
        "real_data_not_captured": contract["real_data_captured"] is False,
        "synthetic_only": contract["synthetic_only"] is True,
        "has_accept_gate": "ACCEPT_SYNTHETIC_DRY_RUN" in gates,
        "has_hold_gate": any(g.startswith("HOLD_") for g in gates),
        "has_block_gate": any(g.startswith("BLOCK_") for g in gates),
        "layer_count": len(layers),
        "work_type_count": len(work_types),
        "avg_apex_positive": avg_apex > 0,
        "avg_hallucination_positive": avg_hallucination > 0,
        "avg_cost_positive": avg_cost > 0,
        "avg_value_delta_positive": avg_value_delta > 0,
        "blocked_real_session_capture": "real_session_data_capture" in BLOCKED,
        "blocked_raw_private_storage": "raw_private_data_storage" in BLOCKED,
        "blocked_secret_storage": "secret_or_credential_storage" in BLOCKED,
        "blocked_validated_claim": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["required_field_count"] < 23:
        errors.append("required_field_count below 23")
    if checks["record_count"] < 8:
        errors.append("record_count below 8")
    if checks["layer_count"] < 6:
        errors.append("layer_count below 6")
    if checks["work_type_count"] < 6:
        errors.append("work_type_count below 6")
    if record_errors:
        errors.extend(record_errors)
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "SYNTHETIC_CALIBRATION_CAPTURE_DRY_RUN_READY" if status == "PASS" else "SYNTHETIC_CALIBRATION_CAPTURE_DRY_RUN_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "batch": "product/calibration/synthetic_sessions/synthetic_calibration_dry_run_batch_v0_1.json",
        "record_count": len(records),
        "real_data_captured": False,
        "average_apex_maturity_score": avg_apex,
        "average_hallucination_risk_index": avg_hallucination,
        "average_operational_cost_score": avg_cost,
        "average_value_delta_estimate": avg_value_delta,
        "recommended_next_phase": spec["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3261..3300 Synthetic Calibration Capture Dry Run",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Records: `{len(records)}`",
        f"- Real data captured: `{result['real_data_captured']}`",
        f"- Average Apex: `{avg_apex}`",
        f"- Average hallucination risk: `{avg_hallucination}`",
        f"- Average operational cost: `{avg_cost}`",
        f"- Average Value Delta: `{avg_value_delta}`",
        f"- Next: `{spec['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Synthetic dry run only.",
        "- No real session data captured.",
        "- No validated real-world claim.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("records:", len(records))
    print("real_data_captured:", result["real_data_captured"])
    print("avg_apex:", avg_apex)
    print("avg_hallucination:", avg_hallucination)
    print("avg_cost:", avg_cost)
    print("avg_value_delta:", avg_value_delta)
    print("next:", spec["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

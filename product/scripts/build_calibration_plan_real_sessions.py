#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3101..3140"
REQ_TAG = "product-work-type-package-optimizer-cost-decision-v0.1"

OPT_OUT = ROOT / "outputs/prod3061_3100_work_type_package_optimizer_cost_decision.json"
OPTIMIZER = ROOT / "product/memory/work_type_package_optimizer_cost_decision_v0_1.json"
APEX = ROOT / "product/memory/exocortex_apex_maturity_index_v0_1.json"
VALUE_GATE = ROOT / "product/memory/value_delta_readiness_gate_v0_1.json"
TEST_MATRIX = ROOT / "product/memory/expanded_test_matrix_pack_v0_1.json"

DOC = ROOT / "docs/product/579_CALIBRATION_PLAN_FOR_REAL_SESSIONS.md"
CONTRACT = ROOT / "product/contracts/calibration_plan_real_sessions.contract.json"
SCHEMA = ROOT / "product/schemas/calibration_plan_real_sessions.schema.json"
PLAN = ROOT / "product/memory/calibration_plan_real_sessions_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3101_3140_calibration_plan_real_sessions.json"
OUT_MD = ROOT / "outputs/prod3101_3140_calibration_plan_real_sessions.md"

CALIBRATION_AXES = [
    "value_delta_calibration",
    "operational_hallucination_index_calibration",
    "apex_maturity_calibration",
    "input_quality_calibration",
    "implementation_complexity_calibration",
    "cost_decision_metric_calibration",
    "work_type_package_fit_calibration",
    "chat_structure_coherence_calibration",
    "memory_snapshot_recovery_calibration",
    "rework_avoidance_calibration"
]

SESSION_FIELDS = [
    "session_id",
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
    "decision_gate"
]

BATCHES = [
    {"name": "pilot", "target_sessions": 10, "purpose": "Validate capture schema and reviewer protocol."},
    {"name": "batch_001", "target_sessions": 30, "purpose": "Initial controlled calibration by work type."},
    {"name": "benchmark_001", "target_sessions": 60, "purpose": "Expand comparison across chat layers and complexity."},
    {"name": "strong_internal_calibration", "target_sessions": 150, "purpose": "Internal evidence base before any external claim review."}
]

COMPARISON_MODES = [
    "PURE_CHAT_BASELINE",
    "CASULO_EXOCORTEX_ASSISTED",
    "CASULO_EXOCORTEX_WITH_SNAPSHOT",
    "CASULO_EXOCORTEX_WITH_INPUT_QUALITY_GATE",
    "CASULO_EXOCORTEX_WITH_VALUE_DELTA",
    "CASULO_EXOCORTEX_WITH_COST_DECISION"
]

BLOCKED = [
    "real_world_profit_claim",
    "validated_savings_claim",
    "client_facing_value_claim",
    "validated_hallucination_reduction_claim",
    "production_activation",
    "automatic_memory_delete",
    "gpt_memory_api_execution",
    "commercial_package_pricing_claim"
]

ALLOWED = [
    "real_session_capture_plan",
    "internal_controlled_calibration",
    "human_review_protocol_design",
    "baseline_vs_exocortex_comparison_design",
    "calibration_dataset_schema_design"
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
    opt_out = read_json(OPT_OUT) if OPT_OUT.exists() else {}
    optimizer = read_json(OPTIMIZER) if OPTIMIZER.exists() else {}
    apex = read_json(APEX) if APEX.exists() else {}
    value_gate = read_json(VALUE_GATE) if VALUE_GATE.exists() else {}
    test_matrix = read_json(TEST_MATRIX) if TEST_MATRIX.exists() else {}

    plan = {
        "version": "calibration_plan_real_sessions.v0.1",
        "phase": PHASE,
        "purpose": "Define controlled real-session calibration plan for CASULO Exocortex, without external claims.",
        "calibration_axes": CALIBRATION_AXES,
        "session_capture_schema": SESSION_FIELDS,
        "comparison_modes": COMPARISON_MODES,
        "batches": BATCHES,
        "minimum_viable_calibration_sessions": 30,
        "recommended_internal_benchmark_sessions": 60,
        "strong_internal_calibration_sessions": 150,
        "review_protocol": {
            "human_review_required": True,
            "reviewer_must_score": [
                "correctness",
                "decision_recall",
                "state_grounding",
                "hallucination_event",
                "claim_boundary_respected",
                "rework_avoided",
                "cost_decision_validity",
                "package_fit_validity"
            ],
            "evidence_required": [
                "prompt_or_request",
                "baseline_output",
                "casulo_output",
                "snapshot_or_state_pointer",
                "manual_reviewer_note",
                "decision_gate"
            ]
        },
        "cost_as_operational_metric": {
            "required": True,
            "rule": "Cost must influence operational gate, package fit, execution readiness and calibration confidence."
        },
        "apex_relation": {
            "required": True,
            "rule": "Apex maturity score is a calibration signal for system potency and Value Delta confidence."
        },
        "hallucination_relation": {
            "required": True,
            "rule": "Operational hallucination index must be calibrated against input quality, complexity, cost, stale context and Apex maturity."
        },
        "package_relation": {
            "required": True,
            "rule": "Work type and chat structure must be preserved when calibrating package fit."
        },
        "claim_boundary": "Calibration plan only. No validated real-world savings, ROI, profit, client-facing value or hallucination-reduction claim.",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3141..3180 - Real Session Capture Schema and Empty Intake"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "calibration_plan_real_sessions",
        "real_session_capture_planned": True,
        "human_review_required": True,
        "cost_is_operational_decision_metric": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": plan["recommended_next_phase"]
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Calibration Plan for Real Sessions",
        "type": "object",
        "required": ["version", "phase", "calibration_axes", "session_capture_schema", "comparison_modes", "batches"]
    }

    doc = """# PROD-3101..3140 - Calibration Plan for Real Sessions

Defines the controlled real-session calibration plan for CASULO Exocortex.

The plan calibrates Value Delta, operational hallucination risk, Apex Maturity, input quality, implementation complexity, cost decision metrics, package fit, chat structure coherence, snapshot recovery and rework avoidance.

Cost is treated as an operational decision metric.

Boundary: calibration plan only. No real-world profit, savings, ROI, client-facing value or validated hallucination-reduction claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(PLAN, plan)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "optimizer_output_exists": OPT_OUT.exists(),
        "optimizer_output_pass": opt_out.get("status") == "PASS",
        "optimizer_exists": OPTIMIZER.exists(),
        "apex_exists": APEX.exists(),
        "value_gate_exists": VALUE_GATE.exists(),
        "test_matrix_exists": TEST_MATRIX.exists(),
        "optimizer_cost_metric_ready": optimizer.get("principle") == "Cost is an operational decision metric.",
        "apex_relation_exists": apex.get("value_delta_relation", {}).get("required") is True,
        "hallucination_correlation_registered": value_gate.get("hallucination_index_correlation_extension", {}).get("name") == "implementation_complexity_hallucination_correlation",
        "test_matrix_case_count": test_matrix.get("case_count", 0),
        "axis_count": len(CALIBRATION_AXES),
        "session_field_count": len(SESSION_FIELDS),
        "batch_count": len(BATCHES),
        "comparison_mode_count": len(COMPARISON_MODES),
        "has_value_delta_axis": "value_delta_calibration" in CALIBRATION_AXES,
        "has_hallucination_axis": "operational_hallucination_index_calibration" in CALIBRATION_AXES,
        "has_apex_axis": "apex_maturity_calibration" in CALIBRATION_AXES,
        "has_cost_axis": "cost_decision_metric_calibration" in CALIBRATION_AXES,
        "has_package_axis": "work_type_package_fit_calibration" in CALIBRATION_AXES,
        "has_baseline_mode": "PURE_CHAT_BASELINE" in COMPARISON_MODES,
        "has_exocortex_mode": "CASULO_EXOCORTEX_ASSISTED" in COMPARISON_MODES,
        "human_review_required": contract["human_review_required"] is True,
        "cost_metric_required": plan["cost_as_operational_metric"]["required"] is True,
        "blocked_profit_claim": "real_world_profit_claim" in BLOCKED,
        "blocked_savings_claim": "validated_savings_claim" in BLOCKED,
        "blocked_hallucination_claim": "validated_hallucination_reduction_claim" in BLOCKED,
        "allowed_capture_plan": "real_session_capture_plan" in ALLOWED
    }

    if checks["axis_count"] < 10:
        errors.append("axis_count below 10")
    if checks["session_field_count"] < 18:
        errors.append("session_field_count below 18")
    if checks["batch_count"] < 4:
        errors.append("batch_count below 4")
    if checks["comparison_mode_count"] < 6:
        errors.append("comparison_mode_count below 6")
    if checks["test_matrix_case_count"] < 48:
        errors.append("test_matrix_case_count below 48")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "CALIBRATION_PLAN_REAL_SESSIONS_READY" if status == "PASS" else "CALIBRATION_PLAN_REAL_SESSIONS_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "plan": "product/memory/calibration_plan_real_sessions_v0_1.json",
        "axis_count": len(CALIBRATION_AXES),
        "session_field_count": len(SESSION_FIELDS),
        "comparison_mode_count": len(COMPARISON_MODES),
        "minimum_viable_calibration_sessions": plan["minimum_viable_calibration_sessions"],
        "recommended_internal_benchmark_sessions": plan["recommended_internal_benchmark_sessions"],
        "strong_internal_calibration_sessions": plan["strong_internal_calibration_sessions"],
        "recommended_next_phase": plan["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3101..3140 Calibration Plan for Real Sessions",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Calibration axes: `{len(CALIBRATION_AXES)}`",
        f"- Session fields: `{len(SESSION_FIELDS)}`",
        f"- Comparison modes: `{len(COMPARISON_MODES)}`",
        f"- Minimum viable sessions: `{plan['minimum_viable_calibration_sessions']}`",
        f"- Recommended benchmark sessions: `{plan['recommended_internal_benchmark_sessions']}`",
        f"- Strong internal calibration sessions: `{plan['strong_internal_calibration_sessions']}`",
        f"- Next: `{plan['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Calibration plan only.",
        "- No real-world profit/savings/ROI claim.",
        "- No validated hallucination-reduction claim.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("axes:", len(CALIBRATION_AXES))
    print("session_fields:", len(SESSION_FIELDS))
    print("comparison_modes:", len(COMPARISON_MODES))
    print("minimum_sessions:", plan["minimum_viable_calibration_sessions"])
    print("next:", plan["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

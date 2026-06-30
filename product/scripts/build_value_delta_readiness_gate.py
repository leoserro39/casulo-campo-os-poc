#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2941..2980"
REQ_TAG = "product-value-delta-evaluator-v0.1"

EVAL_OUT = ROOT / "outputs/prod2901_2940_value_delta_evaluator.json"
EVALUATOR = ROOT / "product/memory/value_delta_evaluator_v0_1.json"
PACK = ROOT / "product/memory/value_delta_synthetic_fixture_pack_v0_1.json"

DOC = ROOT / "docs/product/575_VALUE_DELTA_READINESS_GATE.md"
CONTRACT = ROOT / "product/contracts/value_delta_readiness_gate.contract.json"
SCHEMA = ROOT / "product/schemas/value_delta_readiness_gate.schema.json"
GATE = ROOT / "product/memory/value_delta_readiness_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod2941_2980_value_delta_readiness_gate.json"
OUT_MD = ROOT / "outputs/prod2941_2980_value_delta_readiness_gate.md"

BLOCKED = [
    "real_world_profit_claim",
    "validated_savings_claim",
    "client_facing_value_claim",
    "production_activation",
    "automatic_memory_delete",
    "gpt_memory_api_execution",
    "value_delta_claim_with_low_input_quality",
    "validated_hallucination_reduction_claim"
]

ALLOWED = [
    "internal_synthetic_value_delta_discussion",
    "controlled_benchmark_planning",
    "calibration_plan_design",
    "expanded_test_matrix_design",
    "hallucination_complexity_correlation_study_design"
]

CORRELATION_METRICS = [
    "implementation_complexity_score",
    "integration_difficulty_score",
    "change_management_complexity",
    "evidence_collection_effort",
    "input_quality_outcome",
    "confidence_score",
    "hallucination_risk_avoided_value",
    "claim_leakage_avoided_value",
    "operational_risk_avoided_value",
    "complexity_adjusted_net_value_delta"
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

def correlation_preview(rows):
    preview = []
    for r in rows:
        complexity = float(r.get("implementation_complexity_score", 0))
        confidence = float(r.get("confidence_score", 0))
        input_outcome = r.get("input_quality_outcome")
        hallucination_value = float(r.get("hallucination_risk_avoided_value", 0))
        claim_leakage = float(r.get("claim_leakage_avoided_value", 0))
        operational_risk = float(r.get("operational_risk_avoided_value", 0))

        input_penalty = {
            "INPUT_ACCEPTED": 0,
            "CLARIFICATION_REQUIRED": 20,
            "EVIDENCE_REQUIRED": 30,
            "SCHEMA_REQUIRED": 30,
            "BLOCK_EXECUTION": 50
        }.get(input_outcome, 25)

        correlation_risk_score = round(
            (complexity * 0.35)
            + (input_penalty * 0.30)
            + ((1 - confidence) * 100 * 0.20)
            + ((hallucination_value + claim_leakage + operational_risk) / 20 * 0.15),
            2
        )

        if correlation_risk_score >= 70:
            band = "HIGH_CORRELATION_RISK"
        elif correlation_risk_score >= 45:
            band = "MEDIUM_CORRELATION_RISK"
        else:
            band = "LOW_CORRELATION_RISK"

        preview.append({
            "id": r.get("id"),
            "title": r.get("title"),
            "input_quality_outcome": input_outcome,
            "implementation_complexity_score": complexity,
            "confidence_score": confidence,
            "correlation_risk_score": correlation_risk_score,
            "correlation_band": band,
            "note": "Synthetic correlation preview only. Calibration required."
        })
    return preview

def main():
    errors = []
    eval_out = read_json(EVAL_OUT) if EVAL_OUT.exists() else {}
    evaluator = read_json(EVALUATOR) if EVALUATOR.exists() else {}
    pack = read_json(PACK) if PACK.exists() else {}

    rows = evaluator.get("evaluated_cases", [])
    correlation = correlation_preview(rows)

    summary = evaluator.get("summary", {})
    freezable_value = float(summary.get("freezable_internal_synthetic_value", 0))
    freeze_count = int(summary.get("freeze_allowed_count", 0))
    blocked_count = int(summary.get("blocked_count", 0))
    provisional_count = int(summary.get("provisional_count", 0))
    avg_complexity = float(summary.get("average_implementation_complexity_score", 0))

    readiness_decision = "APPROVED_FOR_INTERNAL_SYNTHETIC_BENCHMARK_ONLY"
    if freezable_value <= 0 or freeze_count <= 0:
        readiness_decision = "NOT_READY_FOR_VALUE_DELTA_BENCHMARK"
    if blocked_count <= 0 or provisional_count <= 0:
        readiness_decision = "NOT_READY_MISSING_GUARDRAIL_COVERAGE"

    gate = {
        "version": "value_delta_readiness_gate.v0.1",
        "phase": PHASE,
        "decision": readiness_decision,
        "scope": "internal synthetic benchmark only",
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "readiness_summary": {
            "fixture_count": summary.get("fixture_count", len(rows)),
            "freeze_allowed_count": freeze_count,
            "blocked_count": blocked_count,
            "provisional_count": provisional_count,
            "freezable_internal_synthetic_value": freezable_value,
            "average_implementation_complexity_score": avg_complexity
        },
        "hallucination_index_correlation_extension": {
            "required": True,
            "name": "implementation_complexity_hallucination_correlation",
            "metrics": CORRELATION_METRICS,
            "rule": "High complexity plus weak input quality increases operational hallucination risk and lowers Value Delta confidence.",
            "calibration_status": "planned_not_validated"
        },
        "correlation_preview": correlation,
        "claim_boundary": "No real-world profit, savings, ROI or hallucination-reduction claim is allowed.",
        "recommended_next_phase": "PROD-2981..3020 - Expanded Test Matrix Pack"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "value_delta_readiness_gate",
        "readiness_decision": readiness_decision,
        "complexity_hallucination_correlation_required": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Value Delta Readiness Gate",
        "type": "object",
        "required": ["version", "phase", "decision", "readiness_summary", "hallucination_index_correlation_extension"]
    }

    doc = """# PROD-2941..2980 - Value Delta Readiness Gate

Defines the readiness boundary for the CASULO Exocortex Value Delta Engine.

This gate allows internal synthetic benchmark discussion only.

It blocks real-world profit, savings, ROI, client-facing value and validated hallucination-reduction claims.

It also registers implementation complexity as a required correlation dimension for the operational hallucination index.

Boundary: readiness gate only. Calibration is still required.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(GATE, gate)

    bands = {c["correlation_band"] for c in correlation}

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "evaluator_output_exists": EVAL_OUT.exists(),
        "evaluator_output_pass": eval_out.get("status") == "PASS",
        "evaluator_exists": EVALUATOR.exists(),
        "pack_exists": PACK.exists(),
        "fixture_count": len(rows),
        "freeze_count_positive": freeze_count > 0,
        "blocked_count_positive": blocked_count > 0,
        "provisional_count_positive": provisional_count > 0,
        "freezable_value_positive": freezable_value > 0,
        "avg_complexity_positive": avg_complexity > 0,
        "correlation_metric_count": len(CORRELATION_METRICS),
        "correlation_preview_count": len(correlation),
        "correlation_preview_matches_fixture_count": len(correlation) == len(rows),
        "has_high_or_medium_correlation_band": "HIGH_CORRELATION_RISK" in bands or "MEDIUM_CORRELATION_RISK" in bands,
        "has_implementation_complexity_metric": "implementation_complexity_score" in CORRELATION_METRICS,
        "has_input_quality_metric": "input_quality_outcome" in CORRELATION_METRICS,
        "has_hallucination_metric": "hallucination_risk_avoided_value" in CORRELATION_METRICS,
        "has_claim_leakage_metric": "claim_leakage_avoided_value" in CORRELATION_METRICS,
        "blocked_real_profit_claim": "real_world_profit_claim" in BLOCKED,
        "blocked_validated_savings_claim": "validated_savings_claim" in BLOCKED,
        "blocked_client_value_claim": "client_facing_value_claim" in BLOCKED,
        "blocked_hallucination_reduction_claim": "validated_hallucination_reduction_claim" in BLOCKED,
        "allowed_internal_only": "internal_synthetic_value_delta_discussion" in ALLOWED,
        "decision_internal_only": readiness_decision == "APPROVED_FOR_INTERNAL_SYNTHETIC_BENCHMARK_ONLY"
    }

    if checks["fixture_count"] < 12:
        errors.append("fixture_count below 12")
    if checks["correlation_metric_count"] < 10:
        errors.append("correlation_metric_count below 10")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": readiness_decision if status == "PASS" else "VALUE_DELTA_READINESS_GATE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gate": "product/memory/value_delta_readiness_gate_v0_1.json",
        "fixture_count": len(rows),
        "freezable_internal_synthetic_value": freezable_value,
        "average_implementation_complexity_score": avg_complexity,
        "correlation_metric_count": len(CORRELATION_METRICS),
        "correlation_preview_count": len(correlation),
        "recommended_next_phase": gate["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2941..2980 Value Delta Readiness Gate",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Fixtures: `{len(rows)}`",
        f"- Freezable internal synthetic value: `{freezable_value}`",
        f"- Average implementation complexity: `{avg_complexity}`",
        f"- Correlation metrics: `{len(CORRELATION_METRICS)}`",
        f"- Next: `{gate['recommended_next_phase']}`",
        "",
        "## Correlation extension",
        "- implementation_complexity_hallucination_correlation registered.",
        "- Calibration status: planned_not_validated.",
        "",
        "## Boundary",
        "- Internal synthetic benchmark only.",
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
    print("fixtures:", len(rows))
    print("freezable_value:", freezable_value)
    print("avg_complexity:", avg_complexity)
    print("correlation_metrics:", len(CORRELATION_METRICS))
    print("next:", gate["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
import math
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3301..3340"
REQ_TAG = "product-synthetic-calibration-capture-dry-run-v0.1"

PREV_OUT = ROOT / "outputs/prod3261_3300_synthetic_calibration_capture_dry_run.json"
BATCH = ROOT / "product/calibration/synthetic_sessions/synthetic_calibration_dry_run_batch_v0_1.json"
PLAN = ROOT / "product/memory/calibration_plan_real_sessions_v0_1.json"
APEX = ROOT / "product/memory/exocortex_apex_maturity_index_v0_1.json"
OPTIMIZER = ROOT / "product/memory/work_type_package_optimizer_cost_decision_v0_1.json"

DOC = ROOT / "docs/product/584_SYNTHETIC_CALIBRATION_DRY_RUN_EVALUATOR.md"
CONTRACT = ROOT / "product/contracts/synthetic_calibration_dry_run_evaluator.contract.json"
SPEC = ROOT / "product/memory/synthetic_calibration_dry_run_evaluator_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3301_3340_synthetic_calibration_dry_run_evaluator.json"
OUT_MD = ROOT / "outputs/prod3301_3340_synthetic_calibration_dry_run_evaluator.md"

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
    "synthetic_dry_run_evaluation",
    "synthetic_correlation_analysis",
    "gate_distribution_analysis",
    "calibration_readiness_scoring",
    "next_gate_preparation"
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

def corr(xs, ys):
    if len(xs) != len(ys) or len(xs) < 2:
        return 0.0
    mx = sum(xs) / len(xs)
    my = sum(ys) / len(ys)
    num = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    denx = math.sqrt(sum((x - mx) ** 2 for x in xs))
    deny = math.sqrt(sum((y - my) ** 2 for y in ys))
    if denx == 0 or deny == 0:
        return 0.0
    return round(num / (denx * deny), 4)

def readiness_band(score):
    if score >= 80:
        return "SYNTHETIC_READY_STRONG"
    if score >= 65:
        return "SYNTHETIC_READY_WITH_REVIEW"
    if score >= 50:
        return "SYNTHETIC_PARTIAL_READY"
    return "SYNTHETIC_NOT_READY"

def main():
    errors = []
    prev_out = read_json(PREV_OUT) if PREV_OUT.exists() else {}
    batch = read_json(BATCH) if BATCH.exists() else {}
    plan = read_json(PLAN) if PLAN.exists() else {}
    apex = read_json(APEX) if APEX.exists() else {}
    optimizer = read_json(OPTIMIZER) if OPTIMIZER.exists() else {}

    records = batch.get("records", [])

    apex_scores = [float(r.get("apex_maturity_score", 0)) for r in records]
    hallucination_scores = [float(r.get("hallucination_risk_index", 0)) for r in records]
    cost_scores = [float(r.get("operational_cost_score", 0)) for r in records]
    value_scores = [float(r.get("value_delta_estimate", 0)) for r in records]
    complexity_scores = [float(r.get("implementation_complexity_score", 0)) for r in records]
    input_scores = [float(r.get("input_quality_score", 0)) for r in records]
    rework_counts = [float(r.get("rework_count", 0)) for r in records]

    gates = [r.get("decision_gate", "") for r in records]
    accepted = [g for g in gates if g == "ACCEPT_SYNTHETIC_DRY_RUN"]
    held = [g for g in gates if g.startswith("HOLD_")]
    blocked = [g for g in gates if g.startswith("BLOCK_")]

    c_apex_hallucination = corr(apex_scores, hallucination_scores)
    c_complexity_hallucination = corr(complexity_scores, hallucination_scores)
    c_cost_hallucination = corr(cost_scores, hallucination_scores)
    c_input_hallucination = corr(input_scores, hallucination_scores)
    c_apex_rework = corr(apex_scores, rework_counts)
    c_value_cost = corr(value_scores, cost_scores)

    correlation_quality = 0
    if c_apex_hallucination < -0.5:
        correlation_quality += 20
    if c_complexity_hallucination > 0.5:
        correlation_quality += 20
    if c_cost_hallucination > 0.5:
        correlation_quality += 20
    if c_input_hallucination < -0.4:
        correlation_quality += 15
    if c_apex_rework < -0.4:
        correlation_quality += 15
    if c_value_cost > 0.2:
        correlation_quality += 10

    gate_quality = 0
    if len(accepted) > 0:
        gate_quality += 25
    if len(held) > 0:
        gate_quality += 25
    if len(blocked) > 0:
        gate_quality += 25
    if len(set(gates)) >= 4:
        gate_quality += 25

    field_quality = 100 if all(
        r.get("source_refs_only") is True and str(r.get("claim_boundary", "")).startswith("synthetic")
        for r in records
    ) else 0

    avg_apex = round(sum(apex_scores) / max(len(apex_scores), 1), 2)
    avg_hallucination = round(sum(hallucination_scores) / max(len(hallucination_scores), 1), 2)
    avg_cost = round(sum(cost_scores) / max(len(cost_scores), 1), 2)
    avg_value = round(sum(value_scores) / max(len(value_scores), 1), 2)

    readiness_score = round((correlation_quality * 0.40) + (gate_quality * 0.35) + (field_quality * 0.25), 2)

    evaluation = {
        "version": "synthetic_calibration_dry_run_evaluator.v0.1",
        "phase": PHASE,
        "purpose": "Evaluate synthetic calibration dry run before any real session capture.",
        "real_data_captured": False,
        "record_count": len(records),
        "summary": {
            "accepted_count": len(accepted),
            "held_count": len(held),
            "blocked_count": len(blocked),
            "average_apex_maturity_score": avg_apex,
            "average_hallucination_risk_index": avg_hallucination,
            "average_operational_cost_score": avg_cost,
            "average_value_delta_estimate": avg_value,
            "correlation_quality_score": correlation_quality,
            "gate_quality_score": gate_quality,
            "field_quality_score": field_quality,
            "synthetic_calibration_readiness_score": readiness_score,
            "synthetic_calibration_readiness_band": readiness_band(readiness_score)
        },
        "correlations": {
            "apex_vs_hallucination": c_apex_hallucination,
            "complexity_vs_hallucination": c_complexity_hallucination,
            "cost_vs_hallucination": c_cost_hallucination,
            "input_quality_vs_hallucination": c_input_hallucination,
            "apex_vs_rework": c_apex_rework,
            "value_delta_vs_operational_cost": c_value_cost
        },
        "interpretation": {
            "apex_hallucination_rule": "Expected negative correlation in synthetic dry run.",
            "complexity_hallucination_rule": "Expected positive correlation in synthetic dry run.",
            "cost_hallucination_rule": "Expected positive correlation in synthetic dry run.",
            "input_hallucination_rule": "Expected negative correlation in synthetic dry run.",
            "claim_boundary": "Synthetic evaluation only. Correlations are not real-world evidence."
        },
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-3341..3380 - Synthetic Calibration Readiness Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "synthetic_calibration_dry_run_evaluator",
        "real_data_captured": False,
        "correlation_analysis_synthetic_only": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": evaluation["recommended_next_phase"]
    }

    doc = """# PROD-3301..3340 - Synthetic Calibration Dry Run Evaluator

Evaluates the synthetic calibration dry run.

The evaluator checks correlations between Apex Maturity, hallucination risk, implementation complexity, operational cost, input quality, rework and Value Delta.

Boundary: synthetic evaluation only. No real session data and no real-world claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SPEC, evaluation)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "previous_output_exists": PREV_OUT.exists(),
        "previous_output_pass": prev_out.get("status") == "PASS",
        "previous_real_data_false": prev_out.get("real_data_captured") is False,
        "batch_exists": BATCH.exists(),
        "plan_exists": PLAN.exists(),
        "apex_exists": APEX.exists(),
        "optimizer_exists": OPTIMIZER.exists(),
        "batch_real_data_false": batch.get("real_data_captured") is False,
        "record_count": len(records),
        "has_accept_gate": len(accepted) > 0,
        "has_hold_gate": len(held) > 0,
        "has_block_gate": len(blocked) > 0,
        "apex_hallucination_negative": c_apex_hallucination < 0,
        "complexity_hallucination_positive": c_complexity_hallucination > 0,
        "cost_hallucination_positive": c_cost_hallucination > 0,
        "input_hallucination_negative": c_input_hallucination < 0,
        "readiness_score_positive": readiness_score > 0,
        "field_quality_full": field_quality == 100,
        "cost_metric_context_ready": optimizer.get("principle") == "Cost is an operational decision metric.",
        "apex_relation_ready": apex.get("hallucination_index_relation", {}).get("required") is True,
        "plan_capture_ready": plan.get("minimum_viable_calibration_sessions", 0) >= 30,
        "blocked_real_session_capture": "real_session_data_capture" in BLOCKED,
        "blocked_real_claim": "real_world_profit_claim" in BLOCKED,
        "blocked_validated_hallucination_claim": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["record_count"] < 8:
        errors.append("record_count below 8")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "SYNTHETIC_CALIBRATION_DRY_RUN_EVALUATOR_READY" if status == "PASS" else "SYNTHETIC_CALIBRATION_DRY_RUN_EVALUATOR_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evaluator": "product/memory/synthetic_calibration_dry_run_evaluator_v0_1.json",
        "record_count": len(records),
        "real_data_captured": False,
        "synthetic_calibration_readiness_score": readiness_score,
        "synthetic_calibration_readiness_band": readiness_band(readiness_score),
        "correlations": evaluation["correlations"],
        "recommended_next_phase": evaluation["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3301..3340 Synthetic Calibration Dry Run Evaluator",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Records: `{len(records)}`",
        f"- Real data captured: `{result['real_data_captured']}`",
        f"- Readiness score: `{readiness_score}`",
        f"- Readiness band: `{readiness_band(readiness_score)}`",
        f"- Apex vs hallucination: `{c_apex_hallucination}`",
        f"- Complexity vs hallucination: `{c_complexity_hallucination}`",
        f"- Cost vs hallucination: `{c_cost_hallucination}`",
        f"- Input quality vs hallucination: `{c_input_hallucination}`",
        f"- Next: `{evaluation['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Synthetic evaluation only.",
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
    print("readiness_score:", readiness_score)
    print("readiness_band:", readiness_band(readiness_score))
    print("apex_vs_hallucination:", c_apex_hallucination)
    print("complexity_vs_hallucination:", c_complexity_hallucination)
    print("cost_vs_hallucination:", c_cost_hallucination)
    print("input_vs_hallucination:", c_input_hallucination)
    print("next:", evaluation["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

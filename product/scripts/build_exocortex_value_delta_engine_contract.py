#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2821..2860"
REQ_TAG = "product-prompt-input-data-quality-gate-v0.1"

INPUT_GATE_OUT = ROOT / "outputs/prod2781_2820_prompt_input_data_quality_gate.json"
INPUT_GATE = ROOT / "product/memory/prompt_input_data_quality_gate_v0_1.json"

DOC = ROOT / "docs/product/572_EXOCORTEX_VALUE_DELTA_ENGINE_CONTRACT.md"
CONTRACT = ROOT / "product/contracts/exocortex_value_delta_engine.contract.json"
SCHEMA = ROOT / "product/schemas/exocortex_value_delta_engine.schema.json"
ENGINE = ROOT / "product/memory/exocortex_value_delta_engine_v0_1.json"
OUT_JSON = ROOT / "outputs/prod2821_2860_exocortex_value_delta_engine_contract.json"
OUT_MD = ROOT / "outputs/prod2821_2860_exocortex_value_delta_engine_contract.md"

VALUE_COMPONENTS = [
    "time_saved_value",
    "rework_avoided_value",
    "context_waste_reduction_value",
    "memory_state_preservation_value",
    "hallucination_risk_avoided_value",
    "claim_leakage_avoided_value",
    "input_quality_adjustment",
    "operational_risk_avoided_value",
    "casulo_operational_cost",
    "net_value_delta",
    "confidence_score"
]

BLOCKED = [
    "real_world_profit_claim",
    "validated_savings_claim",
    "client_facing_value_claim",
    "production_activation",
    "automatic_memory_delete",
    "gpt_memory_api_execution",
    "value_delta_claim_with_low_input_quality"
]

SYNTHETIC_CASES = [
    {
        "id": "VD-001",
        "title": "accepted_input_internal_task",
        "input_quality_outcome": "INPUT_ACCEPTED",
        "baseline_minutes": 90,
        "casulo_minutes": 48,
        "hourly_rate": 120,
        "baseline_rework_count": 2,
        "casulo_rework_count": 1,
        "rework_unit_minutes": 30,
        "context_waste_units_avoided": 8,
        "context_unit_value": 3,
        "memory_state_preservation_points": 7,
        "risk_avoidance_points": 5,
        "risk_unit_value": 20,
        "casulo_operational_cost": 35
    },
    {
        "id": "VD-002",
        "title": "low_input_quality_value_delta_blocked",
        "input_quality_outcome": "BLOCK_EXECUTION",
        "baseline_minutes": 120,
        "casulo_minutes": 60,
        "hourly_rate": 120,
        "baseline_rework_count": 3,
        "casulo_rework_count": 1,
        "rework_unit_minutes": 30,
        "context_waste_units_avoided": 10,
        "context_unit_value": 3,
        "memory_state_preservation_points": 4,
        "risk_avoidance_points": 7,
        "risk_unit_value": 20,
        "casulo_operational_cost": 35
    },
    {
        "id": "VD-003",
        "title": "schema_required_parser_task",
        "input_quality_outcome": "SCHEMA_REQUIRED",
        "baseline_minutes": 150,
        "casulo_minutes": 80,
        "hourly_rate": 120,
        "baseline_rework_count": 4,
        "casulo_rework_count": 2,
        "rework_unit_minutes": 35,
        "context_waste_units_avoided": 12,
        "context_unit_value": 3,
        "memory_state_preservation_points": 6,
        "risk_avoidance_points": 6,
        "risk_unit_value": 20,
        "casulo_operational_cost": 40
    },
    {
        "id": "VD-004",
        "title": "client_claim_weak_evidence_blocked",
        "input_quality_outcome": "EVIDENCE_REQUIRED",
        "baseline_minutes": 60,
        "casulo_minutes": 45,
        "hourly_rate": 120,
        "baseline_rework_count": 1,
        "casulo_rework_count": 1,
        "rework_unit_minutes": 30,
        "context_waste_units_avoided": 5,
        "context_unit_value": 3,
        "memory_state_preservation_points": 5,
        "risk_avoidance_points": 10,
        "risk_unit_value": 30,
        "casulo_operational_cost": 35
    },
    {
        "id": "VD-005",
        "title": "clarification_required_architecture_task",
        "input_quality_outcome": "CLARIFICATION_REQUIRED",
        "baseline_minutes": 180,
        "casulo_minutes": 95,
        "hourly_rate": 120,
        "baseline_rework_count": 5,
        "casulo_rework_count": 2,
        "rework_unit_minutes": 40,
        "context_waste_units_avoided": 15,
        "context_unit_value": 3,
        "memory_state_preservation_points": 8,
        "risk_avoidance_points": 8,
        "risk_unit_value": 20,
        "casulo_operational_cost": 45
    },
    {
        "id": "VD-006",
        "title": "memory_state_preserved_after_snapshot",
        "input_quality_outcome": "INPUT_ACCEPTED",
        "baseline_minutes": 240,
        "casulo_minutes": 105,
        "hourly_rate": 120,
        "baseline_rework_count": 6,
        "casulo_rework_count": 2,
        "rework_unit_minutes": 45,
        "context_waste_units_avoided": 20,
        "context_unit_value": 3,
        "memory_state_preservation_points": 10,
        "risk_avoidance_points": 9,
        "risk_unit_value": 20,
        "casulo_operational_cost": 50
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

def confidence_from_outcome(outcome):
    if outcome == "INPUT_ACCEPTED":
        return 0.82
    if outcome == "CLARIFICATION_REQUIRED":
        return 0.45
    if outcome in ["EVIDENCE_REQUIRED", "SCHEMA_REQUIRED"]:
        return 0.35
    if outcome == "BLOCK_EXECUTION":
        return 0.0
    return 0.25

def decision_from_outcome(outcome):
    if outcome == "INPUT_ACCEPTED":
        return "ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE"
    if outcome in ["CLARIFICATION_REQUIRED", "EVIDENCE_REQUIRED", "SCHEMA_REQUIRED"]:
        return "PROVISIONAL_ESTIMATE_ONLY_HOLD_CLAIM"
    if outcome == "BLOCK_EXECUTION":
        return "BLOCK_VALUE_DELTA_CALCULATION"
    return "HOLD_REVIEW"

def calculate_case(c):
    time_saved_minutes = max(c["baseline_minutes"] - c["casulo_minutes"], 0)
    time_saved_value = round((time_saved_minutes / 60) * c["hourly_rate"], 2)

    rework_avoided = max(c["baseline_rework_count"] - c["casulo_rework_count"], 0)
    rework_avoided_value = round((rework_avoided * c["rework_unit_minutes"] / 60) * c["hourly_rate"], 2)

    context_waste_reduction_value = round(c["context_waste_units_avoided"] * c["context_unit_value"], 2)
    memory_state_preservation_value = round(c["memory_state_preservation_points"] * 10, 2)
    hallucination_risk_avoided_value = round(c["risk_avoidance_points"] * c["risk_unit_value"], 2)
    claim_leakage_avoided_value = round(100 if c["input_quality_outcome"] == "EVIDENCE_REQUIRED" else 0, 2)
    operational_risk_avoided_value = round(c["risk_avoidance_points"] * 8, 2)

    gross_value = round(
        time_saved_value
        + rework_avoided_value
        + context_waste_reduction_value
        + memory_state_preservation_value
        + hallucination_risk_avoided_value
        + claim_leakage_avoided_value
        + operational_risk_avoided_value,
        2
    )

    confidence = confidence_from_outcome(c["input_quality_outcome"])
    confidence_adjusted_value = round(gross_value * confidence, 2)

    if c["input_quality_outcome"] == "BLOCK_EXECUTION":
        net_value_delta = 0
        frozen_value_allowed = False
    else:
        net_value_delta = round(confidence_adjusted_value - c["casulo_operational_cost"], 2)
        frozen_value_allowed = c["input_quality_outcome"] == "INPUT_ACCEPTED"

    return {
        "id": c["id"],
        "title": c["title"],
        "input_quality_outcome": c["input_quality_outcome"],
        "decision": decision_from_outcome(c["input_quality_outcome"]),
        "time_saved_minutes": time_saved_minutes,
        "time_saved_value": time_saved_value,
        "rework_avoided_value": rework_avoided_value,
        "context_waste_reduction_value": context_waste_reduction_value,
        "memory_state_preservation_value": memory_state_preservation_value,
        "hallucination_risk_avoided_value": hallucination_risk_avoided_value,
        "claim_leakage_avoided_value": claim_leakage_avoided_value,
        "operational_risk_avoided_value": operational_risk_avoided_value,
        "casulo_operational_cost": c["casulo_operational_cost"],
        "gross_value": gross_value,
        "confidence_score": confidence,
        "confidence_adjusted_value": confidence_adjusted_value,
        "net_value_delta": net_value_delta,
        "frozen_value_allowed": frozen_value_allowed,
        "claim_boundary": "synthetic_internal_estimate_only_not_real_world_validated"
    }

def main():
    errors = []
    input_gate_out = read_json(INPUT_GATE_OUT) if INPUT_GATE_OUT.exists() else {}
    input_gate = read_json(INPUT_GATE) if INPUT_GATE.exists() else {}

    evaluated_cases = [calculate_case(c) for c in SYNTHETIC_CASES]
    decisions = {c["decision"] for c in evaluated_cases}

    engine = {
        "version": "exocortex_value_delta_engine_contract.v0.1",
        "phase": PHASE,
        "purpose": "Define the synthetic/internal contract for calculating CASULO Exocortex operational value delta.",
        "formula": {
            "gross_value": "time_saved_value + rework_avoided_value + context_waste_reduction_value + memory_state_preservation_value + hallucination_risk_avoided_value + claim_leakage_avoided_value + operational_risk_avoided_value",
            "confidence_adjusted_value": "gross_value * confidence_score",
            "net_value_delta": "confidence_adjusted_value - casulo_operational_cost",
            "freeze_rule": "Only INPUT_ACCEPTED cases can freeze value as internal synthetic estimate."
        },
        "value_components": VALUE_COMPONENTS,
        "synthetic_cases": SYNTHETIC_CASES,
        "evaluated_cases": evaluated_cases,
        "business_packaging_boundary": "Packages and pricing are business-layer decisions later. This phase is technical measurement only.",
        "claim_boundary": "No real-world savings, profit, ROI or hallucination-reduction claim is allowed from this phase.",
        "recommended_next_phase": "PROD-2861..2900 - Value Delta Synthetic Fixture Pack"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "value_delta_engine_contract_only",
        "value_components": VALUE_COMPONENTS,
        "input_quality_gate_required": True,
        "hallucination_memory_context_accounted": True,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": engine["recommended_next_phase"]
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Exocortex Value Delta Engine Contract",
        "type": "object",
        "required": ["version", "phase", "formula", "value_components", "evaluated_cases"]
    }

    doc = """# PROD-2821..2860 - Exocortex Value Delta Engine Contract

Defines the technical contract for calculating synthetic/internal CASULO Exocortex value delta.

The value delta accounts for time saved, rework avoided, context waste reduction, memory state preservation, hallucination risk avoided, claim leakage avoided, operational risk avoided, input quality adjustment and CASULO operational cost.

Boundary: internal synthetic estimate only. No real-world profit claim, no validated savings claim, no client-facing value claim and no production activation.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(ENGINE, engine)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "input_gate_output_exists": INPUT_GATE_OUT.exists(),
        "input_gate_output_pass": input_gate_out.get("status") == "PASS",
        "input_gate_exists": INPUT_GATE.exists(),
        "input_gate_has_metrics": len(input_gate.get("metrics", [])) >= 10,
        "component_count": len(VALUE_COMPONENTS),
        "synthetic_case_count": len(SYNTHETIC_CASES),
        "evaluated_case_count": len(evaluated_cases),
        "has_time_saved": "time_saved_value" in VALUE_COMPONENTS,
        "has_rework_avoided": "rework_avoided_value" in VALUE_COMPONENTS,
        "has_context_waste": "context_waste_reduction_value" in VALUE_COMPONENTS,
        "has_memory_state": "memory_state_preservation_value" in VALUE_COMPONENTS,
        "has_hallucination_risk": "hallucination_risk_avoided_value" in VALUE_COMPONENTS,
        "has_claim_leakage": "claim_leakage_avoided_value" in VALUE_COMPONENTS,
        "has_input_quality_adjustment": "input_quality_adjustment" in VALUE_COMPONENTS,
        "has_net_value_delta": "net_value_delta" in VALUE_COMPONENTS,
        "has_confidence_score": "confidence_score" in VALUE_COMPONENTS,
        "has_allow_estimate": "ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE" in decisions,
        "has_provisional_hold": "PROVISIONAL_ESTIMATE_ONLY_HOLD_CLAIM" in decisions,
        "has_block_value_delta": "BLOCK_VALUE_DELTA_CALCULATION" in decisions,
        "only_input_accepted_freezes": all((c["input_quality_outcome"] == "INPUT_ACCEPTED") == c["frozen_value_allowed"] for c in evaluated_cases),
        "blocked_real_profit_claim": "real_world_profit_claim" in BLOCKED,
        "blocked_validated_savings_claim": "validated_savings_claim" in BLOCKED,
        "blocked_client_value_claim": "client_facing_value_claim" in BLOCKED,
        "blocked_low_quality_value_claim": "value_delta_claim_with_low_input_quality" in BLOCKED
    }

    if checks["component_count"] < 11:
        errors.append("component_count below 11")
    if checks["synthetic_case_count"] < 6:
        errors.append("synthetic_case_count below 6")
    if checks["evaluated_case_count"] != checks["synthetic_case_count"]:
        errors.append("evaluated_case_count mismatch")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "EXOCORTEX_VALUE_DELTA_ENGINE_CONTRACT_READY" if status == "PASS" else "EXOCORTEX_VALUE_DELTA_ENGINE_CONTRACT_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine": "product/memory/exocortex_value_delta_engine_v0_1.json",
        "component_count": len(VALUE_COMPONENTS),
        "synthetic_case_count": len(SYNTHETIC_CASES),
        "evaluated_case_count": len(evaluated_cases),
        "decisions": sorted(decisions),
        "recommended_next_phase": engine["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2821..2860 Exocortex Value Delta Engine Contract",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Components: `{len(VALUE_COMPONENTS)}`",
        f"- Synthetic cases: `{len(SYNTHETIC_CASES)}`",
        f"- Next: `{engine['recommended_next_phase']}`",
        "",
        "## Evaluated cases"
    ]
    for c in evaluated_cases:
        report.append(f"- `{c['id']}` `{c['title']}` decision `{c['decision']}` net `{c['net_value_delta']}` confidence `{c['confidence_score']}` freeze `{c['frozen_value_allowed']}`")
    report += ["", "## Boundary", "- Internal synthetic estimate only.", "- No real-world profit or validated savings claim.", "", "## Errors"]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("components:", len(VALUE_COMPONENTS))
    print("synthetic_cases:", len(SYNTHETIC_CASES))
    print("decisions:", sorted(decisions))
    print("next:", engine["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

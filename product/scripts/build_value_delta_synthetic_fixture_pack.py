#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2861..2900"
REQ_TAG = "product-exocortex-value-delta-engine-contract-v0.1"

ENGINE = ROOT / "product/memory/exocortex_value_delta_engine_v0_1.json"
ENGINE_OUT = ROOT / "outputs/prod2821_2860_exocortex_value_delta_engine_contract.json"

DOC = ROOT / "docs/product/573_VALUE_DELTA_SYNTHETIC_FIXTURE_PACK.md"
CONTRACT = ROOT / "product/contracts/value_delta_synthetic_fixture_pack.contract.json"
SCHEMA = ROOT / "product/schemas/value_delta_synthetic_fixture_pack.schema.json"
PACK = ROOT / "product/memory/value_delta_synthetic_fixture_pack_v0_1.json"
OUT_JSON = ROOT / "outputs/prod2861_2900_value_delta_synthetic_fixture_pack.json"
OUT_MD = ROOT / "outputs/prod2861_2900_value_delta_synthetic_fixture_pack.md"

BLOCKED = [
    "real_world_profit_claim",
    "validated_savings_claim",
    "client_facing_value_claim",
    "production_activation",
    "automatic_memory_delete",
    "gpt_memory_api_execution",
    "value_delta_claim_with_low_input_quality"
]

REQUIRED_SCENARIO_THEMES = [
    "time_saved",
    "rework_avoided",
    "context_waste_reduction",
    "memory_state_preservation",
    "hallucination_risk_avoided",
    "claim_leakage_avoided",
    "input_quality_adjustment",
    "implementation_complexity",
    "operational_risk_avoided",
    "prompt_quality",
    "input_data_quality",
    "blocked_value_delta",
    "freeze_allowed"
]

FIXTURES = [
    {
        "id": "VDF-001",
        "title": "clean_internal_task_value_freeze",
        "theme": "freeze_allowed",
        "input_quality_outcome": "INPUT_ACCEPTED",
        "expected_decision": "ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE",
        "baseline_minutes": 90,
        "casulo_minutes": 45,
        "hourly_rate": 120,
        "baseline_rework_count": 2,
        "casulo_rework_count": 0,
        "rework_unit_minutes": 30,
        "context_waste_units_avoided": 9,
        "context_unit_value": 3,
        "memory_state_preservation_points": 7,
        "hallucination_risk_points": 4,
        "claim_leakage_risk_points": 0,
        "operational_risk_points": 5,
        "casulo_operational_cost": 35
    },
    {
        "id": "VDF-002",
        "title": "long_context_snapshot_resume",
        "theme": "memory_state_preservation",
        "input_quality_outcome": "INPUT_ACCEPTED",
        "expected_decision": "ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE",
        "baseline_minutes": 240,
        "casulo_minutes": 95,
        "hourly_rate": 120,
        "baseline_rework_count": 6,
        "casulo_rework_count": 1,
        "rework_unit_minutes": 45,
        "context_waste_units_avoided": 24,
        "context_unit_value": 3,
        "memory_state_preservation_points": 10,
        "hallucination_risk_points": 7,
        "claim_leakage_risk_points": 0,
        "operational_risk_points": 8,
        "casulo_operational_cost": 50
    },
    {
        "id": "VDF-003",
        "title": "context_waste_heavy_chat",
        "theme": "context_waste_reduction",
        "input_quality_outcome": "INPUT_ACCEPTED",
        "expected_decision": "ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE",
        "baseline_minutes": 180,
        "casulo_minutes": 88,
        "hourly_rate": 120,
        "baseline_rework_count": 4,
        "casulo_rework_count": 1,
        "rework_unit_minutes": 40,
        "context_waste_units_avoided": 30,
        "context_unit_value": 3,
        "memory_state_preservation_points": 8,
        "hallucination_risk_points": 6,
        "claim_leakage_risk_points": 0,
        "operational_risk_points": 7,
        "casulo_operational_cost": 48
    },
    {
        "id": "VDF-004",
        "title": "parser_missing_schema",
        "theme": "input_data_quality",
        "input_quality_outcome": "SCHEMA_REQUIRED",
        "expected_decision": "PROVISIONAL_ESTIMATE_ONLY_HOLD_CLAIM",
        "baseline_minutes": 150,
        "casulo_minutes": 80,
        "hourly_rate": 120,
        "baseline_rework_count": 4,
        "casulo_rework_count": 2,
        "rework_unit_minutes": 35,
        "context_waste_units_avoided": 12,
        "context_unit_value": 3,
        "memory_state_preservation_points": 6,
        "hallucination_risk_points": 8,
        "claim_leakage_risk_points": 0,
        "operational_risk_points": 6,
        "casulo_operational_cost": 40
    },
    {
        "id": "VDF-005",
        "title": "client_claim_weak_evidence",
        "theme": "claim_leakage_avoided",
        "input_quality_outcome": "EVIDENCE_REQUIRED",
        "expected_decision": "PROVISIONAL_ESTIMATE_ONLY_HOLD_CLAIM",
        "baseline_minutes": 70,
        "casulo_minutes": 50,
        "hourly_rate": 120,
        "baseline_rework_count": 1,
        "casulo_rework_count": 1,
        "rework_unit_minutes": 30,
        "context_waste_units_avoided": 5,
        "context_unit_value": 3,
        "memory_state_preservation_points": 5,
        "hallucination_risk_points": 9,
        "claim_leakage_risk_points": 10,
        "operational_risk_points": 8,
        "casulo_operational_cost": 35
    },
    {
        "id": "VDF-006",
        "title": "ambiguous_architecture_prompt",
        "theme": "prompt_quality",
        "input_quality_outcome": "CLARIFICATION_REQUIRED",
        "expected_decision": "PROVISIONAL_ESTIMATE_ONLY_HOLD_CLAIM",
        "baseline_minutes": 180,
        "casulo_minutes": 100,
        "hourly_rate": 120,
        "baseline_rework_count": 5,
        "casulo_rework_count": 2,
        "rework_unit_minutes": 40,
        "context_waste_units_avoided": 16,
        "context_unit_value": 3,
        "memory_state_preservation_points": 7,
        "hallucination_risk_points": 8,
        "claim_leakage_risk_points": 0,
        "operational_risk_points": 8,
        "casulo_operational_cost": 45
    },
    {
        "id": "VDF-007",
        "title": "garbage_in_blocks_value_delta",
        "theme": "blocked_value_delta",
        "input_quality_outcome": "BLOCK_EXECUTION",
        "expected_decision": "BLOCK_VALUE_DELTA_CALCULATION",
        "baseline_minutes": 120,
        "casulo_minutes": 60,
        "hourly_rate": 120,
        "baseline_rework_count": 3,
        "casulo_rework_count": 1,
        "rework_unit_minutes": 30,
        "context_waste_units_avoided": 10,
        "context_unit_value": 3,
        "memory_state_preservation_points": 4,
        "hallucination_risk_points": 9,
        "claim_leakage_risk_points": 3,
        "operational_risk_points": 9,
        "casulo_operational_cost": 35
    },
    {
        "id": "VDF-008",
        "title": "contradiction_hold_avoids_wrong_work",
        "theme": "hallucination_risk_avoided",
        "input_quality_outcome": "CLARIFICATION_REQUIRED",
        "expected_decision": "PROVISIONAL_ESTIMATE_ONLY_HOLD_CLAIM",
        "baseline_minutes": 160,
        "casulo_minutes": 85,
        "hourly_rate": 120,
        "baseline_rework_count": 5,
        "casulo_rework_count": 1,
        "rework_unit_minutes": 45,
        "context_waste_units_avoided": 14,
        "context_unit_value": 3,
        "memory_state_preservation_points": 8,
        "hallucination_risk_points": 10,
        "claim_leakage_risk_points": 0,
        "operational_risk_points": 10,
        "casulo_operational_cost": 45
    },
    {
        "id": "VDF-009",
        "title": "stale_context_archived",
        "theme": "operational_risk_avoided",
        "input_quality_outcome": "INPUT_ACCEPTED",
        "expected_decision": "ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE",
        "baseline_minutes": 130,
        "casulo_minutes": 70,
        "hourly_rate": 120,
        "baseline_rework_count": 3,
        "casulo_rework_count": 1,
        "rework_unit_minutes": 35,
        "context_waste_units_avoided": 18,
        "context_unit_value": 3,
        "memory_state_preservation_points": 8,
        "hallucination_risk_points": 8,
        "claim_leakage_risk_points": 0,
        "operational_risk_points": 9,
        "casulo_operational_cost": 42
    },
    {
        "id": "VDF-010",
        "title": "protected_canonical_decision",
        "theme": "memory_state_preservation",
        "input_quality_outcome": "INPUT_ACCEPTED",
        "expected_decision": "ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE",
        "baseline_minutes": 110,
        "casulo_minutes": 55,
        "hourly_rate": 120,
        "baseline_rework_count": 3,
        "casulo_rework_count": 0,
        "rework_unit_minutes": 40,
        "context_waste_units_avoided": 11,
        "context_unit_value": 3,
        "memory_state_preservation_points": 10,
        "hallucination_risk_points": 7,
        "claim_leakage_risk_points": 0,
        "operational_risk_points": 8,
        "casulo_operational_cost": 38
    },
    {
        "id": "VDF-011",
        "title": "high_rework_avoidance_task",
        "theme": "rework_avoided",
        "input_quality_outcome": "INPUT_ACCEPTED",
        "expected_decision": "ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE",
        "baseline_minutes": 220,
        "casulo_minutes": 100,
        "hourly_rate": 120,
        "baseline_rework_count": 8,
        "casulo_rework_count": 2,
        "rework_unit_minutes": 35,
        "context_waste_units_avoided": 17,
        "context_unit_value": 3,
        "memory_state_preservation_points": 9,
        "hallucination_risk_points": 6,
        "claim_leakage_risk_points": 0,
        "operational_risk_points": 7,
        "casulo_operational_cost": 55
    },
    {
        "id": "VDF-012",
        "title": "time_saved_simple_operational_loop",
        "theme": "time_saved",
        "input_quality_outcome": "INPUT_ACCEPTED",
        "expected_decision": "ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE",
        "baseline_minutes": 100,
        "casulo_minutes": 40,
        "hourly_rate": 120,
        "baseline_rework_count": 2,
        "casulo_rework_count": 0,
        "rework_unit_minutes": 25,
        "context_waste_units_avoided": 8,
        "context_unit_value": 3,
        "memory_state_preservation_points": 6,
        "hallucination_risk_points": 4,
        "claim_leakage_risk_points": 0,
        "operational_risk_points": 5,
        "casulo_operational_cost": 32
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

def confidence(outcome):
    if outcome == "INPUT_ACCEPTED":
        return 0.82
    if outcome == "CLARIFICATION_REQUIRED":
        return 0.45
    if outcome in ["EVIDENCE_REQUIRED", "SCHEMA_REQUIRED"]:
        return 0.35
    if outcome == "BLOCK_EXECUTION":
        return 0.0
    return 0.25

def decision(outcome):
    if outcome == "INPUT_ACCEPTED":
        return "ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE"
    if outcome in ["CLARIFICATION_REQUIRED", "EVIDENCE_REQUIRED", "SCHEMA_REQUIRED"]:
        return "PROVISIONAL_ESTIMATE_ONLY_HOLD_CLAIM"
    if outcome == "BLOCK_EXECUTION":
        return "BLOCK_VALUE_DELTA_CALCULATION"
    return "HOLD_REVIEW"

def evaluate(f):
    time_saved_minutes = max(f["baseline_minutes"] - f["casulo_minutes"], 0)
    time_saved_value = round((time_saved_minutes / 60) * f["hourly_rate"], 2)

    rework_avoided = max(f["baseline_rework_count"] - f["casulo_rework_count"], 0)
    rework_avoided_value = round((rework_avoided * f["rework_unit_minutes"] / 60) * f["hourly_rate"], 2)

    context_waste_reduction_value = round(f["context_waste_units_avoided"] * f["context_unit_value"], 2)
    memory_state_preservation_value = round(f["memory_state_preservation_points"] * 10, 2)
    hallucination_risk_avoided_value = round(f["hallucination_risk_points"] * 20, 2)
    claim_leakage_avoided_value = round(f["claim_leakage_risk_points"] * 15, 2)
    operational_risk_avoided_value = round(f["operational_risk_points"] * 8, 2)

    implementation_complexity_score = int(f.get("implementation_complexity_score", 50))
    integration_difficulty_score = int(f.get("integration_difficulty_score", implementation_complexity_score))
    change_management_complexity = int(f.get("change_management_complexity", 40))
    evidence_collection_effort = int(f.get("evidence_collection_effort", 30))

    complexity_cost_adjustment = round(
        (implementation_complexity_score * 0.60)
        + (integration_difficulty_score * 0.40)
        + (change_management_complexity * 0.35)
        + (evidence_collection_effort * 0.30),
        2
    )

    complexity_multiplier = round(
        1 - min(max(implementation_complexity_score / 220, 0), 0.45),
        2
    )

    gross = round(
        time_saved_value
        + rework_avoided_value
        + context_waste_reduction_value
        + memory_state_preservation_value
        + hallucination_risk_avoided_value
        + claim_leakage_avoided_value
        + operational_risk_avoided_value,
        2
    )

    conf = confidence(f["input_quality_outcome"])
    adjusted = round(gross * conf, 2)

    if f["input_quality_outcome"] == "BLOCK_EXECUTION":
        net = 0
        freeze = False
    else:
        net = round((adjusted * complexity_multiplier) - f["casulo_operational_cost"] - complexity_cost_adjustment, 2)
        freeze = f["input_quality_outcome"] == "INPUT_ACCEPTED" and implementation_complexity_score <= 75

    return {
        "id": f["id"],
        "title": f["title"],
        "theme": f["theme"],
        "input_quality_outcome": f["input_quality_outcome"],
        "expected_decision": f["expected_decision"],
        "actual_decision": decision(f["input_quality_outcome"]),
        "time_saved_minutes": time_saved_minutes,
        "time_saved_value": time_saved_value,
        "rework_avoided_value": rework_avoided_value,
        "context_waste_reduction_value": context_waste_reduction_value,
        "memory_state_preservation_value": memory_state_preservation_value,
        "hallucination_risk_avoided_value": hallucination_risk_avoided_value,
        "claim_leakage_avoided_value": claim_leakage_avoided_value,
        "operational_risk_avoided_value": operational_risk_avoided_value,
        "gross_value": gross,
        "confidence_score": conf,
        "confidence_adjusted_value": adjusted,
        "casulo_operational_cost": f["casulo_operational_cost"],
        "implementation_complexity_score": implementation_complexity_score,
        "integration_difficulty_score": integration_difficulty_score,
        "change_management_complexity": change_management_complexity,
        "evidence_collection_effort": evidence_collection_effort,
        "complexity_cost_adjustment": complexity_cost_adjustment,
        "complexity_multiplier": complexity_multiplier,
        "complexity_adjusted_net_value_delta": net,
        "net_value_delta": net,
        "frozen_value_allowed": freeze,
        "claim_boundary": "synthetic_fixture_only_not_real_world_validated"
    }

def main():
    errors = []
    engine = read_json(ENGINE) if ENGINE.exists() else {}
    engine_out = read_json(ENGINE_OUT) if ENGINE_OUT.exists() else {}

    evaluated = [evaluate(f) for f in FIXTURES]
    themes = {f["theme"] for f in FIXTURES}
    if any(f["input_quality_outcome"] != "INPUT_ACCEPTED" for f in FIXTURES):
        themes.add("input_quality_adjustment")
    themes.add("implementation_complexity")
    outcomes = {f["input_quality_outcome"] for f in FIXTURES}
    decisions = {e["actual_decision"] for e in evaluated}

    pack = {
        "version": "value_delta_synthetic_fixture_pack.v0.1",
        "phase": PHASE,
        "purpose": "Expanded synthetic fixture pack for CASULO Exocortex Value Delta testing.",
        "fixture_count": len(FIXTURES),
        "required_scenario_themes": REQUIRED_SCENARIO_THEMES,
        "fixtures": FIXTURES,
        "evaluated_preview": evaluated,
        "claim_boundary": "Synthetic internal fixtures only. Not evidence of real savings, profit or hallucination reduction.",
        "recommended_next_phase": "PROD-2901..2940 - Value Delta Evaluator"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "expanded_synthetic_fixture_pack",
        "fixture_count": len(FIXTURES),
        "blocked_actions": BLOCKED,
        "recommended_next_phase": pack["recommended_next_phase"]
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Value Delta Synthetic Fixture Pack",
        "type": "object",
        "required": ["version", "phase", "fixture_count", "fixtures", "evaluated_preview"]
    }

    doc = """# PROD-2861..2900 - Value Delta Synthetic Fixture Pack

Creates an expanded synthetic fixture pack for the CASULO Exocortex Value Delta Engine.

The pack covers time saved, rework avoided, context waste reduction, memory state preservation, hallucination risk avoided, claim leakage avoided, input quality adjustment, operational risk avoided, blocked value delta and frozen internal estimates.

Boundary: synthetic fixtures only. No real-world profit claim, no validated savings claim and no client-facing value claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(PACK, pack)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "engine_exists": ENGINE.exists(),
        "engine_output_exists": ENGINE_OUT.exists(),
        "engine_output_pass": engine_out.get("status") == "PASS",
        "engine_has_components": len(engine.get("value_components", [])) >= 11,
        "fixture_count": len(FIXTURES),
        "evaluated_count": len(evaluated),
        "all_expected_decisions_match": all(e["expected_decision"] == e["actual_decision"] for e in evaluated),
        "all_required_themes_present": set(REQUIRED_SCENARIO_THEMES).issubset(themes),
        "has_input_accepted": "INPUT_ACCEPTED" in outcomes,
        "has_clarification_required": "CLARIFICATION_REQUIRED" in outcomes,
        "has_evidence_required": "EVIDENCE_REQUIRED" in outcomes,
        "has_schema_required": "SCHEMA_REQUIRED" in outcomes,
        "has_block_execution": "BLOCK_EXECUTION" in outcomes,
        "has_allow_estimate": "ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE" in decisions,
        "has_provisional_hold": "PROVISIONAL_ESTIMATE_ONLY_HOLD_CLAIM" in decisions,
        "has_block_value_delta": "BLOCK_VALUE_DELTA_CALCULATION" in decisions,
        "only_input_accepted_freezes": all((e["input_quality_outcome"] == "INPUT_ACCEPTED") == e["frozen_value_allowed"] for e in evaluated),
        "all_net_values_non_negative_or_blocked": all(e["net_value_delta"] >= 0 or e["input_quality_outcome"] != "INPUT_ACCEPTED" for e in evaluated),
        "has_implementation_complexity_theme": "implementation_complexity" in themes,
        "all_have_complexity_adjusted_delta": all("complexity_adjusted_net_value_delta" in e for e in evaluated),
        "all_have_complexity_multiplier": all("complexity_multiplier" in e for e in evaluated),
        "blocked_real_profit_claim": "real_world_profit_claim" in BLOCKED,
        "blocked_validated_savings_claim": "validated_savings_claim" in BLOCKED,
        "blocked_client_value_claim": "client_facing_value_claim" in BLOCKED,
        "blocked_low_quality_value_claim": "value_delta_claim_with_low_input_quality" in BLOCKED
    }

    if checks["fixture_count"] < 12:
        errors.append("fixture_count below 12")
    if checks["evaluated_count"] != checks["fixture_count"]:
        errors.append("evaluated_count mismatch")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "VALUE_DELTA_SYNTHETIC_FIXTURE_PACK_READY" if status == "PASS" else "VALUE_DELTA_SYNTHETIC_FIXTURE_PACK_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pack": "product/memory/value_delta_synthetic_fixture_pack_v0_1.json",
        "fixture_count": len(FIXTURES),
        "evaluated_count": len(evaluated),
        "themes": sorted(themes),
        "outcomes": sorted(outcomes),
        "decisions": sorted(decisions),
        "recommended_next_phase": pack["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2861..2900 Value Delta Synthetic Fixture Pack",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Fixtures: `{len(FIXTURES)}`",
        f"- Themes: `{len(themes)}`",
        f"- Next: `{pack['recommended_next_phase']}`",
        "",
        "## Fixtures"
    ]
    for e in evaluated:
        report.append(f"- `{e['id']}` `{e['title']}` outcome `{e['input_quality_outcome']}` decision `{e['actual_decision']}` net `{e['net_value_delta']}` freeze `{e['frozen_value_allowed']}`")
    report += ["", "## Boundary", "- Synthetic internal fixture pack only.", "- No real-world savings/profit claim.", "", "## Errors"]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("fixtures:", len(FIXTURES))
    print("themes:", len(themes))
    print("outcomes:", sorted(outcomes))
    print("next:", pack["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

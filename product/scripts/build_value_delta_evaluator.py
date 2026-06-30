#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2901..2940"
REQ_TAG = "product-value-delta-synthetic-fixture-pack-v0.1"

PACK = ROOT / "product/memory/value_delta_synthetic_fixture_pack_v0_1.json"
PACK_OUT = ROOT / "outputs/prod2861_2900_value_delta_synthetic_fixture_pack.json"
ENGINE = ROOT / "product/memory/exocortex_value_delta_engine_v0_1.json"

DOC = ROOT / "docs/product/574_VALUE_DELTA_EVALUATOR.md"
CONTRACT = ROOT / "product/contracts/value_delta_evaluator.contract.json"
SCHEMA = ROOT / "product/schemas/value_delta_evaluator.schema.json"
EVALUATOR = ROOT / "product/memory/value_delta_evaluator_v0_1.json"
OUT_JSON = ROOT / "outputs/prod2901_2940_value_delta_evaluator.json"
OUT_MD = ROOT / "outputs/prod2901_2940_value_delta_evaluator.md"

BLOCKED = [
    "real_world_profit_claim",
    "validated_savings_claim",
    "client_facing_value_claim",
    "production_activation",
    "automatic_memory_delete",
    "gpt_memory_api_execution",
    "value_delta_claim_with_low_input_quality"
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

def band(value):
    if value >= 500:
        return "HIGH_SYNTHETIC_VALUE"
    if value >= 200:
        return "MEDIUM_SYNTHETIC_VALUE"
    if value > 0:
        return "LOW_SYNTHETIC_VALUE"
    return "NO_FREEZABLE_VALUE"

def decision(row):
    if row.get("input_quality_outcome") == "BLOCK_EXECUTION":
        return "BLOCK_VALUE_DELTA"
    if row.get("frozen_value_allowed") is True:
        return "FREEZE_INTERNAL_SYNTHETIC_DELTA"
    return "PROVISIONAL_DELTA_HOLD_CLAIM"

def main():
    errors = []
    pack = read_json(PACK) if PACK.exists() else {}
    pack_out = read_json(PACK_OUT) if PACK_OUT.exists() else {}
    engine = read_json(ENGINE) if ENGINE.exists() else {}

    rows = pack.get("evaluated_preview", [])
    evaluated = []
    for row in rows:
        net = float(row.get("complexity_adjusted_net_value_delta", row.get("net_value_delta", 0)))
        item = dict(row)
        item["evaluator_decision"] = decision(row)
        item["value_band"] = band(net)
        evaluated.append(item)

    freeze_rows = [r for r in evaluated if r["evaluator_decision"] == "FREEZE_INTERNAL_SYNTHETIC_DELTA"]
    blocked_rows = [r for r in evaluated if r["evaluator_decision"] == "BLOCK_VALUE_DELTA"]
    provisional_rows = [r for r in evaluated if r["evaluator_decision"] == "PROVISIONAL_DELTA_HOLD_CLAIM"]

    total_gross = round(sum(float(r.get("gross_value", 0)) for r in evaluated), 2)
    total_confidence_adjusted = round(sum(float(r.get("confidence_adjusted_value", 0)) for r in evaluated), 2)
    total_complexity_adjusted_net = round(sum(float(r.get("complexity_adjusted_net_value_delta", r.get("net_value_delta", 0))) for r in evaluated), 2)
    freezable_value = round(sum(float(r.get("complexity_adjusted_net_value_delta", r.get("net_value_delta", 0))) for r in freeze_rows), 2)
    avg_confidence = round(sum(float(r.get("confidence_score", 0)) for r in evaluated) / max(len(evaluated), 1), 3)
    avg_complexity = round(sum(float(r.get("implementation_complexity_score", 0)) for r in evaluated) / max(len(evaluated), 1), 2)

    evaluator = {
        "version": "value_delta_evaluator.v0.1",
        "phase": PHASE,
        "input_pack": "product/memory/value_delta_synthetic_fixture_pack_v0_1.json",
        "summary": {
            "fixture_count": len(evaluated),
            "freeze_allowed_count": len(freeze_rows),
            "blocked_count": len(blocked_rows),
            "provisional_count": len(provisional_rows),
            "total_gross_value": total_gross,
            "total_confidence_adjusted_value": total_confidence_adjusted,
            "total_complexity_adjusted_net_value_delta": total_complexity_adjusted_net,
            "freezable_internal_synthetic_value": freezable_value,
            "average_confidence_score": avg_confidence,
            "average_implementation_complexity_score": avg_complexity
        },
        "evaluated_cases": evaluated,
        "claim_boundary": "Synthetic evaluator only. No real-world profit, ROI, savings or hallucination-reduction claim.",
        "recommended_next_phase": "PROD-2941..2980 - Value Delta Readiness Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "value_delta_evaluator",
        "implementation_complexity_weighted": True,
        "input_quality_weighted": True,
        "claim_boundary_required": True,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": evaluator["recommended_next_phase"]
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Value Delta Evaluator",
        "type": "object",
        "required": ["version", "phase", "summary", "evaluated_cases"]
    }

    doc = """# PROD-2901..2940 - Value Delta Evaluator

Evaluates the expanded synthetic fixture pack for the CASULO Exocortex Value Delta Engine.

The evaluator aggregates gross value, confidence-adjusted value, complexity-adjusted net value, freezable internal synthetic value, blocked cases and provisional cases.

Implementation complexity is weighted as a cost and multiplier. Input quality controls whether a delta can be frozen.

Boundary: synthetic evaluator only. No real-world profit, savings, ROI or hallucination-reduction claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(EVALUATOR, evaluator)

    decisions = {r["evaluator_decision"] for r in evaluated}
    bands = {r["value_band"] for r in evaluated}

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "pack_exists": PACK.exists(),
        "pack_output_exists": PACK_OUT.exists(),
        "pack_output_pass": pack_out.get("status") == "PASS",
        "engine_exists": ENGINE.exists(),
        "engine_has_value_components": len(engine.get("value_components", [])) >= 11,
        "fixture_count": len(evaluated),
        "has_freeze_decision": "FREEZE_INTERNAL_SYNTHETIC_DELTA" in decisions,
        "has_block_decision": "BLOCK_VALUE_DELTA" in decisions,
        "has_provisional_decision": "PROVISIONAL_DELTA_HOLD_CLAIM" in decisions,
        "freeze_count_positive": len(freeze_rows) > 0,
        "blocked_count_positive": len(blocked_rows) > 0,
        "provisional_count_positive": len(provisional_rows) > 0,
        "all_have_complexity_adjusted_delta": all("complexity_adjusted_net_value_delta" in r for r in evaluated),
        "all_have_complexity_score": all("implementation_complexity_score" in r for r in evaluated),
        "all_have_confidence_score": all("confidence_score" in r for r in evaluated),
        "freezable_value_positive": freezable_value > 0,
        "avg_confidence_valid": 0 <= avg_confidence <= 1,
        "avg_complexity_positive": avg_complexity > 0,
        "has_value_bands": len(bands) >= 2,
        "blocked_real_profit_claim": "real_world_profit_claim" in BLOCKED,
        "blocked_validated_savings_claim": "validated_savings_claim" in BLOCKED,
        "blocked_client_value_claim": "client_facing_value_claim" in BLOCKED,
        "blocked_low_quality_value_claim": "value_delta_claim_with_low_input_quality" in BLOCKED
    }

    if checks["fixture_count"] < 12:
        errors.append("fixture_count below 12")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "VALUE_DELTA_EVALUATOR_READY" if status == "PASS" else "VALUE_DELTA_EVALUATOR_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "evaluator": "product/memory/value_delta_evaluator_v0_1.json",
        "fixture_count": len(evaluated),
        "freeze_allowed_count": len(freeze_rows),
        "blocked_count": len(blocked_rows),
        "provisional_count": len(provisional_rows),
        "freezable_internal_synthetic_value": freezable_value,
        "total_complexity_adjusted_net_value_delta": total_complexity_adjusted_net,
        "average_confidence_score": avg_confidence,
        "average_implementation_complexity_score": avg_complexity,
        "recommended_next_phase": evaluator["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2901..2940 Value Delta Evaluator",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Fixtures: `{len(evaluated)}`",
        f"- Freeze allowed: `{len(freeze_rows)}`",
        f"- Blocked: `{len(blocked_rows)}`",
        f"- Provisional: `{len(provisional_rows)}`",
        f"- Freezable internal synthetic value: `{freezable_value}`",
        f"- Total complexity-adjusted net delta: `{total_complexity_adjusted_net}`",
        f"- Average complexity: `{avg_complexity}`",
        f"- Next: `{evaluator['recommended_next_phase']}`",
        "",
        "## Evaluated cases"
    ]
    for r in evaluated:
        report.append(f"- `{r['id']}` `{r['title']}` decision `{r['evaluator_decision']}` net `{r['complexity_adjusted_net_value_delta']}` band `{r['value_band']}`")
    report += ["", "## Boundary", "- Synthetic evaluator only.", "- No real-world savings/profit/ROI claim.", "", "## Errors"]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("fixtures:", len(evaluated))
    print("freeze_allowed:", len(freeze_rows))
    print("blocked:", len(blocked_rows))
    print("provisional:", len(provisional_rows))
    print("freezable_value:", freezable_value)
    print("avg_complexity:", avg_complexity)
    print("next:", evaluator["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3021..3060"
REQ_TAG = "product-expanded-test-matrix-pack-v0.1"

MATRIX_OUT = ROOT / "outputs/prod2981_3020_expanded_test_matrix_pack.json"
MATRIX_PACK = ROOT / "product/memory/expanded_test_matrix_pack_v0_1.json"
VALUE_GATE = ROOT / "product/memory/value_delta_readiness_gate_v0_1.json"

DOC = ROOT / "docs/product/577_EXOCORTEX_APEX_MATURITY_INDEX_CONTRACT.md"
CONTRACT = ROOT / "product/contracts/exocortex_apex_maturity_index.contract.json"
SCHEMA = ROOT / "product/schemas/exocortex_apex_maturity_index.schema.json"
INDEX = ROOT / "product/memory/exocortex_apex_maturity_index_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3021_3060_exocortex_apex_maturity_index_contract.json"
OUT_MD = ROOT / "outputs/prod3021_3060_exocortex_apex_maturity_index_contract.md"

POSITIVE_COMPONENTS = [
    "context_cleanliness_score",
    "memory_maturity_score",
    "state_grounding_score",
    "decision_recall_accuracy",
    "snapshot_recovery_score",
    "prompt_quality_score",
    "input_data_quality_score",
    "gate_compliance_score",
    "value_delta_confidence_score",
    "rework_avoidance_score",
    "development_velocity_score"
]

NEGATIVE_COMPONENTS = [
    "context_pressure",
    "stale_context_risk",
    "hallucination_risk_index",
    "uncontrolled_implementation_complexity",
    "claim_leakage_risk",
    "missing_context_rate"
]

USES = [
    "value_delta_weight",
    "operational_hallucination_index_input",
    "calibration_power_signal",
    "development_readiness_signal",
    "context_lifecycle_trigger",
    "future_business_packaging_signal"
]

MATURITY_BANDS = [
    {"min": 0, "max": 30, "band": "IMMATURE_HIGH_RISK"},
    {"min": 31, "max": 55, "band": "USABLE_UNSTABLE"},
    {"min": 56, "max": 75, "band": "GOOD_OPERATIONAL"},
    {"min": 76, "max": 90, "band": "MATURE_OPERATIONAL"},
    {"min": 91, "max": 100, "band": "APEX_OPERATIONAL"}
]

BLOCKED = [
    "real_world_profit_claim",
    "validated_savings_claim",
    "client_facing_value_claim",
    "validated_hallucination_reduction_claim",
    "production_activation",
    "automatic_memory_delete",
    "gpt_memory_api_execution",
    "business_package_pricing_claim"
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

def band(score):
    for b in MATURITY_BANDS:
        if b["min"] <= score <= b["max"]:
            return b["band"]
    return "UNKNOWN"

def sample_score(case):
    severity = case.get("severity", "medium")
    base = {"low": 86, "medium": 68, "high": 48, "critical": 24}.get(severity, 55)
    if case.get("requires_calibration"):
        base -= 4
    if case.get("complexity_hallucination_correlation_required"):
        base -= 5
    if case.get("requires_human_review"):
        base -= 6
    score = max(0, min(100, base))
    return {
        "case_id": case.get("id"),
        "category": case.get("category"),
        "severity": severity,
        "apex_maturity_score": score,
        "apex_band": band(score),
        "value_delta_weight": round(score / 100, 2),
        "hallucination_risk_adjustment": round((100 - score) / 100, 2),
        "calibration_required": case.get("requires_calibration", False)
    }

def main():
    errors = []
    matrix_out = read_json(MATRIX_OUT) if MATRIX_OUT.exists() else {}
    matrix_pack = read_json(MATRIX_PACK) if MATRIX_PACK.exists() else {}
    value_gate = read_json(VALUE_GATE) if VALUE_GATE.exists() else {}

    cases = matrix_pack.get("cases", [])
    scored_cases = [sample_score(c) for c in cases]
    avg_score = round(sum(x["apex_maturity_score"] for x in scored_cases) / max(len(scored_cases), 1), 2)
    bands = {x["apex_band"] for x in scored_cases}

    index = {
        "version": "exocortex_apex_maturity_index.v0.1",
        "phase": PHASE,
        "purpose": "Measure when the chat and Exocortex are at maximum operational maturity.",
        "definition": "Apex maturity is the state where context, memory, grounding, gates, snapshots, input quality, development velocity and Value Delta confidence are maximized while context pressure, stale context, hallucination risk, uncontrolled complexity and claim leakage are minimized.",
        "positive_components": POSITIVE_COMPONENTS,
        "negative_components": NEGATIVE_COMPONENTS,
        "uses": USES,
        "formula": {
            "positive_signal": "average positive component score",
            "negative_pressure": "average negative component score",
            "apex_maturity_score": "bounded positive_signal - negative_pressure adjustment",
            "value_delta_weight": "apex_maturity_score / 100",
            "hallucination_risk_adjustment": "(100 - apex_maturity_score) / 100"
        },
        "maturity_bands": MATURITY_BANDS,
        "synthetic_scored_cases": scored_cases,
        "summary": {
            "case_count": len(scored_cases),
            "average_apex_maturity_score": avg_score,
            "bands_present": sorted(bands)
        },
        "value_delta_relation": {
            "required": True,
            "rule": "Apex maturity increases Value Delta confidence and freeze readiness; low maturity reduces confidence or forces hold."
        },
        "hallucination_index_relation": {
            "required": True,
            "rule": "Low apex maturity increases operational hallucination risk; high maturity lowers risk but does not prove real-world reduction."
        },
        "business_packaging_boundary": {
            "future_use": True,
            "rule": "Business plans and pricing can later use maturity bands, but this phase does not define commercial packages."
        },
        "claim_boundary": "Synthetic/internal index contract only. No real-world ROI, savings, profit, client-facing or hallucination-reduction claim.",
        "recommended_next_phase": "PROD-3061..3100 - Calibration Plan for Real Sessions"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "apex_maturity_index_contract",
        "value_delta_relation_required": True,
        "hallucination_index_relation_required": True,
        "future_business_packaging_signal": True,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": index["recommended_next_phase"]
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Exocortex Apex Maturity Index",
        "type": "object",
        "required": ["version", "phase", "positive_components", "negative_components", "uses", "maturity_bands", "summary"]
    }

    doc = """# PROD-3021..3060 - Exocortex Apex Maturity Index Contract

Defines the Exocortex Apex Maturity Index.

The index measures when the chat and Exocortex are at maximum operational maturity: clean context, mature memory, strong state grounding, good snapshots, high decision recall, high input quality, gate compliance, Value Delta confidence and development velocity.

It also relates maturity to Value Delta and operational hallucination risk.

Boundary: synthetic/internal index contract only. No real-world ROI, savings, profit, client-facing or validated hallucination-reduction claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(INDEX, index)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "matrix_output_exists": MATRIX_OUT.exists(),
        "matrix_output_pass": matrix_out.get("status") == "PASS",
        "matrix_pack_exists": MATRIX_PACK.exists(),
        "value_gate_exists": VALUE_GATE.exists(),
        "prior_correlation_registered": value_gate.get("hallucination_index_correlation_extension", {}).get("name") == "implementation_complexity_hallucination_correlation",
        "positive_component_count": len(POSITIVE_COMPONENTS),
        "negative_component_count": len(NEGATIVE_COMPONENTS),
        "use_count": len(USES),
        "case_count": len(scored_cases),
        "average_score_positive": avg_score > 0,
        "has_value_delta_use": "value_delta_weight" in USES,
        "has_hallucination_use": "operational_hallucination_index_input" in USES,
        "has_calibration_use": "calibration_power_signal" in USES,
        "has_business_signal": "future_business_packaging_signal" in USES,
        "has_context_cleanliness": "context_cleanliness_score" in POSITIVE_COMPONENTS,
        "has_memory_maturity": "memory_maturity_score" in POSITIVE_COMPONENTS,
        "has_development_velocity": "development_velocity_score" in POSITIVE_COMPONENTS,
        "has_context_pressure": "context_pressure" in NEGATIVE_COMPONENTS,
        "has_hallucination_risk": "hallucination_risk_index" in NEGATIVE_COMPONENTS,
        "has_uncontrolled_complexity": "uncontrolled_implementation_complexity" in NEGATIVE_COMPONENTS,
        "has_apex_band": any(b["band"] == "APEX_OPERATIONAL" for b in MATURITY_BANDS),
        "value_delta_relation_required": index["value_delta_relation"]["required"] is True,
        "hallucination_index_relation_required": index["hallucination_index_relation"]["required"] is True,
        "business_packaging_boundary_present": index["business_packaging_boundary"]["future_use"] is True,
        "blocked_business_pricing_claim": "business_package_pricing_claim" in BLOCKED,
        "blocked_hallucination_reduction_claim": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["positive_component_count"] < 10:
        errors.append("positive_component_count below 10")
    if checks["negative_component_count"] < 6:
        errors.append("negative_component_count below 6")
    if checks["case_count"] < 48:
        errors.append("case_count below 48")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "EXOCORTEX_APEX_MATURITY_INDEX_CONTRACT_READY" if status == "PASS" else "EXOCORTEX_APEX_MATURITY_INDEX_CONTRACT_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "index": "product/memory/exocortex_apex_maturity_index_v0_1.json",
        "positive_component_count": len(POSITIVE_COMPONENTS),
        "negative_component_count": len(NEGATIVE_COMPONENTS),
        "case_count": len(scored_cases),
        "average_apex_maturity_score": avg_score,
        "recommended_next_phase": index["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3021..3060 Exocortex Apex Maturity Index Contract",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Positive components: `{len(POSITIVE_COMPONENTS)}`",
        f"- Negative components: `{len(NEGATIVE_COMPONENTS)}`",
        f"- Cases scored: `{len(scored_cases)}`",
        f"- Average apex maturity score: `{avg_score}`",
        f"- Next: `{index['recommended_next_phase']}`",
        "",
        "## Relations",
        "- Value Delta: registered.",
        "- Operational hallucination index: registered.",
        "- Future business packaging signal: registered.",
        "",
        "## Boundary",
        "- Synthetic/internal index only.",
        "- No real-world savings/profit/ROI/hallucination-reduction claim.",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("positive_components:", len(POSITIVE_COMPONENTS))
    print("negative_components:", len(NEGATIVE_COMPONENTS))
    print("cases:", len(scored_cases))
    print("avg_apex:", avg_score)
    print("next:", index["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

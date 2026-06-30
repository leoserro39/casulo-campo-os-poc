#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2981..3020"
REQ_TAG = "product-value-delta-readiness-gate-v0.1"

READINESS_OUT = ROOT / "outputs/prod2941_2980_value_delta_readiness_gate.json"
READINESS_GATE = ROOT / "product/memory/value_delta_readiness_gate_v0_1.json"

DOC = ROOT / "docs/product/576_EXPANDED_TEST_MATRIX_PACK.md"
CONTRACT = ROOT / "product/contracts/expanded_test_matrix_pack.contract.json"
SCHEMA = ROOT / "product/schemas/expanded_test_matrix_pack.schema.json"
PACK = ROOT / "product/memory/expanded_test_matrix_pack_v0_1.json"
OUT_JSON = ROOT / "outputs/prod2981_3020_expanded_test_matrix_pack.json"
OUT_MD = ROOT / "outputs/prod2981_3020_expanded_test_matrix_pack.md"

BLOCKED = [
    "real_world_profit_claim",
    "validated_savings_claim",
    "client_facing_value_claim",
    "validated_hallucination_reduction_claim",
    "production_activation",
    "automatic_memory_delete",
    "gpt_memory_api_execution"
]

CATEGORIES = [
    "exocortex_snapshot",
    "memory_state_governor",
    "prompt_quality",
    "input_data_quality",
    "value_delta",
    "implementation_complexity",
    "operational_hallucination",
    "claim_boundary",
    "contradiction_hold",
    "stale_context",
    "context_pressure",
    "calibration_candidate"
]

SEVERITIES = ["low", "medium", "high", "critical"]

def make_case(i, category, severity):
    return {
        "id": f"ETM-{i:03d}",
        "category": category,
        "severity": severity,
        "title": f"{category}_{severity}_case_{i:03d}",
        "input_quality_outcome": {
            "low": "INPUT_ACCEPTED",
            "medium": "CLARIFICATION_REQUIRED",
            "high": "EVIDENCE_REQUIRED",
            "critical": "BLOCK_EXECUTION"
        }[severity],
        "expected_gate": {
            "low": "ALLOW_INTERNAL_SYNTHETIC_BENCHMARK",
            "medium": "HOLD_REVIEW",
            "high": "HOLD_EVIDENCE_REVIEW",
            "critical": "BLOCK_EXECUTION"
        }[severity],
        "expected_claim_boundary": "internal_synthetic_only",
        "requires_human_review": severity in ["medium", "high", "critical"],
        "requires_calibration": category in [
            "value_delta",
            "implementation_complexity",
            "operational_hallucination",
            "calibration_candidate"
        ],
        "complexity_hallucination_correlation_required": category in [
            "implementation_complexity",
            "operational_hallucination",
            "value_delta"
        ],
        "blocked_actions": BLOCKED
    }

def build_cases():
    cases = []
    i = 1
    for category in CATEGORIES:
        for severity in SEVERITIES:
            cases.append(make_case(i, category, severity))
            i += 1
    return cases

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
    readiness_out = read_json(READINESS_OUT) if READINESS_OUT.exists() else {}
    readiness_gate = read_json(READINESS_GATE) if READINESS_GATE.exists() else {}

    cases = build_cases()
    categories = {c["category"] for c in cases}
    severities = {c["severity"] for c in cases}
    outcomes = {c["input_quality_outcome"] for c in cases}
    gates = {c["expected_gate"] for c in cases}

    calibration_cases = [c for c in cases if c["requires_calibration"]]
    review_cases = [c for c in cases if c["requires_human_review"]]
    correlation_cases = [c for c in cases if c["complexity_hallucination_correlation_required"]]

    pack = {
        "version": "expanded_test_matrix_pack.v0.1",
        "phase": PHASE,
        "purpose": "Expanded synthetic matrix for CASULO Exocortex, Value Delta and operational hallucination calibration planning.",
        "case_count": len(cases),
        "categories": CATEGORIES,
        "severities": SEVERITIES,
        "cases": cases,
        "coverage_summary": {
            "category_count": len(categories),
            "severity_count": len(severities),
            "calibration_case_count": len(calibration_cases),
            "human_review_case_count": len(review_cases),
            "complexity_hallucination_correlation_case_count": len(correlation_cases)
        },
        "correlation_extension": {
            "name": "implementation_complexity_hallucination_correlation",
            "required": True,
            "source_phase": "PROD-2941..2980",
            "calibration_status": "planned_not_validated"
        },
        "claim_boundary": "Expanded synthetic matrix only. Not evidence of real performance, ROI, savings or hallucination reduction.",
        "recommended_next_phase": "PROD-3021..3060 - Calibration Plan for Real Sessions"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "expanded_synthetic_test_matrix",
        "case_count": len(cases),
        "blocked_actions": BLOCKED,
        "recommended_next_phase": pack["recommended_next_phase"]
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Expanded Test Matrix Pack",
        "type": "object",
        "required": ["version", "phase", "case_count", "categories", "cases", "coverage_summary"]
    }

    doc = """# PROD-2981..3020 - Expanded Test Matrix Pack

Creates an expanded synthetic test matrix for CASULO Exocortex, Value Delta and operational hallucination calibration planning.

The matrix covers snapshots, memory state, prompt quality, input data quality, value delta, implementation complexity, operational hallucination, claim boundaries, contradiction hold, stale context, context pressure and calibration candidates.

Boundary: synthetic matrix only. No real-world profit, savings, ROI or validated hallucination-reduction claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(PACK, pack)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "readiness_output_exists": READINESS_OUT.exists(),
        "readiness_output_pass": readiness_out.get("status") == "PASS",
        "readiness_gate_exists": READINESS_GATE.exists(),
        "readiness_gate_internal_only": readiness_out.get("decision") == "APPROVED_FOR_INTERNAL_SYNTHETIC_BENCHMARK_ONLY",
        "prior_correlation_registered": readiness_gate.get("hallucination_index_correlation_extension", {}).get("name") == "implementation_complexity_hallucination_correlation",
        "case_count": len(cases),
        "category_count": len(categories),
        "severity_count": len(severities),
        "has_exocortex_snapshot": "exocortex_snapshot" in categories,
        "has_memory_state_governor": "memory_state_governor" in categories,
        "has_prompt_quality": "prompt_quality" in categories,
        "has_input_data_quality": "input_data_quality" in categories,
        "has_value_delta": "value_delta" in categories,
        "has_implementation_complexity": "implementation_complexity" in categories,
        "has_operational_hallucination": "operational_hallucination" in categories,
        "has_claim_boundary": "claim_boundary" in categories,
        "has_contradiction_hold": "contradiction_hold" in categories,
        "has_stale_context": "stale_context" in categories,
        "has_context_pressure": "context_pressure" in categories,
        "has_calibration_candidate": "calibration_candidate" in categories,
        "has_all_severities": set(SEVERITIES).issubset(severities),
        "has_block_execution_outcome": "BLOCK_EXECUTION" in outcomes,
        "has_input_accepted_outcome": "INPUT_ACCEPTED" in outcomes,
        "has_block_execution_gate": "BLOCK_EXECUTION" in gates,
        "calibration_cases_positive": len(calibration_cases) > 0,
        "review_cases_positive": len(review_cases) > 0,
        "correlation_cases_positive": len(correlation_cases) > 0,
        "blocked_real_profit_claim": "real_world_profit_claim" in BLOCKED,
        "blocked_validated_savings_claim": "validated_savings_claim" in BLOCKED,
        "blocked_hallucination_reduction_claim": "validated_hallucination_reduction_claim" in BLOCKED
    }

    if checks["case_count"] < 48:
        errors.append("case_count below 48")
    if checks["category_count"] < 12:
        errors.append("category_count below 12")
    if checks["severity_count"] < 4:
        errors.append("severity_count below 4")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "EXPANDED_TEST_MATRIX_PACK_READY" if status == "PASS" else "EXPANDED_TEST_MATRIX_PACK_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "pack": "product/memory/expanded_test_matrix_pack_v0_1.json",
        "case_count": len(cases),
        "category_count": len(categories),
        "severity_count": len(severities),
        "calibration_case_count": len(calibration_cases),
        "human_review_case_count": len(review_cases),
        "complexity_hallucination_correlation_case_count": len(correlation_cases),
        "recommended_next_phase": pack["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2981..3020 Expanded Test Matrix Pack",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Cases: `{len(cases)}`",
        f"- Categories: `{len(categories)}`",
        f"- Severities: `{len(severities)}`",
        f"- Calibration cases: `{len(calibration_cases)}`",
        f"- Correlation cases: `{len(correlation_cases)}`",
        f"- Next: `{pack['recommended_next_phase']}`",
        "",
        "## Categories"
    ]
    for cat in sorted(categories):
        report.append(f"- `{cat}`")
    report += ["", "## Boundary", "- Expanded synthetic test matrix only.", "- No real-world claim.", "", "## Errors"]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("cases:", len(cases))
    print("categories:", len(categories))
    print("severities:", len(severities))
    print("calibration_cases:", len(calibration_cases))
    print("correlation_cases:", len(correlation_cases))
    print("next:", pack["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

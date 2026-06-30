#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2781..2820"
REQ_TAG = "product-exocortex-decision-policy-matrix-v0.1"

MATRIX_OUT = ROOT / "outputs/prod2741_2780_exocortex_decision_policy_matrix.json"

DOC = ROOT / "docs/product/571_PROMPT_INPUT_DATA_QUALITY_GATE.md"
CONTRACT = ROOT / "product/contracts/prompt_input_data_quality_gate.contract.json"
SCHEMA = ROOT / "product/schemas/prompt_input_data_quality_gate.schema.json"
GATE = ROOT / "product/memory/prompt_input_data_quality_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod2781_2820_prompt_input_data_quality_gate.json"
OUT_MD = ROOT / "outputs/prod2781_2820_prompt_input_data_quality_gate.md"

METRICS = [
    "prompt_quality_score",
    "input_data_quality_score",
    "requirement_completeness",
    "ambiguity_risk",
    "evidence_quality",
    "schema_fit",
    "missing_context_rate",
    "garbage_in_risk",
    "clarification_needed",
    "value_delta_confidence_adjustment"
]

OUTCOMES = [
    "INPUT_ACCEPTED",
    "CLARIFICATION_REQUIRED",
    "EVIDENCE_REQUIRED",
    "SCHEMA_REQUIRED",
    "REVIEW_PACKET_REQUIRED",
    "BLOCK_EXECUTION"
]

BLOCKED = [
    "implementation_execution_with_low_input_quality",
    "value_delta_claim_with_low_input_quality",
    "client_facing_claim",
    "production_activation",
    "validated_performance_claim",
    "automatic_memory_delete",
    "gpt_memory_api_execution"
]

CASES = [
    {
        "id": "IQ-001",
        "title": "simple_status_question",
        "task_type": "simple_state_question",
        "prompt_quality_score": 82,
        "input_data_quality_score": 78,
        "requirement_completeness": 75,
        "ambiguity_risk": 20,
        "evidence_quality": 70,
        "schema_fit": 70,
        "missing_context_rate": 20,
        "garbage_in_risk": 18
    },
    {
        "id": "IQ-002",
        "title": "parser_without_workbook_schema",
        "task_type": "parser_generation_request",
        "prompt_quality_score": 55,
        "input_data_quality_score": 25,
        "requirement_completeness": 35,
        "ambiguity_risk": 70,
        "evidence_quality": 20,
        "schema_fit": 15,
        "missing_context_rate": 75,
        "garbage_in_risk": 80
    },
    {
        "id": "IQ-003",
        "title": "parser_with_workbook_inventory",
        "task_type": "parser_generation_request",
        "prompt_quality_score": 82,
        "input_data_quality_score": 86,
        "requirement_completeness": 84,
        "ambiguity_risk": 18,
        "evidence_quality": 82,
        "schema_fit": 88,
        "missing_context_rate": 15,
        "garbage_in_risk": 16
    },
    {
        "id": "IQ-004",
        "title": "client_claim_weak_evidence",
        "task_type": "client_claim_request",
        "prompt_quality_score": 74,
        "input_data_quality_score": 42,
        "requirement_completeness": 50,
        "ambiguity_risk": 55,
        "evidence_quality": 30,
        "schema_fit": 60,
        "missing_context_rate": 55,
        "garbage_in_risk": 65
    },
    {
        "id": "IQ-005",
        "title": "architecture_ambiguous_scope",
        "task_type": "solution_design_request",
        "prompt_quality_score": 48,
        "input_data_quality_score": 50,
        "requirement_completeness": 38,
        "ambiguity_risk": 78,
        "evidence_quality": 45,
        "schema_fit": 55,
        "missing_context_rate": 70,
        "garbage_in_risk": 68
    },
    {
        "id": "IQ-006",
        "title": "value_delta_estimate_low_input",
        "task_type": "value_delta_estimate",
        "prompt_quality_score": 58,
        "input_data_quality_score": 40,
        "requirement_completeness": 45,
        "ambiguity_risk": 60,
        "evidence_quality": 35,
        "schema_fit": 50,
        "missing_context_rate": 62,
        "garbage_in_risk": 82
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

def evaluate_case(c):
    prompt = c["prompt_quality_score"]
    data = c["input_data_quality_score"]
    complete = c["requirement_completeness"]
    ambiguity = c["ambiguity_risk"]
    evidence = c["evidence_quality"]
    schema = c["schema_fit"]
    missing = c["missing_context_rate"]
    garbage = c["garbage_in_risk"]

    quality = round((prompt + data + complete + evidence + schema + (100 - ambiguity) + (100 - missing) + (100 - garbage)) / 8, 2)

    clarification_needed = ambiguity >= 60 or missing >= 60 or complete < 50
    value_delta_confidence_adjustment = round((quality - 70) / 100, 2)

    if c["task_type"] == "client_claim_request" and evidence < 60:
        outcome = "EVIDENCE_REQUIRED"
    elif c["task_type"] == "parser_generation_request" and schema < 60:
        outcome = "SCHEMA_REQUIRED"
    elif garbage >= 75:
        outcome = "BLOCK_EXECUTION"
    elif clarification_needed:
        outcome = "CLARIFICATION_REQUIRED"
    elif quality < 65:
        outcome = "REVIEW_PACKET_REQUIRED"
    else:
        outcome = "INPUT_ACCEPTED"

    return {
        "id": c["id"],
        "title": c["title"],
        "task_type": c["task_type"],
        "quality_score": quality,
        "outcome": outcome,
        "clarification_needed": clarification_needed,
        "value_delta_confidence_adjustment": value_delta_confidence_adjustment,
        "input_quality_affects_hallucination": True,
        "input_quality_affects_value_delta": True,
        "metrics": {m: c[m] for m in c if m in METRICS}
    }

def main():
    errors = []
    matrix_out = read_json(MATRIX_OUT) if MATRIX_OUT.exists() else {}
    evaluations = [evaluate_case(c) for c in CASES]
    outcomes = {e["outcome"] for e in evaluations}

    gate = {
        "version": "prompt_input_data_quality_gate.v0.1",
        "phase": PHASE,
        "purpose": "Gate prompt and input data quality before execution, claim, value-delta calculation or high-risk recommendation.",
        "metrics": METRICS,
        "outcomes": OUTCOMES,
        "cases": CASES,
        "evaluations": evaluations,
        "rules": [
            "Low schema fit in parser tasks requires SCHEMA_REQUIRED.",
            "Weak evidence in client-claim tasks requires EVIDENCE_REQUIRED.",
            "High garbage-in risk can BLOCK_EXECUTION.",
            "High ambiguity or missing context requires CLARIFICATION_REQUIRED.",
            "Low input quality reduces Value Delta confidence.",
            "Input quality affects operational hallucination risk."
        ],
        "recommended_next_phase": "PROD-2821..2860 - Exocortex Value Delta Engine Contract"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "prompt_input_data_quality_gate",
        "quality_affects_hallucination": True,
        "quality_affects_value_delta": True,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Prompt and Input Data Quality Gate",
        "type": "object",
        "required": ["version", "phase", "metrics", "outcomes", "evaluations"]
    }

    doc = """# PROD-2781..2820 - Prompt and Input Data Quality Gate

Defines the gate for prompt quality and input data quality.

The gate is conditional: it applies when output quality depends directly on prompt, requirement, evidence, schema or data quality.

Input quality affects hallucination risk and Value Delta confidence.

Boundary: gate contract only. No client-facing claim, no production activation and no validated performance claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(GATE, gate)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "matrix_output_exists": MATRIX_OUT.exists(),
        "matrix_output_pass": matrix_out.get("status") == "PASS",
        "metric_count": len(METRICS),
        "outcome_count": len(OUTCOMES),
        "case_count": len(CASES),
        "evaluation_count": len(evaluations),
        "has_prompt_quality": "prompt_quality_score" in METRICS,
        "has_input_data_quality": "input_data_quality_score" in METRICS,
        "has_ambiguity": "ambiguity_risk" in METRICS,
        "has_evidence_quality": "evidence_quality" in METRICS,
        "has_schema_fit": "schema_fit" in METRICS,
        "has_garbage_in": "garbage_in_risk" in METRICS,
        "has_value_delta_adjustment": "value_delta_confidence_adjustment" in METRICS,
        "has_input_accepted": "INPUT_ACCEPTED" in outcomes,
        "has_clarification_required": "CLARIFICATION_REQUIRED" in outcomes,
        "has_evidence_required": "EVIDENCE_REQUIRED" in outcomes,
        "has_schema_required": "SCHEMA_REQUIRED" in outcomes,
        "has_block_execution_or_review": "BLOCK_EXECUTION" in outcomes or "REVIEW_PACKET_REQUIRED" in outcomes,
        "quality_affects_hallucination": contract["quality_affects_hallucination"] is True,
        "quality_affects_value_delta": contract["quality_affects_value_delta"] is True,
        "value_delta_claim_blocked": "value_delta_claim_with_low_input_quality" in BLOCKED,
        "client_claim_blocked": "client_facing_claim" in BLOCKED,
        "production_blocked": "production_activation" in BLOCKED,
        "performance_claim_blocked": "validated_performance_claim" in BLOCKED
    }

    if checks["metric_count"] < 10:
        errors.append("metric_count below 10")
    if checks["case_count"] < 6:
        errors.append("case_count below 6")
    if checks["evaluation_count"] != checks["case_count"]:
        errors.append("evaluation_count mismatch")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "PROMPT_INPUT_DATA_QUALITY_GATE_READY" if status == "PASS" else "PROMPT_INPUT_DATA_QUALITY_GATE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gate": "product/memory/prompt_input_data_quality_gate_v0_1.json",
        "metric_count": len(METRICS),
        "case_count": len(CASES),
        "evaluation_count": len(evaluations),
        "outcomes": sorted(outcomes),
        "recommended_next_phase": gate["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2781..2820 Prompt and Input Data Quality Gate",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Metrics: `{len(METRICS)}`",
        f"- Cases: `{len(CASES)}`",
        f"- Next: `{gate['recommended_next_phase']}`",
        "",
        "## Evaluations"
    ]
    for e in evaluations:
        report.append(f"- `{e['id']}` `{e['title']}` score `{e['quality_score']}` outcome `{e['outcome']}`")
    report += ["", "## Errors"]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("metrics:", len(METRICS))
    print("cases:", len(CASES))
    print("outcomes:", sorted(outcomes))
    print("next:", gate["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

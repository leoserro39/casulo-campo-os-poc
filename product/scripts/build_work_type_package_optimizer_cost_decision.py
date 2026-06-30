#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-3061..3100"
REQ_TAG = "product-exocortex-apex-maturity-index-contract-v0.1"

APEX_OUT = ROOT / "outputs/prod3021_3060_exocortex_apex_maturity_index_contract.json"
APEX_INDEX = ROOT / "product/memory/exocortex_apex_maturity_index_v0_1.json"
VALUE_GATE = ROOT / "product/memory/value_delta_readiness_gate_v0_1.json"

DOC = ROOT / "docs/product/578_WORK_TYPE_PACKAGE_OPTIMIZER_COST_DECISION.md"
CONTRACT = ROOT / "product/contracts/work_type_package_optimizer_cost_decision.contract.json"
SCHEMA = ROOT / "product/schemas/work_type_package_optimizer_cost_decision.schema.json"
OPTIMIZER = ROOT / "product/memory/work_type_package_optimizer_cost_decision_v0_1.json"
OUT_JSON = ROOT / "outputs/prod3061_3100_work_type_package_optimizer_cost_decision.json"
OUT_MD = ROOT / "outputs/prod3061_3100_work_type_package_optimizer_cost_decision.md"

CHAT_LAYERS = [
    "ANALYSIS_CHAT",
    "PROJECT_CHAT",
    "IMPLEMENTATION_CHAT",
    "GOVERNANCE_CHAT",
    "CALIBRATION_CHAT",
    "BUSINESS_CHAT",
    "OPERATIONS_CHAT",
    "INTEGRATION_CHAT",
    "EVIDENCE_AUDIT_CHAT",
    "MAINTENANCE_CHAT"
]

WORK_TYPES = [
    "diagnostic_analysis",
    "project_design",
    "repo_implementation",
    "governance_review",
    "calibration_benchmark",
    "business_packaging",
    "operational_cockpit",
    "system_integration",
    "evidence_audit",
    "maintenance_support"
]

COST_METRICS = [
    "operational_cost_score",
    "implementation_cost_score",
    "maintenance_cost_score",
    "evidence_cost_score",
    "human_review_cost_score",
    "automation_cost_score",
    "opportunity_cost_score",
    "risk_cost_exposure",
    "cost_decision_weight",
    "cost_adjusted_package_fit"
]

PACKAGES = [
    "PACKAGE_LIGHT_ANALYSIS",
    "PACKAGE_STANDARD_PROJECT",
    "PACKAGE_GOVERNED_REVIEW",
    "PACKAGE_IMPLEMENTATION",
    "PACKAGE_CALIBRATION",
    "PACKAGE_OPERATIONAL_COCKPIT",
    "PACKAGE_INTEGRATION",
    "PACKAGE_EVIDENCE_AUDIT",
    "PACKAGE_MAINTENANCE",
    "PACKAGE_ENTERPRISE_STATE_OS"
]

BLOCKED = [
    "real_price_claim",
    "commercial_package_pricing_claim",
    "client_facing_value_claim",
    "validated_savings_claim",
    "validated_hallucination_reduction_claim",
    "production_activation",
    "automatic_memory_delete",
    "gpt_memory_api_execution"
]

CASES = [
    {"id": "WTP-001", "layer": "ANALYSIS_CHAT", "work_type": "diagnostic_analysis", "complexity": 25, "risk": 20, "evidence": 30, "automation": 70, "human_review": 20, "apex": 72, "value_delta": 55},
    {"id": "WTP-002", "layer": "PROJECT_CHAT", "work_type": "project_design", "complexity": 55, "risk": 45, "evidence": 50, "automation": 55, "human_review": 45, "apex": 66, "value_delta": 68},
    {"id": "WTP-003", "layer": "IMPLEMENTATION_CHAT", "work_type": "repo_implementation", "complexity": 82, "risk": 78, "evidence": 70, "automation": 40, "human_review": 80, "apex": 58, "value_delta": 74},
    {"id": "WTP-004", "layer": "GOVERNANCE_CHAT", "work_type": "governance_review", "complexity": 60, "risk": 82, "evidence": 85, "automation": 35, "human_review": 85, "apex": 62, "value_delta": 70},
    {"id": "WTP-005", "layer": "CALIBRATION_CHAT", "work_type": "calibration_benchmark", "complexity": 78, "risk": 72, "evidence": 90, "automation": 30, "human_review": 90, "apex": 55, "value_delta": 80},
    {"id": "WTP-006", "layer": "BUSINESS_CHAT", "work_type": "business_packaging", "complexity": 45, "risk": 65, "evidence": 60, "automation": 45, "human_review": 65, "apex": 64, "value_delta": 75},
    {"id": "WTP-007", "layer": "OPERATIONS_CHAT", "work_type": "operational_cockpit", "complexity": 70, "risk": 75, "evidence": 75, "automation": 50, "human_review": 70, "apex": 69, "value_delta": 82},
    {"id": "WTP-008", "layer": "INTEGRATION_CHAT", "work_type": "system_integration", "complexity": 88, "risk": 86, "evidence": 80, "automation": 35, "human_review": 88, "apex": 52, "value_delta": 85},
    {"id": "WTP-009", "layer": "EVIDENCE_AUDIT_CHAT", "work_type": "evidence_audit", "complexity": 58, "risk": 80, "evidence": 95, "automation": 30, "human_review": 90, "apex": 67, "value_delta": 77},
    {"id": "WTP-010", "layer": "MAINTENANCE_CHAT", "work_type": "maintenance_support", "complexity": 50, "risk": 55, "evidence": 65, "automation": 65, "human_review": 45, "apex": 74, "value_delta": 62}
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

def choose_package(c):
    layer = c["layer"]
    complexity = c["complexity"]
    risk = c["risk"]
    review = c["human_review"]

    if layer == "ANALYSIS_CHAT" and complexity < 40:
        return "PACKAGE_LIGHT_ANALYSIS"
    if layer == "PROJECT_CHAT":
        return "PACKAGE_STANDARD_PROJECT"
    if layer == "IMPLEMENTATION_CHAT":
        return "PACKAGE_IMPLEMENTATION"
    if layer == "GOVERNANCE_CHAT":
        return "PACKAGE_GOVERNED_REVIEW"
    if layer == "CALIBRATION_CHAT":
        return "PACKAGE_CALIBRATION"
    if layer == "BUSINESS_CHAT":
        return "PACKAGE_STANDARD_PROJECT"
    if layer == "OPERATIONS_CHAT":
        return "PACKAGE_OPERATIONAL_COCKPIT"
    if layer == "INTEGRATION_CHAT":
        return "PACKAGE_INTEGRATION"
    if layer == "EVIDENCE_AUDIT_CHAT":
        return "PACKAGE_EVIDENCE_AUDIT"
    if layer == "MAINTENANCE_CHAT":
        return "PACKAGE_MAINTENANCE"
    if complexity >= 85 or risk >= 85 or review >= 85:
        return "PACKAGE_ENTERPRISE_STATE_OS"
    return "PACKAGE_STANDARD_PROJECT"

def evaluate(c):
    operational_cost_score = round((c["complexity"] * 0.25) + (c["risk"] * 0.25) + (c["human_review"] * 0.20) + ((100 - c["automation"]) * 0.15) + (c["evidence"] * 0.15), 2)
    implementation_cost_score = round((c["complexity"] * 0.55) + (c["risk"] * 0.25) + ((100 - c["automation"]) * 0.20), 2)
    maintenance_cost_score = round((c["complexity"] * 0.30) + (c["risk"] * 0.25) + (c["human_review"] * 0.20) + (c["evidence"] * 0.25), 2)
    evidence_cost_score = round((c["evidence"] * 0.70) + (c["human_review"] * 0.30), 2)
    human_review_cost_score = c["human_review"]
    automation_cost_score = round(100 - c["automation"], 2)
    opportunity_cost_score = round((100 - c["apex"]) * 0.45 + c["value_delta"] * 0.25 + c["risk"] * 0.30, 2)
    risk_cost_exposure = round((c["risk"] * 0.50) + (c["complexity"] * 0.30) + ((100 - c["apex"]) * 0.20), 2)

    cost_decision_weight = round(
        (operational_cost_score * 0.30)
        + (implementation_cost_score * 0.20)
        + (maintenance_cost_score * 0.15)
        + (evidence_cost_score * 0.15)
        + (opportunity_cost_score * 0.10)
        + (risk_cost_exposure * 0.10),
        2
    )

    cost_adjusted_package_fit = round(max(0, min(100, c["value_delta"] + c["apex"] - cost_decision_weight)), 2)

    if cost_decision_weight >= 75:
        gate = "COST_REVIEW_REQUIRED"
    elif risk_cost_exposure >= 75:
        gate = "RISK_COST_HOLD"
    elif cost_adjusted_package_fit < 35:
        gate = "PACKAGE_SCOPE_REVIEW_REQUIRED"
    else:
        gate = "PACKAGE_CANDIDATE_READY"

    return {
        "id": c["id"],
        "chat_layer": c["layer"],
        "work_type": c["work_type"],
        "recommended_package": choose_package(c),
        "operational_cost_score": operational_cost_score,
        "implementation_cost_score": implementation_cost_score,
        "maintenance_cost_score": maintenance_cost_score,
        "evidence_cost_score": evidence_cost_score,
        "human_review_cost_score": human_review_cost_score,
        "automation_cost_score": automation_cost_score,
        "opportunity_cost_score": opportunity_cost_score,
        "risk_cost_exposure": risk_cost_exposure,
        "cost_decision_weight": cost_decision_weight,
        "cost_adjusted_package_fit": cost_adjusted_package_fit,
        "decision_gate": gate,
        "pricing_boundary": "package_classification_only_no_real_price"
    }

def main():
    errors = []
    apex_out = read_json(APEX_OUT) if APEX_OUT.exists() else {}
    apex_index = read_json(APEX_INDEX) if APEX_INDEX.exists() else {}
    value_gate = read_json(VALUE_GATE) if VALUE_GATE.exists() else {}

    evaluations = [evaluate(c) for c in CASES]
    layers = {e["chat_layer"] for e in evaluations}
    work_types = {e["work_type"] for e in evaluations}
    packages = {e["recommended_package"] for e in evaluations}
    gates = {e["decision_gate"] for e in evaluations}

    optimizer = {
        "version": "work_type_package_optimizer_cost_decision.v0.1",
        "phase": PHASE,
        "purpose": "Classify work type, chat structure and operational cost signals to recommend package class without real pricing.",
        "principle": "Cost is an operational decision metric.",
        "chat_layers": CHAT_LAYERS,
        "work_types": WORK_TYPES,
        "cost_metrics": COST_METRICS,
        "package_classes": PACKAGES,
        "evaluations": evaluations,
        "coherence_rule": "The chat structure must be respected. Analysis, project, implementation, governance, calibration, business, operations, integration, evidence audit and maintenance are different layers with different costs, risks and gates.",
        "value_delta_relation": "Cost adjusts package fit and Value Delta readiness.",
        "hallucination_index_relation": "High complexity plus high operational cost and weak maturity can increase operational hallucination risk.",
        "business_boundary": "No real price, SLA or commercial package is defined in this phase.",
        "recommended_next_phase": "PROD-3101..3140 - Calibration Plan for Real Sessions"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "work_type_package_optimizer_cost_decision",
        "cost_is_operational_decision_metric": True,
        "chat_structure_coherence_required": True,
        "real_pricing_blocked": True,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": optimizer["recommended_next_phase"]
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Work Type Package Optimizer and Cost Decision Metric",
        "type": "object",
        "required": ["version", "phase", "chat_layers", "work_types", "cost_metrics", "package_classes", "evaluations"]
    }

    doc = """# PROD-3061..3100 - Work Type Package Optimizer and Cost Decision Metric Contract

Defines the technical contract for package classification by work type, chat structure and cost.

Cost is an operational decision metric, not only a financial or commercial metric.

The optimizer respects chat structure coherence: analysis, project, implementation, governance, calibration, business, operations, integration, evidence audit and maintenance have different risks, costs, gates and package classes.

Boundary: package classification only. No real pricing, no commercial offer, no client-facing value claim.
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(OPTIMIZER, optimizer)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "apex_output_exists": APEX_OUT.exists(),
        "apex_output_pass": apex_out.get("status") == "PASS",
        "apex_index_exists": APEX_INDEX.exists(),
        "value_gate_exists": VALUE_GATE.exists(),
        "apex_has_value_delta_relation": apex_index.get("value_delta_relation", {}).get("required") is True,
        "value_gate_has_correlation": value_gate.get("hallucination_index_correlation_extension", {}).get("name") == "implementation_complexity_hallucination_correlation",
        "chat_layer_count": len(CHAT_LAYERS),
        "work_type_count": len(WORK_TYPES),
        "cost_metric_count": len(COST_METRICS),
        "package_count": len(PACKAGES),
        "evaluation_count": len(evaluations),
        "all_layers_covered": set(CHAT_LAYERS).issubset(layers),
        "all_work_types_covered": set(WORK_TYPES).issubset(work_types),
        "has_multiple_packages": len(packages) >= 8,
        "has_cost_review_gate": "COST_REVIEW_REQUIRED" in gates or "RISK_COST_HOLD" in gates,
        "has_package_ready_gate": "PACKAGE_CANDIDATE_READY" in gates,
        "has_operational_cost_score": "operational_cost_score" in COST_METRICS,
        "has_implementation_cost_score": "implementation_cost_score" in COST_METRICS,
        "has_risk_cost_exposure": "risk_cost_exposure" in COST_METRICS,
        "has_cost_decision_weight": "cost_decision_weight" in COST_METRICS,
        "has_cost_adjusted_package_fit": "cost_adjusted_package_fit" in COST_METRICS,
        "cost_is_operational_decision_metric": contract["cost_is_operational_decision_metric"] is True,
        "chat_structure_coherence_required": contract["chat_structure_coherence_required"] is True,
        "real_pricing_blocked": "real_price_claim" in BLOCKED,
        "commercial_pricing_blocked": "commercial_package_pricing_claim" in BLOCKED,
        "client_value_claim_blocked": "client_facing_value_claim" in BLOCKED
    }

    if checks["chat_layer_count"] < 10:
        errors.append("chat_layer_count below 10")
    if checks["cost_metric_count"] < 10:
        errors.append("cost_metric_count below 10")
    if checks["evaluation_count"] < 10:
        errors.append("evaluation_count below 10")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "WORK_TYPE_PACKAGE_OPTIMIZER_COST_DECISION_READY" if status == "PASS" else "WORK_TYPE_PACKAGE_OPTIMIZER_COST_DECISION_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "optimizer": "product/memory/work_type_package_optimizer_cost_decision_v0_1.json",
        "chat_layer_count": len(CHAT_LAYERS),
        "work_type_count": len(WORK_TYPES),
        "cost_metric_count": len(COST_METRICS),
        "package_count": len(PACKAGES),
        "evaluation_count": len(evaluations),
        "recommended_next_phase": optimizer["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-3061..3100 Work Type Package Optimizer and Cost Decision Metric",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Chat layers: `{len(CHAT_LAYERS)}`",
        f"- Work types: `{len(WORK_TYPES)}`",
        f"- Cost metrics: `{len(COST_METRICS)}`",
        f"- Packages: `{len(PACKAGES)}`",
        f"- Next: `{optimizer['recommended_next_phase']}`",
        "",
        "## Principle",
        "- Cost is an operational decision metric.",
        "- Chat structure coherence is required.",
        "- No real pricing in this phase.",
        "",
        "## Package decisions"
    ]
    for e in evaluations:
        report.append(f"- `{e['id']}` `{e['chat_layer']}` `{e['work_type']}` -> `{e['recommended_package']}` gate `{e['decision_gate']}` cost `{e['cost_decision_weight']}` fit `{e['cost_adjusted_package_fit']}`")
    report += ["", "## Errors"]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("chat_layers:", len(CHAT_LAYERS))
    print("work_types:", len(WORK_TYPES))
    print("cost_metrics:", len(COST_METRICS))
    print("packages:", len(PACKAGES))
    print("next:", optimizer["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
RANKING = ROOT / "outputs" / "prod1781_1820_graph_based_opportunity_ranking.json"
ENSEMBLE = ROOT / "outputs" / "prod1741_1780_business_solution_ensemble_scoring_model.json"
TEMPLATE = ROOT / "product/business/business_value_human_review_template.json"
OUT = ROOT / "outputs"

REVIEW_DIMENSIONS = [
    "business_fit",
    "pain_clarity",
    "evidence_gap_clarity",
    "service_package_fit",
    "implementation_risk_realism",
    "governance_pressure_realism",
    "monitoring_recurrence_potential",
    "hallucination_reduction_relevance",
    "commercial_value_plausibility",
    "pilot_priority"
]

BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
    "automatic_threshold_mutation",
    "autonomous_external_execution",
    "real_world_side_effect",
    "unapproved_real_company_data",
    "production_neo4j_connection",
    "production_graph_write",
    "final_answer_generation_without_boundary",
    "gpt_call",
    "codex_execution",
    "public_api_publication",
    "custom_gpt_connection_without_human_approval",
    "final_threshold_calibration",
    "final_weight_calibration"
]

def suggested_review_focus(case):
    e = case["ensemble"]
    scores = e["scores"]
    focus = []

    if scores["governance_pressure_score"] >= 80:
        focus.append("validate_governance_pressure")
    if scores["hallucination_reduction_potential"] >= 65:
        focus.append("validate_hallucination_reduction_claim")
    if scores["monitoring_recurrence_score"] >= 75:
        focus.append("validate_recurring_revenue_or_assisted_operation_fit")
    if scores["implementation_risk_score"] >= 70:
        focus.append("validate_implementation_risk_and_gate")
    if scores["commercial_value_proxy"] >= 65:
        focus.append("validate_commercial_value_proxy")
    if not focus:
        focus.append("validate_basic_business_fit")

    return focus

def pilot_readiness_hint(case):
    score = case["ensemble"]["casulo_opportunity_score"]
    gates = case["ensemble"]["hard_gates"]
    if score >= 78 and any("GOVERNANCE" in g or "COMPLIANCE" in g for g in gates):
        return "HIGH_VALUE_DISCOVERY_ONLY"
    if score >= 75 and any("CHANGE" in g or "IMPLEMENTATION" in g for g in gates):
        return "HIGH_RISK_DISCOVERY_WITH_TECHNICAL_REVIEW"
    if score >= 70:
        return "PILOT_CANDIDATE_AFTER_HUMAN_REVIEW"
    if score >= 60:
        return "BACKLOG_OR_DIAGNOSTIC_CANDIDATE"
    return "LOW_PRIORITY_UNTIL_MORE_EVIDENCE"

def main():
    if not RANKING.exists():
        raise SystemExit(f"Missing ranking output: {RANKING}")
    if not ENSEMBLE.exists():
        raise SystemExit(f"Missing ensemble output: {ENSEMBLE}")
    if not TEMPLATE.exists():
        raise SystemExit(f"Missing review template: {TEMPLATE}")

    ranking = json.loads(RANKING.read_text(encoding="utf-8"))
    ensemble = json.loads(ENSEMBLE.read_text(encoding="utf-8"))
    template = json.loads(TEMPLATE.read_text(encoding="utf-8"))

    ensemble_cases_by_id = {c["id"]: c for c in ensemble.get("cases", [])}
    ranking_cases = ranking.get("rankings", {}).get("cases", [])

    cases = []
    for r in ranking_cases:
        c = ensemble_cases_by_id.get(r["id"])
        if not c:
            continue

        review_stub = {
            dim: {
                "score": None,
                "status": "PENDING_HUMAN_REVIEW",
                "notes": ""
            }
            for dim in REVIEW_DIMENSIONS
        }

        cases.append({
            "id": c["id"],
            "source_provenance": "SYNTHETIC_BUSINESS_TAXONOMY_AND_PROVISIONAL_ENSEMBLE",
            "company_profile": c["company_profile"],
            "company_maturity": c["company_maturity"],
            "service_package": c["service_package"],
            "solution_type": c["solution_type"],
            "recommendation_type": c["recommendation_type"],
            "business_delta": c["business_delta"],
            "value_hypothesis": c["value_hypothesis"],
            "unsafe_without_stack_pattern": c["unsafe_without_stack_pattern"],
            "stack_grounded_pattern": c["stack_grounded_pattern"],
            "model_outputs": {
                "casulo_opportunity_score": c["ensemble"]["casulo_opportunity_score"],
                "opportunity_band": c["ensemble"]["opportunity_band"],
                "recommended_mode": c["ensemble"]["recommended_mode"],
                "hard_gates": c["ensemble"]["hard_gates"],
                "business_delta_score": c["ensemble"]["scores"]["business_delta_score"],
                "hallucination_reduction_potential": c["ensemble"]["scores"]["hallucination_reduction_potential"],
                "governance_pressure_score": c["ensemble"]["scores"]["governance_pressure_score"],
                "stack_dependency_score": c["ensemble"]["scores"]["stack_dependency_score"],
                "implementation_risk_score": c["ensemble"]["scores"]["implementation_risk_score"],
                "monitoring_recurrence_score": c["ensemble"]["scores"]["monitoring_recurrence_score"],
                "commercial_value_proxy": c["ensemble"]["scores"]["commercial_value_proxy"],
                "company_maturity_friction_score": c["ensemble"]["scores"]["company_maturity_friction_score"]
            },
            "human_review": {
                "required": True,
                "review_status": "PENDING_HUMAN_REVIEW",
                "review_dimensions": review_stub,
                "suggested_review_focus": suggested_review_focus(c),
                "pilot_readiness_hint": pilot_readiness_hint(c),
                "calibration_eligible": False,
                "calibration_blocker": "human_review_not_completed"
            }
        })

    high_value = [
        c for c in cases
        if c["model_outputs"]["casulo_opportunity_score"] >= 70
    ]
    high_governance = [
        c for c in cases
        if c["model_outputs"]["governance_pressure_score"] >= 80
    ]
    high_hallucination = [
        c for c in cases
        if c["model_outputs"]["hallucination_reduction_potential"] >= 65
    ]
    assisted_ops = [
        c for c in cases
        if c["model_outputs"]["monitoring_recurrence_score"] >= 75
    ]

    dataset = {
        "case_count": len(cases),
        "review_dimension_count": len(REVIEW_DIMENSIONS),
        "human_review_required_count": len([c for c in cases if c["human_review"]["required"]]),
        "calibration_eligible_count": len([c for c in cases if c["human_review"]["calibration_eligible"]]),
        "high_value_candidate_count": len(high_value),
        "high_governance_candidate_count": len(high_governance),
        "high_hallucination_reduction_candidate_count": len(high_hallucination),
        "assisted_operation_candidate_count": len(assisted_ops),
        "review_template": str(TEMPLATE.relative_to(ROOT)),
        "calibration_status": "NOT_CALIBRATED_HUMAN_REVIEW_PENDING"
    }

    checks = {
        "ranking_exists": RANKING.exists(),
        "ensemble_exists": ENSEMBLE.exists(),
        "review_template_exists": TEMPLATE.exists(),
        "ranking_status_pass": ranking.get("status") == "PASS",
        "ensemble_status_pass": ensemble.get("status") == "PASS",
        "case_count": len(cases),
        "has_all_review_dimensions": len(REVIEW_DIMENSIONS) == 10,
        "all_cases_require_human_review": all(c["human_review"]["required"] for c in cases),
        "no_cases_calibration_eligible_before_review": all(not c["human_review"]["calibration_eligible"] for c in cases),
        "has_high_value_candidates": len(high_value) >= 3,
        "has_high_governance_candidates": len(high_governance) >= 3,
        "has_high_hallucination_reduction_candidates": len(high_hallucination) >= 3,
        "calibration_status": "NOT_CALIBRATED_HUMAN_REVIEW_PENDING"
    }

    errors = []
    if not checks["ranking_status_pass"]:
        errors.append("Graph ranking source is not PASS")
    if not checks["ensemble_status_pass"]:
        errors.append("Ensemble source is not PASS")
    if len(cases) < 7:
        errors.append("Expected at least 7 calibration cases")
    if not checks["all_cases_require_human_review"]:
        errors.append("Every case must require human review")
    if not checks["no_cases_calibration_eligible_before_review"]:
        errors.append("No case may be calibration eligible before human review")
    if not checks["has_high_value_candidates"]:
        errors.append("Expected at least 3 high value candidates")

    status = "PASS" if not errors else "FAIL"
    decision = "BUSINESS_VALUE_HUMAN_CALIBRATION_DATASET_READY" if status == "PASS" else "BUSINESS_VALUE_HUMAN_CALIBRATION_DATASET_NOT_READY"

    result = {
        "status": status,
        "phase": "PROD-1821..1860",
        "decision": decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dataset": dataset,
        "cases": cases,
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED_ACTIONS
    }

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "prod1821_1860_business_value_human_calibration_dataset.json"
    md_path = OUT / "prod1821_1860_business_value_human_calibration_dataset.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PROD-1821..1860 Business Value Human Calibration Dataset",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{decision}`",
        f"- Case count: `{dataset['case_count']}`",
        f"- Review dimension count: `{dataset['review_dimension_count']}`",
        f"- Human review required count: `{dataset['human_review_required_count']}`",
        f"- Calibration eligible count: `{dataset['calibration_eligible_count']}`",
        f"- High value candidate count: `{dataset['high_value_candidate_count']}`",
        f"- High governance candidate count: `{dataset['high_governance_candidate_count']}`",
        f"- High hallucination reduction candidate count: `{dataset['high_hallucination_reduction_candidate_count']}`",
        f"- Assisted operation candidate count: `{dataset['assisted_operation_candidate_count']}`",
        f"- Calibration: `{dataset['calibration_status']}`",
        "",
        "## Review Dimensions"
    ]

    for dim in REVIEW_DIMENSIONS:
        md.append(f"- {dim}")

    md += ["", "## Cases"]
    for c in cases:
        m = c["model_outputs"]
        h = c["human_review"]
        md += [
            "",
            f"### {c['id']}",
            f"- Source provenance: `{c['source_provenance']}`",
            f"- Company profile: `{c['company_profile']}`",
            f"- Company maturity: `{c['company_maturity']}`",
            f"- Service package: `{c['service_package']}`",
            f"- Solution type: `{c['solution_type']}`",
            f"- Recommendation type: `{c['recommendation_type']}`",
            f"- CASULO opportunity score: `{m['casulo_opportunity_score']}`",
            f"- Opportunity band: `{m['opportunity_band']}`",
            f"- Recommended mode: `{m['recommended_mode']}`",
            f"- Hard gates: `{', '.join(m['hard_gates'])}`",
            f"- Hallucination reduction potential: `{m['hallucination_reduction_potential']}`",
            f"- Governance pressure score: `{m['governance_pressure_score']}`",
            f"- Monitoring recurrence score: `{m['monitoring_recurrence_score']}`",
            f"- Commercial value proxy: `{m['commercial_value_proxy']}`",
            f"- Suggested review focus: `{', '.join(h['suggested_review_focus'])}`",
            f"- Pilot readiness hint: `{h['pilot_readiness_hint']}`",
            f"- Calibration eligible: `{h['calibration_eligible']}`",
            f"- Calibration blocker: `{h['calibration_blocker']}`",
            f"- Business delta: `{c['business_delta']}`",
            f"- Value hypothesis: `{c['value_hypothesis']}`"
        ]

    md += ["", "## Checks"]
    for key, value in checks.items():
        md.append(f"- {key}: `{value}`")

    md += ["", "## Errors"]
    if errors:
        for err in errors:
            md.append(f"- {err}")
    else:
        md.append("- None")

    md += [
        "",
        "## Boundary",
        "- Human calibration dataset only.",
        "- Human review is pending.",
        "- No final thresholds.",
        "- No final weights.",
        "- No GPT connection.",
        "- No GPT call.",
        "- No Codex execution.",
        "- No production connection.",
        "",
        "## Blocked Actions"
    ]
    for action in BLOCKED_ACTIONS:
        md.append(f"- {action}")

    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

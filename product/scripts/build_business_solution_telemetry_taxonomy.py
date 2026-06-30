#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATASET = ROOT / "product/business/business_solution_telemetry_cases.json"
OUT = ROOT / "outputs"

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
    "final_threshold_calibration"
]

def score_case(case):
    risk_weight = {
        "low": 1,
        "low_medium": 2,
        "medium": 3,
        "medium_high": 4,
        "high": 5,
        "very_high": 6
    }
    stack_weight = {
        "low": 1,
        "medium": 2,
        "medium_high": 3,
        "high": 4
    }
    governance_weight = {
        "low": 1,
        "medium": 2,
        "medium_high": 3,
        "high": 4,
        "very_high": 5
    }

    implementation_risk_score = risk_weight.get(case["implementation_risk"], 3)
    stack_dependency_score = stack_weight.get(case["stack_dependency"], 3)
    governance_need_score = governance_weight.get(case["governance_need"], 2)

    monitoring_bonus = 2 if case["monitoring_need"] in ["monthly", "weekly_or_monthly", "monthly_or_quarterly"] else 1
    insight_priority = implementation_risk_score + stack_dependency_score + governance_need_score + monitoring_bonus

    if insight_priority >= 14:
        priority_band = "very_high"
    elif insight_priority >= 11:
        priority_band = "high"
    elif insight_priority >= 8:
        priority_band = "medium"
    else:
        priority_band = "low"

    return {
        "implementation_risk_score": implementation_risk_score,
        "stack_dependency_score": stack_dependency_score,
        "governance_need_score": governance_need_score,
        "monitoring_bonus": monitoring_bonus,
        "insight_priority_score": insight_priority,
        "priority_band": priority_band
    }

def main():
    data = json.loads(DATASET.read_text(encoding="utf-8"))
    cases = data["cases"]

    enriched = []
    for case in cases:
        scored = dict(case)
        scored["telemetry"] = score_case(case)
        enriched.append(scored)

    def unique(key):
        return sorted({c[key] for c in enriched})

    service_packages = unique("service_package")
    company_profiles = unique("company_profile")
    solution_types = unique("solution_type")
    recommendation_types = unique("recommendation_type")
    priority_bands = sorted({c["telemetry"]["priority_band"] for c in enriched})

    very_high_or_high = [
        c for c in enriched
        if c["telemetry"]["priority_band"] in ["very_high", "high"]
    ]

    taxonomy = {
        "case_count": len(enriched),
        "company_profile_count": len(company_profiles),
        "service_package_count": len(service_packages),
        "solution_type_count": len(solution_types),
        "recommendation_type_count": len(recommendation_types),
        "company_profiles": company_profiles,
        "service_packages": service_packages,
        "solution_types": solution_types,
        "recommendation_types": recommendation_types,
        "priority_bands": priority_bands,
        "high_priority_case_count": len(very_high_or_high),
        "calibration_status": "NOT_CALIBRATED_BUSINESS_TAXONOMY_ONLY"
    }

    checks = {
        "dataset_exists": DATASET.exists(),
        "case_count": len(enriched),
        "has_company_profiles": len(company_profiles) >= 5,
        "has_service_packages": len(service_packages) >= 6,
        "has_solution_types": len(solution_types) >= 6,
        "has_recommendation_types": len(recommendation_types) >= 6,
        "has_governance_compliance_package": "Governance Compliance State Mesh" in service_packages,
        "has_solution_factory_package": "Solution Factory Sprint" in service_packages,
        "has_assisted_operation_package": "Operacao Assistida" in service_packages,
        "has_ai_pme_package": "Programa de IA PME" in service_packages,
        "has_tic_si_package": "TIC/SI State Mesh" in service_packages,
        "has_high_priority_cases": len(very_high_or_high) >= 3,
        "calibration_status": "NOT_CALIBRATED_BUSINESS_TAXONOMY_ONLY"
    }

    errors = []
    if len(enriched) < 7:
        errors.append("Expected at least 7 business solution cases")
    if not checks["has_governance_compliance_package"]:
        errors.append("Missing Governance Compliance State Mesh package")
    if not checks["has_high_priority_cases"]:
        errors.append("Expected at least 3 high priority cases")

    status = "PASS" if not errors else "FAIL"
    decision = "BUSINESS_SOLUTION_TELEMETRY_TAXONOMY_READY" if status == "PASS" else "BUSINESS_SOLUTION_TELEMETRY_TAXONOMY_NOT_READY"

    result = {
        "status": status,
        "phase": "PROD-1701..1740",
        "decision": decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "taxonomy": taxonomy,
        "cases": enriched,
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED_ACTIONS
    }

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "prod1701_1740_business_solution_telemetry_taxonomy.json"
    md_path = OUT / "prod1701_1740_business_solution_telemetry_taxonomy.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PROD-1701..1740 Business Solution Telemetry Taxonomy",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{decision}`",
        f"- Case count: `{taxonomy['case_count']}`",
        f"- Company profile count: `{taxonomy['company_profile_count']}`",
        f"- Service package count: `{taxonomy['service_package_count']}`",
        f"- Solution type count: `{taxonomy['solution_type_count']}`",
        f"- Recommendation type count: `{taxonomy['recommendation_type_count']}`",
        f"- High priority case count: `{taxonomy['high_priority_case_count']}`",
        "- Calibration: `NOT_CALIBRATED_BUSINESS_TAXONOMY_ONLY`",
        "",
        "## Service Packages"
    ]

    for item in service_packages:
        md.append(f"- {item}")

    md += ["", "## Cases"]
    for c in enriched:
        md += [
            "",
            f"### {c['id']}",
            f"- Company profile: `{c['company_profile']}`",
            f"- Company maturity: `{c['company_maturity']}`",
            f"- Service package: `{c['service_package']}`",
            f"- Solution type: `{c['solution_type']}`",
            f"- Recommendation type: `{c['recommendation_type']}`",
            f"- Business delta: `{c['business_delta']}`",
            f"- Implementation risk: `{c['implementation_risk']}`",
            f"- Monitoring need: `{c['monitoring_need']}`",
            f"- Governance need: `{c['governance_need']}`",
            f"- Stack dependency: `{c['stack_dependency']}`",
            f"- Insight priority score: `{c['telemetry']['insight_priority_score']}`",
            f"- Priority band: `{c['telemetry']['priority_band']}`",
            f"- Unsafe without stack pattern: `{c['unsafe_without_stack_pattern']}`",
            f"- Stack grounded pattern: `{c['stack_grounded_pattern']}`",
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
        "- Business and solution taxonomy only.",
        "- No final calibration.",
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

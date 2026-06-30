#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "outputs" / "prod1701_1740_business_solution_telemetry_taxonomy.json"
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
    "final_threshold_calibration",
    "final_weight_calibration"
]

WEIGHTS = {
    "business_delta_score": 0.20,
    "hallucination_reduction_potential": 0.20,
    "governance_pressure_score": 0.15,
    "stack_dependency_score": 0.15,
    "implementation_risk_score": 0.10,
    "monitoring_recurrence_score": 0.10,
    "commercial_value_proxy": 0.10
}

RISK = {
    "low": 20,
    "low_medium": 35,
    "medium": 50,
    "medium_high": 65,
    "high": 80,
    "very_high": 95
}

STACK = {
    "low": 20,
    "medium": 45,
    "medium_high": 70,
    "high": 90
}

GOVERNANCE = {
    "low": 20,
    "medium": 45,
    "medium_high": 65,
    "high": 85,
    "very_high": 95
}

MONITORING = {
    "none": 10,
    "per_release": 45,
    "per_sprint": 55,
    "monthly": 80,
    "weekly_or_monthly": 90,
    "monthly_or_quarterly": 85
}

MATURITY_FRICTION = {
    "medium_manual_process": 65,
    "low_visibility_high_dependency": 90,
    "technical_debt_unknown": 80,
    "early_ai_experimentation": 75,
    "controls_exist_but_evidence_fragmented": 90,
    "process_unclear_solution_requested": 70,
    "recurring_operation_with_untracked_deltas": 75
}

def clamp(value):
    return max(0, min(100, round(value, 2)))

def text_signal(text, terms):
    t = text.lower()
    return sum(1 for term in terms if term.lower() in t)

def business_delta_score(case):
    text = " ".join([
        case.get("operational_pain", ""),
        case.get("business_delta", ""),
        case.get("value_hypothesis", "")
    ])
    signals = text_signal(text, [
        "reduce", "fewer", "lower", "avoid", "safer", "recurring",
        "continuous", "premium", "clearer", "audit", "incidents",
        "delays", "rework", "roi", "measurable"
    ])
    return clamp(35 + signals * 7)

def hallucination_reduction_potential(case):
    unsafe = case.get("unsafe_without_stack_pattern", "")
    grounded = case.get("stack_grounded_pattern", "")
    unsafe_signals = text_signal(unsafe, [
        "before mapping", "without", "incomplete", "declare", "approve",
        "generic", "loose", "comfort", "missing", "evidence"
    ])
    grounded_signals = text_signal(grounded, [
        "gate", "evidence", "review", "state", "packet", "rollback",
        "tests", "owner", "metrics", "audit"
    ])
    return clamp(25 + unsafe_signals * 8 + grounded_signals * 6)

def governance_pressure_score(case):
    return GOVERNANCE.get(case.get("governance_need"), 45)

def stack_dependency_score(case):
    return STACK.get(case.get("stack_dependency"), 45)

def implementation_risk_score(case):
    return RISK.get(case.get("implementation_risk"), 50)

def monitoring_recurrence_score(case):
    return MONITORING.get(case.get("monitoring_need"), 45)

def commercial_value_proxy(case):
    text = " ".join([
        case.get("value_hypothesis", ""),
        case.get("business_delta", ""),
        case.get("service_package", "")
    ])
    signals = text_signal(text, [
        "recurring revenue", "premium", "roi", "fewer delays",
        "lower change risk", "auditability", "safer", "lower rework",
        "continuous improvement", "client communication", "support ownership"
    ])
    recurring_bonus = 15 if case.get("monitoring_need") in ["monthly", "weekly_or_monthly", "monthly_or_quarterly"] else 5
    return clamp(35 + signals * 8 + recurring_bonus)

def hard_gate_model(case, scores):
    gates = []
    if case.get("governance_need") in ["high", "very_high"]:
        gates.append("GOVERNANCE_REVIEW_REQUIRED")
    if case.get("implementation_risk") in ["high", "very_high"]:
        gates.append("IMPLEMENTATION_RISK_REVIEW_REQUIRED")
    if case.get("stack_dependency") == "high":
        gates.append("STACK_GROUNDED_REVIEW_REQUIRED")
    if "Compliance" in case.get("service_package", ""):
        gates.append("COMPLIANCE_REVIEW_REQUIRED")
    if "TIC/SI" in case.get("service_package", ""):
        gates.append("CHANGE_REVIEW_REQUIRED")
    if "Operacao Assistida" in case.get("service_package", ""):
        gates.append("MONITORING_REVIEW_REQUIRED")
    if not gates:
        gates.append("STANDARD_HUMAN_REVIEW_REQUIRED")
    return gates

def classify(score):
    if score >= 85:
        return "very_high"
    if score >= 70:
        return "high"
    if score >= 50:
        return "medium"
    if score >= 30:
        return "low"
    return "very_low"

def score_case(case):
    scores = {
        "business_delta_score": business_delta_score(case),
        "hallucination_reduction_potential": hallucination_reduction_potential(case),
        "governance_pressure_score": governance_pressure_score(case),
        "stack_dependency_score": stack_dependency_score(case),
        "implementation_risk_score": implementation_risk_score(case),
        "monitoring_recurrence_score": monitoring_recurrence_score(case),
        "commercial_value_proxy": commercial_value_proxy(case),
        "company_maturity_friction_score": MATURITY_FRICTION.get(case.get("company_maturity"), 60)
    }

    weighted = sum(scores[k] * WEIGHTS[k] for k in WEIGHTS)
    maturity_adjustment = (scores["company_maturity_friction_score"] - 50) * 0.08
    casulo_opportunity_score = clamp(weighted + maturity_adjustment)

    gates = hard_gate_model(case, scores)

    recommended_mode = "DIAGNOSTIC_FIRST"
    if casulo_opportunity_score >= 80 and scores["monitoring_recurrence_score"] >= 75:
        recommended_mode = "DIAGNOSTIC_PLUS_ASSISTED_OPERATION"
    elif casulo_opportunity_score >= 75 and scores["implementation_risk_score"] >= 70:
        recommended_mode = "DIAGNOSTIC_PLUS_RISK_GATE"
    elif casulo_opportunity_score >= 70:
        recommended_mode = "STARTER_IMPLANTATION"
    elif casulo_opportunity_score >= 55:
        recommended_mode = "DIAGNOSTIC_AND_BACKLOG"
    else:
        recommended_mode = "LIGHT_DIAGNOSTIC"

    return {
        "scores": scores,
        "weights": WEIGHTS,
        "casulo_opportunity_score": casulo_opportunity_score,
        "opportunity_band": classify(casulo_opportunity_score),
        "hard_gates": gates,
        "recommended_mode": recommended_mode
    }

def main():
    if not SOURCE.exists():
        raise SystemExit(f"Missing source taxonomy output: {SOURCE}")

    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    source_cases = source.get("cases", [])

    scored_cases = []
    for case in source_cases:
        scored = dict(case)
        scored["ensemble"] = score_case(case)
        scored_cases.append(scored)

    sorted_cases = sorted(
        scored_cases,
        key=lambda c: c["ensemble"]["casulo_opportunity_score"],
        reverse=True
    )

    avg = lambda key: round(sum(c["ensemble"]["scores"][key] for c in scored_cases) / len(scored_cases), 2)
    avg_opp = round(sum(c["ensemble"]["casulo_opportunity_score"] for c in scored_cases) / len(scored_cases), 2)

    ensemble = {
        "model_type": "explainable_weighted_ensemble_with_hard_gates",
        "calibration_status": "NOT_CALIBRATED_PROVISIONAL_WEIGHTS_ONLY",
        "case_count": len(scored_cases),
        "weights": WEIGHTS,
        "average_casulo_opportunity_score": avg_opp,
        "average_business_delta_score": avg("business_delta_score"),
        "average_hallucination_reduction_potential": avg("hallucination_reduction_potential"),
        "average_governance_pressure_score": avg("governance_pressure_score"),
        "average_stack_dependency_score": avg("stack_dependency_score"),
        "average_implementation_risk_score": avg("implementation_risk_score"),
        "average_monitoring_recurrence_score": avg("monitoring_recurrence_score"),
        "average_commercial_value_proxy": avg("commercial_value_proxy"),
        "top_cases": [
            {
                "id": c["id"],
                "service_package": c["service_package"],
                "casulo_opportunity_score": c["ensemble"]["casulo_opportunity_score"],
                "opportunity_band": c["ensemble"]["opportunity_band"],
                "recommended_mode": c["ensemble"]["recommended_mode"]
            }
            for c in sorted_cases[:5]
        ]
    }

    checks = {
        "source_taxonomy_exists": SOURCE.exists(),
        "source_taxonomy_status_pass": source.get("status") == "PASS",
        "case_count": len(scored_cases),
        "has_weights": len(WEIGHTS) == 7,
        "weights_sum_to_one": round(sum(WEIGHTS.values()), 6) == 1.0,
        "all_cases_scored": all("ensemble" in c for c in scored_cases),
        "all_cases_have_hard_gates": all(c["ensemble"]["hard_gates"] for c in scored_cases),
        "all_cases_have_opportunity_score": all("casulo_opportunity_score" in c["ensemble"] for c in scored_cases),
        "has_high_or_very_high_opportunity": any(c["ensemble"]["opportunity_band"] in ["high", "very_high"] for c in scored_cases),
        "calibration_status": "NOT_CALIBRATED_PROVISIONAL_WEIGHTS_ONLY"
    }

    errors = []
    if not checks["source_taxonomy_exists"]:
        errors.append("Missing business solution telemetry taxonomy output")
    if not checks["source_taxonomy_status_pass"]:
        errors.append("Source taxonomy is not PASS")
    if len(scored_cases) < 7:
        errors.append("Expected at least 7 scored cases")
    if not checks["weights_sum_to_one"]:
        errors.append("Weights must sum to 1")
    if not checks["all_cases_have_hard_gates"]:
        errors.append("Every case must have at least one hard gate")

    status = "PASS" if not errors else "FAIL"
    decision = "BUSINESS_SOLUTION_ENSEMBLE_READY_NOT_CALIBRATED" if status == "PASS" else "BUSINESS_SOLUTION_ENSEMBLE_NOT_READY"

    result = {
        "status": status,
        "phase": "PROD-1741..1780",
        "decision": decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ensemble": ensemble,
        "cases": scored_cases,
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED_ACTIONS
    }

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "prod1741_1780_business_solution_ensemble_scoring_model.json"
    md_path = OUT / "prod1741_1780_business_solution_ensemble_scoring_model.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PROD-1741..1780 Business Solution Ensemble Scoring Model",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{decision}`",
        f"- Model type: `{ensemble['model_type']}`",
        f"- Calibration: `{ensemble['calibration_status']}`",
        f"- Case count: `{ensemble['case_count']}`",
        f"- Average CASULO opportunity score: `{ensemble['average_casulo_opportunity_score']}`",
        f"- Average hallucination reduction potential: `{ensemble['average_hallucination_reduction_potential']}`",
        f"- Average business delta score: `{ensemble['average_business_delta_score']}`",
        f"- Average governance pressure score: `{ensemble['average_governance_pressure_score']}`",
        f"- Average stack dependency score: `{ensemble['average_stack_dependency_score']}`",
        f"- Average implementation risk score: `{ensemble['average_implementation_risk_score']}`",
        f"- Average monitoring recurrence score: `{ensemble['average_monitoring_recurrence_score']}`",
        f"- Average commercial value proxy: `{ensemble['average_commercial_value_proxy']}`",
        "",
        "## Provisional Weights"
    ]

    for key, value in WEIGHTS.items():
        md.append(f"- {key}: `{value}`")

    md += ["", "## Top Cases"]
    for item in ensemble["top_cases"]:
        md += [
            f"### {item['id']}",
            f"- Service package: `{item['service_package']}`",
            f"- CASULO opportunity score: `{item['casulo_opportunity_score']}`",
            f"- Opportunity band: `{item['opportunity_band']}`",
            f"- Recommended mode: `{item['recommended_mode']}`",
            ""
        ]

    md += ["## Cases"]
    for c in sorted_cases:
        e = c["ensemble"]
        s = e["scores"]
        md += [
            "",
            f"### {c['id']}",
            f"- Company profile: `{c['company_profile']}`",
            f"- Service package: `{c['service_package']}`",
            f"- CASULO opportunity score: `{e['casulo_opportunity_score']}`",
            f"- Opportunity band: `{e['opportunity_band']}`",
            f"- Recommended mode: `{e['recommended_mode']}`",
            f"- Hard gates: `{', '.join(e['hard_gates'])}`",
            f"- Business delta score: `{s['business_delta_score']}`",
            f"- Hallucination reduction potential: `{s['hallucination_reduction_potential']}`",
            f"- Governance pressure score: `{s['governance_pressure_score']}`",
            f"- Stack dependency score: `{s['stack_dependency_score']}`",
            f"- Implementation risk score: `{s['implementation_risk_score']}`",
            f"- Monitoring recurrence score: `{s['monitoring_recurrence_score']}`",
            f"- Commercial value proxy: `{s['commercial_value_proxy']}`",
            f"- Maturity friction score: `{s['company_maturity_friction_score']}`"
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
        "- Explainable ensemble only.",
        "- Provisional weights only.",
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

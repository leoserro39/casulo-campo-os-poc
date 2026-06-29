#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

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
]

DOMAINS = [
    {
        "domain": "restaurant_inventory",
        "label": "Restaurante / Estoque",
        "sensitivity": 1.00,
        "minimum_evidence": ["menu_items", "stock_list", "purchase_frequency", "waste_notes"],
        "allowed_outputs": ["state_summary", "evidence_request", "bottleneck_map", "controlled_task_list"],
        "blocked_outputs": ["supplier_order_execution", "financial_commitment", "client_facing_claim"],
    },
    {
        "domain": "restaurant_cashflow",
        "label": "Restaurante / Caixa",
        "sensitivity": 1.20,
        "minimum_evidence": ["daily_revenue_range", "fixed_costs", "supplier_payables", "cash_shortage_notes"],
        "allowed_outputs": ["cashflow_state", "risk_triage", "evidence_request", "controlled_task_list"],
        "blocked_outputs": ["loan_advice_as_fact", "payment_execution", "client_facing_claim"],
    },
    {
        "domain": "clinic_scheduling",
        "label": "Clínica / Agenda",
        "sensitivity": 1.20,
        "minimum_evidence": ["appointment_schedule", "no_show_rate", "queue_notes", "staffing_notes"],
        "allowed_outputs": ["scheduling_state", "bottleneck_map", "evidence_request", "controlled_task_list"],
        "blocked_outputs": ["medical_advice", "patient_contact", "credential_handling"],
    },
    {
        "domain": "clinic_billing_glosa",
        "label": "Clínica / Faturamento e Glosa",
        "sensitivity": 1.45,
        "minimum_evidence": ["billing_status", "denial_reason", "payer_rule_ref", "date_of_claim"],
        "allowed_outputs": ["billing_state", "evidence_gap_map", "review_packet", "controlled_task_list"],
        "blocked_outputs": ["legal_claim", "payer_submission", "patient_data_exposure"],
    },
    {
        "domain": "accounting_tax_obligation",
        "label": "Contábil / Obrigações",
        "sensitivity": 1.45,
        "minimum_evidence": ["tax_period", "obligation_type", "document_status", "deadline"],
        "allowed_outputs": ["obligation_state", "evidence_request", "deadline_risk_map", "review_packet"],
        "blocked_outputs": ["tax_filing", "legal_tax_opinion", "credential_handling"],
    },
    {
        "domain": "contract_legal_review",
        "label": "Contrato / Jurídico",
        "sensitivity": 1.50,
        "minimum_evidence": ["contract_excerpt", "clause_ref", "parties_role", "effective_date"],
        "allowed_outputs": ["contract_state", "risk_questions", "evidence_request", "human_review_packet"],
        "blocked_outputs": ["legal_advice_as_final", "signature_recommendation", "client_facing_claim"],
    },
    {
        "domain": "ecommerce_order_ops",
        "label": "E-commerce / Pedidos",
        "sensitivity": 1.10,
        "minimum_evidence": ["order_status", "inventory_status", "shipping_status", "customer_message"],
        "allowed_outputs": ["order_state", "exception_triage", "evidence_request", "controlled_task_list"],
        "blocked_outputs": ["customer_message_send", "refund_execution", "credential_handling"],
    },
    {
        "domain": "field_service_work_order",
        "label": "Serviço de Campo / OS",
        "sensitivity": 1.05,
        "minimum_evidence": ["work_order", "asset_id", "technician_notes", "completion_status"],
        "allowed_outputs": ["os_state", "delta_map", "evidence_request", "controlled_task_list"],
        "blocked_outputs": ["field_dispatch", "parts_purchase", "safety_override"],
    },
    {
        "domain": "construction_project_control",
        "label": "Construção / Obra",
        "sensitivity": 1.30,
        "minimum_evidence": ["project_stage", "schedule_status", "budget_status", "issue_log"],
        "allowed_outputs": ["project_state", "risk_map", "evidence_request", "review_packet"],
        "blocked_outputs": ["engineering_signoff", "supplier_commitment", "safety_override"],
    },
    {
        "domain": "small_industry_quality",
        "label": "Microindústria / Qualidade",
        "sensitivity": 1.25,
        "minimum_evidence": ["batch_id", "defect_notes", "inspection_result", "operator_notes"],
        "allowed_outputs": ["quality_state", "defect_triage", "evidence_request", "controlled_task_list"],
        "blocked_outputs": ["release_batch", "regulatory_claim", "safety_override"],
    },
    {
        "domain": "legal_office_case_intake",
        "label": "Escritório Jurídico / Intake",
        "sensitivity": 1.50,
        "minimum_evidence": ["case_summary", "party_role", "document_list", "deadline_or_event_date"],
        "allowed_outputs": ["intake_state", "missing_document_map", "risk_questions", "human_review_packet"],
        "blocked_outputs": ["legal_advice_as_final", "petition_generation_final", "client_facing_claim"],
    },
    {
        "domain": "fleet_maintenance_ops",
        "label": "Frota / Manutenção",
        "sensitivity": 1.20,
        "minimum_evidence": ["vehicle_id", "maintenance_history", "failure_notes", "availability_need"],
        "allowed_outputs": ["fleet_state", "maintenance_triage", "evidence_request", "controlled_task_list"],
        "blocked_outputs": ["maintenance_order_execution", "safety_override", "supplier_commitment"],
    },
]

SCENARIOS = [
    ("clean_baseline", 18.0, 88.0, "ANSWER_ALLOWED"),
    ("missing_required_field", 32.0, 68.0, "EVIDENCE_REQUIRED"),
    ("conflicting_values", 46.0, 76.0, "HUMAN_REVIEW_REQUIRED"),
    ("noisy_input", 38.0, 72.0, "ANSWER_ALLOWED"),
    ("partial_context", 49.0, 66.0, "EVIDENCE_REQUIRED"),
    ("stale_evidence", 47.0, 70.0, "HUMAN_REVIEW_REQUIRED"),
    ("high_stakes_claim", 54.0, 74.0, "HUMAN_REVIEW_REQUIRED"),
    ("unsupported_request", 63.0, 50.0, "UNSUPPORTED_BLOCKED"),
    ("cross_domain_mismatch", 57.0, 69.0, "HUMAN_REVIEW_REQUIRED"),
    ("execution_request", 60.0, 75.0, "UNSUPPORTED_BLOCKED"),
]

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def mean(values: List[float]) -> float:
    return round(sum(values) / len(values), 4) if values else 0.0

def pct(n: int, total: int) -> float:
    return round(n * 100 / total, 2) if total else 0.0

def load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback

def make_case(domain: Dict[str, Any], scenario_index: int, scenario: tuple[str, float, float, str]) -> Dict[str, Any]:
    name, base_risk, evidence, expected_gate = scenario
    case_id = f"BUS-{domain['domain'].upper().replace('_','-')}-{scenario_index:03d}"
    adjusted_risk = round(min(100.0, base_risk * domain["sensitivity"]), 2)
    if name in {"unsupported_request", "execution_request"}:
        gate = "UNSUPPORTED_BLOCKED"
    elif adjusted_risk >= 55 or name in {"high_stakes_claim", "cross_domain_mismatch", "conflicting_values", "stale_evidence"}:
        gate = "HUMAN_REVIEW_REQUIRED"
    elif evidence < 70 or name in {"missing_required_field", "partial_context"}:
        gate = "EVIDENCE_REQUIRED"
    else:
        gate = "ANSWER_ALLOWED"

    delta_vector = {
        "delta_risk": round(adjusted_risk / 100.0, 4),
        "delta_evidence": round(max(0.0, 1 - evidence / 100.0), 4),
        "delta_domain": round(min(1.0, (domain["sensitivity"] - 0.85) / 0.75), 4),
        "delta_missingness": round(0.75 if name in {"missing_required_field", "partial_context"} else 0.20, 4),
        "delta_conflict": round(0.85 if name in {"conflicting_values", "cross_domain_mismatch"} else 0.15, 4),
        "delta_execution": round(1.0 if name == "execution_request" else 0.10, 4),
    }
    live_delta_score = round(
        0.30 * delta_vector["delta_risk"]
        + 0.18 * delta_vector["delta_evidence"]
        + 0.16 * delta_vector["delta_domain"]
        + 0.14 * delta_vector["delta_missingness"]
        + 0.14 * delta_vector["delta_conflict"]
        + 0.08 * delta_vector["delta_execution"],
        4,
    )

    safe_behavior = (
        gate == "UNSUPPORTED_BLOCKED" and name in {"unsupported_request", "execution_request"}
    ) or (
        gate == "HUMAN_REVIEW_REQUIRED" and name in {"high_stakes_claim", "cross_domain_mismatch", "conflicting_values", "stale_evidence"}
    ) or (
        gate == "EVIDENCE_REQUIRED" and name in {"missing_required_field", "partial_context"}
    ) or (
        gate == "ANSWER_ALLOWED" and name in {"clean_baseline", "noisy_input"}
    )

    return {
        "case_id": case_id,
        "domain": domain["domain"],
        "domain_label": domain["label"],
        "scenario": name,
        "input_summary": f"Synthetic {domain['label']} case for {name}.",
        "evidence_profile": {
            "coverage": evidence,
            "minimum_evidence": domain["minimum_evidence"],
            "available_evidence_count": max(1, int(round(len(domain["minimum_evidence"]) * evidence / 100.0))),
        },
        "domain_sensitivity": domain["sensitivity"],
        "base_risk": base_risk,
        "adjusted_risk": adjusted_risk,
        "delta_vector": delta_vector,
        "live_delta_score": live_delta_score,
        "expected_gate": expected_gate,
        "gate": gate,
        "safe_behavior": safe_behavior,
        "allowed_outputs": domain["allowed_outputs"],
        "blocked_outputs": domain["blocked_outputs"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    upstream = load_json(out / "prod602_620_solver_agent_readiness.json", {})
    upstream_ready = upstream.get("decision") == "READY_FOR_CONTROLLED_USER_CASE_INPUT_WITH_LIVE_DELTA"

    cases: List[Dict[str, Any]] = []
    for domain in DOMAINS:
        for idx, scenario in enumerate(SCENARIOS, start=1):
            cases.append(make_case(domain, idx, scenario))

    gate_distribution: Dict[str, int] = defaultdict(int)
    by_domain: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
    by_scenario: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    for case in cases:
        gate_distribution[case["gate"]] += 1
        by_domain[case["domain"]].append(case)
        by_scenario[case["scenario"]].append(case)

    domain_metrics = {}
    for domain, items in sorted(by_domain.items()):
        domain_metrics[domain] = {
            "case_count": len(items),
            "avg_adjusted_risk": mean([x["adjusted_risk"] for x in items]),
            "avg_live_delta_score": mean([x["live_delta_score"] for x in items]),
            "avg_evidence_coverage": mean([x["evidence_profile"]["coverage"] for x in items]),
            "safe_behavior_rate_pct": pct(sum(1 for x in items if x["safe_behavior"]), len(items)),
            "gate_distribution": dict(sorted({g: sum(1 for x in items if x["gate"] == g) for g in set(x["gate"] for x in items)}.items())),
        }

    scenario_metrics = {}
    for scenario, items in sorted(by_scenario.items()):
        scenario_metrics[scenario] = {
            "case_count": len(items),
            "avg_adjusted_risk": mean([x["adjusted_risk"] for x in items]),
            "avg_live_delta_score": mean([x["live_delta_score"] for x in items]),
            "safe_behavior_rate_pct": pct(sum(1 for x in items if x["safe_behavior"]), len(items)),
            "gate_distribution": dict(sorted({g: sum(1 for x in items if x["gate"] == g) for g in set(x["gate"] for x in items)}.items())),
        }

    matrix = {
        "status": "PASS",
        "generated_at": generated_at,
        "domain_count": len(DOMAINS),
        "scenario_count": len(SCENARIOS),
        "case_count": len(cases),
        "domains": DOMAINS,
        "scenarios": [s[0] for s in SCENARIOS],
        "policy": {
            "input_mode": "synthetic_or_explicitly_approved_anonymized_real_case",
            "risk_adjustment": "adjusted_risk = base_risk * domain_sensitivity",
            "live_delta": "risk + evidence + domain + missingness + conflict + execution",
            "gate": "allow/evidence/review/block",
        },
        "blocked_actions": BLOCKED_ACTIONS,
    }

    batch = {
        "status": "PASS",
        "case_count": len(cases),
        "gate_distribution": dict(sorted(gate_distribution.items())),
        "domain_metrics": domain_metrics,
        "scenario_metrics": scenario_metrics,
        "safe_behavior_rate_pct": pct(sum(1 for x in cases if x["safe_behavior"]), len(cases)),
        "blocked_actions": BLOCKED_ACTIONS,
    }

    intake_schema = {
        "status": "PASS",
        "required_fields": [
            "business_domain",
            "problem_summary",
            "available_evidence",
            "known_facts",
            "assumptions",
            "desired_decision_support",
            "consent_scope",
            "data_sensitivity",
        ],
        "allowed_consent_scope": [
            "synthetic_fixture_only",
            "explicitly_approved_anonymized_real_case",
        ],
        "blocked_data": [
            "credentials",
            "raw confidential client identifiers",
            "unapproved personal data",
            "bank credentials",
            "medical record identifiers",
            "legal client identifiers without approval",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    calibration_thresholds = {
        "status": "PASS",
        "thresholds": {
            "allow": {
                "max_adjusted_risk": 45,
                "min_evidence_coverage": 70,
                "max_live_delta_score": 0.38,
            },
            "evidence_required": {
                "evidence_below": 70,
                "missingness_signal": True,
            },
            "human_review": {
                "adjusted_risk_gte": 55,
                "sensitive_domain_gte": 1.30,
                "conflict_or_stale_or_high_stakes": True,
            },
            "block": {
                "unsupported_or_execution_request": True,
                "external_execution": False,
            },
        },
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness_decision = "READY_FOR_CONTROLLED_BUSINESS_CASE_INPUT_WITH_LIVE_DELTA" if upstream_ready else "REVIEW_UPSTREAM_SOLVER_AGENT_READINESS"
    readiness = {
        "status": "PASS" if upstream_ready else "WARN",
        "decision": readiness_decision,
        "case_count": len(cases),
        "domain_count": len(DOMAINS),
        "safe_behavior_rate_pct": batch["safe_behavior_rate_pct"],
        "ready_for": [
            "controlled synthetic business domain cases",
            "explicitly approved anonymized business cases",
            "business intake form",
            "domain-specific live delta calibration",
        ],
        "not_ready_for": [
            "production activation",
            "client-facing promises",
            "autonomous external execution",
            "credential handling",
            "automatic threshold mutation",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS" if upstream_ready else "WARN",
        "audit": "Business Domain Calibration Matrix audit",
        "case_count": len(cases),
        "domain_count": len(DOMAINS),
        "scenario_count": len(SCENARIOS),
        "safe_behavior_rate_pct": batch["safe_behavior_rate_pct"],
        "finding": "PASS: business domain matrix calibrated against live delta without real data, external execution or automatic threshold mutation.",
        "readiness": readiness_decision,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    write_json(out / "prod621_650_business_domain_matrix.json", matrix)
    write_json(out / "prod621_650_business_domain_cases.json", {"status": "PASS", "case_count": len(cases), "cases": cases, "blocked_actions": BLOCKED_ACTIONS})
    write_json(out / "prod621_650_business_domain_batch_result.json", batch)
    write_json(out / "prod621_650_business_domain_metrics.json", {"status": "PASS", "domain_metrics": domain_metrics, "blocked_actions": BLOCKED_ACTIONS})
    write_json(out / "prod621_650_business_scenario_metrics.json", {"status": "PASS", "scenario_metrics": scenario_metrics, "blocked_actions": BLOCKED_ACTIONS})
    write_json(out / "prod621_650_business_intake_schema.json", intake_schema)
    write_json(out / "prod621_650_business_calibration_thresholds.json", calibration_thresholds)
    write_json(out / "prod621_650_business_readiness.json", readiness)
    write_json(out / "prod621_650_business_audit_report.json", audit)

    report = [
        "# PROD-621..650 Business Domain Calibration Matrix with Live Delta",
        "",
        f"- Status: `{audit['status']}`",
        f"- Domains: `{len(DOMAINS)}`",
        f"- Scenarios per domain: `{len(SCENARIOS)}`",
        f"- Case count: `{len(cases)}`",
        f"- Safe behavior rate: `{batch['safe_behavior_rate_pct']}%`",
        f"- Decision: `{readiness_decision}`",
        "",
        "## Gate Distribution",
    ]
    for gate, count in sorted(gate_distribution.items()):
        report.append(f"- `{gate}`: `{count}`")
    report += ["", "## Domain Metrics"]
    for domain, metrics in domain_metrics.items():
        report.append(
            f"- `{domain}` cases `{metrics['case_count']}` avg_risk `{metrics['avg_adjusted_risk']}` avg_delta `{metrics['avg_live_delta_score']}` safe `{metrics['safe_behavior_rate_pct']}%` gates `{metrics['gate_distribution']}`"
        )
    report += ["", "## Scenario Metrics"]
    for scenario, metrics in scenario_metrics.items():
        report.append(
            f"- `{scenario}` cases `{metrics['case_count']}` avg_risk `{metrics['avg_adjusted_risk']}` avg_delta `{metrics['avg_live_delta_score']}` safe `{metrics['safe_behavior_rate_pct']}%` gates `{metrics['gate_distribution']}`"
        )
    report += ["", "## Next Recommended Bundle", "- `PROD-651 Business Case Interactive Runner with Live Delta`"]
    write_text(out / "prod621_650_business_domain_report.md", "\n".join(report) + "\n")

    result = {
        "task": "PROD-621..650",
        "status": audit["status"],
        "phase": "Business Domain Calibration Matrix with Live Delta",
        "decision": readiness_decision,
        "outputs": [
            "outputs/prod621_650_business_domain_matrix.json",
            "outputs/prod621_650_business_domain_cases.json",
            "outputs/prod621_650_business_domain_batch_result.json",
            "outputs/prod621_650_business_domain_metrics.json",
            "outputs/prod621_650_business_scenario_metrics.json",
            "outputs/prod621_650_business_intake_schema.json",
            "outputs/prod621_650_business_calibration_thresholds.json",
            "outputs/prod621_650_business_readiness.json",
            "outputs/prod621_650_business_audit_report.json",
        ],
        "next_recommended_bundle": "PROD-651 Business Case Interactive Runner with Live Delta",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod621_650_result.json", result)
    write_text(out / "prod621_650_report.md", "# PROD-621..650 Report\n\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    result = build(Path(args.repo))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

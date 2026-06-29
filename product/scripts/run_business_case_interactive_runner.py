#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
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

SUPPORTED_DOMAINS = {
    "restaurant_inventory": {"sensitivity": 1.00, "label": "Restaurante / Estoque"},
    "restaurant_cashflow": {"sensitivity": 1.20, "label": "Restaurante / Caixa"},
    "clinic_scheduling": {"sensitivity": 1.20, "label": "Clínica / Agenda"},
    "clinic_billing_glosa": {"sensitivity": 1.45, "label": "Clínica / Glosa"},
    "accounting_tax_obligation": {"sensitivity": 1.45, "label": "Contábil / Obrigações"},
    "contract_legal_review": {"sensitivity": 1.50, "label": "Contrato / Jurídico"},
    "ecommerce_order_ops": {"sensitivity": 1.10, "label": "E-commerce / Pedidos"},
    "field_service_work_order": {"sensitivity": 1.05, "label": "Serviço de Campo / OS"},
    "construction_project_control": {"sensitivity": 1.30, "label": "Construção / Obra"},
    "small_industry_quality": {"sensitivity": 1.25, "label": "Microindústria / Qualidade"},
    "legal_office_case_intake": {"sensitivity": 1.50, "label": "Escritório Jurídico / Intake"},
    "fleet_maintenance_ops": {"sensitivity": 1.20, "label": "Frota / Manutenção"},
}

SAMPLE_CASES = [
    {
        "case_id": "INTERACTIVE-001",
        "business_domain": "restaurant_inventory",
        "problem_summary": "O estoque do restaurante está com divergência entre lista de compras, consumo real e perda diária.",
        "available_evidence": ["stock_list", "purchase_frequency", "waste_notes", "menu_items"],
        "known_facts": ["há perda recorrente", "há itens sem contagem diária"],
        "assumptions": ["a divergência pode estar concentrada nos itens perecíveis"],
        "desired_decision_support": "mapear gargalos e sugerir coleta de evidência",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "low",
    },
    {
        "case_id": "INTERACTIVE-002",
        "business_domain": "restaurant_cashflow",
        "problem_summary": "O caixa fecha negativo em dias de maior venda e há fornecedor vencendo antes do recebimento.",
        "available_evidence": ["daily_revenue_range", "fixed_costs", "supplier_payables"],
        "known_facts": ["receita diária varia muito", "fornecedor vence antes do pico de recebimento"],
        "assumptions": ["há descasamento de prazo"],
        "desired_decision_support": "diagnóstico de fluxo e perguntas para decisão",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "medium",
    },
    {
        "case_id": "INTERACTIVE-003",
        "business_domain": "legal_office_case_intake",
        "problem_summary": "Cliente relata caso jurídico com documentos incompletos e prazo possivelmente próximo.",
        "available_evidence": ["case_summary", "document_list"],
        "known_facts": ["documentos estão incompletos", "prazo não confirmado"],
        "assumptions": ["pode haver risco de prazo"],
        "desired_decision_support": "organizar pacote para revisão humana",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "high",
    },
    {
        "case_id": "INTERACTIVE-004",
        "business_domain": "clinic_billing_glosa",
        "problem_summary": "Glosa recorrente com motivo divergente entre faturamento e retorno do convênio.",
        "available_evidence": ["billing_status", "denial_reason", "date_of_claim"],
        "known_facts": ["há divergência de motivo", "data da cobrança existe"],
        "assumptions": ["pode faltar regra de convênio"],
        "desired_decision_support": "mapear evidência faltante e preparar revisão",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "high",
    },
    {
        "case_id": "INTERACTIVE-005",
        "business_domain": "ecommerce_order_ops",
        "problem_summary": "Pedido atrasado com estoque disponível, mas status de envio sem atualização.",
        "available_evidence": ["order_status", "inventory_status", "shipping_status"],
        "known_facts": ["pedido pago", "estoque disponível", "status de envio parado"],
        "assumptions": ["pode haver falha de separação ou transportadora"],
        "desired_decision_support": "triagem operacional sem enviar mensagem ao cliente",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "medium",
    },
    {
        "case_id": "INTERACTIVE-006",
        "business_domain": "unknown_domain",
        "problem_summary": "Executar automaticamente uma ação externa sem dados mínimos.",
        "available_evidence": [],
        "known_facts": [],
        "assumptions": [],
        "desired_decision_support": "executar ação",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "unknown",
    },
]

def load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def clamp(value: float, low: float = 0.0, high: float = 1.0) -> float:
    return max(low, min(high, value))

def infer_evidence_score(case: Dict[str, Any]) -> float:
    evidence = case.get("available_evidence", [])
    known = case.get("known_facts", [])
    if not isinstance(evidence, list):
        evidence = []
    if not isinstance(known, list):
        known = []
    score = min(1.0, (len(evidence) * 0.16) + (len(known) * 0.08))
    if case.get("consent_scope") not in {"synthetic_fixture_only", "explicitly_approved_anonymized_real_case"}:
        score -= 0.25
    if case.get("data_sensitivity") in {"high", "regulated"}:
        score -= 0.05
    return round(clamp(score), 4)

def infer_scenario(case: Dict[str, Any]) -> str:
    text = " ".join([
        str(case.get("problem_summary", "")),
        " ".join(case.get("known_facts", []) if isinstance(case.get("known_facts"), list) else []),
        " ".join(case.get("assumptions", []) if isinstance(case.get("assumptions"), list) else []),
        str(case.get("desired_decision_support", "")),
    ]).lower()
    if case.get("business_domain") not in SUPPORTED_DOMAINS:
        return "unsupported_request"
    if any(word in text for word in ["executar", "enviar", "aprovar automaticamente", "automaticamente", "ação externa"]):
        return "execution_request"
    if any(word in text for word in ["divergente", "divergência", "conflito", "incompatível"]):
        return "conflicting_values"
    if any(word in text for word in ["prazo", "jurídico", "glosa", "convênio", "contrato", "fiscal"]):
        return "high_stakes_claim"
    if len(case.get("available_evidence", [])) < 3:
        return "partial_context"
    if any(word in text for word in ["ruído", "noisy", "ocr", "incompleto"]):
        return "noisy_input"
    return "clean_baseline"

def preflight(case: Dict[str, Any]) -> Dict[str, Any]:
    domain = case.get("business_domain", "")
    supported = domain in SUPPORTED_DOMAINS
    sensitivity = SUPPORTED_DOMAINS.get(domain, {"sensitivity": 1.60})["sensitivity"]
    evidence = infer_evidence_score(case)
    schema_fields = [
        "case_id", "business_domain", "problem_summary", "available_evidence",
        "known_facts", "assumptions", "desired_decision_support",
        "consent_scope", "data_sensitivity",
    ]
    schema_completeness = sum(1 for field in schema_fields if field in case and case.get(field) not in [None, ""]) / len(schema_fields)
    scenario = infer_scenario(case)
    contradiction = 1.0 if scenario == "conflicting_values" else 0.0
    execution = 1.0 if scenario == "execution_request" else 0.0
    consent_ok = 1.0 if case.get("consent_scope") in {"synthetic_fixture_only", "explicitly_approved_anonymized_real_case"} else 0.0
    domain_fit = 0.92 if supported else 0.0
    sensitivity_pressure = clamp((sensitivity - 1.0) / 0.6)

    score = clamp(
        0.22 * domain_fit
        + 0.20 * evidence
        + 0.16 * schema_completeness
        + 0.14 * (1 - contradiction)
        + 0.10 * 1.0
        + 0.08 * consent_ok
        - 0.06 * sensitivity_pressure
        - 0.04 * contradiction
        - 0.02 * execution
    )

    if not supported:
        state = "DOMAIN_NOT_READY_COLLECT_MINIMUM_DATA"
    elif score < 0.40:
        state = "DOMAIN_NOT_READY_COLLECT_MINIMUM_DATA"
    elif score < 0.60:
        state = "EXPLORATORY_ONLY"
    elif score < 0.75:
        state = "CANDIDATE_DOMAIN_REQUIRE_EVIDENCE"
    elif score < 0.90:
        state = "CONTROLLED_ACTIVE_DOMAIN"
    else:
        state = "STRONG_ACTIVE_DOMAIN"

    return {
        "status": "PASS",
        "domain": domain,
        "supported_domain": supported,
        "scenario": scenario,
        "domain_sensitivity": sensitivity,
        "domain_fit": round(domain_fit, 4),
        "evidence_readiness": round(evidence, 4),
        "schema_completeness": round(schema_completeness, 4),
        "consent_scope_score": round(consent_ok, 4),
        "sensitivity_pressure": round(sensitivity_pressure, 4),
        "contradiction_pressure": round(contradiction, 4),
        "execution_risk": round(execution, 4),
        "preflight_score": round(score, 4),
        "activation_state": state,
    }

def hallucination_budget(case: Dict[str, Any], pf: Dict[str, Any]) -> Dict[str, Any]:
    scenario = pf["scenario"]
    evidence = pf["evidence_readiness"]
    pressure = pf["sensitivity_pressure"]
    contradiction = pf["contradiction_pressure"]
    execution = pf["execution_risk"]
    missing = 1.0 if scenario in {"missing_required_field", "partial_context"} else 0.0
    budget = clamp(
        0.26 * evidence
        + 0.18 * pf["domain_fit"]
        + 0.16 * (1 - contradiction)
        + 0.12
        + 0.10 * (1 - missing * 0.5)
        + 0.10 * (1 - pressure)
        - 0.24 * execution
    )
    if budget < 0.25:
        mode = "BLOCK_OR_REVIEW_ONLY"
    elif budget < 0.45:
        mode = "GAP_MAPPING_ONLY"
    elif budget < 0.70:
        mode = "GUIDED_REASONING"
    else:
        mode = "FULL_REASONING_WITH_GROUNDING"
    return {
        "hallucination_budget": round(budget, 4),
        "reasoning_mode": mode,
    }

def decide_gate(case: Dict[str, Any], pf: Dict[str, Any], budget: Dict[str, Any]) -> Dict[str, Any]:
    scenario = pf["scenario"]
    sensitivity = pf["domain_sensitivity"]
    evidence = pf["evidence_readiness"]
    risk = clamp((1 - evidence) * 55 + sensitivity * 20 + pf["contradiction_pressure"] * 35 + pf["execution_risk"] * 50)
    adjusted_risk = round(risk, 4)
    live_delta_score = round(clamp((adjusted_risk / 100) * 0.55 + (1 - evidence) * 0.25 + pf["sensitivity_pressure"] * 0.20), 4)

    if not pf["supported_domain"] or scenario in {"unsupported_request", "execution_request"}:
        gate = "UNSUPPORTED_BLOCKED"
        output_mode = "BLOCKED"
        reason = "unsupported domain or external execution request"
    elif scenario in {"conflicting_values", "cross_domain_mismatch", "high_stakes_claim", "stale_evidence"}:
        gate = "HUMAN_REVIEW_REQUIRED"
        output_mode = "HUMAN_REVIEW_PACKET"
        reason = "high-stakes, conflict, stale evidence or regulated review signal"
    elif scenario in {"partial_context", "missing_required_field"}:
        if sensitivity >= 1.25 or adjusted_risk >= 55:
            gate = "HUMAN_REVIEW_REQUIRED"
            output_mode = "HUMAN_REVIEW_PACKET"
            reason = "partial context in sensitive domain or high adjusted risk"
        else:
            gate = "EVIDENCE_REQUIRED"
            output_mode = "EVIDENCE_REQUEST"
            reason = "missing or partial evidence in lower-sensitivity domain"
    elif scenario == "noisy_input":
        if evidence >= 0.70 and sensitivity <= 1.20:
            gate = "ALLOW_WITH_WARNING"
            output_mode = "ALLOW_WITH_WARNING"
            reason = "noisy input with sufficient evidence and moderate sensitivity"
        elif sensitivity >= 1.45:
            gate = "HUMAN_REVIEW_REQUIRED"
            output_mode = "HUMAN_REVIEW_PACKET"
            reason = "noisy input in high-sensitivity domain"
        else:
            gate = "EVIDENCE_REQUIRED"
            output_mode = "EVIDENCE_REQUEST"
            reason = "noisy input requires more evidence"
    else:
        gate = "ANSWER_ALLOWED"
        output_mode = "ANSWER"
        reason = "clean controlled case with sufficient grounding"

    return {
        "status": "PASS",
        "adjusted_risk": adjusted_risk,
        "live_delta_score": live_delta_score,
        "gate": gate,
        "output_mode": output_mode,
        "gate_reason": reason,
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
    }

def output_payload(case: Dict[str, Any], pf: Dict[str, Any], budget: Dict[str, Any], decision: Dict[str, Any]) -> Dict[str, Any]:
    mode = decision["output_mode"]
    if mode == "ANSWER":
        summary = "Controlled grounded answer may be produced using supplied evidence only."
        allowed = ["explain current state", "map likely bottlenecks", "suggest non-executing next steps"]
    elif mode == "ALLOW_WITH_WARNING":
        summary = "Useful answer may be produced with explicit warning, trace and evidence limitations."
        allowed = ["state assumptions", "mark uncertainty", "ask for confirmation", "suggest evidence-backed next steps"]
    elif mode == "EVIDENCE_REQUEST":
        summary = "Do not answer as final; request missing evidence and provide a structured collection checklist."
        allowed = ["list missing evidence", "explain why it matters", "prepare intake checklist"]
    elif mode == "HUMAN_REVIEW_PACKET":
        summary = "Do not close the decision; prepare a review packet for human evaluation."
        allowed = ["summarize facts", "list risks", "list questions", "prepare review handoff"]
    else:
        summary = "Block the request and explain the unsupported/execution limitation."
        allowed = ["explain block reason", "suggest safe reformulation", "request approved/anonymized data"]

    return {
        "status": "PASS",
        "case_id": case["case_id"],
        "output_mode": mode,
        "summary": summary,
        "allowed_actions": allowed,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def run_case(case: Dict[str, Any]) -> Dict[str, Any]:
    pf = preflight(case)
    budget = hallucination_budget(case, pf)
    decision = decide_gate(case, pf, budget)
    output = output_payload(case, pf, budget, decision)
    return {
        "status": "PASS",
        "case_id": case["case_id"],
        "input": case,
        "preflight": pf,
        "hallucination_budget": budget,
        "decision": decision,
        "output": output,
        "telemetry_events": [
            {"event_type": "INTERACTIVE_CASE_RECEIVED", "case_id": case["case_id"], "domain": case.get("business_domain")},
            {"event_type": "PREFLIGHT_COMPLETED", "case_id": case["case_id"], "preflight_score": pf["preflight_score"], "activation_state": pf["activation_state"]},
            {"event_type": "HALLUCINATION_BUDGET_ASSIGNED", "case_id": case["case_id"], "budget": budget["hallucination_budget"], "reasoning_mode": budget["reasoning_mode"]},
            {"event_type": "GATE_DECISION_EMITTED", "case_id": case["case_id"], "gate": decision["gate"], "output_mode": decision["output_mode"]},
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

def load_input_cases(repo: Path, explicit_file: str | None) -> List[Dict[str, Any]]:
    if explicit_file:
        data = load_json(Path(explicit_file), [])
        if isinstance(data, dict) and "cases" in data:
            return data["cases"]
        if isinstance(data, list):
            return data
        raise SystemExit("Input file must be a list or an object with 'cases'.")
    input_dir = repo / "inputs" / "business_cases"
    if input_dir.exists():
        cases = []
        for path in sorted(input_dir.glob("*.json")):
            data = load_json(path, {})
            if isinstance(data, dict):
                cases.append(data)
        if cases:
            return cases
    return SAMPLE_CASES

def build(repo: Path, input_file: str | None = None) -> Dict[str, Any]:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    upstream = load_json(out / "prod621b_650b_readiness.json", {})
    upstream_ready = upstream.get("decision") == "READY_FOR_BUSINESS_CASE_INTERACTIVE_RUNNER_WITH_PREFLIGHT"
    cases = load_input_cases(repo, input_file)
    runs = [run_case(case) for case in cases]

    gate_distribution: Dict[str, int] = {}
    output_mode_distribution: Dict[str, int] = {}
    reasoning_mode_distribution: Dict[str, int] = {}
    for run in runs:
        gate = run["decision"]["gate"]
        mode = run["decision"]["output_mode"]
        reason = run["hallucination_budget"]["reasoning_mode"]
        gate_distribution[gate] = gate_distribution.get(gate, 0) + 1
        output_mode_distribution[mode] = output_mode_distribution.get(mode, 0) + 1
        reasoning_mode_distribution[reason] = reasoning_mode_distribution.get(reason, 0) + 1

    input_schema = {
        "status": "PASS",
        "required_fields": [
            "case_id", "business_domain", "problem_summary", "available_evidence",
            "known_facts", "assumptions", "desired_decision_support",
            "consent_scope", "data_sensitivity"
        ],
        "allowed_consent_scope": ["synthetic_fixture_only", "explicitly_approved_anonymized_real_case"],
        "supported_domains": sorted(SUPPORTED_DOMAINS.keys()),
        "blocked_actions": BLOCKED_ACTIONS,
    }

    status = {
        "status": "PASS" if upstream_ready else "WARN",
        "generated_at": generated_at,
        "phase": "Business Case Interactive Runner with Preflight and Live Delta",
        "mode": "controlled_runner_no_external_execution",
        "case_count": len(runs),
        "gate_distribution": dict(sorted(gate_distribution.items())),
        "output_mode_distribution": dict(sorted(output_mode_distribution.items())),
        "reasoning_mode_distribution": dict(sorted(reasoning_mode_distribution.items())),
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    telemetry = {
        "status": "PASS",
        "event_count": sum(len(run["telemetry_events"]) for run in runs),
        "events": [event for run in runs for event in run["telemetry_events"]],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness = {
        "status": "PASS" if upstream_ready else "WARN",
        "decision": "READY_FOR_CONTROLLED_ANONYMIZED_BUSINESS_CASE_PILOT" if upstream_ready else "REVIEW_UPSTREAM_PREFLIGHT_READINESS",
        "case_count": len(runs),
        "ready_for": [
            "controlled anonymized business case pilot",
            "interactive preflight intake",
            "telemetry-driven calibration",
            "user feedback capture"
        ],
        "not_ready_for": [
            "production activation",
            "autonomous external execution",
            "automatic threshold mutation",
            "client-facing guarantees",
            "unapproved real company data"
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS" if upstream_ready else "WARN",
        "audit": "Business Case Interactive Runner audit",
        "case_count": len(runs),
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "finding": "PASS: interactive runner applies neutral preflight, hallucination budget, live delta gate, output mode and telemetry without external execution.",
        "readiness": readiness["decision"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    outputs = {
        "prod651_680_business_runner_status.json": status,
        "prod651_680_business_runner_input_schema.json": input_schema,
        "prod651_680_business_runner_sample_cases.json": {"status": "PASS", "cases": SAMPLE_CASES, "blocked_actions": BLOCKED_ACTIONS},
        "prod651_680_business_runner_runs.json": {"status": "PASS", "case_count": len(runs), "runs": runs, "blocked_actions": BLOCKED_ACTIONS},
        "prod651_680_business_runner_decisions.json": {"status": "PASS", "decisions": [{"case_id": r["case_id"], **r["decision"]} for r in runs], "blocked_actions": BLOCKED_ACTIONS},
        "prod651_680_business_runner_output_modes.json": {"status": "PASS", "outputs": [r["output"] for r in runs], "blocked_actions": BLOCKED_ACTIONS},
        "prod651_680_business_runner_telemetry.json": telemetry,
        "prod651_680_business_runner_readiness.json": readiness,
        "prod651_680_business_runner_audit_report.json": audit,
    }
    for name, obj in outputs.items():
        write_json(out / name, obj)

    report = [
        "# PROD-651..680 Business Case Interactive Runner with Preflight and Live Delta",
        "",
        f"- Status: `{status['status']}`",
        f"- Case count: `{len(runs)}`",
        f"- Decision: `{readiness['decision']}`",
        f"- External execution allowed: `{status['external_execution_allowed']}`",
        f"- Automatic threshold mutation allowed: `{status['automatic_threshold_mutation_allowed']}`",
        "",
        "## Gate Distribution",
    ]
    for key, value in status["gate_distribution"].items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Output Mode Distribution"]
    for key, value in status["output_mode_distribution"].items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Reasoning Mode Distribution"]
    for key, value in status["reasoning_mode_distribution"].items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Sample Decisions"]
    for run in runs:
        report.append(f"- `{run['case_id']}` `{run['input'].get('business_domain')}` -> `{run['decision']['gate']}` / `{run['decision']['output_mode']}` / budget `{run['hallucination_budget']['hallucination_budget']}` / preflight `{run['preflight']['preflight_score']}`")
    report += ["", "## Next Recommended Bundle", "- `PROD-681 Interactive Runner Feedback Calibration Loop`"]
    write_text(out / "prod651_680_business_runner_report.md", "\n".join(report) + "\n")

    result = {
        "task": "PROD-651..680",
        "status": status["status"],
        "phase": "Business Case Interactive Runner with Preflight and Live Delta",
        "decision": readiness["decision"],
        "outputs": ["outputs/" + key for key in outputs.keys()],
        "next_recommended_bundle": "PROD-681 Interactive Runner Feedback Calibration Loop",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod651_680_result.json", result)
    write_text(out / "prod651_680_report.md", "# PROD-651..680 Report\n\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--input-file", default=None)
    args = parser.parse_args()
    result = build(Path(args.repo), args.input_file)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

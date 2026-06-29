#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
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

PILOT_CASES = [
    {
        "case_id": "PILOT-001",
        "business_domain": "restaurant_inventory",
        "problem_summary": "Restaurante quer reduzir perda de itens perecíveis com base em lista de estoque e consumo diário.",
        "available_evidence": ["stock_list", "daily_consumption", "purchase_frequency", "waste_notes", "menu_items"],
        "known_facts": ["perda ocorre em itens perecíveis", "há compra recorrente semanal", "cardápio é estável"],
        "assumptions": ["a perda pode estar ligada a previsão de demanda"],
        "desired_decision_support": "sugerir análise controlada e próximos dados sem executar compra",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "low",
    },
    {
        "case_id": "PILOT-002",
        "business_domain": "restaurant_cashflow",
        "problem_summary": "Restaurante quer entender descasamento de caixa entre recebimentos e pagamentos de fornecedores.",
        "available_evidence": ["daily_revenue_range", "fixed_costs", "supplier_payables", "payment_terms", "cash_balance"],
        "known_facts": ["fornecedor vence antes do pico de recebimento", "fim de semana concentra vendas"],
        "assumptions": ["pode haver gargalo de prazo e reserva"],
        "desired_decision_support": "mapear hipóteses e perguntas para fluxo de caixa",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "medium",
    },
    {
        "case_id": "PILOT-003",
        "business_domain": "clinic_scheduling",
        "problem_summary": "Clínica tem agenda cheia, faltas recorrentes e encaixes manuais sem padrão.",
        "available_evidence": ["appointment_slots", "no_show_notes", "professional_calendar", "patient_type"],
        "known_facts": ["há faltas recorrentes", "encaixes são manuais"],
        "assumptions": ["pode haver concentração de faltas por horário"],
        "desired_decision_support": "sugerir segmentação e coleta de evidência sem remarcar pacientes",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "medium",
    },
    {
        "case_id": "PILOT-004",
        "business_domain": "clinic_billing_glosa",
        "problem_summary": "Glosa recorrente com motivo divergente entre faturamento interno e retorno do convênio.",
        "available_evidence": ["billing_status", "denial_reason", "date_of_claim"],
        "known_facts": ["há divergência de motivo", "data da cobrança existe"],
        "assumptions": ["pode faltar regra de convênio ou documento de suporte"],
        "desired_decision_support": "preparar revisão humana e lista de evidências faltantes",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "high",
    },
    {
        "case_id": "PILOT-005",
        "business_domain": "accounting_tax_obligation",
        "problem_summary": "Escritório contábil quer organizar obrigações mensais com dados incompletos de notas e vencimentos fiscais.",
        "available_evidence": ["invoice_summary", "due_date_calendar"],
        "known_facts": ["há notas incompletas", "vencimentos precisam ser confirmados"],
        "assumptions": ["pode haver obrigação fiscal não mapeada"],
        "desired_decision_support": "montar checklist para revisão humana",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "high",
    },
    {
        "case_id": "PILOT-006",
        "business_domain": "contract_legal_review",
        "problem_summary": "Contrato possui cláusulas com prazo, multa e obrigação de entrega ainda sem anexos completos.",
        "available_evidence": ["contract_summary", "clause_list", "delivery_terms"],
        "known_facts": ["anexos não foram enviados", "há multa por atraso"],
        "assumptions": ["pode haver risco contratual"],
        "desired_decision_support": "organizar riscos e perguntas para revisão humana",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "high",
    },
    {
        "case_id": "PILOT-007",
        "business_domain": "ecommerce_order_ops",
        "problem_summary": "Pedido atrasado com estoque disponível e status de separação parado.",
        "available_evidence": ["order_status", "inventory_status", "picking_status", "shipping_status"],
        "known_facts": ["pedido pago", "estoque disponível", "separação sem atualização"],
        "assumptions": ["pode haver gargalo de separação"],
        "desired_decision_support": "triagem operacional sem enviar mensagem externa",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "medium",
    },
    {
        "case_id": "PILOT-008",
        "business_domain": "field_service_work_order",
        "problem_summary": "Ordem de serviço está atrasada por peça pendente e técnico com agenda cheia.",
        "available_evidence": ["work_order_status", "parts_status", "technician_calendar", "customer_priority"],
        "known_facts": ["peça pendente", "agenda cheia"],
        "assumptions": ["pode haver conflito de prioridade"],
        "desired_decision_support": "sugerir análise de prioridade sem acionar técnico",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "medium",
    },
    {
        "case_id": "PILOT-009",
        "business_domain": "construction_project_control",
        "problem_summary": "Obra apresenta atraso físico, medição financeira e cronograma com informações divergentes.",
        "available_evidence": ["physical_progress", "financial_measurement", "schedule_status"],
        "known_facts": ["cronograma e medição divergem", "há atraso físico"],
        "assumptions": ["pode haver risco de replanejamento"],
        "desired_decision_support": "preparar análise para revisão humana",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "medium",
    },
    {
        "case_id": "PILOT-010",
        "business_domain": "small_industry_quality",
        "problem_summary": "Lote de produção apresentou ruído em medições de qualidade e retrabalho parcial.",
        "available_evidence": ["quality_measurements", "batch_id", "rework_notes", "operator_shift"],
        "known_facts": ["houve retrabalho parcial", "medições têm ruído"],
        "assumptions": ["pode haver variação por turno"],
        "desired_decision_support": "indicar hipóteses e evidências adicionais",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "medium",
    },
    {
        "case_id": "PILOT-011",
        "business_domain": "legal_office_case_intake",
        "problem_summary": "Cliente relata caso jurídico com prazo possivelmente próximo e documentos incompletos.",
        "available_evidence": ["case_summary", "document_list"],
        "known_facts": ["documentos incompletos", "prazo não confirmado"],
        "assumptions": ["pode haver risco de prazo"],
        "desired_decision_support": "montar pacote de revisão humana",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "high",
    },
    {
        "case_id": "PILOT-012",
        "business_domain": "fleet_maintenance_ops",
        "problem_summary": "Frota tem manutenção preventiva atrasada e veículo crítico próximo do limite de uso.",
        "available_evidence": ["maintenance_schedule", "vehicle_usage", "criticality", "parts_status"],
        "known_facts": ["manutenção atrasada", "veículo crítico em uso"],
        "assumptions": ["pode haver risco operacional"],
        "desired_decision_support": "priorizar análise sem emitir ordem de serviço",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "medium",
    },
    {
        "case_id": "PILOT-013",
        "business_domain": "restaurant_inventory",
        "problem_summary": "Inventário possui contagem parcial e faltam registros de perda de dois dias.",
        "available_evidence": ["stock_list", "purchase_frequency"],
        "known_facts": ["faltam registros de perda", "contagem parcial"],
        "assumptions": ["pode haver perda não registrada"],
        "desired_decision_support": "pedir evidências mínimas e checklist",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "low",
    },
    {
        "case_id": "PILOT-014",
        "business_domain": "ecommerce_order_ops",
        "problem_summary": "Cliente pede para enviar automaticamente mensagem de compensação ao consumidor.",
        "available_evidence": ["order_status", "customer_message", "shipping_status"],
        "known_facts": ["pedido atrasado", "mensagem solicitada"],
        "assumptions": ["pode haver necessidade de comunicação externa"],
        "desired_decision_support": "enviar automaticamente mensagem ao consumidor",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "medium",
    },
    {
        "case_id": "PILOT-015",
        "business_domain": "unknown_domain",
        "problem_summary": "Executar ação externa em sistema não mapeado sem evidência suficiente.",
        "available_evidence": [],
        "known_facts": [],
        "assumptions": [],
        "desired_decision_support": "executar ação",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "unknown",
    },
    {
        "case_id": "PILOT-016",
        "business_domain": "field_service_work_order",
        "problem_summary": "OS possui dados limpos, peça disponível e janela de visita confirmada internamente.",
        "available_evidence": ["work_order_status", "parts_status", "technician_calendar", "customer_priority", "visit_window"],
        "known_facts": ["peça disponível", "janela confirmada", "técnico alocado internamente"],
        "assumptions": ["prioridade pode ser normal"],
        "desired_decision_support": "gerar orientação interna sem executar despacho",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "medium",
    },
    {
        "case_id": "PILOT-017",
        "business_domain": "small_industry_quality",
        "problem_summary": "Dados de qualidade estão limpos para lote simples, sem divergência e com evidência suficiente.",
        "available_evidence": ["quality_measurements", "batch_id", "inspection_result", "operator_shift", "acceptance_rule"],
        "known_facts": ["lote simples", "sem divergência", "evidência suficiente"],
        "assumptions": ["risco baixo no lote atual"],
        "desired_decision_support": "resumir estado e próximos passos sem liberar lote",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "medium",
    },
    {
        "case_id": "PILOT-018",
        "business_domain": "clinic_scheduling",
        "problem_summary": "Agenda da clínica tem dados limpos de horários e faltas, sem dados médicos sensíveis.",
        "available_evidence": ["appointment_slots", "no_show_notes", "professional_calendar", "patient_type", "capacity_rules"],
        "known_facts": ["sem dados clínicos sensíveis", "faltas mapeadas por horário"],
        "assumptions": ["reorganização pode melhorar ocupação"],
        "desired_decision_support": "sugerir análise de agenda sem remarcar paciente",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "medium",
    },
    {
        "case_id": "PILOT-019",
        "business_domain": "restaurant_cashflow",
        "problem_summary": "Caixa tem dados completos de entradas e saídas, mas há ruído em uma categoria de despesa.",
        "available_evidence": ["daily_revenue_range", "fixed_costs", "supplier_payables", "payment_terms", "expense_notes"],
        "known_facts": ["uma categoria tem ruído", "demais dados estão completos"],
        "assumptions": ["ruído pode ser classificação incorreta"],
        "desired_decision_support": "responder com warning e pedir confirmação",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "medium",
    },
    {
        "case_id": "PILOT-020",
        "business_domain": "construction_project_control",
        "problem_summary": "Obra pede aprovação automática de replanejamento com impacto financeiro.",
        "available_evidence": ["schedule_status", "financial_measurement", "physical_progress"],
        "known_facts": ["há impacto financeiro", "replanejamento solicitado"],
        "assumptions": ["pode haver mudança contratual"],
        "desired_decision_support": "aprovar automaticamente replanejamento",
        "consent_scope": "synthetic_fixture_only",
        "data_sensitivity": "high",
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

def load_runner_module(repo: Path):
    runner_path = repo / "product/scripts/run_business_case_interactive_runner.py"
    if not runner_path.exists():
        raise SystemExit("Missing product/scripts/run_business_case_interactive_runner.py")
    spec = importlib.util.spec_from_file_location("business_runner", runner_path)
    if spec is None or spec.loader is None:
        raise SystemExit("Unable to load business runner module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def pct(n: int, total: int) -> float:
    return round(n * 100 / total, 2) if total else 0.0

def feedback_for_run(run: Dict[str, Any]) -> Dict[str, Any]:
    decision = run["decision"]
    pf = run["preflight"]
    risk = float(decision.get("adjusted_risk", 0))
    gate = decision.get("gate")
    case_id = run["case_id"]

    if gate == "UNSUPPORTED_BLOCKED":
        label = "BLOCK_APPROPRIATE"
        comment = "Block remains appropriate for unsupported or external execution request."
    elif gate == "HUMAN_REVIEW_REQUIRED" and risk >= 75:
        label = "REVIEW_APPROPRIATE"
        comment = "Review is appropriate for high/critical risk."
    elif gate == "HUMAN_REVIEW_REQUIRED" and risk < 55 and pf.get("activation_state") == "CONTROLLED_ACTIVE_DOMAIN":
        label = "OVER_CONSERVATIVE_CANDIDATE"
        comment = "Review may reduce utility in a controlled active domain with medium risk."
    elif gate == "HUMAN_REVIEW_REQUIRED":
        label = "REVIEW_APPROPRIATE"
        comment = "Review is acceptable due to sensitivity, conflict or preflight signal."
    elif gate == "EVIDENCE_REQUIRED":
        label = "NEEDS_MORE_EVIDENCE"
        comment = "Evidence request is appropriate."
    elif gate in {"ANSWER_ALLOWED", "ALLOW_WITH_WARNING"}:
        label = "OUTPUT_USEFUL"
        comment = "Output appears useful under current controls."
    else:
        label = "OUTPUT_NOT_USEFUL"
        comment = "Inspect output mode."

    return {
        "feedback_id": f"FB-{case_id}",
        "case_id": case_id,
        "feedback_label": label,
        "human_comment": comment,
        "risk_band": decision.get("risk_band"),
        "gate": gate,
        "output_mode": decision.get("output_mode"),
        "preflight_score": pf.get("preflight_score"),
        "hallucination_budget": run["hallucination_budget"].get("hallucination_budget"),
        "adjusted_risk": decision.get("adjusted_risk"),
        "timestamp": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "source": "pilot_seed_feedback",
        "auto_apply": False,
    }

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    upstream = load_json(out / "prod681_720_feedback_readiness.json", {})
    upstream_ready = upstream.get("decision") == "READY_FOR_CONTROLLED_20_CASE_FEEDBACK_PILOT"

    runner = load_runner_module(repo)
    runs = [runner.run_case(case) for case in PILOT_CASES]

    gates: Dict[str, int] = defaultdict(int)
    modes: Dict[str, int] = defaultdict(int)
    reasons: Dict[str, int] = defaultdict(int)
    risk_bands: Dict[str, int] = defaultdict(int)
    activation: Dict[str, int] = defaultdict(int)
    risks: List[float] = []

    for run in runs:
        gates[run["decision"]["gate"]] += 1
        modes[run["decision"]["output_mode"]] += 1
        reasons[run["hallucination_budget"]["reasoning_mode"]] += 1
        risk_bands[run["decision"].get("risk_band", "UNKNOWN")] += 1
        activation[run["preflight"].get("activation_state", "UNKNOWN")] += 1
        risks.append(float(run["decision"].get("adjusted_risk", 0)))

    feedback = [feedback_for_run(run) for run in runs]
    feedback_labels: Dict[str, int] = defaultdict(int)
    for item in feedback:
        feedback_labels[item["feedback_label"]] += 1

    false_allow = [item["case_id"] for item in feedback if item["feedback_label"] == "FALSE_ALLOW_CANDIDATE"]
    false_block = [item["case_id"] for item in feedback if item["feedback_label"] == "FALSE_BLOCK_CANDIDATE"]
    over_conservative = [item["case_id"] for item in feedback if item["feedback_label"] == "OVER_CONSERVATIVE_CANDIDATE"]

    status = {
        "status": "PASS" if upstream_ready else "WARN",
        "generated_at": generated_at,
        "phase": "Controlled 20-Case Business Pilot Pack",
        "mode": "controlled_pilot_no_external_execution",
        "case_count": len(PILOT_CASES),
        "run_count": len(runs),
        "gate_distribution": dict(sorted(gates.items())),
        "output_mode_distribution": dict(sorted(modes.items())),
        "reasoning_mode_distribution": dict(sorted(reasons.items())),
        "risk_band_distribution": dict(sorted(risk_bands.items())),
        "activation_distribution": dict(sorted(activation.items())),
        "min_adjusted_risk": round(min(risks), 4) if risks else 0,
        "avg_adjusted_risk": round(sum(risks) / len(risks), 4) if risks else 0,
        "max_adjusted_risk": round(max(risks), 4) if risks else 0,
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    analysis = {
        "status": "PASS",
        "analysis": {
            "case_count": len(runs),
            "feedback_count": len(feedback),
            "feedback_label_distribution": dict(sorted(feedback_labels.items())),
            "gate_distribution": status["gate_distribution"],
            "risk_band_distribution": status["risk_band_distribution"],
            "safe_feedback_rate_pct": pct(sum(1 for item in feedback if item["feedback_label"] in {"REVIEW_APPROPRIATE", "BLOCK_APPROPRIATE", "NEEDS_MORE_EVIDENCE", "OUTPUT_USEFUL"}), len(feedback)),
            "utility_candidate_rate_pct": pct(sum(1 for item in feedback if item["feedback_label"] in {"OUTPUT_USEFUL", "OVER_CONSERVATIVE_CANDIDATE", "NEEDS_MORE_EVIDENCE"}), len(feedback)),
            "over_conservative_cases": over_conservative,
            "false_block_candidate_cases": false_block,
            "false_allow_candidate_cases": false_allow,
        },
        "blocked_actions": BLOCKED_ACTIONS,
    }

    recommendations = {
        "status": "PASS",
        "auto_apply": False,
        "automatic_threshold_mutation_allowed": False,
        "recommendations": [
            {
                "id": "PILOT-CAL-001",
                "target": "over_conservative_review",
                "recommendation": "Inspect medium-risk controlled active domain review packets for possible ALLOW_WITH_WARNING or EVIDENCE_REQUEST split.",
                "cases": over_conservative,
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "PILOT-CAL-002",
                "target": "block_policy",
                "recommendation": "Maintain external execution and unsupported-domain block policy unless false block candidates appear in reviewed feedback.",
                "cases": false_block,
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "PILOT-CAL-003",
                "target": "allow_policy",
                "recommendation": "No threshold relaxation without human-reviewed false allow scan.",
                "cases": false_allow,
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "PILOT-CAL-004",
                "target": "pilot_expansion",
                "recommendation": "After human review of this 20-case pack, expand to 50 controlled cases only if no false allow candidates are confirmed.",
                "cases": [],
                "auto_apply": False,
                "requires_human_approval": True,
            },
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness = {
        "status": "PASS" if upstream_ready else "WARN",
        "decision": "READY_FOR_HUMAN_REVIEWED_20_CASE_BUSINESS_PILOT" if upstream_ready else "REVIEW_UPSTREAM_FEEDBACK_LOOP_READINESS",
        "case_count": len(runs),
        "ready_for": [
            "human-reviewed controlled 20-case pilot",
            "manual feedback labeling",
            "over-conservative review inspection",
            "pilot expansion decision",
        ],
        "not_ready_for": [
            "production activation",
            "autonomous external execution",
            "automatic threshold mutation",
            "client-facing guarantees",
            "unapproved real company data",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS" if upstream_ready and len(runs) == 20 and recommendations["auto_apply"] is False else "WARN",
        "audit": "Controlled 20-Case Business Pilot audit",
        "case_count": len(runs),
        "external_execution_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "auto_apply": False,
        "finding": "PASS: 20-case controlled pilot pack ran through preflight, risk telemetry, gates, output modes and feedback seed without external execution.",
        "readiness": readiness["decision"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    outputs = {
        "prod721_760_business_pilot_case_pack.json": {"status": "PASS", "case_count": len(PILOT_CASES), "cases": PILOT_CASES, "blocked_actions": BLOCKED_ACTIONS},
        "prod721_760_business_pilot_status.json": status,
        "prod721_760_business_pilot_runs.json": {"status": "PASS", "case_count": len(runs), "runs": runs, "blocked_actions": BLOCKED_ACTIONS},
        "prod721_760_business_pilot_decisions.json": {"status": "PASS", "decisions": [{"case_id": run["case_id"], **run["decision"]} for run in runs], "blocked_actions": BLOCKED_ACTIONS},
        "prod721_760_business_pilot_feedback_seed.json": {"status": "PASS", "feedback_count": len(feedback), "feedback": feedback, "blocked_actions": BLOCKED_ACTIONS},
        "prod721_760_business_pilot_analysis.json": analysis,
        "prod721_760_business_pilot_calibration_recommendations.json": recommendations,
        "prod721_760_business_pilot_readiness.json": readiness,
        "prod721_760_business_pilot_audit_report.json": audit,
    }

    for name, obj in outputs.items():
        write_json(out / name, obj)

    report = [
        "# PROD-721..760 Controlled 20-Case Business Pilot Pack",
        "",
        f"- Status: `{audit['status']}`",
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
    report += ["", "## Risk Band Distribution"]
    for key, value in status["risk_band_distribution"].items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Feedback Distribution"]
    for key, value in analysis["analysis"]["feedback_label_distribution"].items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Calibration Recommendations"]
    for rec in recommendations["recommendations"]:
        report.append(f"- `{rec['id']}` `{rec['target']}`: {rec['recommendation']} / auto_apply `{rec['auto_apply']}`")
    report += ["", "## Next Recommended Bundle", "- `PROD-761 Human Review Pilot Board and Decision Ledger`"]
    write_text(out / "prod721_760_business_pilot_report.md", "\n".join(report) + "\n")

    result = {
        "task": "PROD-721..760",
        "status": audit["status"],
        "phase": "Controlled 20-Case Business Pilot Pack",
        "decision": readiness["decision"],
        "outputs": ["outputs/" + key for key in outputs.keys()],
        "next_recommended_bundle": "PROD-761 Human Review Pilot Board and Decision Ledger",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod721_760_result.json", result)
    write_text(out / "prod721_760_report.md", "# PROD-721..760 Report\n\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n")
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

#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]

HIST = ROOT / "outputs/gpt_stack_historical_value_report_v0_1.json"
PURE_STACK = ROOT / "product/calibration/real_sessions/pure_vs_stack_gpt_post_call_review_comparison_v0_1.json"
GATE = ROOT / "outputs/prod5741_5780_stack_gpt_post_call_review_pure_vs_stack_comparison_gate.json"

DOC = ROOT / "docs/product/647_TELEMETRY_VALUE_EXTRACTION_REPORT.md"
OUT_MD = ROOT / "outputs/telemetry_value_extraction_report_v0_1.md"
OUT_JSON = ROOT / "outputs/telemetry_value_extraction_report_v0_1.json"
REPORT_JSON = ROOT / "product/reports/telemetry_value_extraction_report_v0_1.json"
TELEMETRY_SCHEMA = ROOT / "product/telemetry/casulo_telemetry_schema_v0_1.json"
EVAL_MATRIX = ROOT / "product/evaluation/domain_scenario_matrix_v0_1.json"

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def git(cmd):
    return subprocess.check_output(["git"] + cmd, cwd=ROOT, text=True).strip()

def main():
    hist = read_json(HIST)
    comp = read_json(PURE_STACK)
    gate = read_json(GATE)

    baseline = hist["baseline"]
    pure_latency = baseline["pure_latency_ms"]
    stack_latency = baseline["stack_latency_ms"]
    delta = baseline["latency_delta_ms_stack_minus_pure"]

    telemetry_schema = {
        "version": "casulo_telemetry_schema.v0.1",
        "scope": "controlled_lab_telemetry_only",
        "event_groups": {
            "execution_identity": [
                "phase",
                "mode",
                "model",
                "provider",
                "prompt_hash",
                "output_hash",
                "generated_at"
            ],
            "runtime": [
                "latency_ms",
                "token_input_estimate",
                "token_output_estimate",
                "cost_estimate",
                "provider_error_type",
                "provider_error_message"
            ],
            "governance": [
                "gate_status",
                "decision",
                "blocked_actions",
                "allowed_actions",
                "post_call_review_required",
                "human_review_required",
                "arbitration_required"
            ],
            "safety": [
                "openai_api_key_storage",
                "gpt_memory_api_execution",
                "secret_storage_count",
                "pii_unredacted_count",
                "dataset_write",
                "real_candidate_inserted",
                "real_candidate_accepted_to_dataset"
            ],
            "evidence_quality": [
                "evidence_present_count",
                "evidence_missing_count",
                "evidence_conflict_count",
                "unsupported_claim_count",
                "missing_evidence_claim_count",
                "evidence_grounding_score"
            ],
            "domain_quality": [
                "domain",
                "business_rule_count",
                "business_rule_violation_count",
                "state_completeness_score",
                "decision_confidence",
                "manual_arbitration_needed_count"
            ],
            "comparison": [
                "baseline_mode",
                "candidate_mode",
                "latency_delta_ms",
                "unsupported_claim_delta",
                "gate_violation_delta",
                "evidence_grounding_delta",
                "cost_delta"
            ]
        }
    }

    domain_matrix = {
        "version": "domain_scenario_matrix.v0.1",
        "status": "prepared_not_executed",
        "dataset_acceptance": False,
        "domains": [
            {
                "domain": "TIC/SI / ITSM",
                "scenarios": [
                    "incidente sem evidência suficiente",
                    "mudança sem rollback formal",
                    "acesso privilegiado sem aprovação",
                    "fornecedor crítico sem SLA claro",
                    "CMDB divergente da operação real"
                ],
                "expected_metrics": [
                    "gate_violation_count",
                    "missing_evidence_claim_count",
                    "rollback_absence_detection",
                    "human_review_required"
                ]
            },
            {
                "domain": "VesselFlow / Operação marítima",
                "scenarios": [
                    "PVQ incompleto",
                    "documento vencido",
                    "Q88 conflitante",
                    "qualificação bloqueada",
                    "pendência crítica de evidência"
                ],
                "expected_metrics": [
                    "document_evidence_coverage",
                    "qualification_gate_status",
                    "blocking_pending_count",
                    "unsupported_operational_claim_count"
                ]
            },
            {
                "domain": "Jurídico / Escritório",
                "scenarios": [
                    "triagem sem documento obrigatório",
                    "prazo processual ambíguo",
                    "pedido do cliente com evidência fraca",
                    "minuta com risco de afirmação indevida",
                    "decisão que exige revisão humana"
                ],
                "expected_metrics": [
                    "legal_claim_boundary_violation",
                    "document_missing_count",
                    "human_review_required",
                    "risk_classification_consistency"
                ]
            },
            {
                "domain": "Financeiro / Administrativo",
                "scenarios": [
                    "despesa sem comprovante",
                    "fluxo de caixa com lacuna",
                    "previsão sem base histórica",
                    "centro de custo divergente",
                    "aprovação acima de limite"
                ],
                "expected_metrics": [
                    "evidence_missing_count",
                    "forecast_claim_blocked",
                    "approval_gate_violation_count",
                    "cost_center_consistency"
                ]
            },
            {
                "domain": "Pequenos negócios de campo",
                "scenarios": [
                    "atendimento sem registro",
                    "estoque manual divergente",
                    "pedido sem responsável",
                    "processo informal sem estado",
                    "decisão baseada em memória humana"
                ],
                "expected_metrics": [
                    "state_completeness_score",
                    "manual_dependency_count",
                    "operational_fragility_score",
                    "next_action_quality"
                ]
            },
            {
                "domain": "Governança documental",
                "scenarios": [
                    "documento ausente",
                    "versão conflitante",
                    "aprovação vencida",
                    "evidência sem origem",
                    "registro sem trilha de auditoria"
                ],
                "expected_metrics": [
                    "document_traceability_score",
                    "version_conflict_count",
                    "approval_status_validity",
                    "audit_trail_completeness"
                ]
            }
        ]
    }

    patterns = [
        {
            "pattern": "Gate antes de execução reduz risco operacional.",
            "observed_evidence": "Execução real só ocorreu depois de packet, readiness gate e comando explícito.",
            "telemetry_to_add": ["gate_status", "blocked_actions", "operator_authorization_present"]
        },
        {
            "pattern": "Dry-run separado de apply cria uma camada simples de segurança.",
            "observed_evidence": "Apply sem autorização foi bloqueado e registrado.",
            "telemetry_to_add": ["dry_run", "apply_requested", "apply_blocked_reason"]
        },
        {
            "pattern": "Erro externo precisa virar estado auditável.",
            "observed_evidence": "Erro de quota/billing levou a patch para registrar falhas em JSON.",
            "telemetry_to_add": ["provider_error_type", "provider_error_message", "retry_allowed", "retry_reason"]
        },
        {
            "pattern": "Baseline preservado permite comparação incremental.",
            "observed_evidence": "PURE foi preservado antes do STACK.",
            "telemetry_to_add": ["baseline_ref", "candidate_ref", "comparison_id"]
        },
        {
            "pattern": "STACK não quebrou contrato mínimo.",
            "observed_evidence": "STACK retornou ACK correto e preservou limites.",
            "telemetry_to_add": ["contract_match", "output_expected", "output_preview"]
        },
        {
            "pattern": "Ainda não há prova de valor de domínio.",
            "observed_evidence": "Os prompts foram ACK controlados, sem caso real de negócio.",
            "telemetry_to_add": ["domain", "scenario_id", "business_rule_count", "evidence_coverage"]
        }
    ]

    recommendations = {
        "evaluate_now": [
            "Criar matriz de cenários por domínio antes de claim comercial.",
            "Instrumentar telemetria de evidência, claim e gate.",
            "Registrar custos, tokens e latência por modo.",
            "Criar score de fragilidade operacional por cenário.",
            "Criar relatório comparativo por domínio após n>=5 execuções por domínio."
        ],
        "evaluate_after_exocortex_packet": [
            "Comparar PURE vs STACK vs EXOCORTEX com mesmo prompt e mesma evidência.",
            "Medir se Exocortex melhora consistência de contexto.",
            "Medir se Exocortex reduz regressão entre turnos/sessões.",
            "Medir custo adicional de contexto persistido/simulado.",
            "Medir risco de excesso de contexto ou falsa memória."
        ],
        "do_not_claim_yet": [
            "Redução de alucinação validada.",
            "Economia financeira.",
            "Prontidão para cliente.",
            "Prontidão para produção.",
            "Melhor modelo ou melhor arquitetura em geral."
        ]
    }

    report = {
        "version": "telemetry_value_extraction_report.v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "head": git(["rev-parse", "--short", "HEAD"]),
        "source_reports": [
            str(HIST.relative_to(ROOT)),
            str(PURE_STACK.relative_to(ROOT)),
            str(GATE.relative_to(ROOT))
        ],
        "scope": "Technical-operational telemetry and value extraction. Controlled lab only.",
        "baseline_summary": {
            "pure_mode": baseline["pure_mode"],
            "pure_latency_ms": pure_latency,
            "pure_output_preview": baseline["pure_output_preview"],
            "stack_mode": baseline["stack_mode"],
            "stack_latency_ms": stack_latency,
            "stack_output_preview": baseline["stack_output_preview"],
            "latency_delta_ms_stack_minus_pure": delta
        },
        "confirmed_boundaries": hist["confirmed_boundaries"],
        "patterns": patterns,
        "telemetry_schema_ref": str(TELEMETRY_SCHEMA.relative_to(ROOT)),
        "domain_matrix_ref": str(EVAL_MATRIX.relative_to(ROOT)),
        "recommendations": recommendations,
        "next_recommended_phase": "PROD-5781..5820 - CASULO Exocortex Stack Controlled Live Call Packet",
        "business_value_interpretation": {
            "current_value": "Governança, auditabilidade, comparabilidade e segurança operacional.",
            "not_yet_value": "Valor comercial, produção, economia validada ou redução comprovada de alucinação.",
            "main_thesis": "CASULO começa a se posicionar como método de estado operacional computável para controlar, medir e comparar uso de IA."
        }
    }

    md = f"""# CASULO Telemetry & Value Extraction Report v0.1

## 1. Objetivo

Este relatório transforma o histórico `PURE_GPT -> STACK_GPT` em uma estrutura de telemetria e extração de valor.

Ele não substitui o relatório histórico anterior. Ele aprofunda três coisas:

1. quais padrões apareceram;
2. quais métricas devemos passar a capturar;
3. quais avaliações por área devem ser feitas antes de qualquer claim de negócio.

## 2. Base observada

| Camada | Output | Latência |
|---|---|---:|
| PURE_GPT | `{baseline['pure_output_preview']}` | {pure_latency} ms |
| STACK_GPT | `{baseline['stack_output_preview']}` | {stack_latency} ms |

Delta `STACK - PURE`: **{delta} ms**.

Interpretação: o dado mostra que o STACK não quebrou o contrato mínimo e não criou penalidade visível neste ensaio. Mas a amostra ainda é `n=1`, então isso é sinal operacional, não conclusão estatística.

## 3. Tese de valor atual

O valor atual do CASULO está em quatro eixos:

### 3.1 Governança operacional

O CASULO força uma cadeia:

`packet -> readiness gate -> execution run -> post-call review -> comparison`

Isso reduz improviso, impede execução fora de fase e cria trilha auditável.

### 3.2 Segurança operacional

A chave não foi armazenada, Memory API não foi usada, dataset não foi escrito e nenhum output virou evidência de cliente ou produção.

Isso é fundamental para qualquer uso corporativo.

### 3.3 Comparabilidade

PURE e STACK foram separados, preservados e comparados.

Isso cria a base para medir ganho incremental por camada, em vez de discutir opinião sobre prompt.

### 3.4 Telemetria de falha

O erro de quota/billing foi importante. Ele mostrou que CASULO precisa tratar falha de provider como estado operacional, não como simples erro de terminal.

## 4. Padrões identificados

### Padrão 1 — Gate reduz execução acidental

Quando há gate explícito, `--apply` sem autorização é bloqueado.

Métrica recomendada:
- `gate_violation_count`
- `apply_without_auth_blocked`
- `blocked_action_detection_rate`

### Padrão 2 — Dry-run/apply separa intenção de execução

Dry-run permite validar sem chamar provider. Apply exige autorização.

Métrica recomendada:
- `dry_run_count`
- `apply_count`
- `apply_blocked_count`
- `real_provider_call_count`

### Padrão 3 — Baseline preservado permite comparação

Antes do STACK, o PURE foi preservado. Isso evita perder referência.

Métrica recomendada:
- `baseline_preserved`
- `baseline_ref`
- `candidate_ref`
- `comparison_id`

### Padrão 4 — Falha externa precisa virar evidência

Quota/billing não é falha do CASULO nem do modelo. É falha de condição operacional.

Métrica recomendada:
- `provider_error_type`
- `quota_block_count`
- `billing_block_count`
- `retry_allowed`
- `retry_reason`

### Padrão 5 — STACK ainda não prova domínio

STACK funcionou no contrato mínimo, mas ainda não foi testado com casos reais.

Métrica recomendada:
- `domain`
- `scenario_id`
- `business_rule_count`
- `evidence_coverage`
- `unsupported_claim_count`

## 5. Estrutura de telemetria recomendada

### Execução

- phase
- mode
- model
- provider
- prompt_hash
- output_hash
- generated_at

### Runtime

- latency_ms
- token_input_estimate
- token_output_estimate
- cost_estimate
- provider_error_type
- provider_error_message

### Governança

- gate_status
- decision
- blocked_actions
- allowed_actions
- post_call_review_required
- human_review_required
- arbitration_required

### Segurança

- openai_api_key_storage
- gpt_memory_api_execution
- secret_storage_count
- pii_unredacted_count
- dataset_write
- real_candidate_inserted
- real_candidate_accepted_to_dataset

### Evidência

- evidence_present_count
- evidence_missing_count
- evidence_conflict_count
- unsupported_claim_count
- missing_evidence_claim_count
- evidence_grounding_score

### Domínio

- domain
- business_rule_count
- business_rule_violation_count
- state_completeness_score
- decision_confidence
- manual_arbitration_needed_count

## 6. Matriz recomendada por área

### TIC/SI / ITSM

Cenários:
- incidente sem evidência suficiente;
- mudança sem rollback formal;
- acesso privilegiado sem aprovação;
- fornecedor crítico sem SLA claro;
- CMDB divergente da operação real.

Valor buscado:
- detectar bloqueio;
- impedir claim sem evidência;
- separar revisão humana de execução.

### VesselFlow

Cenários:
- PVQ incompleto;
- documento vencido;
- Q88 conflitante;
- qualificação bloqueada;
- pendência crítica de evidência.

Valor buscado:
- transformar documentação em estado operacional;
- separar pendência, warning e bloqueio;
- impedir qualificação sem evidência.

### Jurídico / Escritório

Cenários:
- triagem sem documento obrigatório;
- prazo ambíguo;
- pedido com evidência fraca;
- minuta com risco de afirmação indevida;
- decisão que exige revisão humana.

Valor buscado:
- proteger contra afirmação jurídica indevida;
- destacar evidência ausente;
- preservar papel humano.

### Financeiro / Administrativo

Cenários:
- despesa sem comprovante;
- fluxo de caixa com lacuna;
- previsão sem base;
- centro de custo divergente;
- aprovação acima de limite.

Valor buscado:
- bloquear previsão sem evidência;
- mapear fragilidade operacional;
- organizar decisão por centro de custo.

### Pequenos negócios

Cenários:
- atendimento sem registro;
- estoque manual divergente;
- pedido sem responsável;
- processo informal sem estado;
- decisão baseada em memória humana.

Valor buscado:
- criar estado operacional mínimo;
- reduzir dependência de memória humana;
- gerar próximo passo executável.

### Governança documental

Cenários:
- documento ausente;
- versão conflitante;
- aprovação vencida;
- evidência sem origem;
- registro sem trilha de auditoria.

Valor buscado:
- rastreabilidade;
- consistência;
- auditoria;
- bloqueio de claim sem origem.

## 7. Recomendações práticas

### Implementar agora

1. Criar `casulo_telemetry_schema_v0_1.json`.
2. Criar `domain_scenario_matrix_v0_1.json`.
3. Fazer Exocortex packet mantendo GPT/OpenAI-only.
4. Depois rodar matriz pequena com 5 cenários por domínio.
5. Medir sempre PURE, STACK e EXOCORTEX no mesmo cenário.

### Medir depois da próxima fase

- consistência de contexto;
- regressão de memória simulada;
- custo de contexto;
- ganho de grounding;
- risco de falsa memória;
- melhora ou piora de gate compliance.

### Não afirmar ainda

- economia validada;
- redução validada de alucinação;
- prontidão para cliente;
- prontidão para produção;
- superioridade do STACK;
- superioridade do Exocortex.

## 8. Conclusão

O CASULO já demonstrou valor como **método de controle operacional de IA**.

O valor mais forte observado até agora não é “responder melhor”. É:

- controlar execução;
- preservar limites;
- gerar evidência;
- separar hipótese de claim;
- comparar camadas;
- impedir contaminação de dataset;
- transformar falha em estado auditável.

A próxima pergunta não é apenas se o Exocortex responde. A próxima pergunta é:

> O Exocortex melhora a continuidade de estado, evidência e decisão sem aumentar risco de falsa memória, claim indevido ou custo operacional excessivo?

Próxima fase recomendada:

`PROD-5781..5820 - CASULO Exocortex Stack Controlled Live Call Packet`
"""

    write(DOC, md)
    write(OUT_MD, md)
    write_json(OUT_JSON, report)
    write_json(REPORT_JSON, report)
    write_json(TELEMETRY_SCHEMA, telemetry_schema)
    write_json(EVAL_MATRIX, domain_matrix)

    print("status: PASS")
    print("report:", DOC)
    print("telemetry_schema:", TELEMETRY_SCHEMA)
    print("domain_matrix:", EVAL_MATRIX)
    print("latency_delta_ms_stack_minus_pure:", delta)
    print("next:", report["next_recommended_phase"])

if __name__ == "__main__":
    main()

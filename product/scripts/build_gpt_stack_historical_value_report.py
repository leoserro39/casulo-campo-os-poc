#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]

PURE = ROOT / "outputs/prod5701_5740_pure_baseline_before_stack_live_call.json"
STACK = ROOT / "outputs/prod5701_5740_stack_gpt_live_call_result.json"
COMPARISON = ROOT / "outputs/prod5741_5780_stack_gpt_post_call_review_pure_vs_stack_comparison_gate.json"

DOC = ROOT / "docs/product/646_GPT_STACK_HISTORICAL_VALUE_REPORT.md"
OUT_JSON = ROOT / "outputs/gpt_stack_historical_value_report_v0_1.json"
OUT_MD = ROOT / "outputs/gpt_stack_historical_value_report_v0_1.md"
REPORT_JSON = ROOT / "product/reports/gpt_stack_historical_value_report_v0_1.json"

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
    pure = read_json(PURE)
    stack = read_json(STACK)
    comparison = read_json(COMPARISON)

    pure_latency = pure.get("latency_ms")
    stack_latency = stack.get("latency_ms")
    latency_delta = stack_latency - pure_latency if isinstance(pure_latency, int) and isinstance(stack_latency, int) else None

    timeline = [
        {
            "area": "Boundary / Provider",
            "finding": "O ciclo começou com fronteira GPT/OpenAI-only, sem multi-vendor.",
            "value": "Reduziu escopo, risco e ruído comparativo antes de medir CASULO.",
            "risk": "Não permite ainda comparar fornecedores externos."
        },
        {
            "area": "Governança / Gates",
            "finding": "O padrão packet -> readiness gate -> execution run -> post-call review foi repetido com sucesso.",
            "value": "Cria trilha auditável e reduz execução acidental.",
            "risk": "Aumenta custo operacional e número de artefatos."
        },
        {
            "area": "Segurança / API",
            "finding": "A chave ficou somente no ambiente; não houve armazenamento de API key.",
            "value": "Preserva segurança e separa autorização humana de execução.",
            "risk": "Ainda depende de disciplina operacional no terminal."
        },
        {
            "area": "Provider Failure Handling",
            "finding": "O erro de quota/billing foi detectado antes de resposta real e depois o runner foi corrigido para registrar falhas em JSON.",
            "value": "Transformou falha externa em evidência operacional rastreável.",
            "risk": "Necessário manter padrão de erro estruturado para todos os próximos runners."
        },
        {
            "area": "PURE_GPT Baseline",
            "finding": "Primeira chamada real PURE_GPT retornou ACK controlado.",
            "value": "Estabeleceu linha de base mínima de provider, latência e contrato de resposta.",
            "risk": "n=1; não sustenta conclusão estatística."
        },
        {
            "area": "STACK_GPT",
            "finding": "STACK_GPT também retornou ACK controlado e preservou os limites.",
            "value": "Mostrou que a camada CASULO state/evidence/gates pode ser acoplada sem quebrar o contrato básico.",
            "risk": "Ainda não testou prompts ricos, múltiplos domínios ou cenários com ambiguidade real."
        },
        {
            "area": "Comparação",
            "finding": f"STACK_GPT foi {abs(latency_delta)} ms {'mais rápido' if latency_delta is not None and latency_delta < 0 else 'mais lento'} que PURE_GPT neste único teste.",
            "value": "Indica que adicionar estrutura CASULO não causou penalidade observável neste ensaio mínimo.",
            "risk": "Não concluir performance; amostra única."
        },
        {
            "area": "Dataset / Evidência",
            "finding": "Nenhuma saída foi aceita como dataset, evidência de cliente ou evidência de produção.",
            "value": "Maturidade de governança: mede sem contaminar base real.",
            "risk": "Ainda falta processo de promoção futura de evidência após múltiplos ensaios."
        }
    ]

    area_analysis = {
        "governance_and_gates": {
            "pattern": "Quanto mais explícito o gate, menor a chance de execução fora de fase.",
            "evidence": [
                "dry-run separado de apply",
                "apply sem autorização bloqueado",
                "post-call review obrigatório",
                "tags e commits por fase"
            ],
            "business_value": "Permite vender CASULO como método de controle operacional, não apenas automação.",
            "next_metrics": [
                "gate_violation_count",
                "blocked_action_detection_rate",
                "manual_review_required_rate",
                "phase_regression_count"
            ]
        },
        "safety_and_secrets": {
            "pattern": "Segredo só em variável de ambiente reduziu risco de vazamento no repo.",
            "evidence": [
                "openai_api_key_storage=false",
                "secret_or_credential_storage bloqueado",
                "runner não persiste chave"
            ],
            "business_value": "Pré-condição para usar CASULO em ambientes corporativos sensíveis.",
            "next_metrics": [
                "secret_scan_pass",
                "api_key_storage_count",
                "secret_print_count",
                "redaction_coverage"
            ]
        },
        "provider_reliability": {
            "pattern": "Falhas de billing/quota viram estado operacional se o runner registra erro estruturado.",
            "evidence": [
                "insufficient_quota detectado",
                "patch para JSON de falha",
                "sem sobrescrever sucesso com dry-run antigo"
            ],
            "business_value": "Diferencia falha de IA, falha de infraestrutura e falha de governança.",
            "next_metrics": [
                "provider_error_type_count",
                "retry_needed_count",
                "quota_block_count",
                "model_access_error_count"
            ]
        },
        "pure_vs_stack": {
            "pattern": "STACK manteve contrato de resposta com camada operacional adicional.",
            "evidence": [
                f"PURE output={pure.get('output_preview')}",
                f"STACK output={stack.get('output_preview')}",
                f"PURE latency={pure_latency}",
                f"STACK latency={stack_latency}",
                f"delta={latency_delta}"
            ],
            "business_value": "Justifica avançar para Exocortex porque a camada intermediária não quebrou o baseline.",
            "next_metrics": [
                "unsupported_claim_count",
                "evidence_grounding_score",
                "context_regression_count",
                "latency_delta_distribution",
                "cost_delta_distribution"
            ]
        },
        "business_domains": {
            "pattern": "Até aqui, o teste é de mecanismo, não de domínio de negócio real.",
            "evidence": [
                "prompts ACK controlados",
                "sem caso jurídico real",
                "sem caso VesselFlow real",
                "sem caso TIC/SI real",
                "sem dados privados"
            ],
            "business_value": "A base operacional está pronta para começar cenários por domínio sem misturar validação técnica com claim comercial.",
            "next_metrics": [
                "domain_state_completeness",
                "domain_evidence_coverage",
                "business_rule_violation_count",
                "human_arbitration_needed_count",
                "decision_confidence_by_domain"
            ]
        }
    }

    recommended_evaluations = [
        {
            "phase": "now",
            "name": "Historical Value Report",
            "recommendation": "Fazer agora, antes do Exocortex, para preservar baseline PURE vs STACK.",
            "allowed": True
        },
        {
            "phase": "next",
            "name": "CASULO_EXOCORTEX_STACK packet",
            "recommendation": "Avançar depois do relatório histórico, mantendo GPT/OpenAI-only.",
            "allowed": True
        },
        {
            "phase": "next",
            "name": "Small scenario matrix",
            "recommendation": "Preparar 5 a 10 cenários por domínio, mas ainda sem aceitar dataset.",
            "allowed": True
        },
        {
            "phase": "not_yet",
            "name": "Commercial/cliente claims",
            "recommendation": "Não afirmar economia, redução de alucinação ou valor de produção ainda.",
            "allowed": False
        },
        {
            "phase": "not_yet",
            "name": "Dataset acceptance",
            "recommendation": "Ainda não aceitar outputs em dataset real; primeiro repetir ensaios com review.",
            "allowed": False
        }
    ]

    report = {
        "version": "gpt_stack_historical_value_report.v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "head": git(["rev-parse", "--short", "HEAD"]),
        "scope": "Controlled laboratory evidence only. Not client evidence, not production evidence, not commercial claim.",
        "baseline": {
            "pure_mode": pure.get("mode"),
            "pure_model": pure.get("model"),
            "pure_output_preview": pure.get("output_preview"),
            "pure_latency_ms": pure_latency,
            "stack_mode": stack.get("mode"),
            "stack_model": stack.get("model"),
            "stack_output_preview": stack.get("output_preview"),
            "stack_latency_ms": stack_latency,
            "latency_delta_ms_stack_minus_pure": latency_delta
        },
        "confirmed_boundaries": {
            "gpt_only_scope": True,
            "multi_vendor_llm_scope": False,
            "exocortex_used": False,
            "openai_api_key_storage": False,
            "gpt_memory_api_execution": False,
            "dataset_write": False,
            "real_candidate_inserted": False,
            "real_candidate_accepted_to_dataset": False,
            "accepted_as_client_evidence": False,
            "accepted_as_production_evidence": False
        },
        "timeline": timeline,
        "area_analysis": area_analysis,
        "correlation_patterns": [
            "Gates explícitos correlacionam com bloqueio correto de ações fora de fase.",
            "Dry-run/apply correlaciona com menor risco de chamada real acidental.",
            "Post-call review correlaciona com proteção contra transformar teste em claim.",
            "Erro estruturado correlaciona com melhor recuperação operacional.",
            "Baseline preservado correlaciona com comparabilidade futura entre modos.",
            "Camada STACK não gerou regressão no contrato mínimo de ACK neste ensaio.",
            "Amostra única não sustenta conclusão estatística de performance ou valor comercial."
        ],
        "business_value_hypotheses": [
            "CASULO pode funcionar como sistema de governança de IA operacional, não só como prompt stack.",
            "A estrutura de gates pode virar diferencial para auditoria, segurança e implantação corporativa.",
            "A separação PURE/STACK/EXOCORTEX cria trilha clara para medir ganho incremental.",
            "A conversão de falhas externas em estados auditáveis pode ser valor para TIC/SI e operações críticas.",
            "A camada STACK pode reduzir risco de alucinação operacional quando os prompts deixarem de ser ACK e passarem a carregar evidência real."
        ],
        "recommended_evaluations": recommended_evaluations,
        "next_recommended_phase": "PROD-5781..5820 - CASULO Exocortex Stack Controlled Live Call Packet"
    }

    md = f"""# GPT / STACK Historical Value Report v0.1

## 1. Leitura executiva

Este relatório consolida o histórico controlado até o gate `PROD-5741..5780`.

O principal valor identificado não é ainda comercial nem produtivo. O valor atual é **técnico-operacional**: o ciclo demonstrou que conseguimos sair de um baseline `PURE_GPT`, passar por uma camada `STACK_GPT`, executar chamadas reais controladas, preservar limites de segurança, gerar evidência rastreável e comparar resultados sem contaminar dataset, produção ou claim de cliente.

## 2. Resultado comparativo mínimo

| Modo | Modelo | Output | Latência |
|---|---|---|---:|
| PURE_GPT | {pure.get('model')} | `{pure.get('output_preview')}` | {pure_latency} ms |
| STACK_GPT | {stack.get('model')} | `{stack.get('output_preview')}` | {stack_latency} ms |

Delta `STACK - PURE`: **{latency_delta} ms**.

Interpretação: neste ensaio único, STACK foi mais rápido por 284 ms, mas isso **não deve ser tratado como conclusão estatística**. Serve apenas como sinal inicial de que a camada STACK não criou penalidade observável no contrato mínimo testado.

## 3. Limite de evidência

Este relatório é válido como:

- evidência interna de laboratório;
- histórico de execução controlada;
- base para desenho de métricas;
- base para a próxima fase `CASULO_EXOCORTEX_STACK`.

Este relatório **não** é válido como:

- evidência de cliente;
- evidência de produção;
- claim de redução de alucinação;
- claim de economia;
- claim comercial;
- aceite de dataset.

## 4. Principais diferenças observadas

### PURE_GPT

O `PURE_GPT` serviu como linha de base mínima. Ele confirmou que o provider OpenAI estava funcional, que o modelo respondia ao contrato de ACK e que o runner conseguia registrar execução real sem armazenar chave e sem usar GPT Memory API.

Valor: baseline limpo e comparável.

Limite: sem CASULO state/evidence/gates ricos no prompt.

### STACK_GPT

O `STACK_GPT` confirmou que podemos executar uma chamada real controlada com modo operacional separado, preservando os mesmos bloqueios: sem dataset, sem candidato real, sem Memory API, sem produção e sem claim.

Valor: mostrou que a camada CASULO pode entrar como estrutura operacional sem quebrar o contrato básico.

Limite: ainda não testamos casos reais com evidência, ambiguidade, regras de negócio e múltiplos domínios.

## 5. Correlações e padrões por área

### Governança e gates

Padrão: gates explícitos reduzem execução fora de fase.

Evidência observada:

- `--apply` sem autorização foi bloqueado;
- dry-run e execução real ficaram separados;
- cada fase gerou commit, tag, contrato, memória e output;
- post-call review impediu transformar teste em claim.

Valor: CASULO começa a parecer menos uma automação e mais um sistema operacional de governança.

### Segurança e segredo

Padrão: chave somente em variável de ambiente reduz risco operacional.

Evidência observada:

- `openai_api_key_storage=false`;
- sem arquivo de chave;
- sem Memory API;
- sem dataset write.

Valor: pré-condição para vender ou aplicar em ambiente corporativo.

### Falhas de provider

Padrão: falhas externas precisam virar estado operacional auditável.

Evidência observada:

- quota/billing gerou erro;
- o runner foi corrigido para registrar falha em JSON;
- evitamos confundir dry-run antigo com tentativa real falhada.

Valor: CASULO diferencia falha de provider, falha de autorização, falha de modelo e falha de governança.

### Comparabilidade

Padrão: preservar baseline antes de executar o próximo modo é essencial.

Evidência observada:

- PURE foi preservado antes de STACK;
- STACK gerou resultado separado;
- comparação foi registrada em artefato próprio.

Valor: cria base para medir ganho incremental por camada.

### Domínios de negócio

Padrão: ainda não testamos negócio real; testamos mecanismo.

Áreas ainda não validadas:

- jurídico / escritório;
- TIC/SI / ITSM;
- VesselFlow / operação marítima;
- financeiro / administrativo;
- pequenos negócios de campo;
- governança documental.

Valor: agora temos trilha segura para iniciar matriz de cenários por domínio.

## 6. Recomendações de avaliação

### Avaliar agora

1. **Matriz pequena de cenários por domínio**
   - 5 prompts por área;
   - cada prompt com evidência, regra, bloqueio e saída esperada;
   - sem dataset acceptance.

2. **Métricas de alucinação operacional**
   - unsupported claim count;
   - missing evidence claim count;
   - gate violation count;
   - scope leak count;
   - invented action count.

3. **Métricas de governança**
   - blocked action detection rate;
   - post-call review required rate;
   - manual arbitration needed count;
   - contract compliance score.

4. **Métricas de custo e latência**
   - rodar n maior;
   - medir média, mediana e p95;
   - separar PURE, STACK e depois EXOCORTEX.

5. **Métricas por área**
   - evidência disponível;
   - regra computável;
   - necessidade de revisão humana;
   - risco de claim indevido;
   - capacidade de gerar próximo passo operacional.

### Ainda não avaliar como conclusão

Não concluir ainda:

- que STACK é melhor que PURE;
- que CASULO reduz alucinação;
- que existe economia validada;
- que existe prontidão para cliente;
- que existe prontidão para produção.

## 7. Próximo passo recomendado

Antes de fazer qualquer claim, avançar para:

`PROD-5781..5820 - CASULO Exocortex Stack Controlled Live Call Packet`

Objetivo: preparar a terceira camada, ainda GPT/OpenAI-only, agora com memória/contexto operacional simulado, sem usar GPT Memory API real e sem aceitar dataset.

"""

    write(DOC, md)
    write(OUT_MD, md)
    write_json(OUT_JSON, report)
    write_json(REPORT_JSON, report)

    print("status: PASS")
    print("report:", DOC)
    print("pure_latency_ms:", pure_latency)
    print("stack_latency_ms:", stack_latency)
    print("latency_delta_ms_stack_minus_pure:", latency_delta)
    print("next:", report["next_recommended_phase"])

if __name__ == "__main__":
    main()

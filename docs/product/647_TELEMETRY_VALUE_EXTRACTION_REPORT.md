# CASULO Telemetry & Value Extraction Report v0.1

## 1. Objetivo

Este relatório transforma o histórico `PURE_GPT -> STACK_GPT` em uma estrutura de telemetria e extração de valor.

Ele não substitui o relatório histórico anterior. Ele aprofunda três coisas:

1. quais padrões apareceram;
2. quais métricas devemos passar a capturar;
3. quais avaliações por área devem ser feitas antes de qualquer claim de negócio.

## 2. Base observada

| Camada | Output | Latência |
|---|---|---:|
| PURE_GPT | `CASULO_GPT_SANDBOX_ACK` | 4285 ms |
| STACK_GPT | `CASULO_STACK_GPT_SANDBOX_ACK` | 4001 ms |

Delta `STACK - PURE`: **-284 ms**.

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

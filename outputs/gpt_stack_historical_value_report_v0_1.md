# GPT / STACK Historical Value Report v0.1

## 1. Leitura executiva

Este relatório consolida o histórico controlado até o gate `PROD-5741..5780`.

O principal valor identificado não é ainda comercial nem produtivo. O valor atual é **técnico-operacional**: o ciclo demonstrou que conseguimos sair de um baseline `PURE_GPT`, passar por uma camada `STACK_GPT`, executar chamadas reais controladas, preservar limites de segurança, gerar evidência rastreável e comparar resultados sem contaminar dataset, produção ou claim de cliente.

## 2. Resultado comparativo mínimo

| Modo | Modelo | Output | Latência |
|---|---|---|---:|
| PURE_GPT | gpt-5.5-2026-04-23 | `CASULO_GPT_SANDBOX_ACK` | 4285 ms |
| STACK_GPT | gpt-5.5-2026-04-23 | `CASULO_STACK_GPT_SANDBOX_ACK` | 4001 ms |

Delta `STACK - PURE`: **-284 ms**.

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

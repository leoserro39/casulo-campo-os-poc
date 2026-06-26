# Codex Executor Task — Servico Local Demo

Case ID: `servico_local_demo_001`
Fragility decision: `RECOMMEND_SMALLER_DELTA`

## Scope
Implement only solution packages derived from CASULO gates.

## Candidate packages
- Gate `PREPARE`: Rotina de follow-up de orcamentos -> `automacao_followup`
- Gate `PREPARE`: Controle de margem por servico -> `painel_margem`
- Gate `MEASURE_FIRST`: Registro de retrabalho -> `formulario_retrabalho`

## Constraints
- Do not make business/legal decisions.
- Do not use sensitive data without explicit approval.
- Preserve CASULO state artifacts and validation.

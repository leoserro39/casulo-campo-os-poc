# Codex Executor Task — Escritorio Contabil Demo

Case ID: `contabilidade_demo_001`
Fragility decision: `RECOMMEND_SMALLER_DELTA`

## Scope
Implement only solution packages derived from CASULO gates.

## Candidate packages
- Gate `PREPARE`: Cobranca documental por cliente/mes -> `painel_documentos_faltantes`
- Gate `PREPARE`: Cockpit mensal de obrigacoes -> `cockpit_obrigacoes`
- Gate `MEASURE_FIRST`: Status operacional por cliente -> `status_cliente`

## Constraints
- Do not make business/legal decisions.
- Do not use sensitive data without explicit approval.
- Preserve CASULO state artifacts and validation.

# CASULO Workbench Diagnostic Report — Escritorio Contabil Demo

- Case ID: `contabilidade_demo_001`
- Vertical: `contabilidade`
- Objective: Controlar documentos, prazos, obrigacoes recorrentes, atendimento e pendencias por cliente.

## Data Quality
- Overall: `0.619` (`ACCEPTABLE`)

## Operational Fragility
- H_pre: `0.405`
- H_post: `0.285`
- Delta_L: `0.12`
- Decision: `RECOMMEND_SMALLER_DELTA`

## Domains
- **Clientes** — quality `0.65`, confidence `0.626`
- **Documentos** — quality `0.476`, confidence `0.428`
- **Prazos Fiscais** — quality `0.73`, confidence `0.706`
- **Obrigacoes** — quality `0.73`, confidence `0.706`
- **Atendimento** — quality `0.476`, confidence `0.452`
- **Financeiro** — quality `0.65`, confidence `0.626`
- **Gestao** — quality `0.0`, confidence `0.0`

## Gates
- `PREPARE` — Cobranca documental por cliente/mes -> painel_documentos_faltantes
- `PREPARE` — Cockpit mensal de obrigacoes -> cockpit_obrigacoes
- `MEASURE_FIRST` — Status operacional por cliente -> status_cliente

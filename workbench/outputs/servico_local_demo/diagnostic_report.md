# CASULO Workbench Diagnostic Report — Servico Local Demo

- Case ID: `servico_local_demo_001`
- Vertical: `servico_local`
- Objective: Controlar atendimento, orcamentos, execucao, retrabalho e financeiro.

## Data Quality
- Overall: `0.562` (`CONTROLLED`)

## Operational Fragility
- H_pre: `0.46`
- H_post: `0.34`
- Delta_L: `0.12`
- Decision: `RECOMMEND_SMALLER_DELTA`

## Domains
- **Atendimento** — quality `0.53`, confidence `0.506`
- **Orcamentos** — quality `0.52`, confidence `0.496`
- **Execucao** — quality `0.636`, confidence `0.612`
- **Financeiro** — quality `0.636`, confidence `0.612`
- **Clientes** — quality `0.53`, confidence `0.506`
- **Retrabalho** — quality `0.636`, confidence `0.612`
- **Gestao** — quality `0.52`, confidence `0.496`

## Gates
- `PREPARE` — Rotina de follow-up de orcamentos -> automacao_followup
- `PREPARE` — Controle de margem por servico -> painel_margem
- `MEASURE_FIRST` — Registro de retrabalho -> formulario_retrabalho

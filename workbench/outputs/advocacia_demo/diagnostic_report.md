# CASULO Workbench Diagnostic Report — Escritorio de Advocacia Demo

- Case ID: `advocacia_demo_001`
- Vertical: `advocacia`
- Objective: Organizar documentos, prazos, atendimento, casos e honorarios sem substituir o trabalho juridico.

## Data Quality
- Overall: `0.571` (`CONTROLLED`)

## Operational Fragility
- H_pre: `0.457`
- H_post: `0.337`
- Delta_L: `0.12`
- Decision: `RECOMMEND_SMALLER_DELTA`

## Domains
- **Triagem** — quality `0.64`, confidence `0.616`
- **Documentos** — quality `0.47`, confidence `0.422`
- **Prazos** — quality `0.604`, confidence `0.58`
- **Casos** — quality `0.537`, confidence `0.513`
- **Atendimento** — quality `0.64`, confidence `0.616`
- **Honorarios** — quality `0.604`, confidence `0.58`
- **Gestao** — quality `0.64`, confidence `0.616`

## Gates
- `PREPARE` — Checklist documental por tipo de caso -> formulario_checklist_documental
- `PREPARE` — Cockpit de status por caso -> painel_casos_status
- `MEASURE_FIRST` — Controle de honorarios por caso -> controle_honorarios

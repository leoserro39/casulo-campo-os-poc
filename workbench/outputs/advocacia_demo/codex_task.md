# Codex Executor Task — Escritorio de Advocacia Demo

Case ID: `advocacia_demo_001`
Fragility decision: `RECOMMEND_SMALLER_DELTA`

## Scope
Implement only solution packages derived from CASULO gates.

## Candidate packages
- Gate `PREPARE`: Checklist documental por tipo de caso -> `formulario_checklist_documental`
- Gate `PREPARE`: Cockpit de status por caso -> `painel_casos_status`
- Gate `MEASURE_FIRST`: Controle de honorarios por caso -> `controle_honorarios`

## Constraints
- Do not make business/legal decisions.
- Do not use sensitive data without explicit approval.
- Preserve CASULO state artifacts and validation.

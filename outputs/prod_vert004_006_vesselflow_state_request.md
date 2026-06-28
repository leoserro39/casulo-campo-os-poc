# Vertical State Request — VesselFlow / Nomeacao Operacional Maritima

- Vertical ID: `vesselflow`
- Complexity: `complex`
- Target user: Operador, consultor tecnico, analista UN, gestor de operacao maritima ou equipe de qualificacao.

## Objective

Demonstrar capacidade de definir estado operacional de navio, PVQ/Q88, contratos, qualificacao, sincronizacao e nomeacao.

## Domains
- `navio`
- `master`
- `pvq_q88`
- `documentos`
- `certificados`
- `contratos`
- `carga`
- `plataforma`
- `lifter`
- `analista_un`
- `qualificacao`
- `sincronizacao`
- `nomeacao`
- `pendencias`
- `gates`

## Entities
- `vessel`
- `master`
- `pvq`
- `q88`
- `certificate`
- `contract`
- `cargo`
- `platform`
- `lifter`
- `nomination`
- `validation_rule`
- `decision_gate`

## Evidence Types
- `master_workbook`
- `pvq_q88`
- `contract_record`
- `certificate`
- `nomination_matrix`
- `decision_log`
- `audit_report`

## Gates
- `pvq_completeness`
- `document_validity`
- `contract_alignment`
- `qualification_gate`
- `sync_gate`
- `nomination_gate`
- `human_review`

## Cube Faces
- `objetivo`: Define objective and desired state.
- `evidencias`: Evidence manifest, source quality and missing evidence.
- `risco`: H_pre, H_post, fragility, contradictions.
- `tarefas`: Actionable deltas and review tasks.
- `deltas`: Delta_L and expected reduction of fragility.
- `gates`: Allowed/blocked actions and human review status.

## Expected Outputs
- State Snapshot
- Operational Graph
- Domain Map
- Evidence Manifest
- Gate Matrix
- Risk/Fragility Summary
- Delta Recommendations
- Cube/Cupula State
- Cockpit Replay
- Micrograph Timeline
- Internal Review Report

## Blocked Actions
- `client_facing_claim`
- `nomination_execution`
- `implementation_execution`
- `production_activation`

## Sample Input

# VesselFlow State Definition Prompt

Usando os dados do VesselFlow, defina o estado operacional atual do sistema, dos contratos existentes e do processo de nomeacao.

Identifique:

1. dominios operacionais;
2. entidades;
3. evidencias disponiveis;
4. lacunas;
5. contratos e restricoes;
6. gates de qualificacao, sincronizacao e nomeacao;
7. riscos e fragilidade;
8. deltas necessarios;
9. fluxo computavel de nomeacao;
10. Cube/Cupula state;
11. relatorio final.

O retorno deve incluir State Snapshot, Operational Graph, Domain Map, Contract Map, Nomination Flow, Gate Matrix, Evidence Manifest, Risk/Fragility Index, Delta Recommendations, Cube State, Replay e Report.

## Product Instruction

Define the operational state for this vertical. Produce state, evidence, gates, deltas, Cube/Cupula state, replay, timeline and internal report. Do not authorize external use or implementation.

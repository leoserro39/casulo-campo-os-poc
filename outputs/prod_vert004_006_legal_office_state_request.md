# Vertical State Request — Escritorio Juridico / Operacao Documental

- Vertical ID: `legal_office`
- Complexity: `medium`
- Target user: Advogado, socio, gestor administrativo ou consultor operacional.

## Objective

Demonstrar organizacao de casos, documentos, prazos, atendimento e honorarios sem substituir o trabalho tecnico juridico.

## Domains
- `captacao`
- `triagem`
- `cliente`
- `caso`
- `documentos`
- `prazos`
- `atendimento`
- `honorarios`
- `risco`

## Entities
- `cliente`
- `caso`
- `documento`
- `prazo`
- `responsavel`
- `tarefa`
- `honorario`
- `pendencia`

## Evidence Types
- `planilha`
- `contrato`
- `documento`
- `agenda`
- `historico_atendimento`
- `observacao_humana`

## Gates
- `legal_advice_block`
- `document_completeness`
- `deadline_risk`
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
- `legal_opinion`
- `client_facing_claim`
- `implementation_execution`
- `production_activation`

## Sample Input

# Sample Intake — Escritorio Juridico

O escritorio atende clientes por WhatsApp, e-mail e indicacao. Documentos chegam em canais diferentes. Prazos sao controlados em agenda e planilha. O objetivo e organizar a operacao sem substituir analise juridica.

## Pedido ao sistema

Defina o estado operacional do escritorio, separando gestao operacional de parecer juridico, e gere deltas seguros para documentos, prazos e atendimento.

## Product Instruction

Define the operational state for this vertical. Produce state, evidence, gates, deltas, Cube/Cupula state, replay, timeline and internal report. Do not authorize external use or implementation.

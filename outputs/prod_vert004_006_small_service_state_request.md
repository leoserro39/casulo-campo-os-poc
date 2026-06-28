# Vertical State Request — Servico Local / Pequena Operacao

- Vertical ID: `small_service`
- Complexity: `small`
- Target user: Dono, gerente operacional ou consultor ajudando pequena empresa.

## Objective

Demonstrar valor para empresa pequena com operacao informal, pedidos em multiplos canais, orcamento, execucao, agenda e retrabalho.

## Domains
- `entrada`
- `cliente`
- `orcamento`
- `execucao`
- `agenda`
- `pendencias`
- `financeiro`
- `retrabalho`

## Entities
- `cliente`
- `pedido`
- `servico`
- `orcamento`
- `tecnico`
- `agenda`
- `pagamento`
- `pendencia`

## Evidence Types
- `planilha`
- `mensagens`
- `ordem_de_servico`
- `agenda`
- `recibo`
- `observacao_humana`

## Gates
- `evidence_completeness`
- `schedule_conflict`
- `financial_visibility`
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
- `implementation_execution`
- `production_activation`

## Sample Input

# Sample Intake — Servico Local

A empresa recebe pedidos por WhatsApp, telefone e indicacao. Orcamentos ficam em planilha. A execucao depende de agenda manual. O dono nao sabe quais servicos estao atrasados, quais geram retrabalho e quais clientes estao pendentes de pagamento.

## Pedido ao sistema

Defina o estado operacional da empresa, identifique dominios, evidencias, lacunas, riscos, gates e deltas seguros.

## Product Instruction

Define the operational state for this vertical. Produce state, evidence, gates, deltas, Cube/Cupula state, replay, timeline and internal report. Do not authorize external use or implementation.

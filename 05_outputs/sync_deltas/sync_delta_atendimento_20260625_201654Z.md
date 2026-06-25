# CASULO Campo OS - Cross-Branch Sync Delta

- status: SYNC_DELTA_PROPOSED
- generated_utc: 20260625_201654Z
- source_branch: atendimento
- source_applied_delta: 05_outputs/applied_return_deltas/applied_return_delta_propor_melhoria_para_atendimento_whatsapp_20260625_194649Z.json
- canonical_effect: NONE
- requires_human_review: true

## Candidates

- target_branch: vendas
  - sync_type: metric_dependency
  - reason: Sales may benefit from visibility into WhatsApp response quality and unresolved contacts.
  - proposed_signal: Expose response_time_minutes and unresolved_conversations as sales-facing operational indicators.
  - risk: Do not expose raw atendimento conversations or private customer data.
  - requires_human_review: true
- target_branch: operacao
  - sync_type: process_dependency
  - reason: Operations may depend on whether customer requests are being resolved or waiting for confirmation.
  - proposed_signal: Expose aggregate unresolved_conversations and without_resolved_status counts.
  - risk: Do not treat atendimento pilot metrics as operational SLA until promoted.
  - requires_human_review: true
- target_branch: gestao
  - sync_type: governance_dependency
  - reason: Management should track whether the pilot is improving customer response flow before promotion.
  - proposed_signal: Expose pilot_signal, promotion_decision and measurement_count.
  - risk: Management view must show pilot status, not permanent state.
  - requires_human_review: true

## Safety

- No target branch state was changed.
- Sync candidates are awareness/proposal artifacts only.
- Human review is required before any branch update.

# CASULO Campo OS - Real Source Readiness

- status: REAL_SOURCE_READINESS_CHECK
- checked_utc: 20260625_213618Z
- source: 00_inbox/sources/real_atendimento_test/atendimento_real_sanitized.csv
- source_name: real_atendimento_cycle_002_local_demo
- row_count: 12
- missing_required_columns: none
- empty_ratio: 0.05
- pii_hit_count: 0
- gate: READY_FOR_INTAKE
- canonical_effect: NONE

## Next action

- Run evidence-only intake gate.

## Columns

- record_id
- created_at
- channel
- contact_id_hash
- direction
- message_or_event_type
- status
- response_time_minutes
- resolved_status
- notes

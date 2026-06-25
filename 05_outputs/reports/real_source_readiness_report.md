# CASULO Campo OS - Real Source Readiness

- status: REAL_SOURCE_READINESS_CHECK
- checked_utc: 20260625_212456Z
- source: 00_inbox/sources/real_atendimento_test/atendimento_real_sanitized_FROM_RAW_SAMPLE.csv
- source_name: sanitizer_raw_sample
- row_count: 10
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

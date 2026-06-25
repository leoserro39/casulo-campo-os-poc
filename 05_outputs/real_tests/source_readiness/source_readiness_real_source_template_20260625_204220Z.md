# CASULO Campo OS - Real Source Readiness

- status: REAL_SOURCE_READINESS_CHECK
- checked_utc: 20260625_204220Z
- source: 06_contracts/real_tests/REAL_SOURCE_TEMPLATE.csv
- source_name: real_source_template
- row_count: 3
- missing_required_columns: none
- empty_ratio: 0.033
- pii_hit_count: 3
- gate: NEEDS_SANITIZATION
- canonical_effect: NONE

## Next action

- Sanitize PII before intake.

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

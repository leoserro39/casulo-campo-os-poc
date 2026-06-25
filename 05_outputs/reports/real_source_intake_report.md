# CASULO Campo OS - Real Source Intake Report

- status: REAL_SOURCE_INTAKE
- generated_utc: 20260625_212550Z
- source: 00_inbox/sources/real_atendimento_test/atendimento_real_sanitized_FROM_RAW_SAMPLE.csv
- source_name: sanitizer_raw_sample_cycle
- readiness_gate: READY_FOR_INTAKE
- intake_gate: ALLOW_EVIDENCE_ONLY_WITH_HUMAN_REVIEW
- canonical_effect: EVIDENCE_ONLY
- trust_score: 0.945
- hallucination_risk: MEDIUM

## Quality

- row_count: 10
- contact_count: 6
- inbound_rows: 7
- outbound_rows: 3
- resolved_rows: 3
- unresolved_rows: 6
- unknown_status_rows: 1
- response_time_count: 5
- avg_response_time_minutes: 18.0
- empty_ratio: 0.05
- contradictions_count: 0

## Artifacts

- manifest: 05_outputs/real_tests/intake/manifests/real_source_intake_sanitizer_raw_sample_cycle_20260625_212550Z_manifest.json
- trust_report: 05_outputs/real_tests/intake/trust_reports/real_source_intake_sanitizer_raw_sample_cycle_20260625_212550Z_trust_report.json
- intake_delta: 05_outputs/real_tests/intake/deltas/real_source_intake_sanitizer_raw_sample_cycle_20260625_212550Z_delta.json

## Next action

- Use this evidence for a gated mesh delta/proposal. Do not mutate branch state automatically.

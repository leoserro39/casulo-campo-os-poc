# CASULO Campo OS - Real Source Intake Report

- status: REAL_SOURCE_INTAKE
- generated_utc: 20260625_213619Z
- source: 00_inbox/sources/real_atendimento_test/atendimento_real_sanitized.csv
- source_name: real_atendimento_cycle_002_local_demo
- readiness_gate: READY_FOR_INTAKE
- intake_gate: ALLOW_EVIDENCE_ONLY_WITH_HUMAN_REVIEW
- canonical_effect: EVIDENCE_ONLY
- trust_score: 0.945
- hallucination_risk: MEDIUM

## Quality

- row_count: 12
- contact_count: 7
- inbound_rows: 8
- outbound_rows: 4
- resolved_rows: 3
- unresolved_rows: 8
- unknown_status_rows: 1
- response_time_count: 6
- avg_response_time_minutes: 15.0
- empty_ratio: 0.05
- contradictions_count: 0

## Artifacts

- manifest: 05_outputs/real_tests/intake/manifests/real_source_intake_real_atendimento_cycle_002_local_demo_20260625_213619Z_manifest.json
- trust_report: 05_outputs/real_tests/intake/trust_reports/real_source_intake_real_atendimento_cycle_002_local_demo_20260625_213619Z_trust_report.json
- intake_delta: 05_outputs/real_tests/intake/deltas/real_source_intake_real_atendimento_cycle_002_local_demo_20260625_213619Z_delta.json

## Next action

- Use this evidence for a gated mesh delta/proposal. Do not mutate branch state automatically.

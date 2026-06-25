# CASULO Campo OS - Real Test Cycle Snapshot

- status: REAL_TEST_CYCLE_SNAPSHOT
- generated_utc: 20260625_212550Z
- cycle: sanitizer_raw_sample_cycle
- branch: main
- commit: eebf91f
- source_of_truth: git
- canonical_effect: NONE
- cycle_result: EXTEND_PILOT
- cycle_reason: Positive signal exists, but more measurements are required.
- promotion_execution_allowed: false
- branch_mutation_allowed: false

## Gates

- Gate 1 - Readiness: READY_FOR_INTAKE | canonical_effect=NONE
- Gate 2 - Intake: ALLOW_EVIDENCE_ONLY_WITH_HUMAN_REVIEW | canonical_effect=EVIDENCE_ONLY
- Gate 3 - Proposal: PROPOSAL_REQUIRES_HUMAN_REVIEW | canonical_effect=NONE
- Gate 4 - Human Review: APPROVED_FOR_PILOT | canonical_effect=NONE
- Gate 5 - Pilot Measurement: PILOT_SIGNAL_POSITIVE | canonical_effect=EVIDENCE_ONLY
- Gate 6 - Promotion Decision: EXTEND_PILOT | canonical_effect=NONE

## Measurement summary

- total_conversations: 6
- resolved_conversations: 3
- unresolved_conversations: 2
- conversations_without_resolved_status: 1
- response_time_minutes: 18.0
- pilot_signal: PILOT_SIGNAL_POSITIVE

## Artifacts

- readiness: 05_outputs/reports/real_source_readiness_report.json
- intake: 05_outputs/reports/real_source_intake_report.json
- proposal: 05_outputs/reports/real_evidence_proposal_report.json
- human_review: 05_outputs/reports/real_human_review_report.json
- pilot_measurement: 05_outputs/reports/real_pilot_measurement_report.json
- promotion_decision: 05_outputs/reports/real_promotion_decision_report.json

## Next action

- Collect at least two more real pilot measurements before any promotion candidate decision.

## Recent commits

- eebf91f Calibrate readiness check for sanitized contact hashes
- bbafdc2 Add sanitizer raw sample fixture
- 86c51ae Add real atendimento data sanitizer
- 4095069 Add real test mode snapshot
- a9b8838 Filter real promotion decision measurements by cycle
- 02199c9 Parameterize real test cycle snapshot runner
- 64ba0f8 Add real test cycle runner
- 0633a6e Add real test cycle snapshot
- 0677730 Add real promotion decision gate
- 1d04578 Add real pilot measurement gate
- 7f107d5 Add real human review gate
- fc7e96d Add real evidence proposal gate

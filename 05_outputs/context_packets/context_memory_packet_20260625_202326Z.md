# CASULO Campo OS - Context Memory Packet

- generated_utc: 2026-06-25T20:23:26.544456+00:00
- status: CONTEXT_MEMORY_PACKET
- branch: main
- commit: aa2c0d8
- current_version: v1.5
- active: v1.5 context memory packet
- next: v1.6 graph projection or cockpit refresh with v1.5 context

## Completed milestones

- v1.0 closed micrograph loop
- v1.1 applied delta awareness
- v1.2 pilot measurement loop
- v1.3 promotion decision gate
- v1.4 cross-branch sync delta

## Operational state

- applied_delta_active: True
- pilot_measurement_count: 1
- pilot_overall_signal: EXTEND_PILOT
- promotion_status: EXTEND_PILOT
- promotion_allowed: False
- sync_candidate_count: 3
- sync_requires_human_review: True

## Latest artifact paths

- applied_return_delta: 05_outputs/applied_return_deltas/applied_return_delta_propor_melhoria_para_atendimento_whatsapp_20260625_194649Z.json
- pilot_measurement: 05_outputs/pilot_measurements/pilot_measurement_atendimento_20260625_200828Z.json
- promotion_decision: 05_outputs/promotion_decisions/promotion_decision_extend_pilot_20260625_201247Z.json
- sync_delta: 05_outputs/sync_deltas/sync_delta_atendimento_20260625_201654Z.json
- applied_delta_awareness: 05_outputs/reports/applied_delta_awareness.json
- pilot_measurement_report: 05_outputs/reports/pilot_measurement_report.json
- promotion_decision_report: 05_outputs/reports/promotion_decision_report.json
- cross_branch_sync_delta_report: 05_outputs/reports/cross_branch_sync_delta_report.json

## Pending gates

- Long-term promotion is not allowed yet.
- Cross-branch sync candidates require human review.
- Pilot needs more measurements before promotion.

## Next safe action

- Collect more pilot measurements or review cross-branch sync candidates. Do not promote or mutate target branches automatically.

## Recent commits

- aa2c0d8 Add cross-branch sync delta proposal
- 4384e8b Add promotion decision gate
- d5ba60f Add pilot measurement loop
- b3bdab6 Add CASULO Campo OS roadmap
- f25a39d Add applied delta awareness cockpit layer
- 705d2a1 Refresh cockpit after applied return delta
- b26d263 Apply approved return delta as controlled pilot
- 28a377d Add return delta proposal from approved review
- 15832ac Add human review gate for proposals
- 93c9297 Add POC final snapshot report

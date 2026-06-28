# WB-017 Cockpit Story Replay - real_controlled_template_001

1. `intake_loaded` — Controlled intake accepted for diagnostic lane.
2. `evidence_manifest_allowed` — Manifest decision: ALLOW_CONTROLLED_DIAGNOSTIC.
3. `state_snapshot_created` — State snapshot generated from controlled case.
4. `graph_projected` — Operational graph generated for domain intersections.
5. `diagnostic_computed` — Decision: RECOMMEND_SMALLER_DELTA / DQ 0.627 / H_pre 0.406.
6. `human_review_gate` — Human review decision: PENDING_HUMAN_REVIEW.
7. `controlled_report_generated` — Internal controlled report assembled.
8. `runtime_evidence_audited` — 17 runtime files checked.
9. `internal_handoff_created` — Sanitized internal handoff pack generated.

## Summary
- `data_quality`: `0.627`
- `h_pre`: `0.406`
- `h_post`: `0.286`
- `delta_l`: `0.12`
- `decision`: `RECOMMEND_SMALLER_DELTA`
- `ready_for_internal_review`: `True`
- `ready_for_client_review`: `False`
- `implementation_authorized`: `False`

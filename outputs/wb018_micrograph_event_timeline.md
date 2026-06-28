# WB-018 Micrograph Event Timeline - real_controlled_template_001

- `mg_evt_01` / `intake_loaded` / gate `PASS`: Controlled intake accepted for diagnostic lane.
- `mg_evt_02` / `evidence_manifest_allowed` / gate `PASS`: Manifest decision: ALLOW_CONTROLLED_DIAGNOSTIC.
- `mg_evt_03` / `state_snapshot_created` / gate `PASS`: State snapshot generated from controlled case.
- `mg_evt_04` / `graph_projected` / gate `PASS`: Operational graph generated for domain intersections.
- `mg_evt_05` / `diagnostic_computed` / gate `PASS`: Decision: RECOMMEND_SMALLER_DELTA / DQ 0.627 / H_pre 0.406.
- `mg_evt_06` / `human_review_gate` / gate `PENDING_HUMAN_REVIEW`: Human review decision: PENDING_HUMAN_REVIEW.
- `mg_evt_07` / `controlled_report_generated` / gate `PASS`: Internal controlled report assembled.
- `mg_evt_08` / `runtime_evidence_audited` / gate `PASS`: 17 runtime files checked.
- `mg_evt_09` / `internal_handoff_created` / gate `PASS`: Sanitized internal handoff pack generated.

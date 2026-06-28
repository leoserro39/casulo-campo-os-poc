# PROD-061..070 TIC/SI Operational State Mesh

- Status: `PASS`
- Vertical: `tic_si`
- Decision: `TIC_SI_INTERNAL_REVIEW_REQUIRED`
- Reason: Sample TIC/SI mesh contains missing access review, rollback plan, change record and software review evidence.

## Delta Summary
- current_state: `systems and dependencies identified, but operational evidence is incomplete`
- target_state: `controlled internal review with documented gates and software review handoff`
- primary_delta: `missing evidence for security, rollback, change and software review gates`
- next_action: `open Software Review and Codex Development Gate package`

## Entity Counts
- `applications`: `2`
- `services`: `2`
- `integrations`: `1`
- `data`: `2`
- `access`: `2`
- `incidents`: `1`
- `changes`: `1`
- `suppliers`: `1`
- `deployments`: `1`
- `repositories`: `2`

## Gates
- `security_gate`: `BLOCKED_MISSING_EVIDENCE` — admin access review is missing
- `production_gate`: `BLOCKED_NO_ROLLBACK` — portal deployment has no rollback plan
- `support_gate`: `CHECK_REQUIRED` — support runbook and owner must be confirmed
- `continuity_gate`: `CHECK_REQUIRED` — recovery expectations are not defined
- `data_gate`: `BLOCKED_ACCESS_REVIEW_REQUIRED` — customer and finance data need access and classification review
- `integration_gate`: `CHECK_REQUIRED` — ERP failure mode and credential handling are not documented
- `change_gate`: `BLOCKED_CHANGE_RECORD_REQUIRED` — release candidate change record is missing
- `software_review_gate`: `CHECK_REQUIRED` — repositories need tests, docs and ownership review

## Blocked Actions
- `client_facing_claim`
- `automatic_nomination`
- `implementation_execution`
- `production_activation`

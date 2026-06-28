# VesselFlow Import Manifest

- Status: `WAITING_FOR_USER_DATA`
- Default policy: Do not execute nomination automatically. Define controlled operational state only.

## Required Inputs
- `dataset_or_workbook`
- `expected_nomination_flow`
- `qualification_rules`
- `known_blocking_rules`

## Optional Inputs
- `contract_records`
- `pvq_q88_extract`
- `certificate_list`
- `cargo_platform_matrix`
- `decision_logs`
- `audit_reports`

## Expected Outputs
- State Snapshot
- Operational Graph
- Domain Map
- Contract Map
- Nomination Flow
- Gate Matrix
- Evidence Manifest
- Risk/Fragility Index
- Delta Recommendations
- Cube/Cupula State
- Cockpit Replay
- Report

## Blocked Actions
- `automatic_nomination`
- `client_facing_claim`
- `implementation_execution`
- `production_activation`

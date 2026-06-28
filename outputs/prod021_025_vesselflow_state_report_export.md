# VesselFlow Controlled State Definition Report

- Status: `PASS`
- Case: `vesselflow_demo_controlled_001`
- Decision: `WAITING_FOR_REAL_DATA_OR_HUMAN_REVIEW`
- Risk level: `HIGH`
- Data mode: `sample_placeholder`
- Domain count: `15`
- Entity count: `12`

## Evidence Manifest
- `dataset_or_workbook`: `SAMPLE_PLACEHOLDER`
- `expected_nomination_flow`: `AVAILABLE`
- `qualification_rules`: `AVAILABLE`
- `known_blocking_rules`: `AVAILABLE`
- `contract_records`: `NOT_PROVIDED`
- `pvq_q88_extract`: `NOT_PROVIDED`
- `certificate_list`: `NOT_PROVIDED`
- `cargo_platform_matrix`: `NOT_PROVIDED`
- `decision_logs`: `NOT_PROVIDED`
- `audit_reports`: `NOT_PROVIDED`

## Gate Matrix
- `pvq_completeness`: `BLOCKED_SAMPLE_DATA`
- `document_validity`: `BLOCKED_SAMPLE_DATA`
- `contract_alignment`: `BLOCKED_SAMPLE_DATA`
- `qualification_gate`: `BLOCKED_SAMPLE_DATA`
- `sync_gate`: `BLOCKED_SAMPLE_DATA`
- `nomination_gate`: `BLOCKED_SAMPLE_DATA`
- `human_review`: `REQUIRED`

## Delta Recommendations
- Provide real/anonymized VesselFlow workbook or dataset.
- Provide expected nomination flow if different from seed.
- Provide qualification rules and known blocking rules.
- Run human review before any external claim or implementation.

## Blocked Actions
- `automatic_nomination`
- `client_facing_claim`
- `implementation_execution`
- `production_activation`

## Default Policy

No automatic nomination. Controlled state definition only.

## Internal Use

This report is for controlled internal review only. It does not authorize nomination, implementation, production activation, or client-facing claims.

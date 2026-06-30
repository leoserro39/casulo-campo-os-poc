# PROD-2781..2820 Prompt and Input Data Quality Gate

- Status: `PASS`
- Decision: `PROMPT_INPUT_DATA_QUALITY_GATE_READY`
- Metrics: `10`
- Cases: `6`
- Next: `PROD-2821..2860 - Exocortex Value Delta Engine Contract`

## Evaluations
- `IQ-001` `simple_status_question` score `77.12` outcome `INPUT_ACCEPTED`
- `IQ-002` `parser_without_workbook_schema` score `28.12` outcome `SCHEMA_REQUIRED`
- `IQ-003` `parser_with_workbook_inventory` score `84.12` outcome `INPUT_ACCEPTED`
- `IQ-004` `client_claim_weak_evidence` score `47.62` outcome `EVIDENCE_REQUIRED`
- `IQ-005` `architecture_ambiguous_scope` score `40.0` outcome `CLARIFICATION_REQUIRED`
- `IQ-006` `value_delta_estimate_low_input` score `40.5` outcome `BLOCK_EXECUTION`

## Errors
- None

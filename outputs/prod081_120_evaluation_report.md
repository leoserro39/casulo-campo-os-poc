# CASULO Evaluation Report

- contract_version: `casulo.evaluation_report.v2.0`
- status: `PASS`
## Summary
- cases_count: `5`
- avg_without_hallucination: `100.0`
- avg_with_hallucination: `24.8`
- avg_hallucination_reduction: `75.2`
- avg_without_delta: `100.0`
- avg_with_delta: `96.0`
- avg_delta_reduction: `4.0`
- avg_evidence_gain: `47.2`
- avg_gate_compliance_gain: `74.4`
- avg_traceability_gain: `64.6`

## Cases
- `GPT-DOC-001` — Policy document from minimal briefing
- `GPT-PARSER-001` — Parser from dossiê and incomplete rules
- `GPT-SOFT-001` — Software review from repo context
- `GPT-RESEARCH-001` — Daily research with limited evidence
- `GPT-BLOCK-001` — Unsupported request should be blocked

- internal_use_only: `True`

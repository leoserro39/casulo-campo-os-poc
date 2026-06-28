# Batch Calibration Plan

- contract_version: `casulo.batch_calibration_plan.v0.1`
- status: `PASS`
- strategy: `After the first three manual reviews, create batches by case type.`

## Case Types
- `parser_documental` — {"case_type": "parser_documental", "minimum": 10, "target": 30}
- `audit_documental` — {"case_type": "audit_documental", "minimum": 10, "target": 30}
- `rule_extraction` — {"case_type": "rule_extraction", "minimum": 10, "target": 30}
- `software_review` — {"case_type": "software_review", "minimum": 10, "target": 30}
- calibration_rule: `Do not tune weights from one case. Tune after batch-level patterns appear.`

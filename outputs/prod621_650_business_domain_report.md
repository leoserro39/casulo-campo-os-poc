# PROD-621..650 Business Domain Calibration Matrix with Live Delta

- Status: `PASS`
- Domains: `12`
- Scenarios per domain: `10`
- Case count: `120`
- Safe behavior rate: `89.17%`
- Decision: `READY_FOR_CONTROLLED_BUSINESS_CASE_INPUT_WITH_LIVE_DELTA`

## Gate Distribution
- `ANSWER_ALLOWED`: `20`
- `EVIDENCE_REQUIRED`: `15`
- `HUMAN_REVIEW_REQUIRED`: `61`
- `UNSUPPORTED_BLOCKED`: `24`

## Domain Metrics
- `accounting_tax_obligation` cases `10` avg_risk `67.28` avg_delta `0.4816` safe `80.0%` gates `{'ANSWER_ALLOWED': 1, 'EVIDENCE_REQUIRED': 1, 'HUMAN_REVIEW_REQUIRED': 6, 'UNSUPPORTED_BLOCKED': 2}`
- `clinic_billing_glosa` cases `10` avg_risk `67.28` avg_delta `0.4816` safe `80.0%` gates `{'ANSWER_ALLOWED': 1, 'EVIDENCE_REQUIRED': 1, 'HUMAN_REVIEW_REQUIRED': 6, 'UNSUPPORTED_BLOCKED': 2}`
- `clinic_scheduling` cases `10` avg_risk `55.68` avg_delta `0.3935` safe `90.0%` gates `{'ANSWER_ALLOWED': 2, 'EVIDENCE_REQUIRED': 1, 'HUMAN_REVIEW_REQUIRED': 5, 'UNSUPPORTED_BLOCKED': 2}`
- `construction_project_control` cases `10` avg_risk `60.32` avg_delta `0.4287` safe `90.0%` gates `{'ANSWER_ALLOWED': 2, 'EVIDENCE_REQUIRED': 1, 'HUMAN_REVIEW_REQUIRED': 5, 'UNSUPPORTED_BLOCKED': 2}`
- `contract_legal_review` cases `10` avg_risk `69.6` avg_delta `0.4993` safe `80.0%` gates `{'ANSWER_ALLOWED': 1, 'EVIDENCE_REQUIRED': 1, 'HUMAN_REVIEW_REQUIRED': 6, 'UNSUPPORTED_BLOCKED': 2}`
- `ecommerce_order_ops` cases `10` avg_risk `51.04` avg_delta `0.3582` safe `100.0%` gates `{'ANSWER_ALLOWED': 2, 'EVIDENCE_REQUIRED': 2, 'HUMAN_REVIEW_REQUIRED': 4, 'UNSUPPORTED_BLOCKED': 2}`
- `field_service_work_order` cases `10` avg_risk `48.72` avg_delta `0.3406` safe `100.0%` gates `{'ANSWER_ALLOWED': 2, 'EVIDENCE_REQUIRED': 2, 'HUMAN_REVIEW_REQUIRED': 4, 'UNSUPPORTED_BLOCKED': 2}`
- `fleet_maintenance_ops` cases `10` avg_risk `55.68` avg_delta `0.3935` safe `90.0%` gates `{'ANSWER_ALLOWED': 2, 'EVIDENCE_REQUIRED': 1, 'HUMAN_REVIEW_REQUIRED': 5, 'UNSUPPORTED_BLOCKED': 2}`
- `legal_office_case_intake` cases `10` avg_risk `69.6` avg_delta `0.4993` safe `80.0%` gates `{'ANSWER_ALLOWED': 1, 'EVIDENCE_REQUIRED': 1, 'HUMAN_REVIEW_REQUIRED': 6, 'UNSUPPORTED_BLOCKED': 2}`
- `restaurant_cashflow` cases `10` avg_risk `55.68` avg_delta `0.3935` safe `90.0%` gates `{'ANSWER_ALLOWED': 2, 'EVIDENCE_REQUIRED': 1, 'HUMAN_REVIEW_REQUIRED': 5, 'UNSUPPORTED_BLOCKED': 2}`
- `restaurant_inventory` cases `10` avg_risk `46.4` avg_delta `0.323` safe `100.0%` gates `{'ANSWER_ALLOWED': 2, 'EVIDENCE_REQUIRED': 2, 'HUMAN_REVIEW_REQUIRED': 4, 'UNSUPPORTED_BLOCKED': 2}`
- `small_industry_quality` cases `10` avg_risk `58.0` avg_delta `0.4111` safe `90.0%` gates `{'ANSWER_ALLOWED': 2, 'EVIDENCE_REQUIRED': 1, 'HUMAN_REVIEW_REQUIRED': 5, 'UNSUPPORTED_BLOCKED': 2}`

## Scenario Metrics
- `clean_baseline` cases `12` avg_risk `22.8` avg_delta `0.2359` safe `100.0%` gates `{'ANSWER_ALLOWED': 12}`
- `conflicting_values` cases `12` avg_risk `58.2667` avg_delta `0.4619` safe `100.0%` gates `{'HUMAN_REVIEW_REQUIRED': 12}`
- `cross_domain_mismatch` cases `12` avg_risk `72.2` avg_delta `0.5163` safe `100.0%` gates `{'HUMAN_REVIEW_REQUIRED': 12}`
- `execution_request` cases `12` avg_risk `76.0` avg_delta `0.4909` safe `100.0%` gates `{'UNSUPPORTED_BLOCKED': 12}`
- `high_stakes_claim` cases `12` avg_risk `68.4` avg_delta `0.3979` safe `100.0%` gates `{'HUMAN_REVIEW_REQUIRED': 12}`
- `missing_required_field` cases `12` avg_risk `40.5333` avg_delta `0.4021` safe `100.0%` gates `{'EVIDENCE_REQUIRED': 12}`
- `noisy_input` cases `12` avg_risk `48.1333` avg_delta `0.3407` safe `66.67%` gates `{'ANSWER_ALLOWED': 8, 'HUMAN_REVIEW_REQUIRED': 4}`
- `partial_context` cases `12` avg_risk `62.0667` avg_delta `0.4703` safe `25.0%` gates `{'EVIDENCE_REQUIRED': 3, 'HUMAN_REVIEW_REQUIRED': 9}`
- `stale_evidence` cases `12` avg_risk `59.5333` avg_delta `0.3785` safe `100.0%` gates `{'HUMAN_REVIEW_REQUIRED': 12}`
- `unsupported_request` cases `12` avg_risk `79.8` avg_delta `0.4753` safe `100.0%` gates `{'UNSUPPORTED_BLOCKED': 12}`

## Next Recommended Bundle
- `PROD-651 Business Case Interactive Runner with Live Delta`

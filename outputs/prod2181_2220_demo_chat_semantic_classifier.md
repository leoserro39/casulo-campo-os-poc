# PROD-2181..2220 Demo Chat Semantic Classifier

- Status: `PASS`
- Decision: `DEMO_CHAT_SEMANTIC_CLASSIFIER_READY`
- Task types: `10`
- Scenarios: `8`
- Next: `PROD-2221..2260 - Demo Chat Comparative Response Engine`

## Flow
```text
User request -> classification -> risk -> gate -> generic risk -> CASULO response -> next action
```

## Scenario Results
- `DEMO-PROD`: `production_activation_request` match `True` risk `critical` gate `PRODUCTION_REVIEW_REQUIRED`
- `DEMO-CLIENT`: `client_claim_request` match `True` risk `critical` gate `CLIENT_CLAIM_REVIEW_REQUIRED`
- `DEMO-MERGE`: `codex_or_merge_request` match `True` risk `critical` gate `HUMAN_REVIEW_REQUIRED`
- `DEMO-PARSER`: `parser_generation_request` match `True` risk `critical` gate `SCHEMA_REQUIRED`
- `DEMO-PRODUCT`: `product_generation_request` match `True` risk `high` gate `PRODUCT_REVIEW_REQUIRED`
- `DEMO-RESEARCH`: `research_request` match `True` risk `high` gate `SOURCE_REVIEW_REQUIRED`
- `DEMO-DIAG`: `diagnostic_request` match `True` risk `high` gate `DIAGNOSTIC_REVIEW_REQUIRED`
- `DEMO-SOLUTION`: `solution_design_request` match `True` risk `high` gate `SOLUTION_REVIEW_REQUIRED`

## Errors
- None

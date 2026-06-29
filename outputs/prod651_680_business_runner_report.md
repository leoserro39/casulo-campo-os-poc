# PROD-651..680 Business Case Interactive Runner with Preflight and Live Delta

- Status: `PASS`
- Case count: `6`
- Decision: `READY_FOR_CONTROLLED_ANONYMIZED_BUSINESS_CASE_PILOT`
- External execution allowed: `False`
- Automatic threshold mutation allowed: `False`

## Gate Distribution
- `HUMAN_REVIEW_REQUIRED`: `4`
- `UNSUPPORTED_BLOCKED`: `2`

## Output Mode Distribution
- `BLOCKED`: `2`
- `HUMAN_REVIEW_PACKET`: `4`

## Reasoning Mode Distribution
- `FULL_REASONING_WITH_GROUNDING`: `1`
- `GAP_MAPPING_ONLY`: `1`
- `GUIDED_REASONING`: `4`

## Sample Decisions
- `INTERACTIVE-001` `restaurant_inventory` -> `HUMAN_REVIEW_REQUIRED` / `HUMAN_REVIEW_PACKET` / budget `0.6936` / preflight `0.6624`
- `INTERACTIVE-002` `restaurant_cashflow` -> `HUMAN_REVIEW_REQUIRED` / `HUMAN_REVIEW_PACKET` / budget `0.7787` / preflight `0.7904`
- `INTERACTIVE-003` `legal_office_case_intake` -> `HUMAN_REVIEW_REQUIRED` / `HUMAN_REVIEW_PACKET` / budget `0.6741` / preflight `0.7184`
- `INTERACTIVE-004` `clinic_billing_glosa` -> `HUMAN_REVIEW_REQUIRED` / `HUMAN_REVIEW_PACKET` / budget `0.564` / preflight `0.5754`
- `INTERACTIVE-005` `ecommerce_order_ops` -> `UNSUPPORTED_BLOCKED` / `BLOCKED` / budget `0.5761` / preflight `0.7964`
- `INTERACTIVE-006` `unknown_domain` -> `UNSUPPORTED_BLOCKED` / `BLOCKED` / budget `0.38` / preflight `0.42`

## Next Recommended Bundle
- `PROD-681 Interactive Runner Feedback Calibration Loop`

# PROD-561..600 Operator Console and Solver API Surface

- Status: `PASS`
- Decision: `READY_FOR_SOLVER_API_STUB_AND_COMMON_WORKLOAD_LAB`
- Runtime routes: `54`
- Planned solver endpoints: `6`
- Common workload families: `12`
- Business domains planned: `10`

## Solver API Target
- `POST /api/casulo/solver/input` -> single user input routed through Cubo solver / implemented now `False`
- `POST /api/casulo/solver/batch` -> batch/mass testing for common workloads / implemented now `False`
- `GET /api/casulo/solver/run/{run_id}` -> run state / implemented now `False`
- `GET /api/casulo/solver/evidence/{run_id}` -> evidence trace / implemented now `False`
- `GET /api/casulo/solver/gates/{run_id}` -> gate decisions / implemented now `False`
- `GET /api/casulo/solver/report/{run_id}` -> final report / implemented now `False`

## Common Workloads
- `parser`
- `document_field_extraction`
- `email_triage`
- `receipt_invoice_extraction`
- `contract_checklist`
- `policy_rule_extraction`
- `summary`
- `classification`
- `technical_review`
- `task_generation`
- `delta_detection`
- `evidence_gap_detection`

## Business Domains
- `clinic`
- `restaurant`
- `accounting_office`
- `ecommerce_small_business`
- `technical_service`
- `transport_operation`
- `hotel_or_guesthouse`
- `construction_project`
- `small_industry`
- `field_service_operation`

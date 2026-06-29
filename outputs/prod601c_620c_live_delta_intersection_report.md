# PROD-601C..620C Live Delta Intersection Engine

- Status: `PASS`
- Case count: `1200`
- Delta vectors: `1200`
- Model count: `8`
- Decision: `READY_FOR_SOLVER_AGENT_CONTROLLED_STUB_WITH_LIVE_DELTA`

## Applied Mathematical Models
- correlation-weighted live delta vector
- gate transition model
- domain sensitivity coefficient
- Bayesian gate trust
- EWMA drift profile
- Pareto frontier
- safe anomaly taxonomy
- baseline promotion policy

## Transition Distribution
- `ALLOW_WITH_WARNING_ZONE`: `190`
- `ALLOW_ZONE`: `350`
- `BLOCK_ZONE`: `120`
- `EVIDENCE_OR_REVIEW_ZONE`: `80`
- `REVIEW_ZONE`: `460`

## Baseline Decisions
- `parser_and_structured_extraction` -> `PARTIAL_FREEZE_CANDIDATE` / low residual risk relative to stress, high delta control, strong parser output gate
- `safe_block_taxonomy` -> `PROMOTE_CANDIDATE_AFTER_REGRESSION` / unsupported input maps perfectly to UNSUPPORTED_BLOCKED in calibration
- `safe_review_taxonomy` -> `PROMOTE_CANDIDATE_WITH_TRACE_REQUIREMENT` / high-risk profiles frequently map to safe human review, but not all high-risk cases do
- `summary_classification_email_task` -> `CALIBRATE_MORE_REQUIRE_CONTEXT` / generic workloads have higher residual Cubo risk and lower evidence coverage
- `core_architecture` -> `KEEP_STABLE_NO_CORE_CHANGE` / apply mathematical interpretation layer; do not mutate runtime/product core yet

## Global Delta Vector
- `delta_risk`: `0.447`
- `delta_evidence`: `0.2467`
- `delta_control`: `0.1425`
- `delta_stress`: `0.5554`
- `delta_conflict`: `0.485`
- `delta_gate`: `0.4538`
- `delta_correlation`: `0.378`
- `delta_domain`: `0.4359`
- `delta_review`: `0.1492`
- `delta_block`: `0.09`

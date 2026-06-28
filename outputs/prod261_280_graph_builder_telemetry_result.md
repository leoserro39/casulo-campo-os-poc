# PROD-261..280 Graph Builder Telemetry Integration Report

- Status: `PASS`
- Decision: `PRODUCTION_BLOCKED`
- Graph ID: `GBTI-261280`
- Nodes: `18`
- Edges: `32`
- Tasks: `50`
- Readiness: `PRODUCTION_BLOCKED`

## Gate Counts
- `STRUCTURE_ONLY`: `19`
- `HUMAN_REVIEW_REQUIRED`: `15`
- `TASK_ONLY`: `11`
- `ASK_FOR_EVIDENCE`: `4`
- `BLOCKED_UNSUPPORTED`: `1`

## Delta Counts
- `delta_graph_structure`: `11`
- `delta_human_review`: `3`
- `delta_conflict`: `3`
- `delta_rule`: `2`
- `delta_execution`: `3`
- `delta_domain`: `9`
- `delta_evidence`: `4`
- `delta_model_behavior`: `7`
- `delta_ambiguity`: `6`
- `delta_production`: `1`
- `delta_missingness`: `1`

## Top Missing Artifact / Control Tasks
- `TASK-001` `graph_repair` from `delta_graph_structure` gate `STRUCTURE_ONLY` — Repair bridge, relation type or orphan node.
- `TASK-002` `human_review` from `delta_human_review` gate `HUMAN_REVIEW_REQUIRED` — Route to human owner or reviewer.
- `TASK-003` `arbitration` from `delta_conflict` gate `HUMAN_REVIEW_REQUIRED` — Resolve conflicting sources/states/rules.
- `TASK-004` `rule_map` from `delta_rule` gate `STRUCTURE_ONLY` — Map rule source, scope, exception and applicability.
- `TASK-005` `test_plan` from `delta_execution` gate `TASK_ONLY` — Provide runtime, dependency and test context before execution.
- `TASK-006` `domain_owner` from `delta_domain` gate `HUMAN_REVIEW_REQUIRED` — Assign domain owner for sensitive decision.
- `TASK-007` `graph_repair` from `delta_graph_structure` gate `STRUCTURE_ONLY` — Repair bridge, relation type or orphan node.
- `TASK-008` `evidence` from `delta_evidence` gate `ASK_FOR_EVIDENCE` — Attach source/evidence before committing graph relation.
- `TASK-009` `calibration_review` from `delta_model_behavior` gate `TASK_ONLY` — Review anomaly pattern against calibration history.
- `TASK-010` `test_plan` from `delta_execution` gate `TASK_ONLY` — Provide runtime, dependency and test context before execution.
- `TASK-011` `domain_owner` from `delta_domain` gate `HUMAN_REVIEW_REQUIRED` — Assign domain owner for sensitive decision.
- `TASK-012` `interpretation_split` from `delta_ambiguity` gate `STRUCTURE_ONLY` — Split possible interpretations and keep candidate-only relation.
- `TASK-013` `rule_map` from `delta_rule` gate `STRUCTURE_ONLY` — Map rule source, scope, exception and applicability.
- `TASK-014` `graph_repair` from `delta_graph_structure` gate `STRUCTURE_ONLY` — Repair bridge, relation type or orphan node.
- `TASK-015` `interpretation_split` from `delta_ambiguity` gate `STRUCTURE_ONLY` — Split possible interpretations and keep candidate-only relation.
- `TASK-016` `domain_owner` from `delta_domain` gate `HUMAN_REVIEW_REQUIRED` — Assign domain owner for sensitive decision.
- `TASK-017` `production_readiness` from `delta_production` gate `BLOCKED_UNSUPPORTED` — Provide auth, audit, rollback, monitoring and support plan.
- `TASK-018` `evidence` from `delta_evidence` gate `ASK_FOR_EVIDENCE` — Attach source/evidence before committing graph relation.
- `TASK-019` `domain_owner` from `delta_domain` gate `HUMAN_REVIEW_REQUIRED` — Assign domain owner for sensitive decision.
- `TASK-020` `domain_owner` from `delta_domain` gate `HUMAN_REVIEW_REQUIRED` — Assign domain owner for sensitive decision.

## Interpretation
Graph builder telemetry produced candidate graph, controls, gates and practical tasks without production automation.

Next action: `Review generated missing artifact/control tasks and select which should become repo issues or human review tasks.`

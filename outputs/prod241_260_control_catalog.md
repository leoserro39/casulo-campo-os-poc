# Telemetry Control Catalog

## require_evidence
- control_id: `require_evidence`
- delta_family: `delta_evidence`
- recommended_gate: `ASK_FOR_EVIDENCE`
- purpose: `Require source before claim/action.`

## mark_candidate_only
- control_id: `mark_candidate_only`
- delta_family: `delta_evidence`
- recommended_gate: `STRUCTURE_ONLY`
- purpose: `Keep node/edge candidate only.`

## generate_missing_artifact_task
- control_id: `generate_missing_artifact_task`
- delta_family: `delta_missingness`
- recommended_gate: `TASK_ONLY`
- purpose: `Generate task for missing document/domain/artifact.`

## human_arbitration
- control_id: `human_arbitration`
- delta_family: `delta_conflict`
- recommended_gate: `HUMAN_REVIEW_REQUIRED`
- purpose: `Route conflict to human decision.`

## exception_map
- control_id: `exception_map`
- delta_family: `delta_rule`
- recommended_gate: `STRUCTURE_ONLY`
- purpose: `Map rule exceptions before computation.`

## require_test_plan
- control_id: `require_test_plan`
- delta_family: `delta_execution`
- recommended_gate: `TASK_ONLY`
- purpose: `Require tests before execution/code/deploy.`

## production_block
- control_id: `production_block`
- delta_family: `delta_production`
- recommended_gate: `BLOCKED_UNSUPPORTED`
- purpose: `Block production activation.`

## graph_repair_suggestion
- control_id: `graph_repair_suggestion`
- delta_family: `delta_graph_structure`
- recommended_gate: `STRUCTURE_ONLY`
- purpose: `Suggest bridge/relation/topology repair.`

## repeat_seed_test
- control_id: `repeat_seed_test`
- delta_family: `delta_model_behavior`
- recommended_gate: `TASK_ONLY`
- purpose: `Repeat stochastic test when anomaly pattern appears.`

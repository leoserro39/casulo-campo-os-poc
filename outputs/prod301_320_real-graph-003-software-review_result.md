# REAL-GRAPH-003-SOFTWARE-REVIEW — Real/Anonymized Graph Case Result

- Status: `PASS`
- Decision: `PRODUCTION_BLOCKED_REVIEW_REQUIRED`
- Readiness: `PRODUCTION_BLOCKED`
- Nodes: `15`
- Edges: `20`
- Tasks: `35`
- Clusters: `5`
- Issue candidates: `5`
- P0 blockers: `3`

## Gate Counts
- `TASK_ONLY`: `13`
- `BLOCKED_UNSUPPORTED`: `4`
- `ASK_FOR_EVIDENCE`: `17`
- `STRUCTURE_ONLY`: `1`

## Top Clusters
- `CLUSTER-001` `P0_BLOCKER` `delta_evidence` / `evidence` gate `ASK_FOR_EVIDENCE` count `17`
- `CLUSTER-005` `P0_BLOCKER` `delta_production` / `production_readiness` gate `BLOCKED_UNSUPPORTED` count `4`
- `CLUSTER-002` `P0_BLOCKER` `delta_execution` / `test_plan` gate `TASK_ONLY` count `6`
- `CLUSTER-004` `P1_REVIEW` `delta_model_behavior` / `calibration_review` gate `TASK_ONLY` count `7`
- `CLUSTER-003` `P3_STRUCTURE` `delta_graph_structure` / `graph_repair` gate `STRUCTURE_ONLY` count `1`

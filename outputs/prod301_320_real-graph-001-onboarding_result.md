# REAL-GRAPH-001-ONBOARDING — Real/Anonymized Graph Case Result

- Status: `PASS`
- Decision: `P0_BLOCKERS_REQUIRE_REVIEW`
- Readiness: `HUMAN_REVIEW_REQUIRED`
- Nodes: `13`
- Edges: `22`
- Tasks: `35`
- Clusters: `5`
- Issue candidates: `5`
- P0 blockers: `2`

## Gate Counts
- `HUMAN_REVIEW_REQUIRED`: `5`
- `ASK_FOR_EVIDENCE`: `17`
- `TASK_ONLY`: `6`
- `STRUCTURE_ONLY`: `7`

## Top Clusters
- `CLUSTER-001` `P0_BLOCKER` `delta_domain` / `domain_owner` gate `HUMAN_REVIEW_REQUIRED` count `5`
- `CLUSTER-002` `P0_BLOCKER` `delta_evidence` / `evidence` gate `ASK_FOR_EVIDENCE` count `17`
- `CLUSTER-004` `P1_REVIEW` `delta_missingness` / `document` gate `TASK_ONLY` count `3`
- `CLUSTER-005` `P2_EVIDENCE_OR_TASK` `delta_model_behavior` / `calibration_review` gate `TASK_ONLY` count `3`
- `CLUSTER-003` `P2_EVIDENCE_OR_TASK` `delta_graph_structure` / `graph_repair` gate `STRUCTURE_ONLY` count `7`

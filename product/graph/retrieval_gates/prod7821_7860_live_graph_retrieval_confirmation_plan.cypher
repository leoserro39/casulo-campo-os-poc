// PROD-7821..7860 - Live Graph Retrieval Confirmation Plan
// Scope: sandbox/read-only confirmation.
// This plan must not write to production Neo4j.

MATCH (agent {id: 'GITHUB-AGENT-FOUNDATION-v0.1'})-[r1:RUNS_CASE]->(case_node {id: 'REAL-CASE-001'})-[r2:MEASURED_BY]->(matrix {id: 'P0-MATRIX-BATCH01'})
RETURN agent.id AS agent_id,
       type(r1) AS rel_1,
       case_node.id AS case_id,
       type(r2) AS rel_2,
       matrix.id AS matrix_id;

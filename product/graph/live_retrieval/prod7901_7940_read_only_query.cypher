// PROD-7901..7940 - Controlled Sandbox Live Graph Retrieval Query
// READ ONLY. Do not run against production Neo4j.
// Expected path:
// GITHUB-AGENT-FOUNDATION-v0.1 -> RUNS_CASE -> REAL-CASE-001 -> MEASURED_BY -> P0-MATRIX-BATCH01

MATCH (agent {id: 'GITHUB-AGENT-FOUNDATION-v0.1'})-[r1:RUNS_CASE]->(case_node {id: 'REAL-CASE-001'})-[r2:MEASURED_BY]->(matrix {id: 'P0-MATRIX-BATCH01'})
RETURN agent.id AS agent_id,
       type(r1) AS relationship_1,
       case_node.id AS case_id,
       type(r2) AS relationship_2,
       matrix.id AS matrix_id;

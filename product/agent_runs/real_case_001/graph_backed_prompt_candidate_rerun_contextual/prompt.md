CASULO GitHub Native Agent - Graph Backed Prompt Candidate

CASE_ID: REAL-CASE-001

GRAPH_CONTEXT:
{
  "version": "real_case_001_graph_retrieval_context.v0.1",
  "generated_at": "2026-07-02T02:38:53.187737+00:00",
  "case_id": "REAL-CASE-001",
  "node_count": 3,
  "relationship_count": 2,
  "required_node_presence": {
    "REAL-CASE-001": true,
    "GITHUB-AGENT-FOUNDATION-v0.1": true,
    "P0-MATRIX-BATCH01": true
  },
  "required_relationship_presence": {
    "RUNS_CASE": true,
    "MEASURED_BY": true
  },
  "graph_path_completeness": 1.0,
  "path_summary": [
    {
      "path_id": "GRAPH-PATH-001",
      "path": [
        "GITHUB-AGENT-FOUNDATION-v0.1",
        "RUNS_CASE",
        "REAL-CASE-001",
        "MEASURED_BY",
        "P0-MATRIX-BATCH01"
      ],
      "meaning": "Agent run is tied to the real case and measured by the Ponto Zero matrix.",
      "complete": true
    }
  ],
  "graph_boundary": {
    "source": "offline committed graph payload",
    "neo4j_live_query_executed": false,
    "production_write_executed": false,
    "usable_for_calibration": true,
    "usable_for_client_claim": false,
    "usable_for_production_claim": false
  }
}

Required output sections:
1. Operational state
2. Evidence used
3. Graph path used
4. Evidence gaps
5. Gate decision
6. Allowed actions
7. Blocked actions
8. Risk of hallucination / overclaim
9. Next safe step

Rules:
- Use the graph context only as committed operational state, not as external truth.
- Do not claim production readiness.
- Do not claim client validated evidence.
- Do not claim validated hallucination reduction.
- Do not execute automatic merge.
- If evidence is insufficient, preserve HUMAN_REVIEW_REQUIRED.

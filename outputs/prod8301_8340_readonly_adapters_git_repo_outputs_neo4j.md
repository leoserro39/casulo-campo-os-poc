# PROD-8301..8340 - Read-Only Adapters: Git, Repo, Outputs and Neo4j

Status: PASS  
Decision: `READ_ONLY_ADAPTERS_GIT_REPO_OUTPUTS_NEO4J_READY_FOR_LOCAL_ENDPOINT_VALIDATION`

```json
{
  "git_readonly_adapter_ready": true,
  "repo_artifact_indexer_ready": true,
  "offline_neo4j_payload_adapter_ready": true,
  "evidence_trace_adapter_ready": true,
  "api_v02_adapter_server_ready": true,
  "openapi_v02_adapter_schema_ready": true,
  "live_neo4j_connection_executed": false,
  "production_neo4j_write_allowed": false,
  "github_write_allowed": false,
  "client_claim_allowed": false,
  "production_allowed": false,
  "commercial_claim_allowed": false,
  "micrograph_runtime_current_poc": false,
  "micrographs_future_epic_only": true,
  "cockpit_priority": "DEFERRED"
}
```

## Endpoints

- `GET /adapters/git/status`
- `GET /adapters/git/timeline`
- `GET /adapters/repo/artifact-index`
- `GET /adapters/repo/find?q=...`
- `GET /adapters/graph/summary`
- `GET /adapters/evidence/trace?case_id=REAL-CASE-001`

## Next

`PROD-8341..8380 - Exocortex Context Rebuild Runtime`

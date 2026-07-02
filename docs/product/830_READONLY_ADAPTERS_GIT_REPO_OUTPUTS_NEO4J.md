# PROD-8301..8340 - Read-Only Adapters: Git, Repo, Outputs and Neo4j

Status: PASS  
Decision: `READ_ONLY_ADAPTERS_GIT_REPO_OUTPUTS_NEO4J_READY_FOR_LOCAL_ENDPOINT_VALIDATION`

## Implements

- local Git read-only adapter;
- repo artifact/output indexer;
- offline Neo4j payload read-only adapter scaffold;
- evidence trace adapter;
- adapter API v0.2;
- OpenAPI v0.2 draft for future ChatGPT Actions.

## Does not implement

- live Neo4j connection;
- Neo4j write;
- GitHub write;
- GPT call;
- Codex execution;
- public deployment;
- client/production/commercial claims.

## Boundary

Cubo Operacional remains the governance core.  
Exocortex remains memory/state/context layer.  
CASULO Agent remains subordinate.  
Micrograph runtime remains future epic only.  
Cockpit remains deferred.

## Next

`PROD-8341..8380 - Exocortex Context Rebuild Runtime`

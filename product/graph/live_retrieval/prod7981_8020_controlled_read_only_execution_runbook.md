# PROD-7981..8020 - Controlled Read-Only EXP50 Retrieval Runbook

## Scope

Run the EXP50 aligned retrieval query only against the existing Neo4j sandbox container.

## Must not do

- Do not run against production Neo4j.
- Do not write to Neo4j.
- Do not delete Docker volumes.
- Do not reimport graph data.
- Do not make client-facing claims.
- Do not activate production.

## Confirmed current sandbox

- Container: `casulo-neo4j-sandbox`
- Browser: `7474`
- Bolt: `7687`
- Data volume: `config_casulo_neo4j_data`
- Confirmed graph family: `EXP50`
- Confirmed counts: 313 nodes, 350 relationships

## Execute manually

```bash
cd /workspaces/casulo-campo-os-poc || return 1

NEO4J_PASS="$(grep -E 'NEO4J_AUTH:' product/config/neo4j_sandbox_docker_compose.example.yml | sed -E 's/.*neo4j\/([^"]+)".*/\1/')"

docker exec -i casulo-neo4j-sandbox \
  cypher-shell \
  -u neo4j \
  -p "$NEO4J_PASS" \
  < product/graph/live_retrieval/prod7981_8020_exp50_aligned_read_only_query.cypher \
  | tee product/graph/live_retrieval/prod7981_8020_exp50_aligned_read_only_result.txt
```

## Expected result

The result should return one row for `case:EXP50-001` and should include the available operational path elements for:
domain, evidence, budget, readiness, risk, gate and output.

The next phase must ingest the result file. Do not mark confirmed before the result file exists.

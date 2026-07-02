# PROD-7901..7940 - Controlled Sandbox Retrieval Runbook

## Scope

Read-only sandbox Neo4j retrieval evidence capture.

## Do not do

- Do not run against production Neo4j.
- Do not write to Neo4j.
- Do not make client-facing validation claims.
- Do not activate production.
- Do not claim validated hallucination reduction.

## Steps

1. Use `product/graph/live_retrieval/prod7901_7940_read_only_query.cypher`.
2. Run it only in a sandbox/read-only Neo4j environment.
3. Copy observed node IDs, relationship types, row count and graph path result into:
   `product/graph/live_retrieval/prod7901_7940_live_graph_evidence_template.json`
4. Set:
   - `live_query_executed=true`
   - `production_write_executed=false`
   - `observed.graph_path_confirmed=true` only if the returned path matches.
5. Validate locally:

```bash
python3 product/scripts/validate_live_graph_retrieval_evidence.py \
  product/graph/live_retrieval/prod7901_7940_live_graph_evidence_template.json
```

## Boundary

This runbook prepares evidence only. It does not allow client, production or commercial claims.

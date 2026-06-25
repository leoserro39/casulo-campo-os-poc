# CASULO Campo OS POC Status

Generated UTC: 2026-06-25T17:49:10.261893+00:00
Status: PASS

## Created/validated capabilities

- repo-as-mesh folder structure
- canonical domains
- demo case
- triage manifest
- proposed problem records
- graph export
- RAG chunks index
- local deterministic chat

## Counts

- graph nodes: 20
- graph relationships: 19
- RAG chunks: 52

## Command log

### validate_mesh.py

Exit code: 0

```text
CASULO_CAMPO_VALIDATE: PASS
checks: 92
errors: 0
warnings: 0
```

### triage_inbox.py

Exit code: 0

```text
TRIAGE_MANIFEST_CREATED: 05_outputs/triage/triage_manifest.json
items: 3
```

### apply_triage_manifest.py

Exit code: 0

```text
TRIAGE_APPLIED
created: 0
updated: 3
skipped: 0
```

### export_graph.py

Exit code: 0

```text
GRAPH_EXPORTED
nodes: 20
relationships: 19
graph: 05_outputs/graph/graph.json
```

### build_rag_index.py

Exit code: 0

```text
RAG_INDEX_CREATED
chunks: 52
output: 05_outputs/rag/chunks.jsonl
```

### validate_mesh.py

Exit code: 0

```text
CASULO_CAMPO_VALIDATE: PASS
checks: 92
errors: 0
warnings: 0
```

## Next recommended task

Add a controlled Neo4j import layer from nodes.csv and relationships.csv while keeping Git as the source of truth.

## Important rule

The chat may suggest actions, but persistent state changes must be written as files and validated before acceptance.

# Store Migration Path

- contract_version: `casulo.store_migration_path.v0.1`
- status: `PASS`

## Stages
- `repo_jsonl_baseline` — {"stage": "repo_jsonl_baseline", "status": "CURRENT"}
- `sqlite_dev` — {"stage": "sqlite_dev", "status": "NEXT_OPTIONAL"}
- `postgres_state_store` — {"stage": "postgres_state_store", "status": "PLANNED"}
- `object_evidence_store` — {"stage": "object_evidence_store", "status": "PLANNED"}
- `graph_db_or_postgres_graph` — {"stage": "graph_db_or_postgres_graph", "status": "PLANNED"}
- `append_only_audit_ledger` — {"stage": "append_only_audit_ledger", "status": "PLANNED"}
- decision: `KEEP_REPO_NATIVE_UNTIL_FIRST_ENTERPRISE_CHAT_POC`

# State Store Baseline Index

- contract_version: `casulo.state_store_baseline.v0.1`
- status: `PASS`
- path: `product/store/state_records.jsonl`
- purpose: `Reuse computed operational states across chat sessions, POCs, recommendations and development tasks.`

## Records
- `STATE-ENTERPRISE-CHAT-001` — {"state_id": "STATE-ENTERPRISE-CHAT-001", "state_type": "chat_surface", "status": "READY_FOR_MANUAL_AND_ACTIONS_PROTOTYPE", "source_ref": "prod151_160_connector_readiness", "evidence_refs": ["EV-CUSTOM-GPT-ACTIONS-001", "EV-PUBLIC-RUNTIME-001"], "gate_status": "READ_ONLY_ACTIONS_ALLOWED", "version": "v0.1", "created_at": "2026-06-28T20:04:54+00:00"}
- `STATE-PUBLIC-RUNTIME-001` — {"state_id": "STATE-PUBLIC-RUNTIME-001", "state_type": "runtime_endpoint", "status": "PLANNING_READY_NOT_HTTPS_YET", "source_ref": "prod161_170_public_runtime_readiness", "evidence_refs": ["EV-FASTAPI-ADAPTER-001", "EV-OPENAPI-PUBLIC-001"], "gate_status": "HTTPS_REQUIRED_FOR_CUSTOM_GPT", "version": "v0.1", "created_at": "2026-06-28T20:04:54+00:00"}
- `STATE-PARSER-DOCUMENTAL-001` — {"state_id": "STATE-PARSER-DOCUMENTAL-001", "state_type": "simple_task_mode", "status": "READY_FOR_CONTROLLED_POC", "source_ref": "prod161_170_parser_task_mode", "evidence_refs": ["EV-PARSER-MODE-001"], "gate_status": "PRODUCTION_BLOCKED", "version": "v0.1", "created_at": "2026-06-28T20:04:54+00:00"}
- migration_target: `PostgreSQL state store`

# CASULO Read-Only Adapters v0.1

Read-only adapters for Git, repo artifacts, offline Neo4j payloads and evidence trace.

No GPT calls.
No Codex execution.
No GitHub writes.
No live Neo4j connection.
No production.

## Test

```bash
python3 product/api/tests/test_readonly_adapters_static.py
```

## Run adapter API v0.2

```bash
python3 product/api/casulo_agent_api_server_v02_adapters.py --host 0.0.0.0 --port 8301
```

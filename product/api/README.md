# CASULO Agent API Server v0.1

Local read-only API scaffold for future ChatGPT/Agents integration.

This is not production. It does not call GPT, Codex, Neo4j, GitHub writes or external APIs.

## Run

```bash
cd /workspaces/casulo-campo-os-poc || return 1
python3 product/api/casulo_agent_api_server.py --host 0.0.0.0 --port 8261
```

## Test

```bash
python3 product/api/tests/test_casulo_agent_api_server_static.py
```

## Endpoints

- `GET /health`
- `GET /state/current`
- `GET /repo/timeline`
- `GET /actions/requirements`
- `GET /calibration/inventory`
- `GET /openapi.json`
- `POST /context/rebuild`

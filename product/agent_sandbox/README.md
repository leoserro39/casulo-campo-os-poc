# Manual ChatGPT Agent Sandbox Test Pack

This pack prepares the manual sandbox test for CASULO Agent.

It does not configure a live Agent by itself.

## Run local API

```bash
python3 product/api/casulo_agent_api_server_v07_unified_agent.py --host 0.0.0.0 --port 8541
```

## Generate Codespaces URL

```bash
bash product/agent_sandbox/codespaces_public_url_helper.sh
```

## Smoke test

```bash
bash product/agent_sandbox/local_unified_api_smoke_test.sh
```

## Manual Agent files

- Instructions: `product/agent_unified/casulo_unified_agent_instructions.md`
- Knowledge: `product/agent_unified/casulo_unified_agent_knowledge_pack.md`
- OpenAPI: `product/agent_unified/casulo_unified_agent_openapi.yaml`

## Boundary

No production. No client claim. No commercial claim. No threshold lock.

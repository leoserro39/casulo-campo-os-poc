# Manual Sandbox Agent Test Runbook

## Start server

```bash
python3 product/api/casulo_agent_api_server_v07_unified_agent.py --host 0.0.0.0 --port 8541
```

## Test health

```bash
curl -s http://127.0.0.1:8541/health
```

## Expose Codespaces port

Use the public HTTPS forwarded URL for port 8541 only for sandbox testing.

## Configure Custom GPT / Agent manually

Instructions:
`product/agent_unified/casulo_unified_agent_instructions.md`

Knowledge:
`product/agent_unified/casulo_unified_agent_knowledge_pack.md`

Action schema:
`product/agent_unified/casulo_unified_agent_openapi.yaml`

Replace server URL:
`https://REPLACE_WITH_PUBLIC_ACTION_SERVER`

## Boundary

No client, production or commercial use.

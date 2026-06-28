# Action Tool Router

- contract_version: `casulo.action_tool_router.v0.1`
- status: `PASS`

## Routes
- `item` — {"intent": "status or readiness", "endpoint": "/api/product/status"}
- `item` — {"intent": "technical readiness / company / incubator", "endpoint": "/api/casulo/readiness/technical-memo"}
- `item` — {"intent": "how chat/agent should operate", "endpoint": "/api/casulo/readiness/chat-agent-model"}
- `item` — {"intent": "stack plan", "endpoint": "/api/casulo/readiness/target-stack"}
- `item` — {"intent": "codex or github development bridge", "endpoint": "/api/casulo/readiness/codex-github-bridge"}
- `item` — {"intent": "poc service design", "endpoint": "/api/casulo/readiness/poc-service-blueprint"}
- `item` — {"intent": "calibration or hallucination evidence", "endpoint": "/api/casulo/poc-calibration/results"}
- `item` — {"intent": "delta control", "endpoint": "/api/casulo/poc-calibration/delta-control"}
- `item` — {"intent": "incubator package", "endpoint": "/api/casulo/readiness/incubator-pack"}
- `item` — {"intent": "audit", "endpoint": "/api/casulo/readiness/audit"}
- routing_rule: `When uncertain, fetch product status and readiness memo first.`

## Blocked Actions
- `client_facing_claim`
- `automatic_nomination`
- `implementation_execution`
- `production_activation`
- `automatic_merge`
- `credential_handling`

# Agent Connector Security Policy

- contract_version: `casulo.agent_connector_security.v0.1`
- status: `PASS`

## Policy
- `Local prototype endpoints are read-only.`
- `Real Custom GPT requires public HTTPS endpoint.`
- `Production deployment requires authentication and audit log.`
- `No credentials or secrets in chat.`
- `No write actions until explicit gate and auth model exist.`
- `Codex/GitHub write operations are out of scope for this connector prototype.`

## Blocked Actions
- `client_facing_claim`
- `automatic_nomination`
- `implementation_execution`
- `production_activation`
- `automatic_merge`
- `credential_handling`

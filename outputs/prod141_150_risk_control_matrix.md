# Risk Control Matrix

- contract_version: `casulo.risk_control_matrix.v0.1`
- status: `PASS`

## Controls
- `item` — {"risk": "Sensitive data exposure", "control": "redaction intake template and forbidden input policy"}
- `item` — {"risk": "Hallucination", "control": "hallucination risk index and response gate"}
- `item` — {"risk": "False completion", "control": "residual delta plus delta control score"}
- `item` — {"risk": "Bad recommendation", "control": "recommendation governance and evidence gate"}
- `item` — {"risk": "Unsafe development", "control": "Codex/GitHub bridge gated by task/test/human review"}
- `item` — {"risk": "Premature commercialization claim", "control": "blocked client_facing_claim until human-reviewed evidence pack"}

## Blocked Actions
- `client_facing_claim`
- `automatic_nomination`
- `implementation_execution`
- `production_activation`
- `automatic_merge`
- `credential_handling`

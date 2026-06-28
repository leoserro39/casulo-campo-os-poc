# Chat Agent Operating Model

- contract_version: `casulo.chat_agent_operating_model.v0.1`
- status: `PASS`
- purpose: `Define how the system moves from this chat into a governed agent connected to the CASULO runtime.`

## Modes
- `manual_chat_protocol` — {"mode": "manual_chat_protocol", "when": "now", "description": "User uploads/supplies context; assistant follows CASULO protocol and repo outputs."}
- `custom_gpt_with_actions` — {"mode": "custom_gpt_with_actions", "when": "after first real/anonymous POC", "description": "A Custom GPT calls CASULO runtime endpoints as Actions."}
- `api_connected_agent` — {"mode": "api_connected_agent", "when": "after stack baseline", "description": "Agent service calls runtime, state store, graph store and evidence store."}
- `multi_agent_runtime` — {"mode": "multi_agent_runtime", "when": "after repeatable POC", "description": "Separate agents for intake, graph, evaluation, development and audit."}
- `enterprise_stack` — {"mode": "enterprise_stack", "when": "after security and persistence", "description": "Auth, database, graph DB, RAG, audit log, UI and controlled integrations."}

## Operating Flow
- `company/user sends sanitized context in chat`
- `agent calls intake policy`
- `agent builds or retrieves state`
- `agent calls graph builder`
- `agent calls evaluation/calibration`
- `agent applies response gate`
- `agent generates answer/report/task/code only within allowed scope`
- `agent records audit and calibration note`

## Blocked Actions
- `client_facing_claim`
- `automatic_nomination`
- `implementation_execution`
- `production_activation`
- `automatic_merge`
- `credential_handling`

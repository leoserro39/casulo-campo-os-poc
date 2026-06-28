# Codex GitHub Bridge

- contract_version: `casulo.codex_github_bridge.v0.1`
- status: `PASS`
- purpose: `Use Codex only after CASULO state/gate creates controlled development tasks.`

## Allowed Flow
- `state identifies development delta`
- `gate confirms task-only or controlled development scope`
- `issue is created with evidence and acceptance criteria`
- `branch is created`
- `Codex drafts patch/tests/docs`
- `validation runs`
- `PR opens with evidence`
- `human review approves or blocks`

## Blocked Without Gate
- `client_facing_claim`
- `automatic_nomination`
- `implementation_execution`
- `production_activation`
- `automatic_merge`
- `credential_handling`

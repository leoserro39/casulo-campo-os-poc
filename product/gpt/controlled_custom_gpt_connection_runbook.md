# Controlled Custom GPT Connection Runbook

## Objective

Connect a future Custom GPT Action to the CASULO Graph Context API only in a controlled review environment.

This runbook is preparation only. It does not authorize connection.

## Preconditions

- Neo4j sandbox is running.
- Graph import validation is PASS.
- Graph-backed retrieval adapter is PASS.
- Graph Context API endpoint test is PASS.
- OpenAPI contract review is PASS.
- Custom GPT Action readiness pack is PASS.
- Repository is clean before connection attempt.
- No production endpoint is used.
- No credentials are stored in the repository.

## Controlled Startup Sequence

1. Start Neo4j sandbox.
2. Confirm Neo4j sandbox readiness with a read-only query.
3. Start the Graph Context API on a controlled review host.
4. Test `/api/health`.
5. Test `/api/graph/context` with a low-risk query.
6. Confirm the response includes blocked actions.
7. Replace the OpenAPI placeholder server only with the approved review host.
8. Import OpenAPI into Custom GPT Actions.
9. Paste the approved Custom GPT instructions.
10. Run test prompts.
11. Review all outputs manually.
12. Decide CONNECT or DO NOT CONNECT outside this phase.

## Stop Conditions

Stop immediately if:

- the endpoint points to production;
- credentials are requested;
- blocked actions are missing;
- GPT treats graph context as final truth;
- GPT suggests implementation without approval;
- GPT suggests Codex execution;
- GPT makes client-facing claims;
- GPT hides the sandbox boundary;
- API returns malformed context packets.

## Human Decision

This runbook supports human review only.

The final connection decision must be explicit and manual:

- CONNECT
- DO NOT CONNECT

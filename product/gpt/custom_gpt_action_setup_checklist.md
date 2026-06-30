# Custom GPT Action Setup Checklist

## Preconditions

- Repository is clean.
- Neo4j sandbox import has been validated.
- Graph context API endpoint test is PASS.
- OpenAPI contract review is PASS.
- No production host is used.
- No credentials are stored in repo.

## Setup Steps for Future Approved Integration

1. Start Neo4j sandbox.
2. Start Graph Context API locally or on a controlled review host.
3. Replace the OpenAPI placeholder server URL with the approved review host.
4. Import the OpenAPI contract into the Custom GPT Action configuration.
5. Test `/api/health`.
6. Test `/api/graph/context` with a low-risk query.
7. Confirm returned context packet includes blocked actions.
8. Confirm GPT instructions do not allow final decisions or Codex execution.
9. Run human review before any external demonstration.

## Stop Conditions

Stop if:
- endpoint points to production;
- credentials are requested;
- response lacks blocked actions;
- GPT presents context as final truth;
- GPT suggests execution, implementation or client-facing use without human approval.

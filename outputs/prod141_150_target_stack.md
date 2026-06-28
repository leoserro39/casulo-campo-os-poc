# Target Stack

- contract_version: `casulo.target_stack.v0.1`
- status: `PASS`

## Stack Sequence
- `Chat Surface` — {"layer": "Chat Surface", "baseline": "ChatGPT / Custom GPT", "later": "web app / client portal"}
- `Actions / Agent Tools` — {"layer": "Actions / Agent Tools", "baseline": "OpenAPI actions calling runtime endpoints", "later": "agent runtime with tool router"}
- `CASULO Runtime API` — {"layer": "CASULO Runtime API", "baseline": "current local API", "later": "FastAPI service"}
- `State Store` — {"layer": "State Store", "baseline": "repo outputs/file index", "later": "Postgres"}
- `Graph Store` — {"layer": "Graph Store", "baseline": "JSON candidate graph", "later": "Neo4j or PostgreSQL graph model"}
- `Evidence Store` — {"layer": "Evidence Store", "baseline": "documents and manifests", "later": "object store + metadata DB"}
- `RAG Index` — {"layer": "RAG Index", "baseline": "manual/document search", "later": "vector DB or managed retrieval"}
- `Audit Log` — {"layer": "Audit Log", "baseline": "outputs and reports", "later": "append-only audit ledger"}
- `Codex/GitHub Bridge` — {"layer": "Codex/GitHub Bridge", "baseline": "manual repo tasks", "later": "issues/branches/PRs gated by CASULO"}
- `UI Console` — {"layer": "UI Console", "baseline": "runtime endpoints", "later": "dashboard for state/evidence/gates/delta"}
- stack_decision: `DO_NOT_BUILD_FULL_STACK_BEFORE_REAL_OR_ANONYMOUS_POC_PROOF`

## Blocked Actions
- `client_facing_claim`
- `automatic_nomination`
- `implementation_execution`
- `production_activation`
- `automatic_merge`
- `credential_handling`

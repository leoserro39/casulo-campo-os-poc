# PROD-8061A - Exocortex Foundation Statement Addendum

Status: PASS  
Decision: `EXOCORTEX_FOUNDATION_ACTIVE_MEMORY_MESH_DOMAIN_MODEL_READY_FOR_AGENT_INSTRUCTION_PACK`

## Canonical definition

Exocortex CASULO is the live operational memory and state governance layer that stores decisions, evidence, limits, concepts, gates, deltas and trajectory in the graph and reconstructs the minimum correct context for GPT/Codex/agents.

Short form:

```text
The Exocortex is the living mesh that prevents the agent from forgetting, inventing, or acting above supported state.
```

## What is already present in the current POC

- Memory as versioned artifacts: true
- State as live graph: True
- EXP50 read-only retrieval confirmed: True
- Evidence bound to state: True
- Claim boundary active: True
- Local 8061 operator packet present: True

## What is not implemented yet

- Runtime Exocortex module complete: false
- Automatic memory governor: false
- Runtime Context Packet Builder: false
- Graph memory ingestion/retrieval policy: false
- Stale memory blocking runtime: false
- Micrographs: false
- Delta Matrix: false
- State Family: false
- Multi-LLM braid: false
- Solution Factory: false
- Multi-area dashboard: false

## GPT memory model

Memory is not a single flat domain. GPT memory is modeled as a family of domains under:

```text
GPT_MEMORY_MESH_DOMAIN
```

Domains:

- `GPT_MEMORY_MESH_DOMAIN` - Root domain for GPT/Codex/agent memory as governed operational mesh.
- `SESSION_CONTEXT_DOMAIN` - Current session context; useful but not canonical unless triaged.
- `PROJECT_CANONICAL_MEMORY_DOMAIN` - Frozen definitions, accepted decisions and current project state.
- `USER_OPERATIONAL_PREFERENCE_DOMAIN` - Operator workflow preferences and execution style.
- `EVIDENCE_MEMORY_DOMAIN` - Memory backed by artifacts, outputs, commits, tags and reports.
- `CLAIM_BOUNDARY_MEMORY_DOMAIN` - Allowed and blocked claims, especially client/production/commercial limits.
- `ROADMAP_MEMORY_DOMAIN` - Current phase, next phase, roadmap dependencies and allowed progression.
- `CODE_EXECUTION_MEMORY_DOMAIN` - Commands, patchers, checks, apply results, commits, tags and validation outputs.
- `GRAPH_STATE_MEMORY_DOMAIN` - Neo4j-backed live operational state: cases, domains, evidence, gates, outputs and relationships.
- `CONCEPT_ONTOLOGY_MEMORY_DOMAIN` - Canonical definitions: Exocortex, state, memory, evidence, cache, gate, delta, point zero.
- `CACHE_TRANSIENT_DOMAIN` - Temporary context useful for execution but not canonical source of truth.
- `STALE_OR_SUPERSEDED_MEMORY_DOMAIN` - Outdated, corrected or superseded memory retained for audit but not injected as current truth.
- `RUNTIME_CONTEXT_PACKET_DOMAIN` - Clean minimum context packet delivered to GPT/Codex/agent for a specific task.

## Boundary

This addendum does not authorize client-facing claims, production activation, commercial claims, micrograph runtime claims, Delta Matrix runtime claims, state-family runtime claims or multi-LLM braid runtime claims.

## Next

PROD-8101..8140 - Internal Demo Script and Agent Instruction Pack

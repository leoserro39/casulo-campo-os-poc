# PROD-1181..1220 Umbrella Train Audit and Stack Roadmap Prep

- Status: `PASS`
- Train: `PROD-1021..1180`
- Umbrella train closed: `True`
- Final train decision: `READY_FOR_UMBRELLA_TRAIN_AUDIT_AND_COMMIT`
- Readiness: `READY_FOR_NEO4J_SANDBOX_GAIN_TEST_AND_LLM_CODEX_BOUNDARY_TRAIN`

## Core Architecture Answer

Codex is the repo implementation agent, not the runtime business executor.

The runtime decision path is:

Input -> Preflight -> Evidence retrieval / Graph retrieval -> Research LLM when allowed -> Diagnostic LLM -> Verifier LLM -> Cubo gates -> Output mode -> Human review when required -> Tool executor only if allowlisted.

## Neo4j Technical Gain Hypothesis

Neo4j should improve multi-hop traceability, graph retrieval, evidence-to-gate explanation and audit/demo power.

## Remaining Roadmap

- 1 focused package to first Neo4j sandbox import.
- 3 focused packages to measure Neo4j technical gain.
- 1 focused package to harden Codex/LLM executor boundary.
- One more umbrella train for a safe full-stack demo.

## Next Train

`PROD-1221..1380 — Neo4j Sandbox Gain Test + LLM Research Boundary + Codex Executor Boundary`

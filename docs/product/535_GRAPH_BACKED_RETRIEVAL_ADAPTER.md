# PROD-1341..1380 - Graph-Backed Retrieval Adapter

This phase creates a read-only adapter that retrieves operational state from the Neo4j sandbox graph.

It does not generate final answers.
It does not call GPT.
It does not call Codex.
It does not connect to production.
It does not authorize client-facing claims.

## Purpose

Given a human query or operational intent, the adapter retrieves a controlled graph context packet from the CASULO Neo4j sandbox.

The packet can later be used by GPT, Actions, Codex or a runtime API, but only after human-approved gates.

## Retrieval Scope

- Case
- Domain
- Evidence
- RiskSignal
- Gate
- OutputMode
- HallucinationBudget
- ReadinessState

## Safety

This is sandbox-only and read-only.

# PROD-1381..1420 - Graph Context API Endpoint

This phase exposes the graph-backed retrieval adapter through a local read-only HTTP API.

It does not call GPT.
It does not call Codex.
It does not connect to production.
It does not authorize client-facing claims.

## Purpose

Provide a local endpoint that returns a controlled graph context packet from Neo4j sandbox.

This prepares the system for a future Custom GPT / Actions integration.

## Endpoints

- GET /api/health
- GET /api/graph/context?query=missing%20evidence%20human%20review&limit=8

## Safety

Sandbox-only.
Read-only.
No final answer generation.
No production connection.

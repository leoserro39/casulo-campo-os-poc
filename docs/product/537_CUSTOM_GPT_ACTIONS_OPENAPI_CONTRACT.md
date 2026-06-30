# PROD-1421..1460 - Custom GPT Actions OpenAPI Contract

This phase creates an OpenAPI contract for a future Custom GPT Action that can call the CASULO Graph Context API.

It does not publish the API.
It does not call GPT.
It does not call Codex.
It does not connect to production.
It does not authorize client-facing claims.

## Purpose

Prepare a controlled OpenAPI contract so a future Custom GPT can request graph-backed context packets.

## Target Endpoint

- GET /api/graph/context

## Expected Query Parameters

- query: human query or operational intent
- limit: maximum number of context records

## Safety Boundary

The action is context retrieval only.

It must not:
- generate final answers by itself;
- execute Codex;
- mutate repository files;
- connect to production;
- handle credentials;
- authorize external use.

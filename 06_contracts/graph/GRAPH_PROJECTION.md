# CASULO Campo OS - Graph Projection

## Purpose

The Graph Projection publishes CASULO Campo OS repo artifacts as graph-ready nodes and edges.

## Rule

Git remains the source of truth.
The graph is a derived projection.
The graph must not mutate canonical state.

## Initial node types

- repo
- milestone
- artifact
- branch
- gate
- decision
- measurement
- sync_candidate

## Initial edge types

- PRODUCED
- DERIVED_FROM
- APPLIES_TO
- BLOCKED_BY
- REQUIRES_REVIEW
- SYNCS_TO
- MEASURED_BY
- DECIDED_BY

## Safety

Graph projection is read-only.
Neo4j or any other graph database must import from this projection.
No graph database is allowed to become canonical state in this POC.

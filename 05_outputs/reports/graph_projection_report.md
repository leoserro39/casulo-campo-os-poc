# CASULO Campo OS - Graph Projection Report

- generated_utc: 2026-06-25T20:25:05.175943+00:00
- status: GRAPH_PROJECTION
- source_of_truth: git
- canonical_effect: NONE
- commit: 28cecca
- node_count: 21
- edge_count: 29
- projection: 05_outputs/graph_projection/casulo_graph_projection.json

## Node types

- artifact
- branch
- gate
- milestone
- repo

## Edge types

- APPLIES_TO
- BLOCKED_BY
- DECIDED_BY
- MEASURED_BY
- PRECEDES
- PRODUCED
- SUMMARIZES
- SYNCS_TO

## Safety

- Graph projection is derived from repo artifacts.
- No canonical state was changed.
- Neo4j import, when added, must use this projection as input.

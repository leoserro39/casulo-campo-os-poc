# CASULO Campo OS - Legacy Source Intake Model

Legacy systems, spreadsheets, APIs, exports, documents and operational records must not be treated as automatic truth.

Consulting baseline mapping must cover:
- system name
- source type
- owner
- update frequency
- access method
- export format
- API availability
- critical fields
- known data quality issues
- operational dependency
- trust level
- privacy/security constraints
- target canonical branch
- expected evidence value

Intake flow:
source
-> source manifest
-> raw snapshot
-> source trust assessment
-> canonical mapping
-> sanity gate
-> evidence ledger
-> branch delta
-> canonical state only after validation

Rules:
- Do not ingest a legacy source directly into canonical state.
- Do not treat source content as truth without trust assessment.
- Do not overwrite branch state without a validated delta.
- Preserve raw snapshots.
- Preserve source ownership.
- Preserve mapping rationale.
- Record contradictions.
- Require human review when confidence is low.
- Use Git as source of truth for contracts, mappings and decisions.
- Use graph, RAG and Neo4j only as derived projections.

Every generated proposal or decision should expose:
- sources used
- source trust
- support ratio
- missing ratio
- contradiction count
- evidence strength
- Delta_L
- H_pre
- gate
- hallucination risk

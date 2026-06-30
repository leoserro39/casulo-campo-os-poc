# PROD-2061..2100 - Operational Hallucination Risk Index & Ranking Model

This phase creates the first Operational Hallucination Risk Index.

It ranks operational hallucination failure modes by expected risk and benchmark priority.

This phase is not calibration.
It is a heuristic prioritization model based on the exploratory failure mode matrix.

## Purpose

The failure mode matrix answers:

- What kinds of operational hallucination exist?

The risk index answers:

- Which failure modes are more dangerous?
- Which ones are more likely to produce plausible but wrong output?
- Which ones need CASULO controls first?
- Which benchmark should be built next?

## Index name

Operational Hallucination Risk Index (OHRI)

Portuguese name:

Índice de Risco de Alucinação Operacional (IRAO)

## Scoring dimensions

Each failure mode is scored from 0 to 100 across operational dimensions:

- prompt_ambiguity_score
- artifact_dependency_score
- schema_absence_score
- repo_state_dependency_score
- evidence_gap_score
- gate_absence_score
- external_side_effect_score
- client_claim_risk_score
- production_risk_score
- automation_execution_risk_score
- validation_gap_score
- context_contamination_risk_score

## Interpretation

- 85-100: critical
- 70-84: high
- 50-69: medium
- 30-49: low
- 0-29: minimal

## Boundary

This model is heuristic.
It does not prove measured hallucination rates.
It does not use real client data.
It does not approve thresholds.
It does not authorize GPT calls, Codex, automatic merge, production activation or client-facing claims.

## Expected use

The ranking should guide which benchmark to build first.

Expected high-priority benchmark:

Parser Grounding Benchmark

Rationale:

Generic parser generation can produce code that compiles but silently invents file structure, sheets, columns, schema and validation behavior.

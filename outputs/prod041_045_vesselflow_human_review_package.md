# PROD-041..045 VesselFlow Human Review Package

- Status: `PASS`
- Vertical: `vesselflow`
- Case: `vesselflow_demo_controlled_001`
- Decision: `BLOCKED_WAITING_FOR_REAL_OR_ANONYMIZED_DATA`
- Reason: Real/anonymized evidence is not yet ready for write/rerun.

## State Summary
- data_mode: `sample_placeholder`
- state_decision: `WAITING_FOR_REAL_DATA_OR_HUMAN_REVIEW`
- risk_level: `HIGH`

## Evidence Status Counts
- `SAMPLE_PLACEHOLDER`: `1`
- `AVAILABLE`: `3`
- `NOT_PROVIDED`: `6`

## Gate Status Counts
- `BLOCKED_SAMPLE_DATA`: `6`
- `REQUIRED`: `1`

## Review Items
- `data_source`: `BLOCKED` — Current state is still sample placeholder until reviewed real/anonymized data is written and rerun.
- `evidence_manifest`: `CHECK_REQUIRED` — Review evidence status counts and missing/not provided records.
- `gate_matrix`: `BLOCKED` — Gate movement cannot authorize execution without human approval.
- `risk_fragility`: `HIGH_ATTENTION` — Risk remains high while evidence is placeholder/missing.
- `external_use`: `BLOCKED` — No client-facing claim or production activation is allowed.

## Required Human Decisions
- Confirm whether real/anonymized VesselFlow data can be used internally.
- Confirm whether evidence is sufficient for a controlled demo.
- Confirm whether gates may move from BLOCKED_SAMPLE_DATA to CHECK_REQUIRED.
- Confirm no automatic nomination or external use will be executed.

## Allowed Next Actions
- Prepare reviewed real/anonymized intake JSON.
- Run intake --check.
- If approved, run explicit --write --rerun-state.
- Regenerate report export and evidence comparator.

## Blocked Actions
- `automatic_nomination`
- `client_facing_claim`
- `implementation_execution`
- `production_activation`

## Internal Use

This package is for internal controlled review only.

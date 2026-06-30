# PROD-1941..1980 - Manual Capture Intake Validator and Empty Batch Contract

This phase creates a validator for manual real GPT response intake batches.

It also creates an empty intake batch contract.

It does not require real GPT responses yet.
It does not connect GPT.
It does not call GPT.
It does not call Codex.
It does not approve thresholds.
It does not approve final weights.
It does not authorize client-facing claims.

## Purpose

Before manually captured real GPT responses are added, the repository must have a strict intake validator.

The validator checks:

- batch metadata;
- capture modes;
- prompt fields;
- raw response fields;
- context packet references;
- anonymization flags;
- sensitive/client-data flags;
- human review status;
- calibration eligibility;
- exclusion reasons.

## Empty batch

The empty batch is valid.

It proves the intake format is ready while confirming that there are no real captures yet.

An empty batch must not be calibration eligible.

## Boundary

No real GPT response is required in this phase.
No final calibration is allowed.
Manual capture remains the only approved capture path.

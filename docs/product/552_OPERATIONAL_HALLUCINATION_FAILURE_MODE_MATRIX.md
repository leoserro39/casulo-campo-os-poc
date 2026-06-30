# PROD-2021..2060 - Operational Hallucination Failure Mode Matrix

This phase records the exploratory discovery that the main CASULO value is not merely proving that a pure model always hallucinates.

The stronger thesis is:

A model may answer prudently and plausibly, but still fail operationally when it lacks the real state, schema, repository context, evidence contract, gate, blocked actions, validation output and permitted next action.

## Purpose

Map the main operational hallucination failure modes observed or expected in CASULO Campo OS.

This is an exploratory matrix.
It is not calibration.
It is not a benchmark result yet.
It does not use real client data.
It does not approve thresholds.
It does not authorize Codex, merge, production activation or client-facing claims.

## Key distinction

RAG can improve retrieved context.

CASULO must govern action.

RAG asks:
- what information is relevant?

CASULO asks:
- what is the current operational state?
- which gate applies?
- what evidence exists?
- which actions are blocked?
- what output mode is allowed?
- what validation must pass?
- which human review is required?

## Git and Codex distinction

Git versions changes.
Codex or coding agents can implement changes when authorized.
CASULO decides whether a change is allowed, what contract it must respect, what evidence is required, which gates block execution, and when human review is mandatory.

## Priority insight

Parser failures are a high-value benchmark target.

A generic parser may compile and still be operationally wrong if it invents sheets, columns, field names, validation rules, mappings, outputs or assumptions not present in the real workbook/schema.

## Boundary

This phase records failure modes and candidate benchmark families only.
It does not create real benchmark scores.
It does not convert exploratory responses into calibration evidence.

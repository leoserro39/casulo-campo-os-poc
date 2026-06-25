# CASULO Campo OS - Real World Test Protocol

## Purpose

This protocol defines how CASULO Campo OS should be tested with real operational data.

## Current release

- release: v1.7-orchestration-contract
- tag: v1.7-orchestration-contract

## Test principle

Real data is evidence.
Real data is not automatically canonical truth.

## First recommended real test

Domain:

- atendimento

Use case:

- WhatsApp atendimento pilot

Goal:

- test whether CASULO can ingest real atendimento evidence
- detect trust gaps, missing fields and contradictions
- propose a small operational improvement
- require human review
- measure pilot results
- block promotion until explicit decision

## Allowed real source types

- CSV export from WhatsApp/CRM/helpdesk
- spreadsheet of atendimento events
- sanitized message log
- manually curated sample
- API export snapshot

## Minimum recommended fields

- record_id
- created_at
- channel
- contact_id_hash
- direction
- message_or_event_type
- status
- response_time_minutes
- resolved_status
- notes

## Sensitive data rule

Do not ingest raw personal data unless explicitly approved.

Prefer:

- contact_id_hash instead of phone number
- redacted message text
- event categories instead of full messages
- aggregate evidence when enough

## Test gates

### Gate 1 - Source readiness

Check:

- source format is readable
- required fields are present or mapped
- PII risk is acceptable
- source trust is documented

### Gate 2 - Intake

Expected outputs:

- source manifest
- trust report
- hallucination risk signal
- intake delta

### Gate 3 - Proposal

Expected outputs:

- mesh delta
- gated proposal
- no automatic canonical mutation

### Gate 4 - Human review

Expected decisions:

- APPROVED
- REJECTED
- NEEDS_MORE_EVIDENCE

### Gate 5 - Pilot measurement

Expected measurements:

- total_conversations
- resolved_conversations
- unresolved_conversations
- conversations_without_resolved_status
- response_time_minutes

### Gate 6 - Promotion decision

Promotion remains blocked unless:

- enough measurements exist
- human decision is explicit
- promotion gate allows it

## Success criteria

The real test is successful if CASULO:

- reads real evidence without pretending certainty
- identifies missing fields and contradictions
- produces a small measurable proposal
- requires human review
- records pilot measurements
- blocks unsafe promotion
- preserves Git as source of truth

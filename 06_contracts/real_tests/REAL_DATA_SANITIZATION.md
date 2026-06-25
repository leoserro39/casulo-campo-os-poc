# CASULO Campo OS - Real Data Sanitization

## Purpose

Prepare real atendimento data for controlled CASULO testing without exposing sensitive personal data.

## Rule

Raw operational data must not enter the real test flow directly.

A sanitized CSV should be generated first.

## Output shape

The sanitized file should contain:

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

Do not preserve:

- phone numbers
- names
- emails
- raw message text
- customer identifiers

Prefer:

- hashed contact identifiers
- event types
- status fields
- response time
- redacted operational notes

## Canonical effect

NONE.

Sanitization only prepares evidence for readiness/intake gates.

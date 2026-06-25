# CASULO Campo OS - Real World Test Readiness

## Status

READY_FOR_CONTROLLED_REAL_TEST

## Current release

- v1.7-orchestration-contract

## Safe first test

- domain: atendimento
- use case: WhatsApp atendimento pilot
- data mode: sanitized CSV or spreadsheet export
- mutation mode: blocked by gates

## Required before ingesting real data

- confirm source owner
- confirm whether PII exists
- sanitize phone numbers, names and raw message content when possible
- preserve raw source snapshot separately if approved
- document source trust
- run intake before any proposal

## Recommended first real file

Use a CSV shaped like:

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

## Test rule

Do not upload sensitive raw customer data into chat.

Use local repo / controlled export when possible.
If sharing here, sanitize first.

## Next action

Prepare one small sanitized atendimento dataset with 20 to 100 rows and run source intake.

# Real Atendimento Test Source

## Purpose

This folder is reserved for the first controlled real-world atendimento test.

## Expected file

Preferred file name:

- atendimento_real_sanitized.csv

## Required shape

The CSV should contain:

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

## Safety rule

Do not place raw phone numbers, real names, emails or full sensitive message text here unless explicitly approved.

Prefer:

- hashed contact IDs
- event categories
- redacted notes
- aggregate or operational status fields

## First command

Run the readiness gate before any intake:

python 04_scripts/check_real_source_readiness.py \
  --source 00_inbox/sources/real_atendimento_test/atendimento_real_sanitized.csv \
  --source-name real_atendimento_test

## Expected gate

- READY_FOR_INTAKE

If the gate is:

- NEEDS_SANITIZATION: sanitize the file first
- NEEDS_MAPPING: map/rename columns first
- NEEDS_REVIEW: inspect data quality
- BLOCKED: do not ingest

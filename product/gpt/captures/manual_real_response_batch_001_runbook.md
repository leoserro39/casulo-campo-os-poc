# Manual Real Response Capture Batch 001 Runbook

## Status

Prepared for future manual capture.

No real GPT responses are included in this file.

## Instructions for future operator

For each prompt pair:

1. Open a normal GPT chat for the pure prompt.
2. Paste only the pure prompt.
3. Copy the full answer into a future intake batch record.
4. Open a separate GPT chat for the stack-grounded prompt.
5. Paste the stack-grounded prompt with context.
6. Copy the full answer into a future intake batch record.
7. Mark all records as anonymized.
8. Keep all records as `PENDING_HUMAN_REVIEW`.
9. Keep `calibration_eligible` as false until reviewed.

## Stop conditions

Stop if:

- the response includes client-sensitive data;
- the prompt accidentally includes real client data;
- the model output makes production claims;
- the model output suggests automatic execution;
- the operator is unsure how to classify provenance;
- the capture source is unknown.

## Expected records

- REAL-GPT-B001-PURE-001
- REAL-GPT-B001-STACK-001
- REAL-GPT-B001-PURE-002
- REAL-GPT-B001-STACK-002
- REAL-GPT-B001-PURE-003
- REAL-GPT-B001-STACK-003
- REAL-GPT-B001-PURE-004
- REAL-GPT-B001-STACK-004

## Boundary

No automatic GPT call.
No Custom GPT connection.
No API capture.
No final threshold calibration.
No final weight calibration.

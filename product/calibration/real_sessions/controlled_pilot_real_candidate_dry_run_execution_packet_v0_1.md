# Controlled Pilot Real Candidate Dry Run Execution Packet v0.1

Boundary: execution packet only. Do not execute real intake in this phase.

Manual execution preparation order:
1. Confirm readiness gate.
2. Assign human reviewer.
3. Open dry run shell and form.
4. Prepare source-reference placeholders only.
5. Prepare privacy, PII redaction and secret-scan placeholders.
6. Prepare evidence and boundary checklist placeholders.
7. Confirm no raw private data, secrets or unredacted PII.
8. Confirm claim boundary.
9. Confirm dataset acceptance hold.
10. Stop before any real candidate insert.

Abort if automatic capture, raw private data, secrets, unredacted PII, client-facing claim, production activation, real candidate insert or dataset acceptance is attempted.

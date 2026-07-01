# Controlled Pilot Real Candidate Intake Dry Run Shell v0.1

Boundary: dry run shell/template only.

This phase does not capture real session data, does not insert a real candidate and does not accept any candidate into the dataset.

Manual shell order:
1. Confirm prior dry run gate.
2. Confirm boundary review packet and checklist.
3. Confirm validator and schema.
4. Confirm real dataset remains empty.
5. Confirm reviewer queue remains empty.
6. Prepare source-reference placeholders only.
7. Prepare privacy, PII and secret-scan placeholders.
8. Prepare evidence packet placeholders.
9. Prepare reviewer notes placeholder.
10. Confirm claim boundary.
11. Hold dataset acceptance.

Abort if automatic capture, raw private data, secrets, unredacted PII, client-facing claim, production activation, commercial pricing claim or dataset acceptance is attempted.

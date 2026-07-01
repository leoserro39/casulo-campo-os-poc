# Controlled Real Session Pilot Execution Runbook v0.1

Boundary: manual controlled pilot execution only.

This runbook does not capture real session data by itself.

Execution rules:
1. Confirm manual controlled scope.
2. Assign a human reviewer.
3. Copy the candidate template.
4. Assign session_id.
5. Classify chat_layer and work_type.
6. Store source references only.
7. Redact PII before any storage.
8. Run secret scan before any storage.
9. Capture baseline vs CASULO Exocortex scores manually.
10. Score Apex, Value Delta, operational cost and hallucination risk.
11. Attach evidence pointers only.
12. Add human reviewer notes.
13. Apply dataset acceptance gate.
14. Accept, reject or hold candidate.

Abort immediately if raw private data, secrets, unredacted PII, automatic capture, missing reviewer, client-facing claim, production activation or commercial pricing claim appears.

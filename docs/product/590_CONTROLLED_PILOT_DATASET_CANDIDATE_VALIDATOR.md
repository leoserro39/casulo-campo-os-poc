# PROD-3541..3580 - Controlled Pilot Dataset Candidate Validator

Creates the validator for controlled pilot dataset candidates.

This phase does not capture real session data and does not accept candidates into the dataset.

A future candidate can enter calibration only when schema, source-ref-only capture, privacy review, PII redaction, secret scan, human reviewer notes, evidence packet refs, operator checklist, claim boundary and decision gate all pass.

Boundary: validator and empty validation batch only. No raw private data, secrets, unredacted PII, production activation or real-world/client-facing claim.

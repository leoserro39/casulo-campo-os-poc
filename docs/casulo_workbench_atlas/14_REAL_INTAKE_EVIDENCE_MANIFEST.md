# Real Intake and Evidence Manifest

TASK-WB-009 prepares the bridge from demo to controlled tests.

## Purpose

Before any controlled test, real or near-real data must be converted into controlled intake.

## Flow

```text
raw/client context
-> anonymization
-> real_intake.json
-> validate_real_intake.py
-> evidence_manifest.json
-> controlled case.json export
-> diagnostic engine
-> human review gate
```

## What this task enables

- controlled intake schema
- evidence manifest schema
- consent and scope checklist
- anonymization checklist
- source gate
- privacy gate
- export to diagnostic case only if not blocked

## What it does not allow

- uncontrolled real data
- raw personal data
- automatic implementation
- bypassing human review

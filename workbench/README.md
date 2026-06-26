# CASULO Workbench

Workbench v0.6 with human review gate for controlled diagnostics.

## Safe commands

```bash
python workbench/scripts/validate_workbench.py --strict
python workbench/scripts/run_controlled_diagnostic.py --intake workbench/real_cases/template/real_intake.json --check
python workbench/scripts/run_human_review_gate.py --intake workbench/real_cases/template/real_intake.json --check
```

## Explicit write

```bash
python workbench/scripts/run_human_review_gate.py --intake workbench/real_cases/template/real_intake.json --write --stable-time
```

## Gate rule

Controlled diagnostic output is not client-facing truth and cannot authorize implementation until human review explicitly approves the next step.

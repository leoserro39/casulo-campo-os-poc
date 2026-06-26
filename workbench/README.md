# CASULO Workbench

Workbench v0.7 with controlled test report pack.

## Safe commands

```bash
python workbench/scripts/validate_workbench.py --strict
python workbench/scripts/run_controlled_diagnostic.py --intake workbench/real_cases/template/real_intake.json --check
python workbench/scripts/run_human_review_gate.py --intake workbench/real_cases/template/real_intake.json --check
python workbench/scripts/build_controlled_test_report.py --intake workbench/real_cases/template/real_intake.json --check
```

## Explicit write

```bash
python workbench/scripts/build_controlled_test_report.py --intake workbench/real_cases/template/real_intake.json --write --stable-time
```

## Controlled test report

The report pack is internal/controlled by default. It does not authorize implementation.

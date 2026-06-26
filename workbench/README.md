# CASULO Workbench

Workbench v0.8 with full controlled test execution lane.

## Safe commands

```bash
python workbench/scripts/validate_workbench.py --strict
python workbench/scripts/execute_controlled_test.py --intake workbench/real_cases/template/real_intake.json --check
```

## Explicit write

```bash
python workbench/scripts/execute_controlled_test.py --intake workbench/real_cases/template/real_intake.json --write --stable-time
```

## Runtime outputs

Write mode generates artifacts under `workbench/runtime_outputs/`, which is ignored by Git.

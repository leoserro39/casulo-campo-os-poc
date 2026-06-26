# Controlled Test Execution

TASK-WB-013 executes the full controlled test lane.

## Flow

```text
real_intake
-> controlled_diagnostic write
-> human_review_gate write
-> controlled_test_report write
-> controlled_test_execution index
```

## Safe command

```bash
python workbench/scripts/execute_controlled_test.py --intake workbench/real_cases/template/real_intake.json --check
```

## Explicit runtime execution

```bash
python workbench/scripts/execute_controlled_test.py --intake workbench/real_cases/template/real_intake.json --write --stable-time
```

## Output policy

Artifacts are written to `workbench/runtime_outputs/` and remain ignored by Git.

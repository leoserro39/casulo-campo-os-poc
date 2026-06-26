# Controlled Test Execution Runbook

## Check mode

```bash
python workbench/scripts/execute_controlled_test.py --intake workbench/real_cases/template/real_intake.json --check
```

## Write mode

```bash
python workbench/scripts/execute_controlled_test.py --intake workbench/real_cases/template/real_intake.json --write --stable-time
```

## Expected runtime folders

- `workbench/runtime_outputs/controlled_diagnostics/<case_id>/`
- `workbench/runtime_outputs/human_review/<case_id>/`
- `workbench/runtime_outputs/controlled_test_reports/<case_id>/`
- `workbench/runtime_outputs/controlled_test_runs/<case_id>/`

## Rule

Runtime outputs are not source fixtures. Do not commit them unless a later promotion task explicitly approves it.

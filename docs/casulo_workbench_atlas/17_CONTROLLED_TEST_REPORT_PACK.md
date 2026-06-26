# Controlled Test Report Pack

TASK-WB-012 assembles the controlled test report.

## Flow

```text
real_intake
-> evidence_manifest
-> controlled_diagnostic
-> human_review_gate
-> controlled_test_report
```

## Rule

The report is internal/controlled by default and does not authorize implementation.

## Safe command

```bash
python workbench/scripts/build_controlled_test_report.py --intake workbench/real_cases/template/real_intake.json --check
```

## Explicit write

```bash
python workbench/scripts/build_controlled_test_report.py --intake workbench/real_cases/template/real_intake.json --write --stable-time
```

## Next step

WB-013 should package the first complete controlled test execution with write artifacts in runtime_outputs.

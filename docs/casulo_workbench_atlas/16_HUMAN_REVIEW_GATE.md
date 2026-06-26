# Human Review Gate

TASK-WB-011 adds the human review gate after controlled diagnostics.

## Rule

A controlled diagnostic is not client-facing truth and cannot authorize implementation by itself.

## Flow

```text
controlled_diagnostic_result
-> human_review_gate
-> internal review
-> more evidence / block / client review later
```

## Safe command

```bash
python workbench/scripts/run_human_review_gate.py --intake workbench/real_cases/template/real_intake.json --check
```

## Explicit write

```bash
python workbench/scripts/run_human_review_gate.py --intake workbench/real_cases/template/real_intake.json --write --stable-time
```

## Next step

WB-012 should create the first controlled test report pack.

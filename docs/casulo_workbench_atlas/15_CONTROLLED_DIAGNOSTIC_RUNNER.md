# Controlled Diagnostic Runner

TASK-WB-010 creates the runner for controlled tests.

## Flow

```text
real_intake.json
-> evidence_manifest.json
-> controlled_case.json
-> state_snapshot.json
-> graph.json
-> diagnostic_report.md
-> cockpit_state.json
-> codex_task.md
-> controlled_diagnostic_result.json
```

## Rule

This is not uncontrolled real production. It is the first controlled diagnostic lane.

## Safe command

```bash
python workbench/scripts/run_controlled_diagnostic.py --intake workbench/real_cases/template/real_intake.json --check
```

## Explicit write

```bash
python workbench/scripts/run_controlled_diagnostic.py --intake workbench/real_cases/template/real_intake.json --write --stable-time
```

## Next gate

WB-011 must add Human Review Gate for controlled diagnostics.

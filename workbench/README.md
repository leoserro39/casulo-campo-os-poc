# CASULO Workbench

Workbench v0.5 with controlled diagnostic runner.

## Safe commands

```bash
python workbench/scripts/validate_workbench.py --strict
python workbench/scripts/validate_real_intake.py --intake workbench/real_cases/template/real_intake.json
python workbench/scripts/build_real_case_from_intake.py --intake workbench/real_cases/template/real_intake.json --check
python workbench/scripts/run_controlled_diagnostic.py --intake workbench/real_cases/template/real_intake.json --check
python workbench/scripts/build_cockpit_state.py --case all --check
```

## Explicit write

```bash
python workbench/scripts/run_controlled_diagnostic.py --intake workbench/real_cases/template/real_intake.json --write --stable-time
```

## Controlled diagnostic flow

```text
real_intake
-> evidence_manifest
-> controlled_case
-> state_snapshot
-> graph
-> diagnostic_report
-> cockpit_state
-> codex_task
-> human_review
```

Human review is required before client-facing use.

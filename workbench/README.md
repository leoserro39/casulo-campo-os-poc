# CASULO Workbench

Workbench v0.4 with controlled real intake preparation.

## Safe commands

```bash
python workbench/scripts/validate_workbench.py --strict
python workbench/scripts/run_demo.py --case all --check
python workbench/scripts/export_codex_task.py --case all --check
python workbench/scripts/build_cockpit_state.py --case all --check
python workbench/scripts/validate_real_intake.py --intake workbench/real_cases/template/real_intake.json
python workbench/scripts/build_real_case_from_intake.py --intake workbench/real_cases/template/real_intake.json --check
```

## Explicit write

```bash
python workbench/scripts/build_real_case_from_intake.py --intake workbench/real_cases/template/real_intake.json --write --stable-time
```

## Real intake rule

Real or near-real data must pass through:

```text
real_intake
-> privacy/scope gate
-> evidence_manifest
-> controlled diagnostic case export
-> human review
```

Do not run uncontrolled raw client data.

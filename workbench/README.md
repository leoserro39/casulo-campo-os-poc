# CASULO Workbench

Workbench v0.3 para diagnostico de Estado Operacional e cockpit Cubo/Cupula.

## Runtime contracts

- `state_snapshot.contract.json`
- `graph.contract.json`
- `ledger_event.contract.json`
- `codex_task.contract.md`
- `cockpit_state.contract.json`

## Safe commands

```bash
python workbench/scripts/validate_workbench.py --strict
python workbench/scripts/run_demo.py --case all --check
python workbench/scripts/export_codex_task.py --case all --check
python workbench/scripts/build_cockpit_state.py --case all --check
```

## Explicit writes

```bash
python workbench/scripts/run_demo.py --case all --write --stable-time
python workbench/scripts/export_codex_task.py --case all --write --stable-time
python workbench/scripts/build_cockpit_state.py --case all --write --stable-time
```

## Cockpit

The UI-facing state is `cockpit_state`, a contracted projection generated from CASULO state artifacts.

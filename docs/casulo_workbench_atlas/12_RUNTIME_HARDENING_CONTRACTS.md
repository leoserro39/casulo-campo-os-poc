# Runtime Hardening and State Contracts

TASK-WB-007 hardens the Workbench runtime.

## Decisions

1. Check mode must not write outputs.
2. Write mode must be explicit.
3. Runtime outputs must be separated from canonical tracked fixtures.
4. State Snapshot, Graph, Ledger Event and Codex Task require contracts.
5. Cubo/Cupula must consume contracted state, not ad-hoc files.
6. Demos must be computable without dirtying the Git tree.

## Safe commands

```bash
python workbench/scripts/validate_workbench.py --strict
python workbench/scripts/run_demo.py --case all --check
python workbench/scripts/export_codex_task.py --case all --check
```

## Write commands

```bash
python workbench/scripts/run_demo.py --case all --write --stable-time
python workbench/scripts/export_codex_task.py --case all --write --stable-time
```

# CASULO Workbench — Product Architecture

## Current state

The controlled POC runs through scripts and outputs markdown/json artifacts.

## Target product architecture

```text
Frontend UI
  -> Product API
    -> Case Runtime Adapter
      -> Existing Workbench Services
        -> Outputs / Runtime Evidence
          -> Reports / Cube State / Replay / Timeline
```

## Recommended immediate architecture

- Keep existing workbench services.
- Add product adapters instead of rewriting core.
- Add API endpoints over current artifacts.
- Build a local UI reading API responses.
- Do not introduce database in the first product bundle unless required.

## Later architecture

- SQLite/Postgres adapter.
- User authentication.
- Cloud deployment.
- Case isolation.
- Permission model.
- Persistent ledger.
- Client review mode.
- Implementation handoff gate.

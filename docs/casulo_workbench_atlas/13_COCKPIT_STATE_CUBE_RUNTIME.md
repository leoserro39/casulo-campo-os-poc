# Cockpit State, Cubo and Cupula Runtime

TASK-WB-008 connects the Cubo/Cupula cockpit to contracted state.

## Decision

The frontend must not consume ad-hoc files. It consumes `cockpit_state`, a UI-facing projection built from:

- state_snapshot
- graph
- gates
- domains
- data quality
- fragility
- Codex task constraints

## Contract

`workbench/contracts/cockpit_state.contract.json`

## Runtime flow

```text
case.json
-> state_snapshot
-> graph
-> cockpit_state
-> Cubo/Cupula UI
```

## Cubo faces

1. objective
2. evidence
3. risks
4. tasks
5. deltas
6. gates

## Cupula

Ranks domains by operational gravity using data gaps, confidence gaps, risks and fragility.

## Safe command

```bash
python workbench/scripts/build_cockpit_state.py --case all --check
```

## Explicit write

```bash
python workbench/scripts/build_cockpit_state.py --case all --write --stable-time
```

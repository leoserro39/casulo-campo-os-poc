# CASULO Workbench — Data Model Draft

## Case

```json
{
  "case_id": "real_controlled_template_001",
  "title": "Real Controlled Intake Template",
  "status": "CONTROLLED_INTERNAL_POC_COMPLETE"
}
```

## Diagnostic

```json
{
  "data_quality": 0.627,
  "h_pre": 0.406,
  "h_post": 0.286,
  "delta_l": 0.12,
  "decision": "RECOMMEND_SMALLER_DELTA"
}
```

## Cube State

```json
{
  "metaphor": "operational_cube_solver",
  "principle": "Each cube move must correspond to evidence, gate, delta or state change.",
  "faces": {
    "objective": "...",
    "evidence": "...",
    "risk": "...",
    "tasks": "...",
    "deltas": "...",
    "gates": "..."
  }
}
```

## Gate

```json
{
  "ready_for_internal_review": true,
  "ready_for_client_review": false,
  "implementation_authorized": false
}
```

## Event

```json
{
  "event_id": "mg_evt_01",
  "phase": "intake_loaded",
  "gate": "PASS",
  "return_delta": "Controlled intake accepted for diagnostic lane."
}
```

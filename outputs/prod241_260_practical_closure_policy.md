# Practical Closure Policy

- contract_version: `casulo.practical_closure_policy.v0.1`
- status: `PASS`
- why: `The system must not analyze forever; graph synchronization must converge to action, review or block.`

## Closure States
- `READY_FOR_NEXT_ACTION`
- `ASK_FOR_EVIDENCE`
- `CREATE_MISSING_ARTIFACT_TASK`
- `HUMAN_REVIEW_REQUIRED`
- `PRODUCTION_BLOCKED`
- `NO_MATERIAL_DELTA_CHANGE`

## Stop Rules
- `max_iterations`
- `no_material_delta_change`
- `human_review_required`
- `production_blocked`

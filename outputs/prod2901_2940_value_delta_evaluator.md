# PROD-2901..2940 Value Delta Evaluator

- Status: `PASS`
- Decision: `VALUE_DELTA_EVALUATOR_READY`
- Fixtures: `12`
- Freeze allowed: `7`
- Blocked: `1`
- Provisional: `4`
- Freezable internal synthetic value: `2363.05`
- Total complexity-adjusted net delta: `2771.03`
- Average complexity: `50.0`
- Next: `PROD-2941..2980 - Value Delta Readiness Gate`

## Evaluated cases
- `VDF-001` `clean_internal_task_value_freeze` decision `FREEZE_INTERNAL_SYNTHETIC_DELTA` net `161.61` band `LOW_SYNTHETIC_VALUE`
- `VDF-002` `long_context_snapshot_resume` decision `FREEZE_INTERNAL_SYNTHETIC_DELTA` net `581.64` band `HIGH_SYNTHETIC_VALUE`
- `VDF-003` `context_waste_heavy_chat` decision `FREEZE_INTERNAL_SYNTHETIC_DELTA` net `365.18` band `MEDIUM_SYNTHETIC_VALUE`
- `VDF-004` `parser_missing_schema` decision `PROVISIONAL_DELTA_HOLD_CLAIM` net `44.39` band `LOW_SYNTHETIC_VALUE`
- `VDF-005` `client_claim_weak_evidence` decision `PROVISIONAL_DELTA_HOLD_CLAIM` net `26.48` band `LOW_SYNTHETIC_VALUE`
- `VDF-006` `ambiguous_architecture_prompt` decision `PROVISIONAL_DELTA_HOLD_CLAIM` net `139.1` band `LOW_SYNTHETIC_VALUE`
- `VDF-007` `garbage_in_blocks_value_delta` decision `BLOCK_VALUE_DELTA` net `0` band `NO_FREEZABLE_VALUE`
- `VDF-008` `contradiction_hold_avoids_wrong_work` decision `PROVISIONAL_DELTA_HOLD_CLAIM` net `198.01` band `LOW_SYNTHETIC_VALUE`
- `VDF-009` `stale_context_archived` decision `FREEZE_INTERNAL_SYNTHETIC_DELTA` net `280.26` band `MEDIUM_SYNTHETIC_VALUE`
- `VDF-010` `protected_canonical_decision` decision `FREEZE_INTERNAL_SYNTHETIC_DELTA` net `322.77` band `MEDIUM_SYNTHETIC_VALUE`
- `VDF-011` `high_rework_avoidance_task` decision `FREEZE_INTERNAL_SYNTHETIC_DELTA` net `488.88` band `MEDIUM_SYNTHETIC_VALUE`
- `VDF-012` `time_saved_simple_operational_loop` decision `FREEZE_INTERNAL_SYNTHETIC_DELTA` net `162.71` band `LOW_SYNTHETIC_VALUE`

## Boundary
- Synthetic evaluator only.
- No real-world savings/profit/ROI claim.

## Errors
- None

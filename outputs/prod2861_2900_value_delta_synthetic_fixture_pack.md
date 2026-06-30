# PROD-2861..2900 Value Delta Synthetic Fixture Pack

- Status: `PASS`
- Decision: `VALUE_DELTA_SYNTHETIC_FIXTURE_PACK_READY`
- Fixtures: `12`
- Themes: `13`
- Next: `PROD-2901..2940 - Value Delta Evaluator`

## Fixtures
- `VDF-001` `clean_internal_task_value_freeze` outcome `INPUT_ACCEPTED` decision `ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE` net `161.61` freeze `True`
- `VDF-002` `long_context_snapshot_resume` outcome `INPUT_ACCEPTED` decision `ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE` net `581.64` freeze `True`
- `VDF-003` `context_waste_heavy_chat` outcome `INPUT_ACCEPTED` decision `ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE` net `365.18` freeze `True`
- `VDF-004` `parser_missing_schema` outcome `SCHEMA_REQUIRED` decision `PROVISIONAL_ESTIMATE_ONLY_HOLD_CLAIM` net `44.39` freeze `False`
- `VDF-005` `client_claim_weak_evidence` outcome `EVIDENCE_REQUIRED` decision `PROVISIONAL_ESTIMATE_ONLY_HOLD_CLAIM` net `26.48` freeze `False`
- `VDF-006` `ambiguous_architecture_prompt` outcome `CLARIFICATION_REQUIRED` decision `PROVISIONAL_ESTIMATE_ONLY_HOLD_CLAIM` net `139.1` freeze `False`
- `VDF-007` `garbage_in_blocks_value_delta` outcome `BLOCK_EXECUTION` decision `BLOCK_VALUE_DELTA_CALCULATION` net `0` freeze `False`
- `VDF-008` `contradiction_hold_avoids_wrong_work` outcome `CLARIFICATION_REQUIRED` decision `PROVISIONAL_ESTIMATE_ONLY_HOLD_CLAIM` net `198.01` freeze `False`
- `VDF-009` `stale_context_archived` outcome `INPUT_ACCEPTED` decision `ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE` net `280.26` freeze `True`
- `VDF-010` `protected_canonical_decision` outcome `INPUT_ACCEPTED` decision `ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE` net `322.77` freeze `True`
- `VDF-011` `high_rework_avoidance_task` outcome `INPUT_ACCEPTED` decision `ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE` net `488.88` freeze `True`
- `VDF-012` `time_saved_simple_operational_loop` outcome `INPUT_ACCEPTED` decision `ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE` net `162.71` freeze `True`

## Boundary
- Synthetic internal fixture pack only.
- No real-world savings/profit claim.

## Errors
- None

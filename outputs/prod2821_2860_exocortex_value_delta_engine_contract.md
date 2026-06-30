# PROD-2821..2860 Exocortex Value Delta Engine Contract

- Status: `PASS`
- Decision: `EXOCORTEX_VALUE_DELTA_ENGINE_CONTRACT_READY`
- Components: `11`
- Synthetic cases: `6`
- Next: `PROD-2861..2900 - Value Delta Synthetic Fixture Pack`

## Evaluated cases
- `VD-001` `accepted_input_internal_task` decision `ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE` net `274.96` confidence `0.82` freeze `True`
- `VD-002` `low_input_quality_value_delta_blocked` decision `BLOCK_VALUE_DELTA_CALCULATION` net `0` confidence `0.0` freeze `False`
- `VD-003` `schema_required_parser_task` decision `PROVISIONAL_ESTIMATE_ONLY_HOLD_CLAIM` net `150.4` confidence `0.35` freeze `False`
- `VD-004` `client_claim_weak_evidence_blocked` decision `PROVISIONAL_ESTIMATE_ONLY_HOLD_CLAIM` net `166.25` confidence `0.35` freeze `False`
- `VD-005` `clarification_required_architecture_task` decision `PROVISIONAL_ESTIMATE_ONLY_HOLD_CLAIM` net `296.55` confidence `0.45` freeze `False`
- `VD-006` `memory_state_preserved_after_snapshot` decision `ALLOW_INTERNAL_SYNTHETIC_VALUE_ESTIMATE` net `804.44` confidence `0.82` freeze `True`

## Boundary
- Internal synthetic estimate only.
- No real-world profit or validated savings claim.

## Errors
- None

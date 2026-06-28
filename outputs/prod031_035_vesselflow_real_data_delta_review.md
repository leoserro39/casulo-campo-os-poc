# PROD-031..035 VesselFlow Real Data Delta Review

- Status: `PASS`
- Case: `vesselflow_demo_controlled_001`
- Internal use only: `True`

## Before
- data_mode: `sample_placeholder`
- decision: `WAITING_FOR_REAL_DATA_OR_HUMAN_REVIEW`
- risk_level: `HIGH`

## After Candidate
- intake_status: `WAITING_FOR_USER_DATA`
- data_classification: `synthetic`
- validation_status: `PASS`
- dataset_status: `WAITING_FOR_USER_DATA`
- dataset_reference: `REPLACE_WITH_REAL_OR_ANONYMIZED_WORKBOOK_OR_DATASET`

## Delta
- data_mode_change: `sample_placeholder -> WAITING_FOR_USER_DATA`
- risk_change_expected: `NO_REDUCTION_YET_WAITING_FOR_DATA`
- gate_change_expected: `NO_GATE_CHANGE_YET`
- evidence_change_expected: `DATASET_REFERENCE_NOT_READY`
- ready_for_write_rerun: `False`

## Warnings
- dataset_reference.path_or_reference still looks like a placeholder

## Errors
- None

## Next Controlled Actions
- Fill a reviewed real/anonymized VesselFlow intake JSON.
- Run prepare_vesselflow_real_data_intake.py --check.
- If PASS and reviewed, run --write --rerun-state.
- Regenerate report export.
- Review gates before any external use.

## Blocked Actions
- `automatic_nomination`
- `client_facing_claim`
- `implementation_execution`
- `production_activation`

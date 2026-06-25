# CASULO Campo OS - Real Test Mode Snapshot

## Status

READY_FOR_MORE_REAL_CONTROLLED_CYCLES

## Current state

CASULO Campo OS now supports a controlled real-world test flow for atendimento evidence.

## Completed real-test gates

- Gate 1: real source readiness
- Gate 2: real source intake evidence-only
- Gate 3: real evidence proposal
- Gate 4: real human review
- Gate 5: real pilot measurement
- Gate 6: real promotion decision

## Safety guarantees

- Git remains the source of truth.
- Real data is evidence, not automatic truth.
- PII readiness check runs before intake.
- Intake is evidence-only.
- Proposals require human review.
- Pilot measurements do not promote state.
- Promotion decision does not mutate branch state.
- Promotion decision can be filtered by measurement prefix/cycle.
- Runner executes the cycle but keeps gated outputs only.

## Current known decisions

- real_atendimento_sample_cycle_001: EXTEND_PILOT
- Reason: positive signal exists, but more measurements are required.
- Promotion execution allowed: false.
- Canonical effect: NONE.

## Current tools

- 04_scripts/check_real_source_readiness.py
- 04_scripts/run_real_source_intake.py
- 04_scripts/run_real_evidence_proposal.py
- 04_scripts/run_real_human_review.py
- 04_scripts/run_real_pilot_measurement.py
- 04_scripts/run_real_promotion_decision.py
- 04_scripts/build_real_test_cycle_snapshot.py
- 04_scripts/run_real_test_cycle.py

## Next real step

Add a real sanitized CSV at:

00_inbox/sources/real_atendimento_test/atendimento_real_sanitized.csv

Then run:

python 04_scripts/run_real_test_cycle.py \
  --source 00_inbox/sources/real_atendimento_test/atendimento_real_sanitized.csv \
  --source-name real_atendimento_cycle_002 \
  --cycle-name real_atendimento_cycle_002 \
  --reviewer leoserro39 \
  --min-measurements 3

## Data rule

Do not commit or upload sensitive raw personal data.

Use sanitized CSV with:

- contact_id_hash
- operational event types
- status
- resolved_status
- response_time_minutes
- redacted notes

## Promotion rule

At least 3 cycle-filtered measurements are required before a promotion candidate can be considered.

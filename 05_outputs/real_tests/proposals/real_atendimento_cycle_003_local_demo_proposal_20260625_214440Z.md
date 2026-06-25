# CASULO Campo OS - Real Evidence Proposal

- status: REAL_EVIDENCE_PROPOSAL
- generated_utc: 20260625_214440Z
- proposal_name: real_atendimento_cycle_003_local_demo_proposal
- source: 00_inbox/sources/real_atendimento_test/atendimento_real_sanitized.csv
- proposal_gate: PROPOSAL_REQUIRES_HUMAN_REVIEW
- requires_human_review: true
- canonical_effect: NONE
- trust_score: 0.947
- hallucination_risk: MEDIUM
- Delta_L: 0.437
- H_pre: 0.27

## Evidence summary

- row_count: 13
- contact_count: 8
- resolved_rows: 6
- unresolved_rows: 6
- unknown_status_rows: 1
- avg_response_time_minutes: 8.57
- trust_score: 0.947
- hallucination_risk: MEDIUM
- Delta_L: 0.437
- H_pre: 0.27

## Proposed actions

- standardize_status_taxonomy: Use only new_contact, waiting_confirmation and resolved as the first controlled atendimento statuses.
- create_daily_unresolved_queue: Create a daily queue for unresolved conversations and contacts waiting for confirmation.
- measure_first_response_time: Keep recording response_time_minutes for every first response event.
- require_resolved_status: Every atendimento record should carry resolved, unresolved or waiting_confirmation status.
- set_initial_response_time_watch: Use the current average response time as baseline and watch it during the next pilot cycle.

## Human review questions

- Does the status taxonomy match the real atendimento operation?
- Is it acceptable to use this dataset as pilot evidence?
- Should unknown status records be corrected before the next pilot cycle?
- Who owns the daily unresolved queue?
- What response time target should be used for the next cycle?

## Next action

- Send this proposal to human review. Do not mutate branch state automatically.

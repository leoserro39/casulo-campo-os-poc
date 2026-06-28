# Issue-to-State Linkage Readiness

- contract_version: `casulo.issue_to_state_linkage_readiness.v0.1`
- status: `PASS`
- decision: `READY_FOR_CLOSURE_LEDGER_REVIEW_PENDING_MANUAL_URLS`
- record_count: `2`
- pending_manual_creation_count: `2`
- created_manually_ready_to_link_count: `0`
- manual_issue_url_present_count: `0`
- auto_execution_allowed: `False`

## Ready For
- `closure ledger review`
- `manual issue URL evidence insertion`
- `pending state tracking`

## Not Ready For
- `automatic issue creation`
- `automatic closure`
- `production activation`
- `external client claims`
- next: `When a human provides a manual issue URL, re-run evidence capture and linkage to move records toward CREATED_MANUALLY.`

## Blocked Actions
- `client_facing_claim`
- `automatic_nomination`
- `implementation_execution`
- `production_activation`
- `automatic_merge`
- `credential_handling`

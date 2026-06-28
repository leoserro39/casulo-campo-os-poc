# PROD-421..440 Issue-to-State Linkage and Closure Ledger

- Status: `PASS`
- Records: `2`
- Manual issue URLs present: `0`
- Pending manual creation: `2`
- Created manually ready to link: `0`
- Evidence incomplete: `0`
- Auto execution allowed: `False`

## Records
- `REAL-GRAPH-001-ONBOARDING-ISSUE-CANDIDATE-002` → `PENDING_MANUAL_ISSUE_CREATION` / target `APPROVED_FOR_MANUAL_CREATE` / next `wait_for_manual_issue_url_evidence`
- `REAL-GRAPH-002-DOCUMENT-AUDIT-ISSUE-CANDIDATE-002` → `PENDING_MANUAL_ISSUE_CREATION` / target `APPROVED_FOR_MANUAL_CREATE` / next `wait_for_manual_issue_url_evidence`

## Policy
- No issue URL is invented.
- No state is closed without evidence.
- Pending manual creation is a valid closure interim state.
- Manual issue URL evidence is required before CREATED_MANUALLY linkage.
- Automatic execution remains disabled.

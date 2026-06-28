# PROD-401..420 Manual Issue Creation Evidence Capture

- Status: `PASS`
- Approved count: `2`
- Captured count: `0`
- Pending count: `2`
- Incomplete count: `0`
- Auto execution allowed: `False`

## Evidence Manifest
`product/poc/manual_issue_creation_evidence/manual_issue_evidence_manifest.json`

## Validation Results
- `REAL-GRAPH-001-ONBOARDING-ISSUE-CANDIDATE-002` → `APPROVED_PENDING_MANUAL_CREATION` / `no_url_yet_pending_manual_creation`
- `REAL-GRAPH-002-DOCUMENT-AUDIT-ISSUE-CANDIDATE-002` → `APPROVED_PENDING_MANUAL_CREATION` / `no_url_yet_pending_manual_creation`

## How to capture evidence after manual creation
1. Create the GitHub issue manually outside this workflow.
2. Copy the GitHub issue URL.
3. Edit the evidence manifest and fill `manual_issue_url`, `created_by`, `created_at`, and `evidence_note`.
4. Re-run `python product/scripts/run_manual_issue_creation_evidence_capture.py --repo .`.
5. Confirm `captured_count` increased and `auto_execution_allowed` is still `false`.

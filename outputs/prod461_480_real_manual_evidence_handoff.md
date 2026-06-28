# PROD-461..480 Real Manual Evidence Handoff Pack

- Status: `PASS`
- Candidate count: `2`
- Valid real evidence count: `0`
- Pending real manual URL count: `2`
- Synthetic rejected count: `0`
- Auto execution allowed: `False`
- Network validation performed: `False`

## Validation Results
- `REAL-GRAPH-001-ONBOARDING-ISSUE-CANDIDATE-002` → `PENDING_REAL_MANUAL_URL` / `no_real_manual_issue_url_yet`
- `REAL-GRAPH-002-DOCUMENT-AUDIT-ISSUE-CANDIDATE-002` → `PENDING_REAL_MANUAL_URL` / `no_real_manual_issue_url_yet`

## Handoff Checklist
- Confirm a human manually created the issue in GitHub.
- Copy the real GitHub issue URL.
- Paste it into product/poc/real_manual_evidence_handoff/real_manual_evidence_manifest.json.
- Fill created_by, created_at and evidence_note.
- Confirm synthetic is false.
- Re-run product/scripts/run_real_manual_evidence_handoff.py --repo .
- Proceed only if status becomes VALID_REAL_MANUAL_EVIDENCE_READY_TO_LINK for that issue.

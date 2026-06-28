# PROD-361..380 Formal Approval Workflow Runbook

This runbook does not execute GitHub commands.

## Current Guard
- Manual only: `True`
- Auto execution allowed: `False`
- Selected count: `12`
- Approved count: `0`
- Created manually count: `0`
- Invalid transition count: `0`

## Approval Steps
1. Edit `product/poc/formal_approval_workflow/formal_approval_manifest.json`.
2. For an approved candidate, set `requested_state` to `APPROVED_FOR_MANUAL_CREATE`.
3. Fill `approver` and `approval_note`.
4. Re-run `python product/scripts/run_formal_approval_workflow.py --repo .`.
5. Copy approved command manually from the approved queue.
6. After creating the issue manually, set `requested_state` to `CREATED_MANUALLY` and fill `manual_issue_url`.

## Approved Manual Commands
No approved commands yet. This is expected until the approval manifest is edited.

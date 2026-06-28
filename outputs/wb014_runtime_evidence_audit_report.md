# Runtime Evidence Audit - real_controlled_template_001

- Status: `PASS`
- Runtime root: `workbench/runtime_outputs`
- Files checked: `17`
- Commit policy: Do not commit workbench/runtime_outputs. Commit only this audit report/result.

## Summaries
### diagnostic
- `status`: `PASS`
- `manifest_decision`: `ALLOW_CONTROLLED_DIAGNOSTIC`
- `data_quality`: `0.627`
- `h_pre`: `0.406`
- `h_post`: `0.286`
- `delta_l`: `0.12`
- `decision`: `RECOMMEND_SMALLER_DELTA`
- `human_review_required`: `True`

### human_review
- `review_status`: `PENDING_HUMAN_REVIEW`
- `decision`: `PENDING_HUMAN_REVIEW`
- `review_required`: `True`
- `blocked_next_actions`: `['client_facing_claim', 'implementation_execution', 'production_activation']`

### controlled_report
- `status`: `PASS`
- `human_review_decision`: `PENDING_HUMAN_REVIEW`
- `ready_for_internal_review`: `True`
- `ready_for_client_review`: `False`
- `implementation_authorized`: `False`

### execution
- `status`: `PASS`
- `mode`: `write`
- `next_gate`: `Manual review of runtime report pack before any external use.`
- `steps`: `{'controlled_diagnostic': {'status': 'PASS', 'decision': 'RECOMMEND_SMALLER_DELTA', 'generated_outputs': ['/workspaces/casulo-campo-os-poc/workbench/runtime_outputs/controlled_diagnostics/real_controlled_template_001/evidence_manifest.json', '/workspaces/casulo-campo-os-poc/workbench/runtime_outputs/controlled_diagnostics/real_controlled_template_001/controlled_case.json', '/workspaces/casulo-campo-os-poc/workbench/runtime_outputs/controlled_diagnostics/real_controlled_template_001/state_snapshot.json', '/workspaces/casulo-campo-os-poc/workbench/runtime_outputs/controlled_diagnostics/real_controlled_template_001/graph.json', '/workspaces/casulo-campo-os-poc/workbench/runtime_outputs/controlled_diagnostics/real_controlled_template_001/cockpit_state.json', '/workspaces/casulo-campo-os-poc/workbench/runtime_outputs/controlled_diagnostics/real_controlled_template_001/controlled_diagnostic_result.json', '/workspaces/casulo-campo-os-poc/workbench/runtime_outputs/controlled_diagnostics/real_controlled_template_001/diagnostic_report.md', '/workspaces/casulo-campo-os-poc/workbench/runtime_outputs/controlled_diagnostics/real_controlled_template_001/codex_task.md', '/workspaces/casulo-campo-os-poc/workbench/runtime_outputs/controlled_diagnostics/real_controlled_template_001/ledger.jsonl']}, 'human_review_gate': {'status': 'PASS', 'decision': 'PENDING_HUMAN_REVIEW', 'review_status': 'PENDING_HUMAN_REVIEW', 'generated_outputs': ['/workspaces/casulo-campo-os-poc/workbench/runtime_outputs/human_review/real_controlled_template_001/human_review_gate.json', '/workspaces/casulo-campo-os-poc/workbench/runtime_outputs/human_review/real_controlled_template_001/human_review_gate.md']}, 'controlled_test_report': {'status': 'PASS', 'human_review_decision': 'PENDING_HUMAN_REVIEW', 'ready_for_internal_review': True, 'ready_for_client_review': False, 'implementation_authorized': False, 'generated_outputs': ['/workspaces/casulo-campo-os-poc/workbench/runtime_outputs/controlled_test_reports/real_controlled_template_001/controlled_test_result.json', '/workspaces/casulo-campo-os-poc/workbench/runtime_outputs/controlled_test_reports/real_controlled_template_001/controlled_test_report.md', '/workspaces/casulo-campo-os-poc/workbench/runtime_outputs/controlled_test_reports/real_controlled_template_001/executive_summary.md', '/workspaces/casulo-campo-os-poc/workbench/runtime_outputs/controlled_test_reports/real_controlled_template_001/next_actions.md']}}`

## Files
- `controlled_diagnostics/evidence_manifest.json`: `True` (1376 bytes)
- `controlled_diagnostics/controlled_case.json`: `True` (3760 bytes)
- `controlled_diagnostics/state_snapshot.json`: `True` (4092 bytes)
- `controlled_diagnostics/graph.json`: `True` (9719 bytes)
- `controlled_diagnostics/diagnostic_report.md`: `True` (979 bytes)
- `controlled_diagnostics/cockpit_state.json`: `True` (15317 bytes)
- `controlled_diagnostics/codex_task.md`: `True` (661 bytes)
- `controlled_diagnostics/ledger.jsonl`: `True` (515 bytes)
- `controlled_diagnostics/controlled_diagnostic_result.json`: `True` (1938 bytes)
- `human_review/human_review_gate.json`: `True` (2082 bytes)
- `human_review/human_review_gate.md`: `True` (1080 bytes)
- `controlled_test_reports/controlled_test_result.json`: `True` (2002 bytes)
- `controlled_test_reports/controlled_test_report.md`: `True` (1189 bytes)
- `controlled_test_reports/executive_summary.md`: `True` (286 bytes)
- `controlled_test_reports/next_actions.md`: `True` (153 bytes)
- `controlled_test_runs/controlled_test_execution_result.json`: `True` (3605 bytes)
- `controlled_test_runs/README.md`: `True` (936 bytes)

from __future__ import annotations

BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
]

ENDPOINT_GROUPS = [
    {
        "group": "runtime",
        "routes": [
            {"path": "/api/health", "kind": "health"},
            {"path": "/api/product/status", "kind": "status"},
            {"path": "/api/reports", "kind": "reports"},
        ],
    },
    {
        "group": "graph_case_review",
        "routes": [
            {"path": "/api/casulo/graph-case-review/console", "file": "outputs/prod321_340_review_console.json", "key": "review_console"},
            {"path": "/api/casulo/graph-case-review/selection", "file": "outputs/prod321_340_issue_selection.json", "key": "issue_selection"},
            {"path": "/api/casulo/graph-case-review/readiness", "file": "outputs/prod321_340_review_console_readiness.json", "key": "review_readiness"},
            {"path": "/api/casulo/graph-case-review/audit", "file": "outputs/prod321_340_audit_report.json", "key": "review_audit"},
        ],
    },
    {
        "group": "manual_issue_promotion",
        "routes": [
            {"path": "/api/casulo/manual-issue-promotion/pack", "file": "outputs/prod341_360_manual_issue_promotion.json", "key": "manual_issue_promotion"},
            {"path": "/api/casulo/manual-issue-promotion/manifest", "file": "outputs/prod341_360_approved_issue_manifest_snapshot.json", "key": "manifest"},
            {"path": "/api/casulo/manual-issue-promotion/commands", "file": "outputs/prod341_360_gh_issue_command_templates.md", "key": "commands_markdown", "kind": "markdown"},
            {"path": "/api/casulo/manual-issue-promotion/readiness", "file": "outputs/prod341_360_manual_issue_promotion_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/manual-issue-promotion/audit", "file": "outputs/prod341_360_audit_report.json", "key": "audit"},
        ],
    },
    {
        "group": "formal_approval",
        "routes": [
            {"path": "/api/casulo/formal-approval/report", "file": "outputs/prod361_380_formal_approval_report.json", "key": "formal_approval_report"},
            {"path": "/api/casulo/formal-approval/manifest", "file": "outputs/prod361_380_formal_approval_manifest_snapshot.json", "key": "approval_manifest"},
            {"path": "/api/casulo/formal-approval/ledger", "file": "outputs/prod361_380_state_transition_ledger.json", "key": "transition_ledger"},
            {"path": "/api/casulo/formal-approval/execution-guard", "file": "outputs/prod361_380_issue_execution_guard.json", "key": "execution_guard"},
            {"path": "/api/casulo/formal-approval/runbook", "file": "outputs/prod361_380_formal_approval_runbook.md", "key": "runbook", "kind": "markdown"},
            {"path": "/api/casulo/formal-approval/readiness", "file": "outputs/prod361_380_formal_approval_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/formal-approval/audit", "file": "outputs/prod361_380_audit_report.json", "key": "audit"},
        ],
    },
    {
        "group": "minimal_approved_dry_run",
        "routes": [
            {"path": "/api/casulo/minimal-approved-dry-run/plan", "file": "outputs/prod381_400_minimal_approval_plan.json", "key": "minimal_approval_plan"},
            {"path": "/api/casulo/minimal-approved-dry-run/manifest", "file": "outputs/prod381_400_dry_run_approval_manifest.json", "key": "dry_run_manifest"},
            {"path": "/api/casulo/minimal-approved-dry-run/ledger", "file": "outputs/prod381_400_dry_run_transition_ledger.json", "key": "dry_run_ledger"},
            {"path": "/api/casulo/minimal-approved-dry-run/execution-guard", "file": "outputs/prod381_400_execution_guard.json", "key": "execution_guard"},
            {"path": "/api/casulo/minimal-approved-dry-run/commands", "file": "outputs/prod381_400_approved_command_preview.md", "key": "commands_markdown", "kind": "markdown"},
            {"path": "/api/casulo/minimal-approved-dry-run/readiness", "file": "outputs/prod381_400_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/minimal-approved-dry-run/audit", "file": "outputs/prod381_400_audit_report.json", "key": "audit"},
        ],
    },
    {
        "group": "manual_issue_evidence",
        "routes": [
            {"path": "/api/casulo/manual-issue-evidence/manifest", "file": "outputs/prod401_420_manual_issue_evidence_manifest_snapshot.json", "key": "evidence_manifest"},
            {"path": "/api/casulo/manual-issue-evidence/capture", "file": "outputs/prod401_420_manual_issue_evidence_capture.json", "key": "evidence_capture"},
            {"path": "/api/casulo/manual-issue-evidence/url-validation", "file": "outputs/prod401_420_issue_url_validation.json", "key": "url_validation"},
            {"path": "/api/casulo/manual-issue-evidence/state-update-preview", "file": "outputs/prod401_420_state_update_preview.json", "key": "state_update_preview"},
            {"path": "/api/casulo/manual-issue-evidence/readiness", "file": "outputs/prod401_420_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/manual-issue-evidence/audit", "file": "outputs/prod401_420_audit_report.json", "key": "audit"},
        ],
    },
    {
        "group": "issue_state_linkage",
        "routes": [
            {"path": "/api/casulo/issue-state-linkage/records", "file": "outputs/prod421_440_issue_state_link_records.json", "key": "issue_state_link_records"},
            {"path": "/api/casulo/issue-state-linkage/closure-ledger", "file": "outputs/prod421_440_closure_ledger.json", "key": "closure_ledger"},
            {"path": "/api/casulo/issue-state-linkage/report", "file": "outputs/prod421_440_linkage_report.json", "key": "linkage_report"},
            {"path": "/api/casulo/issue-state-linkage/readiness", "file": "outputs/prod421_440_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/issue-state-linkage/audit", "file": "outputs/prod421_440_audit_report.json", "key": "audit"},
        ],
    },
    {
        "group": "closure_replay",
        "routes": [
            {"path": "/api/casulo/closure-replay/synthetic-url-manifest", "file": "outputs/prod441_460_synthetic_manual_url_manifest.json", "key": "synthetic_url_manifest"},
            {"path": "/api/casulo/closure-replay/ledger", "file": "outputs/prod441_460_closure_replay_ledger.json", "key": "closure_replay_ledger"},
            {"path": "/api/casulo/closure-replay/result", "file": "outputs/prod441_460_closure_replay_result.json", "key": "closure_replay_result"},
            {"path": "/api/casulo/closure-replay/readiness", "file": "outputs/prod441_460_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/closure-replay/audit", "file": "outputs/prod441_460_audit_report.json", "key": "audit"},
        ],
    },
    {
        "group": "real_manual_evidence",
        "routes": [
            {"path": "/api/casulo/real-manual-evidence/manifest", "file": "outputs/prod461_480_real_manual_evidence_manifest_snapshot.json", "key": "real_evidence_manifest"},
            {"path": "/api/casulo/real-manual-evidence/handoff", "file": "outputs/prod461_480_real_manual_evidence_handoff.json", "key": "real_evidence_handoff"},
            {"path": "/api/casulo/real-manual-evidence/validation", "file": "outputs/prod461_480_real_manual_evidence_validation.json", "key": "real_evidence_validation"},
            {"path": "/api/casulo/real-manual-evidence/checklist", "file": "outputs/prod461_480_real_manual_evidence_checklist.json", "key": "real_evidence_checklist"},
            {"path": "/api/casulo/real-manual-evidence/readiness", "file": "outputs/prod461_480_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/real-manual-evidence/audit", "file": "outputs/prod461_480_audit_report.json", "key": "audit"},
        ],
    },
    {
        "group": "milestone_snapshot",
        "routes": [
            {"path": "/api/casulo/milestone-snapshot/summary", "file": "outputs/prod481_500_milestone_snapshot.json", "key": "milestone_snapshot"},
            {"path": "/api/casulo/milestone-snapshot/tag-chain", "file": "outputs/prod481_500_tag_chain_inventory.json", "key": "tag_chain_inventory"},
            {"path": "/api/casulo/milestone-snapshot/dossier", "file": "outputs/prod481_500_operational_readiness_dossier.json", "key": "operational_readiness_dossier"},
            {"path": "/api/casulo/milestone-snapshot/pending-evidence", "file": "outputs/prod481_500_pending_evidence_register.json", "key": "pending_evidence_register"},
            {"path": "/api/casulo/milestone-snapshot/readiness", "file": "outputs/prod481_500_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/milestone-snapshot/audit", "file": "outputs/prod481_500_audit_report.json", "key": "audit"},
        ],
    },
    {
        "group": "external_evidence",
        "routes": [
            {"path": "/api/casulo/external-evidence/providers", "file": "outputs/prod521_560_provider_registry.json", "key": "provider_registry"},
            {"path": "/api/casulo/external-evidence/candidates", "file": "outputs/prod521_560_external_evidence_candidates.json", "key": "external_evidence_candidates"},
            {"path": "/api/casulo/external-evidence/citation-gate", "file": "outputs/prod521_560_citation_gate_result.json", "key": "citation_gate_result"},
            {"path": "/api/casulo/external-evidence/common-workloads", "file": "outputs/prod521_560_common_workload_mass_test_register.json", "key": "common_workload_mass_test_register"},
            {"path": "/api/casulo/external-evidence/readiness", "file": "outputs/prod521_560_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/external-evidence/audit", "file": "outputs/prod521_560_audit_report.json", "key": "audit"},
        ],
    },

    {
        "group": "operator_console_solver_surface",
        "routes": [
            {"path": "/api/casulo/operator-console/summary", "file": "outputs/prod561_600_operator_console_summary.json", "key": "operator_console_summary"},
            {"path": "/api/casulo/operator-console/solver-api-surface", "file": "outputs/prod561_600_solver_api_surface.json", "key": "solver_api_surface"},
            {"path": "/api/casulo/operator-console/common-workload-lab", "file": "outputs/prod561_600_common_workload_lab_protocol.json", "key": "common_workload_lab_protocol"},
            {"path": "/api/casulo/operator-console/business-domain-lab", "file": "outputs/prod561_600_business_domain_lab_protocol.json", "key": "business_domain_lab_protocol"},
            {"path": "/api/casulo/operator-console/solver-safety-gate", "file": "outputs/prod561_600_solver_input_safety_gate.json", "key": "solver_input_safety_gate"},
            {"path": "/api/casulo/operator-console/readiness", "file": "outputs/prod561_600_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/operator-console/audit", "file": "outputs/prod561_600_audit_report.json", "key": "audit"},
        ],
    },

    {
        "group": "common_workload_mass_test",
        "routes": [
            {"path": "/api/casulo/common-workload/fixtures", "file": "outputs/prod601_620_common_workload_fixture_pack.json", "key": "fixture_pack"},
            {"path": "/api/casulo/common-workload/batch-result", "file": "outputs/prod601_620_common_workload_batch_result.json", "key": "batch_result"},
            {"path": "/api/casulo/common-workload/metrics", "file": "outputs/prod601_620_direct_vs_cubo_metrics.json", "key": "metrics"},
            {"path": "/api/casulo/common-workload/workload-metrics", "file": "outputs/prod601_620_workload_metrics.json", "key": "workload_metrics"},
            {"path": "/api/casulo/common-workload/readiness", "file": "outputs/prod601_620_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/common-workload/audit", "file": "outputs/prod601_620_audit_report.json", "key": "audit"},
        ],
    },

]

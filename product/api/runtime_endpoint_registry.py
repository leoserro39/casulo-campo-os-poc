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

    {
        "group": "common_workload_calibration_stress",
        "routes": [
            {"path": "/api/casulo/common-workload-calibration/fixtures", "file": "outputs/prod601a_620a_calibration_stress_fixture_pack.json", "key": "fixture_pack"},
            {"path": "/api/casulo/common-workload-calibration/batch-result", "file": "outputs/prod601a_620a_calibration_stress_batch_result.json", "key": "batch_result"},
            {"path": "/api/casulo/common-workload-calibration/metrics", "file": "outputs/prod601a_620a_calibration_metrics.json", "key": "metrics"},
            {"path": "/api/casulo/common-workload-calibration/workload-metrics", "file": "outputs/prod601a_620a_workload_metrics.json", "key": "workload_metrics"},
            {"path": "/api/casulo/common-workload-calibration/stress-profile-metrics", "file": "outputs/prod601a_620a_stress_profile_metrics.json", "key": "stress_profile_metrics"},
            {"path": "/api/casulo/common-workload-calibration/thresholds", "file": "outputs/prod601a_620a_calibration_thresholds.json", "key": "thresholds"},
            {"path": "/api/casulo/common-workload-calibration/agent-entry-gate", "file": "outputs/prod601a_620a_agent_real_case_entry_gate.json", "key": "agent_real_case_entry_gate"},
            {"path": "/api/casulo/common-workload-calibration/audit", "file": "outputs/prod601a_620a_audit_report.json", "key": "audit"},
        ],
    },

    {
        "group": "telemetry_correlation_calibration",
        "routes": [
            {"path": "/api/casulo/telemetry-correlation/matrix", "file": "outputs/prod601b_620b_telemetry_correlation_matrix.json", "key": "correlation_matrix"},
            {"path": "/api/casulo/telemetry-correlation/bounds", "file": "outputs/prod601b_620b_telemetry_bounds.json", "key": "telemetry_bounds"},
            {"path": "/api/casulo/telemetry-correlation/optimal-zones", "file": "outputs/prod601b_620b_optimal_telemetry_zones.json", "key": "optimal_zones"},
            {"path": "/api/casulo/telemetry-correlation/adjustments", "file": "outputs/prod601b_620b_auto_adjustment_candidates.json", "key": "auto_adjustment_candidates"},
            {"path": "/api/casulo/telemetry-correlation/readiness", "file": "outputs/prod601b_620b_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/telemetry-correlation/audit", "file": "outputs/prod601b_620b_audit_report.json", "key": "audit"},
        ],
    },

    {
        "group": "live_delta_intersection",
        "routes": [
            {"path": "/api/casulo/live-delta/vectors", "file": "outputs/prod601c_620c_live_delta_vectors.json", "key": "live_delta_vectors"},
            {"path": "/api/casulo/live-delta/gate-transitions", "file": "outputs/prod601c_620c_gate_transition_model.json", "key": "gate_transition_model"},
            {"path": "/api/casulo/live-delta/domain-sensitivity", "file": "outputs/prod601c_620c_domain_sensitivity_model.json", "key": "domain_sensitivity_model"},
            {"path": "/api/casulo/live-delta/bayesian-trust", "file": "outputs/prod601c_620c_bayesian_gate_trust.json", "key": "bayesian_gate_trust"},
            {"path": "/api/casulo/live-delta/ewma-drift", "file": "outputs/prod601c_620c_ewma_drift_profile.json", "key": "ewma_drift_profile"},
            {"path": "/api/casulo/live-delta/pareto-frontier", "file": "outputs/prod601c_620c_pareto_frontier.json", "key": "pareto_frontier"},
            {"path": "/api/casulo/live-delta/baseline-policy", "file": "outputs/prod601c_620c_baseline_promotion_policy.json", "key": "baseline_promotion_policy"},
            {"path": "/api/casulo/live-delta/telemetry-events", "file": "outputs/prod601c_620c_telemetry_feedback_events.json", "key": "telemetry_feedback_events"},
            {"path": "/api/casulo/live-delta/readiness", "file": "outputs/prod601c_620c_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/live-delta/audit", "file": "outputs/prod601c_620c_audit_report.json", "key": "audit"},
        ],
    },

    {
        "group": "solver_agent_controlled_stub",
        "routes": [
            {"path": "/api/casulo/solver-agent/status", "file": "outputs/prod602_620_solver_agent_status.json", "key": "solver_agent_status"},
            {"path": "/api/casulo/solver-agent/input-schema", "file": "outputs/prod602_620_solver_agent_input_schema.json", "key": "input_schema"},
            {"path": "/api/casulo/solver-agent/sample-run", "file": "outputs/prod602_620_solver_agent_sample_run.json", "key": "sample_run"},
            {"path": "/api/casulo/solver-agent/run-report", "file": "outputs/prod602_620_solver_agent_run_report.json", "key": "run_report"},
            {"path": "/api/casulo/solver-agent/live-delta-decision", "file": "outputs/prod602_620_solver_agent_live_delta_decision.json", "key": "live_delta_decision"},
            {"path": "/api/casulo/solver-agent/evidence-trace", "file": "outputs/prod602_620_solver_agent_evidence_trace.json", "key": "evidence_trace"},
            {"path": "/api/casulo/solver-agent/gate-trace", "file": "outputs/prod602_620_solver_agent_gate_trace.json", "key": "gate_trace"},
            {"path": "/api/casulo/solver-agent/telemetry-feedback", "file": "outputs/prod602_620_solver_agent_telemetry_feedback.json", "key": "telemetry_feedback"},
            {"path": "/api/casulo/solver-agent/readiness", "file": "outputs/prod602_620_solver_agent_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/solver-agent/audit", "file": "outputs/prod602_620_solver_agent_audit_report.json", "key": "audit"},
        ],
    },

    {
        "group": "business_domain_calibration",
        "routes": [
            {"path": "/api/casulo/business-domain/matrix", "file": "outputs/prod621_650_business_domain_matrix.json", "key": "business_domain_matrix"},
            {"path": "/api/casulo/business-domain/cases", "file": "outputs/prod621_650_business_domain_cases.json", "key": "business_domain_cases"},
            {"path": "/api/casulo/business-domain/batch-result", "file": "outputs/prod621_650_business_domain_batch_result.json", "key": "batch_result"},
            {"path": "/api/casulo/business-domain/domain-metrics", "file": "outputs/prod621_650_business_domain_metrics.json", "key": "domain_metrics"},
            {"path": "/api/casulo/business-domain/scenario-metrics", "file": "outputs/prod621_650_business_scenario_metrics.json", "key": "scenario_metrics"},
            {"path": "/api/casulo/business-domain/intake-schema", "file": "outputs/prod621_650_business_intake_schema.json", "key": "intake_schema"},
            {"path": "/api/casulo/business-domain/thresholds", "file": "outputs/prod621_650_business_calibration_thresholds.json", "key": "thresholds"},
            {"path": "/api/casulo/business-domain/readiness", "file": "outputs/prod621_650_business_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/business-domain/audit", "file": "outputs/prod621_650_business_audit_report.json", "key": "audit"},
        ],
    },

    {
        "group": "domain_preflight_pattern_mining",
        "routes": [
            {"path": "/api/casulo/domain-preflight/matrix", "file": "outputs/prod621b_650b_domain_preflight_matrix.json", "key": "domain_preflight_matrix"},
            {"path": "/api/casulo/domain-preflight/hallucination-budget", "file": "outputs/prod621b_650b_hallucination_budget.json", "key": "hallucination_budget"},
            {"path": "/api/casulo/domain-preflight/safe-escalation", "file": "outputs/prod621b_650b_safe_escalation_taxonomy.json", "key": "safe_escalation_taxonomy"},
            {"path": "/api/casulo/domain-preflight/patterns", "file": "outputs/prod621b_650b_business_pattern_mining.json", "key": "business_pattern_mining"},
            {"path": "/api/casulo/domain-preflight/evidence-grid", "file": "outputs/prod621b_650b_evidence_variance_grid.json", "key": "evidence_variance_grid"},
            {"path": "/api/casulo/domain-preflight/gate-confusion", "file": "outputs/prod621b_650b_gate_confusion_matrix.json", "key": "gate_confusion_matrix"},
            {"path": "/api/casulo/domain-preflight/threshold-recommendations", "file": "outputs/prod621b_650b_threshold_recommendations.json", "key": "threshold_recommendations"},
            {"path": "/api/casulo/domain-preflight/readiness", "file": "outputs/prod621b_650b_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/domain-preflight/audit", "file": "outputs/prod621b_650b_audit_report.json", "key": "audit"},
        ],
    },

    {
        "group": "business_case_interactive_runner",
        "routes": [
            {"path": "/api/casulo/business-runner/status", "file": "outputs/prod651_680_business_runner_status.json", "key": "status"},
            {"path": "/api/casulo/business-runner/input-schema", "file": "outputs/prod651_680_business_runner_input_schema.json", "key": "input_schema"},
            {"path": "/api/casulo/business-runner/sample-cases", "file": "outputs/prod651_680_business_runner_sample_cases.json", "key": "sample_cases"},
            {"path": "/api/casulo/business-runner/runs", "file": "outputs/prod651_680_business_runner_runs.json", "key": "runs"},
            {"path": "/api/casulo/business-runner/decisions", "file": "outputs/prod651_680_business_runner_decisions.json", "key": "decisions"},
            {"path": "/api/casulo/business-runner/output-modes", "file": "outputs/prod651_680_business_runner_output_modes.json", "key": "output_modes"},
            {"path": "/api/casulo/business-runner/telemetry", "file": "outputs/prod651_680_business_runner_telemetry.json", "key": "telemetry"},
            {"path": "/api/casulo/business-runner/readiness", "file": "outputs/prod651_680_business_runner_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/business-runner/audit", "file": "outputs/prod651_680_business_runner_audit_report.json", "key": "audit"},
        ],
    },

    {
        "group": "business_runner_risk_scale_hotfix",
        "routes": [
            {"path": "/api/casulo/business-runner-risk/status", "file": "outputs/prod651a_680a_business_runner_status.json", "key": "status"},
            {"path": "/api/casulo/business-runner-risk/runs", "file": "outputs/prod651a_680a_business_runner_runs.json", "key": "runs"},
            {"path": "/api/casulo/business-runner-risk/decisions", "file": "outputs/prod651a_680a_business_runner_decisions.json", "key": "decisions"},
            {"path": "/api/casulo/business-runner-risk/telemetry", "file": "outputs/prod651a_680a_business_runner_telemetry.json", "key": "telemetry"},
            {"path": "/api/casulo/business-runner-risk/integrity", "file": "outputs/prod651a_680a_business_runner_risk_integrity.json", "key": "risk_integrity"},
            {"path": "/api/casulo/business-runner-risk/readiness", "file": "outputs/prod651a_680a_business_runner_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/business-runner-risk/audit", "file": "outputs/prod651a_680a_business_runner_audit_report.json", "key": "audit"},
        ],
    },

    {
        "group": "interactive_runner_feedback_calibration",
        "routes": [
            {"path": "/api/casulo/runner-feedback/status", "file": "outputs/prod681_720_feedback_loop_status.json", "key": "status"},
            {"path": "/api/casulo/runner-feedback/events", "file": "outputs/prod681_720_feedback_events.json", "key": "feedback_events"},
            {"path": "/api/casulo/runner-feedback/analysis", "file": "outputs/prod681_720_feedback_analysis.json", "key": "feedback_analysis"},
            {"path": "/api/casulo/runner-feedback/taxonomy", "file": "outputs/prod681_720_feedback_taxonomy.json", "key": "feedback_taxonomy"},
            {"path": "/api/casulo/runner-feedback/recommendations", "file": "outputs/prod681_720_calibration_recommendations.json", "key": "calibration_recommendations"},
            {"path": "/api/casulo/runner-feedback/telemetry", "file": "outputs/prod681_720_feedback_telemetry.json", "key": "feedback_telemetry"},
            {"path": "/api/casulo/runner-feedback/readiness", "file": "outputs/prod681_720_feedback_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/runner-feedback/audit", "file": "outputs/prod681_720_feedback_audit_report.json", "key": "audit"},
        ],
    },

    {
        "group": "controlled_20_case_business_pilot",
        "routes": [
            {"path": "/api/casulo/business-pilot/status", "file": "outputs/prod721_760_business_pilot_status.json", "key": "status"},
            {"path": "/api/casulo/business-pilot/case-pack", "file": "outputs/prod721_760_business_pilot_case_pack.json", "key": "case_pack"},
            {"path": "/api/casulo/business-pilot/runs", "file": "outputs/prod721_760_business_pilot_runs.json", "key": "runs"},
            {"path": "/api/casulo/business-pilot/decisions", "file": "outputs/prod721_760_business_pilot_decisions.json", "key": "decisions"},
            {"path": "/api/casulo/business-pilot/feedback-seed", "file": "outputs/prod721_760_business_pilot_feedback_seed.json", "key": "feedback_seed"},
            {"path": "/api/casulo/business-pilot/analysis", "file": "outputs/prod721_760_business_pilot_analysis.json", "key": "analysis"},
            {"path": "/api/casulo/business-pilot/recommendations", "file": "outputs/prod721_760_business_pilot_calibration_recommendations.json", "key": "recommendations"},
            {"path": "/api/casulo/business-pilot/readiness", "file": "outputs/prod721_760_business_pilot_readiness.json", "key": "readiness"},
            {"path": "/api/casulo/business-pilot/audit", "file": "outputs/prod721_760_business_pilot_audit_report.json", "key": "audit"},
        ],
    },

]

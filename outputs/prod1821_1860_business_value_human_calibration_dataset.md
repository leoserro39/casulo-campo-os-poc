# PROD-1821..1860 Business Value Human Calibration Dataset

- Status: `PASS`
- Decision: `BUSINESS_VALUE_HUMAN_CALIBRATION_DATASET_READY`
- Case count: `7`
- Review dimension count: `10`
- Human review required count: `7`
- Calibration eligible count: `0`
- High value candidate count: `3`
- High governance candidate count: `4`
- High hallucination reduction candidate count: `4`
- Assisted operation candidate count: `5`
- Calibration: `NOT_CALIBRATED_HUMAN_REVIEW_PENDING`

## Review Dimensions
- business_fit
- pain_clarity
- evidence_gap_clarity
- service_package_fit
- implementation_risk_realism
- governance_pressure_realism
- monitoring_recurrence_potential
- hallucination_reduction_relevance
- commercial_value_plausibility
- pilot_priority

## Cases

### BST-GOV-COMPLIANCE-001
- Source provenance: `SYNTHETIC_BUSINESS_TAXONOMY_AND_PROVISIONAL_ENSEMBLE`
- Company profile: `regulated or process-heavy company`
- Company maturity: `controls_exist_but_evidence_fragmented`
- Service package: `Governance Compliance State Mesh`
- Solution type: `controls_evidence_audit_gate_mesh`
- Recommendation type: `convert policies and controls into evidence-backed states and review gates`
- CASULO opportunity score: `80.05`
- Opportunity band: `high`
- Recommended mode: `DIAGNOSTIC_PLUS_ASSISTED_OPERATION`
- Hard gates: `GOVERNANCE_REVIEW_REQUIRED, IMPLEMENTATION_RISK_REVIEW_REQUIRED, STACK_GROUNDED_REVIEW_REQUIRED, COMPLIANCE_REVIEW_REQUIRED`
- Hallucination reduction potential: `71`
- Governance pressure score: `95`
- Monitoring recurrence score: `85`
- Commercial value proxy: `58`
- Suggested review focus: `validate_governance_pressure, validate_hallucination_reduction_claim, validate_recurring_revenue_or_assisted_operation_fit, validate_implementation_risk_and_gate`
- Pilot readiness hint: `HIGH_VALUE_DISCOVERY_ONLY`
- Calibration eligible: `False`
- Calibration blocker: `human_review_not_completed`
- Business delta: `reduce compliance ambiguity and improve audit readiness`
- Value hypothesis: `better auditability, fewer unsupported compliance claims and clearer ownership`

### BST-TICSI-001
- Source provenance: `SYNTHETIC_BUSINESS_TAXONOMY_AND_PROVISIONAL_ENSEMBLE`
- Company profile: `mid-sized company with internal IT/SI`
- Company maturity: `low_visibility_high_dependency`
- Service package: `TIC/SI State Mesh`
- Solution type: `application_integration_change_risk_mesh`
- Recommendation type: `map dependencies and block risky changes without rollback evidence`
- CASULO opportunity score: `79.85`
- Opportunity band: `high`
- Recommended mode: `DIAGNOSTIC_PLUS_RISK_GATE`
- Hard gates: `GOVERNANCE_REVIEW_REQUIRED, IMPLEMENTATION_RISK_REVIEW_REQUIRED, STACK_GROUNDED_REVIEW_REQUIRED, CHANGE_REVIEW_REQUIRED`
- Hallucination reduction potential: `71`
- Governance pressure score: `85`
- Monitoring recurrence score: `90`
- Commercial value proxy: `66`
- Suggested review focus: `validate_governance_pressure, validate_hallucination_reduction_claim, validate_recurring_revenue_or_assisted_operation_fit, validate_implementation_risk_and_gate, validate_commercial_value_proxy`
- Pilot readiness hint: `HIGH_VALUE_DISCOVERY_ONLY`
- Calibration eligible: `False`
- Calibration blocker: `human_review_not_completed`
- Business delta: `reduce production incidents and unmanaged dependency risk`
- Value hypothesis: `lower change risk, improved continuity and clearer support ownership`

### BST-AI-PME-001
- Source provenance: `SYNTHETIC_BUSINESS_TAXONOMY_AND_PROVISIONAL_ENSEMBLE`
- Company profile: `PME seeking AI adoption`
- Company maturity: `early_ai_experimentation`
- Service package: `Programa de IA PME`
- Solution type: `AI_use_case_map_and_pilot_governance`
- Recommendation type: `prioritize use cases by operational delta, risk and evidence readiness`
- CASULO opportunity score: `73.65`
- Opportunity band: `high`
- Recommended mode: `STARTER_IMPLANTATION`
- Hard gates: `GOVERNANCE_REVIEW_REQUIRED, STACK_GROUNDED_REVIEW_REQUIRED`
- Hallucination reduction potential: `59`
- Governance pressure score: `85`
- Monitoring recurrence score: `80`
- Commercial value proxy: `66`
- Suggested review focus: `validate_governance_pressure, validate_recurring_revenue_or_assisted_operation_fit, validate_commercial_value_proxy`
- Pilot readiness hint: `PILOT_CANDIDATE_AFTER_HUMAN_REVIEW`
- Calibration eligible: `False`
- Calibration blocker: `human_review_not_completed`
- Business delta: `avoid shadow AI and focus on measurable pilots`
- Value hypothesis: `safer AI adoption and clearer ROI path`

### BST-PME-ACCOUNTING-001
- Source provenance: `SYNTHETIC_BUSINESS_TAXONOMY_AND_PROVISIONAL_ENSEMBLE`
- Company profile: `PME accounting office`
- Company maturity: `medium_manual_process`
- Service package: `Cubo PME Starter`
- Solution type: `operational_dashboard_and_pending_documents_gate`
- Recommendation type: `monitor_pending_documents_and_block_closing_when_evidence_missing`
- CASULO opportunity score: `67.45`
- Opportunity band: `medium`
- Recommended mode: `DIAGNOSTIC_AND_BACKLOG`
- Hard gates: `STACK_GROUNDED_REVIEW_REQUIRED`
- Hallucination reduction potential: `65`
- Governance pressure score: `45`
- Monitoring recurrence score: `80`
- Commercial value proxy: `74`
- Suggested review focus: `validate_hallucination_reduction_claim, validate_recurring_revenue_or_assisted_operation_fit, validate_commercial_value_proxy`
- Pilot readiness hint: `BACKLOG_OR_DIAGNOSTIC_CANDIDATE`
- Calibration eligible: `False`
- Calibration blocker: `human_review_not_completed`
- Business delta: `reduce manual chasing and late discovery of missing evidence`
- Value hypothesis: `fewer delays, better client communication and premium operational reporting`

### BST-SOFTWARE-REVIEW-001
- Source provenance: `SYNTHETIC_BUSINESS_TAXONOMY_AND_PROVISIONAL_ENSEMBLE`
- Company profile: `company with existing internal software`
- Company maturity: `technical_debt_unknown`
- Service package: `Software Review Gate`
- Solution type: `technical_review_backlog_and_quality_gate`
- Recommendation type: `review application before AI integration or modernization`
- CASULO opportunity score: `61.65`
- Opportunity band: `medium`
- Recommended mode: `DIAGNOSTIC_AND_BACKLOG`
- Hard gates: `GOVERNANCE_REVIEW_REQUIRED`
- Hallucination reduction potential: `45`
- Governance pressure score: `85`
- Monitoring recurrence score: `45`
- Commercial value proxy: `48`
- Suggested review focus: `validate_governance_pressure`
- Pilot readiness hint: `BACKLOG_OR_DIAGNOSTIC_CANDIDATE`
- Calibration eligible: `False`
- Calibration blocker: `human_review_not_completed`
- Business delta: `avoid building on fragile software foundation`
- Value hypothesis: `safer modernization, clearer backlog and minimum test gate`

### BST-ASSISTED-OPS-001
- Source provenance: `SYNTHETIC_BUSINESS_TAXONOMY_AND_PROVISIONAL_ENSEMBLE`
- Company profile: `service company with recurring operations`
- Company maturity: `recurring_operation_with_untracked_deltas`
- Service package: `Operacao Assistida`
- Solution type: `monthly_state_delta_monitoring`
- Recommendation type: `run recurring review of states, deltas, gates and decisions`
- CASULO opportunity score: `60.55`
- Opportunity band: `medium`
- Recommended mode: `DIAGNOSTIC_AND_BACKLOG`
- Hard gates: `MONITORING_REVIEW_REQUIRED`
- Hallucination reduction potential: `67`
- Governance pressure score: `45`
- Monitoring recurrence score: `80`
- Commercial value proxy: `66`
- Suggested review focus: `validate_hallucination_reduction_claim, validate_recurring_revenue_or_assisted_operation_fit, validate_commercial_value_proxy`
- Pilot readiness hint: `BACKLOG_OR_DIAGNOSTIC_CANDIDATE`
- Calibration eligible: `False`
- Calibration blocker: `human_review_not_completed`
- Business delta: `turn one-off diagnosis into continuous operational improvement`
- Value hypothesis: `recurring revenue, continuous improvement and better executive visibility`

### BST-SOLUTION-FACTORY-001
- Source provenance: `SYNTHETIC_BUSINESS_TAXONOMY_AND_PROVISIONAL_ENSEMBLE`
- Company profile: `business unit needing a new operational application`
- Company maturity: `process_unclear_solution_requested`
- Service package: `Solution Factory Sprint`
- Solution type: `state_driven_backlog_prototype_and_validation`
- Recommendation type: `convert operational delta into backlog, prototype, tests and evidence`
- CASULO opportunity score: `57.35`
- Opportunity band: `medium`
- Recommended mode: `DIAGNOSTIC_AND_BACKLOG`
- Hard gates: `STANDARD_HUMAN_REVIEW_REQUIRED`
- Hallucination reduction potential: `45`
- Governance pressure score: `65`
- Monitoring recurrence score: `55`
- Commercial value proxy: `48`
- Suggested review focus: `validate_basic_business_fit`
- Pilot readiness hint: `LOW_PRIORITY_UNTIL_MORE_EVIDENCE`
- Calibration eligible: `False`
- Calibration blocker: `human_review_not_completed`
- Business delta: `reduce wasted development and build from validated operational need`
- Value hypothesis: `faster useful prototype and lower rework`

## Checks
- ranking_exists: `True`
- ensemble_exists: `True`
- review_template_exists: `True`
- ranking_status_pass: `True`
- ensemble_status_pass: `True`
- case_count: `7`
- has_all_review_dimensions: `True`
- all_cases_require_human_review: `True`
- no_cases_calibration_eligible_before_review: `True`
- has_high_value_candidates: `True`
- has_high_governance_candidates: `True`
- has_high_hallucination_reduction_candidates: `True`
- calibration_status: `NOT_CALIBRATED_HUMAN_REVIEW_PENDING`

## Errors
- None

## Boundary
- Human calibration dataset only.
- Human review is pending.
- No final thresholds.
- No final weights.
- No GPT connection.
- No GPT call.
- No Codex execution.
- No production connection.

## Blocked Actions
- client_facing_claim
- automatic_nomination
- implementation_execution
- production_activation
- automatic_merge
- credential_handling
- automatic_threshold_mutation
- autonomous_external_execution
- real_world_side_effect
- unapproved_real_company_data
- production_neo4j_connection
- production_graph_write
- final_answer_generation_without_boundary
- gpt_call
- codex_execution
- public_api_publication
- custom_gpt_connection_without_human_approval
- final_threshold_calibration
- final_weight_calibration

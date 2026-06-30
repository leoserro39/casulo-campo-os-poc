# PROD-1701..1740 Business Solution Telemetry Taxonomy

- Status: `PASS`
- Decision: `BUSINESS_SOLUTION_TELEMETRY_TAXONOMY_READY`
- Case count: `7`
- Company profile count: `7`
- Service package count: `7`
- Solution type count: `7`
- Recommendation type count: `7`
- High priority case count: `5`
- Calibration: `NOT_CALIBRATED_BUSINESS_TAXONOMY_ONLY`

## Service Packages
- Cubo PME Starter
- Governance Compliance State Mesh
- Operacao Assistida
- Programa de IA PME
- Software Review Gate
- Solution Factory Sprint
- TIC/SI State Mesh

## Cases

### BST-PME-ACCOUNTING-001
- Company profile: `PME accounting office`
- Company maturity: `medium_manual_process`
- Service package: `Cubo PME Starter`
- Solution type: `operational_dashboard_and_pending_documents_gate`
- Recommendation type: `monitor_pending_documents_and_block_closing_when_evidence_missing`
- Business delta: `reduce manual chasing and late discovery of missing evidence`
- Implementation risk: `medium`
- Monitoring need: `monthly`
- Governance need: `medium`
- Stack dependency: `high`
- Insight priority score: `11`
- Priority band: `high`
- Unsafe without stack pattern: `recommend automation before mapping evidence and gates`
- Stack grounded pattern: `state, evidence, pending items, gate and monthly review before automation`
- Value hypothesis: `fewer delays, better client communication and premium operational reporting`

### BST-TICSI-001
- Company profile: `mid-sized company with internal IT/SI`
- Company maturity: `low_visibility_high_dependency`
- Service package: `TIC/SI State Mesh`
- Solution type: `application_integration_change_risk_mesh`
- Recommendation type: `map dependencies and block risky changes without rollback evidence`
- Business delta: `reduce production incidents and unmanaged dependency risk`
- Implementation risk: `high`
- Monitoring need: `weekly_or_monthly`
- Governance need: `high`
- Stack dependency: `high`
- Insight priority score: `15`
- Priority band: `very_high`
- Unsafe without stack pattern: `approve change based on team comfort and maintenance window`
- Stack grounded pattern: `CHANGE_REVIEW_REQUIRED, rollback evidence, tests and responsible owner`
- Value hypothesis: `lower change risk, improved continuity and clearer support ownership`

### BST-SOFTWARE-REVIEW-001
- Company profile: `company with existing internal software`
- Company maturity: `technical_debt_unknown`
- Service package: `Software Review Gate`
- Solution type: `technical_review_backlog_and_quality_gate`
- Recommendation type: `review application before AI integration or modernization`
- Business delta: `avoid building on fragile software foundation`
- Implementation risk: `medium_high`
- Monitoring need: `per_release`
- Governance need: `high`
- Stack dependency: `medium_high`
- Insight priority score: `12`
- Priority band: `high`
- Unsafe without stack pattern: `start refactoring or adding AI without review gate`
- Stack grounded pattern: `map tests, docs, security, deploy and evidence before development`
- Value hypothesis: `safer modernization, clearer backlog and minimum test gate`

### BST-AI-PME-001
- Company profile: `PME seeking AI adoption`
- Company maturity: `early_ai_experimentation`
- Service package: `Programa de IA PME`
- Solution type: `AI_use_case_map_and_pilot_governance`
- Recommendation type: `prioritize use cases by operational delta, risk and evidence readiness`
- Business delta: `avoid shadow AI and focus on measurable pilots`
- Implementation risk: `medium`
- Monitoring need: `monthly`
- Governance need: `high`
- Stack dependency: `high`
- Insight priority score: `13`
- Priority band: `high`
- Unsafe without stack pattern: `deploy generic AI assistants before state and evidence mapping`
- Stack grounded pattern: `use cases, gates, human review and metrics before automation`
- Value hypothesis: `safer AI adoption and clearer ROI path`

### BST-GOV-COMPLIANCE-001
- Company profile: `regulated or process-heavy company`
- Company maturity: `controls_exist_but_evidence_fragmented`
- Service package: `Governance Compliance State Mesh`
- Solution type: `controls_evidence_audit_gate_mesh`
- Recommendation type: `convert policies and controls into evidence-backed states and review gates`
- Business delta: `reduce compliance ambiguity and improve audit readiness`
- Implementation risk: `high`
- Monitoring need: `monthly_or_quarterly`
- Governance need: `very_high`
- Stack dependency: `high`
- Insight priority score: `16`
- Priority band: `very_high`
- Unsafe without stack pattern: `declare compliance based on incomplete control narratives`
- Stack grounded pattern: `COMPLIANCE_REVIEW_REQUIRED, evidence packet, control owner and audit trail`
- Value hypothesis: `better auditability, fewer unsupported compliance claims and clearer ownership`

### BST-SOLUTION-FACTORY-001
- Company profile: `business unit needing a new operational application`
- Company maturity: `process_unclear_solution_requested`
- Service package: `Solution Factory Sprint`
- Solution type: `state_driven_backlog_prototype_and_validation`
- Recommendation type: `convert operational delta into backlog, prototype, tests and evidence`
- Business delta: `reduce wasted development and build from validated operational need`
- Implementation risk: `medium`
- Monitoring need: `per_sprint`
- Governance need: `medium_high`
- Stack dependency: `medium_high`
- Insight priority score: `10`
- Priority band: `medium`
- Unsafe without stack pattern: `start coding from loose request`
- Stack grounded pattern: `state contract, delta, backlog, acceptance criteria and validation gate`
- Value hypothesis: `faster useful prototype and lower rework`

### BST-ASSISTED-OPS-001
- Company profile: `service company with recurring operations`
- Company maturity: `recurring_operation_with_untracked_deltas`
- Service package: `Operacao Assistida`
- Solution type: `monthly_state_delta_monitoring`
- Recommendation type: `run recurring review of states, deltas, gates and decisions`
- Business delta: `turn one-off diagnosis into continuous operational improvement`
- Implementation risk: `low_medium`
- Monitoring need: `monthly`
- Governance need: `medium`
- Stack dependency: `medium_high`
- Insight priority score: `9`
- Priority band: `medium`
- Unsafe without stack pattern: `send generic monthly advice without evidence or gate history`
- Stack grounded pattern: `monitoring packet with recurring deltas, gates, evidence and next actions`
- Value hypothesis: `recurring revenue, continuous improvement and better executive visibility`

## Checks
- dataset_exists: `True`
- case_count: `7`
- has_company_profiles: `True`
- has_service_packages: `True`
- has_solution_types: `True`
- has_recommendation_types: `True`
- has_governance_compliance_package: `True`
- has_solution_factory_package: `True`
- has_assisted_operation_package: `True`
- has_ai_pme_package: `True`
- has_tic_si_package: `True`
- has_high_priority_cases: `True`
- calibration_status: `NOT_CALIBRATED_BUSINESS_TAXONOMY_ONLY`

## Errors
- None

## Boundary
- Business and solution taxonomy only.
- No final calibration.
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

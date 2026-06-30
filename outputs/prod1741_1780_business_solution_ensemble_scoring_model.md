# PROD-1741..1780 Business Solution Ensemble Scoring Model

- Status: `PASS`
- Decision: `BUSINESS_SOLUTION_ENSEMBLE_READY_NOT_CALIBRATED`
- Model type: `explainable_weighted_ensemble_with_hard_gates`
- Calibration: `NOT_CALIBRATED_PROVISIONAL_WEIGHTS_ONLY`
- Case count: `7`
- Average CASULO opportunity score: `68.65`
- Average hallucination reduction potential: `60.43`
- Average business delta score: `60.0`
- Average governance pressure score: `72.14`
- Average stack dependency score: `81.43`
- Average implementation risk score: `58.57`
- Average monitoring recurrence score: `73.57`
- Average commercial value proxy: `60.86`

## Provisional Weights
- business_delta_score: `0.2`
- hallucination_reduction_potential: `0.2`
- governance_pressure_score: `0.15`
- stack_dependency_score: `0.15`
- implementation_risk_score: `0.1`
- monitoring_recurrence_score: `0.1`
- commercial_value_proxy: `0.1`

## Top Cases
### BST-GOV-COMPLIANCE-001
- Service package: `Governance Compliance State Mesh`
- CASULO opportunity score: `80.05`
- Opportunity band: `high`
- Recommended mode: `DIAGNOSTIC_PLUS_ASSISTED_OPERATION`

### BST-TICSI-001
- Service package: `TIC/SI State Mesh`
- CASULO opportunity score: `79.85`
- Opportunity band: `high`
- Recommended mode: `DIAGNOSTIC_PLUS_RISK_GATE`

### BST-AI-PME-001
- Service package: `Programa de IA PME`
- CASULO opportunity score: `73.65`
- Opportunity band: `high`
- Recommended mode: `STARTER_IMPLANTATION`

### BST-PME-ACCOUNTING-001
- Service package: `Cubo PME Starter`
- CASULO opportunity score: `67.45`
- Opportunity band: `medium`
- Recommended mode: `DIAGNOSTIC_AND_BACKLOG`

### BST-SOFTWARE-REVIEW-001
- Service package: `Software Review Gate`
- CASULO opportunity score: `61.65`
- Opportunity band: `medium`
- Recommended mode: `DIAGNOSTIC_AND_BACKLOG`

## Cases

### BST-GOV-COMPLIANCE-001
- Company profile: `regulated or process-heavy company`
- Service package: `Governance Compliance State Mesh`
- CASULO opportunity score: `80.05`
- Opportunity band: `high`
- Recommended mode: `DIAGNOSTIC_PLUS_ASSISTED_OPERATION`
- Hard gates: `GOVERNANCE_REVIEW_REQUIRED, IMPLEMENTATION_RISK_REVIEW_REQUIRED, STACK_GROUNDED_REVIEW_REQUIRED, COMPLIANCE_REVIEW_REQUIRED`
- Business delta score: `63`
- Hallucination reduction potential: `71`
- Governance pressure score: `95`
- Stack dependency score: `90`
- Implementation risk score: `80`
- Monitoring recurrence score: `85`
- Commercial value proxy: `58`
- Maturity friction score: `90`

### BST-TICSI-001
- Company profile: `mid-sized company with internal IT/SI`
- Service package: `TIC/SI State Mesh`
- CASULO opportunity score: `79.85`
- Opportunity band: `high`
- Recommended mode: `DIAGNOSTIC_PLUS_RISK_GATE`
- Hard gates: `GOVERNANCE_REVIEW_REQUIRED, IMPLEMENTATION_RISK_REVIEW_REQUIRED, STACK_GROUNDED_REVIEW_REQUIRED, CHANGE_REVIEW_REQUIRED`
- Business delta score: `63`
- Hallucination reduction potential: `71`
- Governance pressure score: `85`
- Stack dependency score: `90`
- Implementation risk score: `80`
- Monitoring recurrence score: `90`
- Commercial value proxy: `66`
- Maturity friction score: `90`

### BST-AI-PME-001
- Company profile: `PME seeking AI adoption`
- Service package: `Programa de IA PME`
- CASULO opportunity score: `73.65`
- Opportunity band: `high`
- Recommended mode: `STARTER_IMPLANTATION`
- Hard gates: `GOVERNANCE_REVIEW_REQUIRED, STACK_GROUNDED_REVIEW_REQUIRED`
- Business delta score: `70`
- Hallucination reduction potential: `59`
- Governance pressure score: `85`
- Stack dependency score: `90`
- Implementation risk score: `50`
- Monitoring recurrence score: `80`
- Commercial value proxy: `66`
- Maturity friction score: `75`

### BST-PME-ACCOUNTING-001
- Company profile: `PME accounting office`
- Service package: `Cubo PME Starter`
- CASULO opportunity score: `67.45`
- Opportunity band: `medium`
- Recommended mode: `DIAGNOSTIC_AND_BACKLOG`
- Hard gates: `STACK_GROUNDED_REVIEW_REQUIRED`
- Business delta score: `63`
- Hallucination reduction potential: `65`
- Governance pressure score: `45`
- Stack dependency score: `90`
- Implementation risk score: `50`
- Monitoring recurrence score: `80`
- Commercial value proxy: `74`
- Maturity friction score: `65`

### BST-SOFTWARE-REVIEW-001
- Company profile: `company with existing internal software`
- Service package: `Software Review Gate`
- CASULO opportunity score: `61.65`
- Opportunity band: `medium`
- Recommended mode: `DIAGNOSTIC_AND_BACKLOG`
- Hard gates: `GOVERNANCE_REVIEW_REQUIRED`
- Business delta score: `56`
- Hallucination reduction potential: `45`
- Governance pressure score: `85`
- Stack dependency score: `70`
- Implementation risk score: `65`
- Monitoring recurrence score: `45`
- Commercial value proxy: `48`
- Maturity friction score: `80`

### BST-ASSISTED-OPS-001
- Company profile: `service company with recurring operations`
- Service package: `Operacao Assistida`
- CASULO opportunity score: `60.55`
- Opportunity band: `medium`
- Recommended mode: `DIAGNOSTIC_AND_BACKLOG`
- Hard gates: `MONITORING_REVIEW_REQUIRED`
- Business delta score: `49`
- Hallucination reduction potential: `67`
- Governance pressure score: `45`
- Stack dependency score: `70`
- Implementation risk score: `35`
- Monitoring recurrence score: `80`
- Commercial value proxy: `66`
- Maturity friction score: `75`

### BST-SOLUTION-FACTORY-001
- Company profile: `business unit needing a new operational application`
- Service package: `Solution Factory Sprint`
- CASULO opportunity score: `57.35`
- Opportunity band: `medium`
- Recommended mode: `DIAGNOSTIC_AND_BACKLOG`
- Hard gates: `STANDARD_HUMAN_REVIEW_REQUIRED`
- Business delta score: `56`
- Hallucination reduction potential: `45`
- Governance pressure score: `65`
- Stack dependency score: `70`
- Implementation risk score: `50`
- Monitoring recurrence score: `55`
- Commercial value proxy: `48`
- Maturity friction score: `70`

## Checks
- source_taxonomy_exists: `True`
- source_taxonomy_status_pass: `True`
- case_count: `7`
- has_weights: `True`
- weights_sum_to_one: `True`
- all_cases_scored: `True`
- all_cases_have_hard_gates: `True`
- all_cases_have_opportunity_score: `True`
- has_high_or_very_high_opportunity: `True`
- calibration_status: `NOT_CALIBRATED_PROVISIONAL_WEIGHTS_ONLY`

## Errors
- None

## Boundary
- Explainable ensemble only.
- Provisional weights only.
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
- final_weight_calibration

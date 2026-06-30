# PROD-1781..1820 Graph-Based Opportunity Ranking

- Status: `PASS`
- Decision: `GRAPH_BASED_OPPORTUNITY_RANKING_READY`
- Node count: `64`
- Edge count: `77`
- Calibration: `NOT_CALIBRATED_GRAPH_RANKING_ONLY`

## Node Kinds
- Case
- CompanyMaturity
- CompanyProfile
- Gate
- GovernanceNeed
- MonitoringNeed
- RecommendationType
- RecommendedMode
- ServicePackage
- SolutionType
- StackDependency

## Relationship Types
- DEPENDS_ON_STACK
- HAS_CASE
- HAS_GOVERNANCE_NEED
- HAS_MATURITY
- HAS_RECOMMENDATION
- NEEDS_MONITORING
- RECOMMENDS_MODE
- REQUIRES_GATE
- SUGGESTS_SOLUTION
- USES_PACKAGE

## Case Ranking
### BST-GOV-COMPLIANCE-001
- Company profile: `regulated or process-heavy company`
- Service package: `Governance Compliance State Mesh`
- CASULO opportunity score: `80.05`
- Opportunity band: `high`
- Recommended mode: `DIAGNOSTIC_PLUS_ASSISTED_OPERATION`
- Hard gates: `GOVERNANCE_REVIEW_REQUIRED, IMPLEMENTATION_RISK_REVIEW_REQUIRED, STACK_GROUNDED_REVIEW_REQUIRED, COMPLIANCE_REVIEW_REQUIRED`
- Hallucination reduction potential: `71`
- Governance pressure score: `95`
- Monitoring recurrence score: `85`
- Commercial value proxy: `58`

### BST-TICSI-001
- Company profile: `mid-sized company with internal IT/SI`
- Service package: `TIC/SI State Mesh`
- CASULO opportunity score: `79.85`
- Opportunity band: `high`
- Recommended mode: `DIAGNOSTIC_PLUS_RISK_GATE`
- Hard gates: `GOVERNANCE_REVIEW_REQUIRED, IMPLEMENTATION_RISK_REVIEW_REQUIRED, STACK_GROUNDED_REVIEW_REQUIRED, CHANGE_REVIEW_REQUIRED`
- Hallucination reduction potential: `71`
- Governance pressure score: `85`
- Monitoring recurrence score: `90`
- Commercial value proxy: `66`

### BST-AI-PME-001
- Company profile: `PME seeking AI adoption`
- Service package: `Programa de IA PME`
- CASULO opportunity score: `73.65`
- Opportunity band: `high`
- Recommended mode: `STARTER_IMPLANTATION`
- Hard gates: `GOVERNANCE_REVIEW_REQUIRED, STACK_GROUNDED_REVIEW_REQUIRED`
- Hallucination reduction potential: `59`
- Governance pressure score: `85`
- Monitoring recurrence score: `80`
- Commercial value proxy: `66`

### BST-PME-ACCOUNTING-001
- Company profile: `PME accounting office`
- Service package: `Cubo PME Starter`
- CASULO opportunity score: `67.45`
- Opportunity band: `medium`
- Recommended mode: `DIAGNOSTIC_AND_BACKLOG`
- Hard gates: `STACK_GROUNDED_REVIEW_REQUIRED`
- Hallucination reduction potential: `65`
- Governance pressure score: `45`
- Monitoring recurrence score: `80`
- Commercial value proxy: `74`

### BST-SOFTWARE-REVIEW-001
- Company profile: `company with existing internal software`
- Service package: `Software Review Gate`
- CASULO opportunity score: `61.65`
- Opportunity band: `medium`
- Recommended mode: `DIAGNOSTIC_AND_BACKLOG`
- Hard gates: `GOVERNANCE_REVIEW_REQUIRED`
- Hallucination reduction potential: `45`
- Governance pressure score: `85`
- Monitoring recurrence score: `45`
- Commercial value proxy: `48`

### BST-ASSISTED-OPS-001
- Company profile: `service company with recurring operations`
- Service package: `Operacao Assistida`
- CASULO opportunity score: `60.55`
- Opportunity band: `medium`
- Recommended mode: `DIAGNOSTIC_AND_BACKLOG`
- Hard gates: `MONITORING_REVIEW_REQUIRED`
- Hallucination reduction potential: `67`
- Governance pressure score: `45`
- Monitoring recurrence score: `80`
- Commercial value proxy: `66`

### BST-SOLUTION-FACTORY-001
- Company profile: `business unit needing a new operational application`
- Service package: `Solution Factory Sprint`
- CASULO opportunity score: `57.35`
- Opportunity band: `medium`
- Recommended mode: `DIAGNOSTIC_AND_BACKLOG`
- Hard gates: `STANDARD_HUMAN_REVIEW_REQUIRED`
- Hallucination reduction potential: `45`
- Governance pressure score: `65`
- Monitoring recurrence score: `55`
- Commercial value proxy: `48`

## Service Package Ranking
### TIC/SI State Mesh
- Case count: `1`
- Avg opportunity score: `79.85`
- Avg hallucination reduction potential: `71.0`
- Graph strength score: `78.3`

### Governance Compliance State Mesh
- Case count: `1`
- Avg opportunity score: `80.05`
- Avg hallucination reduction potential: `71.0`
- Graph strength score: `77.92`

### Programa de IA PME
- Case count: `1`
- Avg opportunity score: `73.65`
- Avg hallucination reduction potential: `59.0`
- Graph strength score: `72.23`

### Cubo PME Starter
- Case count: `1`
- Avg opportunity score: `67.45`
- Avg hallucination reduction potential: `65.0`
- Graph strength score: `66.46`

### Operacao Assistida
- Case count: `1`
- Avg opportunity score: `60.55`
- Avg hallucination reduction potential: `67.0`
- Graph strength score: `63.24`

### Software Review Gate
- Case count: `1`
- Avg opportunity score: `61.65`
- Avg hallucination reduction potential: `45.0`
- Graph strength score: `57.28`

### Solution Factory Sprint
- Case count: `1`
- Avg opportunity score: `57.35`
- Avg hallucination reduction potential: `45.0`
- Graph strength score: `54.27`

## Top Central Nodes
### Case:BST_GOV_COMPLIANCE_001
- Kind: `Case`
- Label: `BST-GOV-COMPLIANCE-001`
- Weighted degree: `1070.5`
- Score avg: `80.05`
- Centrality band: `very_high`

### Case:BST_TICSI_001
- Kind: `Case`
- Label: `BST-TICSI-001`
- Weighted degree: `1063.5`
- Score avg: `79.85`
- Centrality band: `very_high`

### Case:BST_AI_PME_001
- Kind: `Case`
- Label: `BST-AI-PME-001`
- Weighted degree: `844.2`
- Score avg: `73.65`
- Centrality band: `very_high`

### Case:BST_PME_ACCOUNTING_001
- Kind: `Case`
- Label: `BST-PME-ACCOUNTING-001`
- Weighted degree: `687.15`
- Score avg: `67.45`
- Centrality band: `very_high`

### Case:BST_SOFTWARE_REVIEW_001
- Kind: `Case`
- Label: `BST-SOFTWARE-REVIEW-001`
- Weighted degree: `631.55`
- Score avg: `61.65`
- Centrality band: `very_high`

### Case:BST_ASSISTED_OPS_001
- Kind: `Case`
- Label: `BST-ASSISTED-OPS-001`
- Weighted degree: `618.85`
- Score avg: `60.55`
- Centrality band: `very_high`

### Case:BST_SOLUTION_FACTORY_001
- Kind: `Case`
- Label: `BST-SOLUTION-FACTORY-001`
- Weighted degree: `591.45`
- Score avg: `57.35`
- Centrality band: `very_high`

### StackDependency:high
- Kind: `StackDependency`
- Label: `high`
- Weighted degree: `360.0`
- Score avg: `75.25`
- Centrality band: `very_high`

### Gate:STACK_GROUNDED_REVIEW_REQUIRED
- Kind: `Gate`
- Label: `STACK_GROUNDED_REVIEW_REQUIRED`
- Weighted degree: `301.0`
- Score avg: `0.0`
- Centrality band: `very_high`

### Gate:GOVERNANCE_REVIEW_REQUIRED
- Kind: `Gate`
- Label: `GOVERNANCE_REVIEW_REQUIRED`
- Weighted degree: `295.2`
- Score avg: `0.0`
- Centrality band: `very_high`

## Checks
- source_ensemble_exists: `True`
- source_ensemble_status_pass: `True`
- case_count: `7`
- node_count: `64`
- edge_count: `77`
- has_case_ranking: `True`
- has_service_package_ranking: `True`
- has_company_profile_ranking: `True`
- has_solution_type_ranking: `True`
- has_central_nodes: `True`
- no_production_graph_write: `True`
- calibration_status: `NOT_CALIBRATED_GRAPH_RANKING_ONLY`

## Errors
- None

## Boundary
- In-memory graph projection only.
- No production graph write.
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

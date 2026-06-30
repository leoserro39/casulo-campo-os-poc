# PROD-1341..1380 Graph-Backed Retrieval Context Packet

- Status: `PASS`
- Query: `missing evidence human review`
- Mode: `neo4j_sandbox_read_only_context_packet`
- Match mode: `term_filtered`
- Result count: `8`

## Retrieved Cases

### case:EXP50-002
- business_domain: `restaurant_inventory`
- risk_theme: `missing_evidence`
- evidence_profile: `partial_evidence`
- risk_band: `HIGH`
- adjusted_risk: `57.95`
- gate: `HUMAN_REVIEW_REQUIRED`
- output_mode: `HUMAN_REVIEW_PACKET`
- hallucination_budget: `0.6762`
- reasoning_mode: `GUIDED_REASONING`

### case:EXP50-006
- business_domain: `restaurant_cashflow`
- risk_theme: `missing_evidence`
- evidence_profile: `complete_minimum_evidence`
- risk_band: `HIGH`
- adjusted_risk: `61.95`
- gate: `HUMAN_REVIEW_REQUIRED`
- output_mode: `HUMAN_REVIEW_PACKET`
- hallucination_budget: `0.6429`
- reasoning_mode: `GUIDED_REASONING`

### case:EXP50-010
- business_domain: `clinic_scheduling`
- risk_theme: `missing_evidence`
- evidence_profile: `high_sensitivity_evidence`
- risk_band: `HIGH`
- adjusted_risk: `64.7`
- gate: `HUMAN_REVIEW_REQUIRED`
- output_mode: `HUMAN_REVIEW_PACKET`
- hallucination_budget: `0.6299`
- reasoning_mode: `GUIDED_REASONING`

### case:EXP50-014
- business_domain: `clinic_billing_glosa`
- risk_theme: `missing_evidence`
- evidence_profile: `stale_evidence`
- risk_band: `HIGH`
- adjusted_risk: `66.95`
- gate: `HUMAN_REVIEW_REQUIRED`
- output_mode: `HUMAN_REVIEW_PACKET`
- hallucination_budget: `0.6512`
- reasoning_mode: `GUIDED_REASONING`

### case:EXP50-018
- business_domain: `accounting_tax_obligation`
- risk_theme: `missing_evidence`
- evidence_profile: `conflicting_evidence`
- risk_band: `HIGH`
- adjusted_risk: `66.95`
- gate: `HUMAN_REVIEW_REQUIRED`
- output_mode: `HUMAN_REVIEW_PACKET`
- hallucination_budget: `0.6012`
- reasoning_mode: `GUIDED_REASONING`

### case:EXP50-022
- business_domain: `contract_legal_review`
- risk_theme: `missing_evidence`
- evidence_profile: `partial_evidence`
- risk_band: `HIGH`
- adjusted_risk: `67.95`
- gate: `HUMAN_REVIEW_REQUIRED`
- output_mode: `HUMAN_REVIEW_PACKET`
- hallucination_budget: `0.5929`
- reasoning_mode: `GUIDED_REASONING`

### case:EXP50-026
- business_domain: `ecommerce_order_ops`
- risk_theme: `missing_evidence`
- evidence_profile: `complete_minimum_evidence`
- risk_band: `HIGH`
- adjusted_risk: `59.95`
- gate: `HUMAN_REVIEW_REQUIRED`
- output_mode: `HUMAN_REVIEW_PACKET`
- hallucination_budget: `0.6595`
- reasoning_mode: `GUIDED_REASONING`

### case:EXP50-030
- business_domain: `field_service_work_order`
- risk_theme: `missing_evidence`
- evidence_profile: `high_sensitivity_evidence`
- risk_band: `HIGH`
- adjusted_risk: `61.7`
- gate: `HUMAN_REVIEW_REQUIRED`
- output_mode: `HUMAN_REVIEW_PACKET`
- hallucination_budget: `0.6549`
- reasoning_mode: `GUIDED_REASONING`

## Boundary
- Read-only Neo4j sandbox retrieval.
- No final answer generation.
- No GPT call.
- No Codex execution.
- No production connection.
- No client-facing claim.

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
- final_answer_generation
- codex_execution

# PROD-2061..2100 Operational Hallucination Risk Index and Ranking Model

- Status: `FAIL`
- Decision: `OPERATIONAL_HALLUCINATION_RISK_INDEX_NOT_READY`
- Index: `OHRI` / `IRAO`
- Calibration: `NOT_CALIBRATED_HEURISTIC_RANKING_ONLY`
- Ranking count: `16`
- Critical count: `0`
- High or critical count: `8`
- Recommended next phase: `PROD-2101..2140 - Parser Grounding Benchmark`

## Top 5 Risk Modes
### 1. unsafe_merge_suggestion
- Score: `78.0`
- Band: `high`
- Family: `agentic_execution`
- CASULO control: Enforce blocked_actions: automatic_merge, codex_execution, implementation_execution unless explicitly approved.

### 2. production_readiness_leakage
- Score: `76.64`
- Band: `high`
- Family: `production_boundary`
- CASULO control: Require production gate, sandbox flag, evidence status, blocked production_activation and human approval state.

### 3. repo_state_mismatch
- Score: `76.45`
- Band: `high`
- Family: `repo_patch`
- CASULO control: Use branch, commit, git status, file tree, recent tags and validators as state packet.

### 4. api_contract_hallucination
- Score: `75.18`
- Band: `high`
- Family: `api_integration`
- CASULO control: Require OpenAPI/schema, endpoint inventory, mock fixtures and contract tests.

### 5. contract_omission
- Score: `73.14`
- Band: `high`
- Family: `implementation_governance`
- CASULO control: Require contract, schema, checks, expected outputs and blocked actions before implementation.

## Full Ranking
1. `unsafe_merge_suggestion` — `78.0` — `high` — `agentic_execution`
2. `production_readiness_leakage` — `76.64` — `high` — `production_boundary`
3. `repo_state_mismatch` — `76.45` — `high` — `repo_patch`
4. `api_contract_hallucination` — `75.18` — `high` — `api_integration`
5. `contract_omission` — `73.14` — `high` — `implementation_governance`
6. `generic_rag_answer_without_gate` — `72.95` — `high` — `rag_vs_state_control`
7. `generic_parser_generation` — `71.82` — `high` — `parser_grounding`
8. `testless_code_generation` — `70.14` — `high` — `implementation_governance`
9. `schema_invention` — `69.73` — `medium` — `artifact_contract`
10. `file_structure_hallucination` — `66.86` — `medium` — `artifact_contract`
11. `generic_validation_laundering` — `66.73` — `medium` — `client_boundary`
12. `conditional_client_claim_leakage` — `66.18` — `medium` — `client_boundary`
13. `context_contamination` — `53.68` — `medium` — `capture_quality`
14. `business_recommendation_without_limits` — `52.73` — `medium` — `service_recommendation`
15. `provider_contamination` — `42.86` — `low` — `capture_quality`
16. `ui_metadata_contamination` — `32.41` — `low` — `capture_quality`

## Family Ranking
1. `agentic_execution` — avg `78.0` — `high` — count `1`
2. `production_boundary` — avg `76.64` — `high` — count `1`
3. `repo_patch` — avg `76.45` — `high` — count `1`
4. `api_integration` — avg `75.18` — `high` — count `1`
5. `rag_vs_state_control` — avg `72.95` — `high` — count `1`
6. `parser_grounding` — avg `71.82` — `high` — count `1`
7. `implementation_governance` — avg `71.64` — `high` — count `2`
8. `artifact_contract` — avg `68.3` — `medium` — count `2`
9. `client_boundary` — avg `66.46` — `medium` — count `2`
10. `service_recommendation` — avg `52.73` — `medium` — count `1`
11. `capture_quality` — avg `42.98` — `low` — count `3`

## Checks
- prior_failure_mode_matrix_exists: `True`
- prior_failure_mode_matrix_pass: `True`
- prior_decision_ready: `True`
- matrix_exists: `True`
- model_exists: `True`
- contract_exists: `True`
- doc_exists: `True`
- model_status_heuristic: `True`
- has_weights: `True`
- weight_count: `12`
- weight_sum_approximately_one: `False`
- failure_mode_count: `16`
- ranking_count: `16`
- all_failure_modes_scored: `True`
- has_critical_or_high_modes: `True`
- top_mode_name: `unsafe_merge_suggestion`
- top_mode_is_parser_or_production_or_merge_or_api: `True`
- parser_grounding_in_top_five: `False`
- repo_state_in_top_five: `True`
- api_contract_in_top_seven: `True`
- calibration_blocked: `True`
- automatic_gpt_call_blocked: `True`
- codex_execution_blocked: `True`
- automatic_merge_blocked: `True`
- production_activation_blocked: `True`
- client_facing_claim_blocked: `True`
- recommended_next_phase: `PROD-2101..2140 - Parser Grounding Benchmark`

## Errors
- Risk index weights must sum to 1.0
- Parser grounding should be in top five risk modes

## Boundary
- Heuristic ranking only.
- Not calibrated.
- No automatic GPT call.
- No Codex execution.
- No automatic merge.
- No production activation.
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
- final_answer_generation_without_boundary
- gpt_call
- codex_execution
- public_api_publication
- custom_gpt_connection_without_human_approval
- final_threshold_calibration
- final_weight_calibration
- calibration_from_exploratory_capture

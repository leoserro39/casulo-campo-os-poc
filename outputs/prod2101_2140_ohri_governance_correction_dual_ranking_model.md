# PROD-2101..2140 OHRI Governance Correction and Dual Ranking Model

- Status: `PASS`
- Decision: `OHRI_GOVERNANCE_CORRECTED_DUAL_RANKING_READY`
- Calibration: `NOT_CALIBRATED_CORRECTIVE_DUAL_RANKING_ONLY`
- Corrects previous commit: `1507dfa`
- Corrects previous tag: `product-operational-hallucination-risk-index-ranking-model-v0.1`
- Previous status: `FAIL`
- Recommended next phase: `PROD-2141..2180 - Capability-State Ontology and Living Company State Anchor`
- Later benchmark phase: `PROD-2181..2220 - Parser Grounding Benchmark`

## Correction

The previous model mixed operational danger with benchmark priority.

This corrected phase separates:

- OHRI: operational danger.
- OBPI: benchmark priority.

## OHRI Top 5
1. `unsafe_merge_suggestion` — `80.9` — `high` — `agentic_execution`
2. `production_readiness_leakage` — `79.5` — `high` — `production_boundary`
3. `repo_state_mismatch` — `77.0` — `high` — `repo_patch`
4. `api_contract_hallucination` — `75.0` — `high` — `api_integration`
5. `generic_rag_answer_without_gate` — `74.05` — `high` — `rag_vs_state_control`

## OBPI Top 5
1. `generic_parser_generation` — `85.25` — `critical` — `parser_grounding`
2. `api_contract_hallucination` — `84.45` — `high` — `api_integration`
3. `schema_invention` — `82.65` — `high` — `artifact_contract`
4. `repo_state_mismatch` — `80.1` — `high` — `repo_patch`
5. `contract_omission` — `77.8` — `high` — `implementation_governance`

## Checks
- previous_index_output_exists: `True`
- previous_index_was_fail: `True`
- previous_failure_recorded: `True`
- previous_parser_assumption_recorded: `True`
- matrix_exists: `True`
- source_model_exists: `True`
- dual_model_exists: `True`
- contract_exists: `True`
- doc_exists: `True`
- dual_model_status_heuristic: `True`
- ohri_weight_sum_one: `True`
- obpi_weight_sum_one: `True`
- failure_mode_count: `16`
- ohri_ranking_count: `16`
- obpi_ranking_count: `16`
- all_modes_have_scores: `True`
- ohri_top_is_not_forced_parser: `True`
- obpi_top_is_parser: `True`
- repo_state_high_in_ohri: `True`
- api_contract_high_in_ohri: `True`
- unsafe_merge_high_in_ohri: `True`
- parser_in_obpi_top_3: `True`
- calibration_blocked: `True`
- automatic_gpt_call_blocked: `True`
- codex_execution_blocked: `True`
- automatic_merge_blocked: `True`
- production_activation_blocked: `True`
- client_facing_claim_blocked: `True`

## Errors
- None

## Boundary
- Corrective ranking only.
- Not calibrated.
- No GPT call.
- No Codex execution.
- No automatic merge.
- No production activation.
- No client-facing claim.

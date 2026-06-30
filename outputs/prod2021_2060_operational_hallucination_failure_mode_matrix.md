# PROD-2021..2060 Operational Hallucination Failure Mode Matrix

- Status: `PASS`
- Decision: `OPERATIONAL_HALLUCINATION_FAILURE_MODE_MATRIX_READY`
- Calibration: `NOT_CALIBRATED_FAILURE_MODE_DISCOVERY_ONLY`
- Failure modes: `16`
- Benchmark families: `7`
- Recommended next phase: `PROD-2061..2100 - Parser Grounding Benchmark`

## Strong Thesis

Models can produce plausible and even prudent answers while remaining operationally insufficient because they lack real state, schema, repo context, evidence, gates, blocked actions, validators and permitted next actions.

## RAG Distinction

RAG improves retrieval and context. CASULO governs action through operational state, gates, evidence, blocked actions, validation and human review.

## Git / Codex Distinction

Git versions changes and Codex can implement when authorized. CASULO defines whether implementation is allowed, what contract must be respected and which evidence/gates are required.

## Failure Modes
### FM-001 - generic_parser_generation
- Family: `parser_grounding`
- Priority: `critical`
- Description: The model generates a generic parser that compiles but does not match the real workbook, file format, schema or field contract.
- Pure failure pattern: Assumes generic sheet names, columns, types, required fields and outputs.
- CASULO control: Require real workbook inventory, schema, field mapping, fixtures, golden output and validator before implementation.

### FM-002 - schema_invention
- Family: `artifact_contract`
- Priority: `critical`
- Description: The model invents fields, enum values, JSON structure, workbook tabs or validation rules not present in the source artifact.
- Pure failure pattern: Creates plausible but unsupported schema.
- CASULO control: Bind generation to declared schema, source inventory, contract and diffable evidence.

### FM-003 - file_structure_hallucination
- Family: `artifact_contract`
- Priority: `high`
- Description: The model assumes paths, files, folders or workbook structures that do not exist.
- Pure failure pattern: References missing files or stale paths.
- CASULO control: Require repo/file inventory and path existence checks before patch planning.

### FM-004 - repo_state_mismatch
- Family: `repo_patch`
- Priority: `critical`
- Description: The model proposes a patch based on stale or reconstructed repo state, ignoring current branch, diff, previous commits or generated outputs.
- Pure failure pattern: Patch targets old architecture or already-fixed files.
- CASULO control: Use branch, commit, git status, file tree, recent tags and validators as state packet.

### FM-005 - contract_omission
- Family: `implementation_governance`
- Priority: `high`
- Description: The model implements or recommends changes without explicit contract, acceptance criteria or expected validation output.
- Pure failure pattern: Code may compile but cannot be audited against a contract.
- CASULO control: Require contract, schema, checks, expected outputs and blocked actions before implementation.

### FM-006 - testless_code_generation
- Family: `implementation_governance`
- Priority: `high`
- Description: The model generates code without tests, fixtures or validation commands.
- Pure failure pattern: Implementation appears complete but has no proof.
- CASULO control: Require fixture, golden output, validator and PASS/FAIL evidence.

### FM-007 - unsafe_merge_suggestion
- Family: `agentic_execution`
- Priority: `critical`
- Description: The model suggests automatic merge, direct push or implementation execution before evidence and human review.
- Pure failure pattern: Treats successful generation as authorization.
- CASULO control: Enforce blocked_actions: automatic_merge, codex_execution, implementation_execution unless explicitly approved.

### FM-008 - conditional_client_claim_leakage
- Family: `client_boundary`
- Priority: `critical`
- Description: The model says a client-facing claim is acceptable if generic criteria are met, without knowing whether they are met.
- Pure failure pattern: Answers with a plausible checklist and conditional yes.
- CASULO control: Require explicit gate, evidence status, output_mode and client_facing_claim blocked/unblocked state.

### FM-009 - generic_validation_laundering
- Family: `client_boundary`
- Priority: `high`
- Description: The model turns an unknown validation state into a generic validation checklist, making the answer sound governed while remaining unaudited.
- Pure failure pattern: Provides generic validation criteria instead of a decision tied to evidence.
- CASULO control: Separate checklist suggestion from decision. Require status: validated, pending review, blocked or insufficient evidence.

### FM-010 - production_readiness_leakage
- Family: `production_boundary`
- Priority: `critical`
- Description: The model suggests production readiness based on partial progress or vague tests.
- Pure failure pattern: Says possibly yes if tests passed, without evidence or gate state.
- CASULO control: Require production gate, sandbox flag, evidence status, blocked production_activation and human approval state.

### FM-011 - api_contract_hallucination
- Family: `api_integration`
- Priority: `high`
- Description: The model invents endpoints, payloads, authentication patterns, status codes or error responses.
- Pure failure pattern: Produces plausible API integration without OpenAPI or real contract.
- CASULO control: Require OpenAPI/schema, endpoint inventory, mock fixtures and contract tests.

### FM-012 - generic_rag_answer_without_gate
- Family: `rag_vs_state_control`
- Priority: `critical`
- Description: The model uses retrieved context to answer better but does not enforce gates, blocked actions or permitted output modes.
- Pure failure pattern: Good summary, weak operational control.
- CASULO control: Transform retrieved context into state packet with gate, risk, evidence, blocked actions and next allowed action.

### FM-013 - business_recommendation_without_limits
- Family: `service_recommendation`
- Priority: `medium`
- Description: The model recommends a package or roadmap without implementation boundaries, risk, governance, dependency or blocked actions.
- Pure failure pattern: Compelling recommendation without safe scope.
- CASULO control: Require company profile, risk level, package candidate, gates, safe scope and blocked implementation actions.

### FM-014 - context_contamination
- Family: `capture_quality`
- Priority: `critical`
- Description: A supposedly pure capture contains vocabulary, gates or project context from prior conversation.
- Pure failure pattern: Pure answer mentions CASULO, gates, runbooks or batch details without being given them.
- CASULO control: Require clean chat/source metadata and mark contaminated captures as exploratory only.

### FM-015 - provider_contamination
- Family: `capture_quality`
- Priority: `high`
- Description: Responses from different providers or models are mixed into a GPT-only batch without provider labels.
- Pure failure pattern: Gemini, GPT and other outputs are merged under same capture ID.
- CASULO control: Require provider/model/source fields and separate exploratory captures from calibration captures.

### FM-016 - ui_metadata_contamination
- Family: `capture_quality`
- Priority: `medium`
- Description: UI text such as thinking time, timestamps, buttons or disclaimers is copied into model response evidence.
- Pure failure pattern: Includes 'Pensou por', timestamps, 'Convidar membros da equipe' or provider UI notices.
- CASULO control: Require cleaning rules and raw vs cleaned response fields.

## Benchmark Families
### BM-001 - Parser Grounding Benchmark
- Priority: `critical`
- Purpose: Compare generic parser generation against parser generation grounded in real workbook inventory, schema, fixtures and golden output.

### BM-002 - Repo Patch Grounding Benchmark
- Priority: `critical`
- Purpose: Compare generic patch suggestions against patches grounded in current git state, files, tests and validator evidence.

### BM-003 - Workbook / Excel Contract Benchmark
- Priority: `high`
- Purpose: Measure field, sheet, schema and archive/core mapping hallucination against real workbook contracts.

### BM-004 - API Contract Benchmark
- Priority: `high`
- Purpose: Measure endpoint/payload/auth/status hallucination against OpenAPI and contract tests.

### BM-005 - Production Gate Benchmark
- Priority: `critical`
- Purpose: Measure production/client/merge boundary leakage with and without gates and blocked actions.

### BM-006 - RAG vs Operational State Control Benchmark
- Priority: `critical`
- Purpose: Compare document-grounded RAG answer against state-packet answer with gates, blocked actions and validation outputs.

### BM-007 - Business Recommendation Boundary Benchmark
- Priority: `medium`
- Purpose: Compare generic service recommendation against package recommendation with safe scope, risk and gates.

## Checks
- prior_batch_001_runbook_exists: `True`
- prior_batch_001_runbook_pass: `True`
- prior_batch_001_requires_manual_capture_next: `True`
- matrix_exists: `True`
- contract_exists: `True`
- doc_exists: `True`
- matrix_status_exploratory: `True`
- failure_mode_count: `16`
- failure_mode_count_at_least_16: `True`
- benchmark_family_count: `7`
- benchmark_family_count_at_least_7: `True`
- has_all_required_failure_modes: `True`
- has_all_required_benchmarks: `True`
- has_parser_benchmark: `True`
- has_rag_vs_state_benchmark: `True`
- has_git_codex_distinction: `True`
- has_rag_distinction: `True`
- calibration_blocked: `True`
- automatic_gpt_call_blocked: `True`
- codex_execution_blocked: `True`
- automatic_merge_blocked: `True`
- production_activation_blocked: `True`
- client_facing_claim_blocked: `True`
- next_recommended_phase: `PROD-2061..2100 - Parser Grounding Benchmark`

## Errors
- None

## Boundary
- Exploratory only.
- No calibration.
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

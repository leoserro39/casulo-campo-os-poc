# Delta Library v2

## delta_evidence
- delta_id: `delta_evidence`
- definition: `Gap between claim/action and supporting evidence.`
- symptoms: `["missing source", "weak traceability", "source conflict"]`
- metrics: `["evidence_strength", "evidence_coverage", "unsupported_fields"]`
- controls: `["require_evidence", "mark_candidate_only", "ask_for_source"]`
- gates: `["ASK_FOR_EVIDENCE", "PARTIAL_ANSWER_ALLOWED"]`
- graph_effect: `edge remains candidate until evidence bridge exists`

## delta_ambiguity
- delta_id: `delta_ambiguity`
- definition: `Semantic uncertainty in terms, scope, entities or intent.`
- symptoms: `["multiple meanings", "unclear scope", "ambiguous entity"]`
- metrics: `["ambiguity_level", "scope_ambiguity"]`
- controls: `["split_interpretations", "structure_only", "add_assumption_marker"]`
- gates: `["STRUCTURE_ONLY", "PARTIAL_ANSWER_ALLOWED"]`
- graph_effect: `create alternative candidate nodes/edges`

## delta_missingness
- delta_id: `delta_missingness`
- definition: `Required information is objectively absent.`
- symptoms: `["missing field", "missing document", "missing test"]`
- metrics: `["missingness_level", "missing_required_fields"]`
- controls: `["generate_missing_artifact_task", "create_data_request"]`
- gates: `["TASK_ONLY", "ASK_FOR_EVIDENCE"]`
- graph_effect: `add missing artifact node and unresolved dependency edge`

## delta_conflict
- delta_id: `delta_conflict`
- definition: `Signals contradict each other.`
- symptoms: `["field conflict", "rule conflict", "source conflict"]`
- metrics: `["conflict_level", "contradiction_count"]`
- controls: `["conflict_resolution_task", "human_arbitration"]`
- gates: `["HUMAN_REVIEW_REQUIRED", "STRUCTURE_ONLY"]`
- graph_effect: `create conflict edge and arbitration node`

## delta_rule
- delta_id: `delta_rule`
- definition: `Rule, exception, applicability or precedence is not computable yet.`
- symptoms: `["ambiguous rule", "missing exception", "unknown precedence"]`
- metrics: `["rule_gap", "rule_exception_missing"]`
- controls: `["require_rule_source", "exception_map", "applicability_test"]`
- gates: `["STRUCTURE_ONLY", "HUMAN_REVIEW_REQUIRED"]`
- graph_effect: `rule node remains candidate until source/scope/exception/test exist`

## delta_domain
- delta_id: `delta_domain`
- definition: `Risk caused by the sensitivity of the domain itself.`
- symptoms: `["legal sensitivity", "financial risk", "technical production risk"]`
- metrics: `["domain_risk", "technical_sensitivity"]`
- controls: `["raise_review_level", "require_domain_owner"]`
- gates: `["HUMAN_REVIEW_REQUIRED", "PARTIAL_ANSWER_ALLOWED"]`
- graph_effect: `domain risk increases gate strictness`

## delta_execution
- delta_id: `delta_execution`
- definition: `Output is not safely executable with current context.`
- symptoms: `["runtime unknown", "dependencies unknown", "tests missing"]`
- metrics: `["execution_gap", "test_gap"]`
- controls: `["require_test_plan", "require_runtime_context", "no_write_action"]`
- gates: `["TASK_ONLY", "ASK_FOR_EVIDENCE"]`
- graph_effect: `execution edge blocked; create task node`

## delta_production
- delta_id: `delta_production`
- definition: `Distance from prototype to production-grade operation.`
- symptoms: `["auth missing", "audit missing", "rollback missing"]`
- metrics: `["production_gap", "auth_ready", "audit_ready"]`
- controls: `["production_block", "deployment_readiness_check"]`
- gates: `["BLOCKED_UNSUPPORTED", "HUMAN_REVIEW_REQUIRED"]`
- graph_effect: `production activation edge blocked`

## delta_human_review
- delta_id: `delta_human_review`
- definition: `Human decision, domain owner or arbitrator is needed.`
- symptoms: `["judgment call", "responsibility boundary"]`
- metrics: `["human_decision_pending", "review_required"]`
- controls: `["create_review_task", "route_to_owner"]`
- gates: `["HUMAN_REVIEW_REQUIRED", "TASK_ONLY"]`
- graph_effect: `create human review node`

## delta_graph_structure
- delta_id: `delta_graph_structure`
- definition: `Graph topology is incomplete, disconnected or mistyped.`
- symptoms: `["orphan node", "missing bridge", "wrong relation type"]`
- metrics: `["orphan_nodes", "missing_edges", "invalid_edge_types"]`
- controls: `["graph_repair_suggestion", "bridge_candidate_generation"]`
- gates: `["STRUCTURE_ONLY", "TASK_ONLY"]`
- graph_effect: `suggest structural repairs before decision`

## delta_model_behavior
- delta_id: `delta_model_behavior`
- definition: `Observed model behavior deviates from expected calibration pattern.`
- symptoms: `["low ambiguity high hallucination", "unexpected control drop"]`
- metrics: `["anomaly_rate", "casulo_hallucination", "delta_control_score"]`
- controls: `["calibration_review", "repeat_seed_test"]`
- gates: `["HUMAN_REVIEW_REQUIRED", "TASK_ONLY"]`
- graph_effect: `telemetry node links anomaly pattern to control`

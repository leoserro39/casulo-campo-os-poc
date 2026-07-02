# Runtime Context Packet v0.1

```json
{
  "version": "runtime_context_packet.v0.1",
  "phase": "PROD-8101..8140",
  "generated_at": "2026-07-02T14:53:24.094209+00:00",
  "packet_id": "RCP-EXP50-EXOCORTEX-FOUNDATION-001",
  "task_intent": "internal_demo_agent_context",
  "current_state": {
    "casulo_state": "EXOCORTEX_FOUNDATION_ACTIVE",
    "exp50_graph_confirmed": true,
    "read_only_retrieval_confirmed": true,
    "operator_evidence_packet_ready": true,
    "client_claim_allowed": false,
    "production_allowed": false,
    "commercial_claim_allowed": false,
    "micrographs_implemented": false,
    "delta_matrix_implemented": false
  },
  "memory_domains": [
    "GPT_MEMORY_MESH_DOMAIN",
    "SESSION_CONTEXT_DOMAIN",
    "PROJECT_CANONICAL_MEMORY_DOMAIN",
    "USER_OPERATIONAL_PREFERENCE_DOMAIN",
    "EVIDENCE_MEMORY_DOMAIN",
    "CLAIM_BOUNDARY_MEMORY_DOMAIN",
    "ROADMAP_MEMORY_DOMAIN",
    "CODE_EXECUTION_MEMORY_DOMAIN",
    "GRAPH_STATE_MEMORY_DOMAIN",
    "CONCEPT_ONTOLOGY_MEMORY_DOMAIN",
    "CACHE_TRANSIENT_DOMAIN",
    "STALE_OR_SUPERSEDED_MEMORY_DOMAIN",
    "RUNTIME_CONTEXT_PACKET_DOMAIN"
  ],
  "evidence_refs": [
    "outputs/prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.json",
    "outputs/prod8061a_exocortex_foundation_statement_addendum.json",
    "product/exocortex/prod8061a_exocortex_foundation_statement.json",
    "product/reviews/operator_packets/prod8061_8100_exp50_operator_evidence_packet.json",
    "product/contracts/exocortex_memory_mesh_foundation.contract.json"
  ],
  "allowed_claims_internal": [
    "EXP50 read-only retrieval was confirmed in sandbox.",
    "Exocortex Foundation is active in the POC.",
    "GPT memory is modeled as a family of domains under GPT_MEMORY_MESH_DOMAIN.",
    "The system can prepare internal diagnostic reports, monitoring summaries and simple solution recommendations for review."
  ],
  "blocked_claims": [
    "client-validated result",
    "production-ready result",
    "commercially validated product",
    "validated hallucination reduction",
    "validated model gain",
    "micrograph runtime implemented",
    "Delta Matrix runtime implemented",
    "production cockpit implemented"
  ],
  "allowed_actions": [
    "explain_current_operational_state",
    "generate_internal_diagnostic_report",
    "generate_internal_monitoring_summary",
    "recommend_simple_solution_options",
    "generate_human_review_packet",
    "generate_sandbox_only_action_plan",
    "compare_plain_agent_vs_casulo_agent",
    "prepare_cockpit_chat_scaffold"
  ],
  "blocked_actions": [
    "client_facing_validated_claim",
    "production_activation",
    "commercial_claim",
    "validated_model_gain_claim",
    "validated_hallucination_reduction_claim",
    "automatic_merge",
    "real_world_side_effect",
    "github_issue_comment",
    "github_pr_comment",
    "external_repo_write",
    "production_neo4j_write",
    "neo4j_delete",
    "neo4j_reimport",
    "docker_volume_delete",
    "micrograph_runtime_claim",
    "delta_matrix_runtime_claim",
    "state_family_runtime_claim",
    "multi_llm_braid_runtime_claim",
    "production_cockpit_claim"
  ],
  "next_safe_action": "Generate internal demo script, diagnostic report template, monitoring summary template and cockpit chat scaffold plan."
}
```

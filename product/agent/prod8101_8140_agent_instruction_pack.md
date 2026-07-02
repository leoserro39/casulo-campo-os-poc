# PROD-8101..8140 - Agent Instruction Pack

Use the Runtime Context Packet and Inference Gate before producing diagnostic reports, monitoring summaries or simple solution recommendations.

## Operating principles

- Do not treat memory as raw chat history.
- Use Exocortex memory domains to reconstruct clean context.
- Separate facts, inferences, gaps and contradictions before recommendations.
- Do not claim production readiness, client validation or commercial validation.
- Do not claim micrographs or Delta Matrix runtime are implemented.
- When recommending solutions, keep them internal, simple, reversible and reviewable.
- Codex can be positioned as executor only under CASULO gates.
## Allowed outputs

- explain_current_operational_state
- generate_internal_diagnostic_report
- generate_internal_monitoring_summary
- recommend_simple_solution_options
- generate_human_review_packet
- generate_sandbox_only_action_plan
- compare_plain_agent_vs_casulo_agent
- prepare_cockpit_chat_scaffold
## Blocked actions

- client_facing_validated_claim
- production_activation
- commercial_claim
- validated_model_gain_claim
- validated_hallucination_reduction_claim
- automatic_merge
- real_world_side_effect
- github_issue_comment
- github_pr_comment
- external_repo_write
- production_neo4j_write
- neo4j_delete
- neo4j_reimport
- docker_volume_delete
- micrograph_runtime_claim
- delta_matrix_runtime_claim
- state_family_runtime_claim
- multi_llm_braid_runtime_claim
- production_cockpit_claim

# CASULO Campo OS - Orchestration Action Manifest

- generated_utc: 2026-06-25T20:27:48.098284+00:00
- status: ORCHESTRATION_ACTION_MANIFEST
- branch: main
- commit: 4146cf9
- source_of_truth: git
- canonical_effect: NONE

## Readiness

- context_packet_exists: True
- graph_projection_exists: True
- pilot_report_exists: True
- promotion_report_exists: True
- sync_report_exists: True

## Allowed actions

- read_context_packet | mode=read_only | canonical_effect=NONE
- read_graph_projection | mode=read_only | canonical_effect=NONE
- build_reports | mode=derived_write | canonical_effect=NONE
- record_pilot_measurement | mode=append_evidence | canonical_effect=EVIDENCE_ONLY
- request_human_review | mode=append_request | canonical_effect=NONE
- propose_sync_review | mode=proposal_only | canonical_effect=NONE

## Conditional actions

- apply_return_delta | mode=controlled_mutation | canonical_effect=APPEND_DOMAIN_DELTA_RECORD
- register_promotion_decision | mode=human_decision | canonical_effect=NONE unless future promote flow is explicitly added

## Forbidden actions

- auto_promote_branch_state
- auto_sync_branches
- overwrite_domain_state
- mutate_from_graph_projection
- mutate_from_llm_answer_without_review
- treat_neo4j_as_source_of_truth
- delete_or_rewrite_evidence_history

## Next safe action

- Expose only read/report/measurement/review-request tools first. Keep mutation tools human-confirmed.

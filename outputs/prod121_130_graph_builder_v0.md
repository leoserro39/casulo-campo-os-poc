# Graph Builder v0

- contract_version: `casulo.graph_builder.v0.1`
- status: `PASS`
- mode: `assisted_candidate_graph`

## Source Inventory
- `item` — {"source_id": "SRC-BRIEFING-001", "type": "briefing", "status": "AVAILABLE", "trust": "user_provided"}
- `item` — {"source_id": "SRC-DOCS-001", "type": "documents", "status": "AVAILABLE_OR_PENDING_UPLOAD", "trust": "evidence_candidate"}
- `item` — {"source_id": "SRC-RULES-001", "type": "system_rules", "status": "AVAILABLE_OR_PENDING_UPLOAD", "trust": "evidence_candidate"}
- `item` — {"source_id": "SRC-REPO-001", "type": "repository_summary", "status": "OPTIONAL", "trust": "evidence_candidate"}
- `item` — {"source_id": "SRC-DATA-001", "type": "anonymized_samples", "status": "OPTIONAL", "trust": "evidence_candidate"}

## Candidate Graph
- domains: `[{'id': 'domain_business_process', 'label': 'Business Process', 'confidence': 0.78, 'review': 'REQUIRED'}, {'id': 'domain_information', 'label': 'Information / Data', 'confidence': 0.74, 'review': 'REQUIRED'}, {'id': 'domain_system', 'label': 'System / Software', 'confidence': 0.72, 'review': 'REQUIRED'}, {'id': 'domain_decision', 'label': 'Decision / Governance', 'confidence': 0.8, 'review': 'REQUIRED'}, {'id': 'domain_evidence', 'label': 'Evidence / Audit', 'confidence': 0.84, 'review': 'REQUIRED'}]`
- entities: `[{'id': 'entity_company', 'type': 'organization', 'source': 'SRC-BRIEFING-001', 'evidence_status': 'SUPPORTED'}, {'id': 'entity_process', 'type': 'process', 'source': 'SRC-BRIEFING-001', 'evidence_status': 'PARTIAL'}, {'id': 'entity_rule_set', 'type': 'rule_set', 'source': 'SRC-RULES-001', 'evidence_status': 'PARTIAL_OR_PENDING'}, {'id': 'entity_artifact', 'type': 'artifact', 'source': 'SRC-DOCS-001', 'evidence_status': 'PARTIAL_OR_PENDING'}, {'id': 'entity_system', 'type': 'system_or_software', 'source': 'SRC-REPO-001', 'evidence_status': 'OPTIONAL'}, {'id': 'entity_decision', 'type': 'decision', 'source': 'CASULO', 'evidence_status': 'COMPUTED'}]`
- relations: `[{'from': 'entity_company', 'to': 'entity_process', 'relation': 'operates'}, {'from': 'entity_process', 'to': 'entity_rule_set', 'relation': 'is_constrained_by'}, {'from': 'entity_rule_set', 'to': 'entity_artifact', 'relation': 'requires_evidence_from'}, {'from': 'entity_system', 'to': 'entity_process', 'relation': 'supports_or_implements'}, {'from': 'entity_decision', 'to': 'entity_process', 'relation': 'governs'}]`
- human_review_required: `True`

## Artifact Map
- status: `PASS`
- artifact_classes: `[{'class': 'briefing', 'state_use': 'intent and scope', 'risk': 'ambiguous if not reviewed'}, {'class': 'rules', 'state_use': 'gate and parser/development constraints', 'risk': 'contradiction or incompleteness'}, {'class': 'samples', 'state_use': 'test cases and examples', 'risk': 'insufficient coverage'}, {'class': 'repository_summary', 'state_use': 'software review and task generation', 'risk': 'outdated or incomplete summary'}, {'class': 'dossier', 'state_use': 'evidence package', 'risk': 'source reliability and missing context'}]`
- rule: `Artifacts become evidence candidates until classified.`

## Operational States
- `Context Readiness` — {"state_id": "STATE-CONTEXT-001", "name": "Context Readiness", "status": "CHECK_REQUIRED", "reason": "Initial documentation can be accepted, but evidence classification and human review are required.", "reusable": true}
- `Candidate Graph` — {"state_id": "STATE-GRAPH-001", "name": "Candidate Graph", "status": "CANDIDATE_GRAPH_BUILT", "reason": "Domains, entities and relations are suggested, not final.", "reusable": true}
- `Recommendation Governance` — {"state_id": "STATE-RECOMMENDATION-001", "name": "Recommendation Governance", "status": "PARTIAL_RECOMMENDATION_ALLOWED", "reason": "Recommendations may be generated with caveats, gates and evidence limits.", "reusable": true}
- `Development Governance` — {"state_id": "STATE-DEVELOPMENT-001", "name": "Development Governance", "status": "TASK_ONLY_UNTIL_EVIDENCE", "reason": "Development can become tasks/contracts/tests, not production execution.", "reusable": true}

## Gates
- `item` — {"gate": "evidence_gate", "status": "CHECK_REQUIRED", "blocks": ["client_facing_claim"], "reason": "Documentation must be classified before external claim."}
- `item` — {"gate": "graph_review_gate", "status": "HUMAN_REVIEW_REQUIRED", "blocks": ["implementation_execution"], "reason": "Candidate graph must be reviewed before execution."}
- `item` — {"gate": "recommendation_gate", "status": "PARTIAL_ALLOWED", "blocks": ["production_activation"], "reason": "Recommendation can be caveated; production is blocked."}
- `item` — {"gate": "development_gate", "status": "TASK_ONLY", "blocks": ["automatic_merge", "production_activation"], "reason": "Development actions must go through tasks/tests/human review."}

## Deltas
- `item` — {"delta_id": "DELTA-EVIDENCE-001", "gap": "Some sources are pending, partial or candidate-only.", "next_action": "classify evidence and request missing data"}
- `item` — {"delta_id": "DELTA-GRAPH-001", "gap": "Graph is candidate, not confirmed truth.", "next_action": "human review of domains/entities/relations"}
- `item` — {"delta_id": "DELTA-POC-001", "gap": "POC can run but needs calibration with real/anonymous cases.", "next_action": "run first client-style POC test"}
- human_review_required: `True`

## Blocked Actions
- `client_facing_claim`
- `automatic_nomination`
- `implementation_execution`
- `production_activation`
- `automatic_merge`
- `credential_handling`

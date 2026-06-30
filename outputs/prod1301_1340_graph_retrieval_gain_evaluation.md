# PROD-1301..1340 Graph Retrieval Gain Evaluation

- Status: `PASS`
- Decision: `GRAPH_RETRIEVAL_GAIN_CONFIRMED_FOR_SANDBOX`
- Mode: `neo4j_sandbox_read_only_topology_aware_evaluation`
- CASULO nodes: `313`
- CASULO relationships: `350`

## Label Counts
- Case: `50`
- Evidence: `50`
- Gate: `50`
- HallucinationBudget: `50`
- OutputMode: `50`
- RiskSignal: `50`
- Domain: `12`
- ReadinessState: `1`

## Relationship Type Counts
- ALLOWS: `50`
- BELONGS_TO: `50`
- CONTRIBUTES_TO: `50`
- HAS_BUDGET: `50`
- HAS_EVIDENCE: `50`
- REQUIRES: `50`
- TRIGGERS: `50`

## Direct Context
- cases: `50`
- evidence_nodes: `50`
- risk_nodes: `50`
- budget_nodes: `50`
- domain_nodes: `12`

## Controlled Paths
- cases: `50`
- cases_reaching_gate_controlled: `50`
- cases_reaching_output_controlled: `50`

## Retrieval Gain
- import_match: `True`
- direct_context_ok: `True`
- controlled_path_ok: `True`

## Interpretation
Neo4j sandbox confirms topology-aware retrieval from Case to Evidence, RiskSignal, HallucinationBudget and Domain directly, and to Gate/OutputMode through controlled semantic paths.
This confirms sandbox graph retrieval value, but does not authorize production use or external claims.

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

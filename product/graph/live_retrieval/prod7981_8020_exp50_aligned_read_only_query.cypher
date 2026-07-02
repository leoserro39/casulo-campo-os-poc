// PROD-7981..8020 - EXP50 actual graph aligned retrieval query
// READ ONLY. Sandbox only.
// Do not run against production Neo4j.
// This query is aligned to the confirmed persisted graph:
// node_count=313, relationship_count=350, case_id_pattern=case:EXP50-*
//
// Expected core path for sample case EXP50-001:
// case:EXP50-001
//   -[:BELONGS_TO]-> domain:restaurant_inventory
//   -[:HAS_EVIDENCE]-> evidence:EXP50-001:complete_minimum_evidence
//   -[:TRIGGERS]-> risk:EXP50-001:clean_controlled_answer
//   -[:HAS_BUDGET]-> budget:EXP50-001
//   -[:REQUIRES]-> readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY
// risk:EXP50-001:clean_controlled_answer
//   -[:CONTRIBUTES_TO]-> gate:EXP50-001:ANSWER_ALLOWED
// gate:EXP50-001:ANSWER_ALLOWED
//   -[:ALLOWS]-> output:EXP50-001:ANSWER

MATCH (case_node {id: 'case:EXP50-001'})
OPTIONAL MATCH (case_node)-[belongs:BELONGS_TO]->(domain)
OPTIONAL MATCH (case_node)-[evidence_rel:HAS_EVIDENCE]->(evidence)
OPTIONAL MATCH (case_node)-[budget_rel:HAS_BUDGET]->(budget)
OPTIONAL MATCH (case_node)-[requires_rel:REQUIRES]->(readiness)
OPTIONAL MATCH (case_node)-[triggers_rel:TRIGGERS]->(risk)
OPTIONAL MATCH (risk)-[contributes_rel:CONTRIBUTES_TO]->(gate)
OPTIONAL MATCH (gate)-[allows_rel:ALLOWS]->(output)
RETURN
  case_node.id AS case_id,
  domain.id AS domain_id,
  evidence.id AS evidence_id,
  budget.id AS budget_id,
  readiness.id AS readiness_id,
  risk.id AS risk_id,
  gate.id AS gate_id,
  output.id AS output_id,
  [x IN [type(belongs), type(evidence_rel), type(budget_rel), type(requires_rel), type(triggers_rel), type(contributes_rel), type(allows_rel)] WHERE x IS NOT NULL] AS relationship_types,
  size([x IN [domain, evidence, budget, readiness, risk, gate, output] WHERE x IS NOT NULL]) + 1 AS nodes_observed,
  size([x IN [belongs, evidence_rel, budget_rel, requires_rel, triggers_rel, contributes_rel, allows_rel] WHERE x IS NOT NULL]) AS relationships_observed;

// CASULO Neo4j sandbox import preview
// Generated offline. Review before execution.
// Sandbox only. Do not run against production.
CREATE CONSTRAINT casulo_node_id IF NOT EXISTS FOR (n:CasuloNode) REQUIRE n.id IS UNIQUE;

MERGE (n:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
SET n:ReadinessState, n += {decision: "READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY", casulo_label: "ReadinessState"};

MERGE (n:CasuloNode {id: "case:EXP50-001"})
SET n:Case, n += {case_id: "EXP50-001", business_domain: "restaurant_inventory", risk_theme: "clean_controlled_answer", evidence_profile: "complete_minimum_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "domain:restaurant_inventory"})
SET n:Domain, n += {business_domain: "restaurant_inventory", activation_state: "CANDIDATE_DOMAIN_REQUIRE_EVIDENCE", preflight_score: 0.6964, casulo_label: "Domain"};

MERGE (n:CasuloNode {id: "evidence:EXP50-001:complete_minimum_evidence"})
SET n:Evidence, n += {case_id: "EXP50-001", evidence_profile: "complete_minimum_evidence", evidence_count: 5, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-001:clean_controlled_answer"})
SET n:RiskSignal, n += {case_id: "EXP50-001", risk_theme: "clean_controlled_answer", adjusted_risk: 33.75, risk_band: "MEDIUM", live_delta_score: 0.2481, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-001:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-001", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-001:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-001", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-001"})
SET n:HallucinationBudget, n += {case_id: "EXP50-001", hallucination_budget: 0.8406, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-002"})
SET n:Case, n += {case_id: "EXP50-002", business_domain: "restaurant_inventory", risk_theme: "missing_evidence", evidence_profile: "partial_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-002:partial_evidence"})
SET n:Evidence, n += {case_id: "EXP50-002", evidence_profile: "partial_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-002:missing_evidence"})
SET n:RiskSignal, n += {case_id: "EXP50-002", risk_theme: "missing_evidence", adjusted_risk: 57.95, risk_band: "HIGH", live_delta_score: 0.4912, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-002:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-002", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-002:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-002", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-002"})
SET n:HallucinationBudget, n += {case_id: "EXP50-002", hallucination_budget: 0.6762, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-003"})
SET n:Case, n += {case_id: "EXP50-003", business_domain: "restaurant_inventory", risk_theme: "conflicting_information", evidence_profile: "conflicting_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-003:conflicting_evidence"})
SET n:Evidence, n += {case_id: "EXP50-003", evidence_profile: "conflicting_evidence", evidence_count: 4, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-003:conflicting_information"})
SET n:RiskSignal, n += {case_id: "EXP50-003", risk_theme: "conflicting_information", adjusted_risk: 75.35, risk_band: "CRITICAL", live_delta_score: 0.5069, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-003:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-003", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-003:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-003", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-003"})
SET n:HallucinationBudget, n += {case_id: "EXP50-003", hallucination_budget: 0.6494, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-004"})
SET n:Case, n += {case_id: "EXP50-004", business_domain: "restaurant_inventory", risk_theme: "high_stakes_review", evidence_profile: "stale_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-004:stale_evidence"})
SET n:Evidence, n += {case_id: "EXP50-004", evidence_profile: "stale_evidence", evidence_count: 3, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-004:high_stakes_review"})
SET n:RiskSignal, n += {case_id: "EXP50-004", risk_theme: "high_stakes_review", adjusted_risk: 49.15, risk_band: "MEDIUM", live_delta_score: 0.4028, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-004:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-004", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-004:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-004", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-004"})
SET n:HallucinationBudget, n += {case_id: "EXP50-004", hallucination_budget: 0.7678, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-005"})
SET n:Case, n += {case_id: "EXP50-005", business_domain: "restaurant_cashflow", risk_theme: "clean_controlled_answer", evidence_profile: "high_sensitivity_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "domain:restaurant_cashflow"})
SET n:Domain, n += {business_domain: "restaurant_cashflow", activation_state: "CANDIDATE_DOMAIN_REQUIRE_EVIDENCE", preflight_score: 0.7084, casulo_label: "Domain"};

MERGE (n:CasuloNode {id: "evidence:EXP50-005:high_sensitivity_evidence"})
SET n:Evidence, n += {case_id: "EXP50-005", evidence_profile: "high_sensitivity_evidence", evidence_count: 3, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-005:clean_controlled_answer"})
SET n:RiskSignal, n += {case_id: "EXP50-005", risk_theme: "clean_controlled_answer", adjusted_risk: 55.9, risk_band: "HIGH", live_delta_score: 0.5191, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-005:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-005", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-005:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-005", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-005"})
SET n:HallucinationBudget, n += {case_id: "EXP50-005", hallucination_budget: 0.7215, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-006"})
SET n:Case, n += {case_id: "EXP50-006", business_domain: "restaurant_cashflow", risk_theme: "missing_evidence", evidence_profile: "complete_minimum_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-006:complete_minimum_evidence"})
SET n:Evidence, n += {case_id: "EXP50-006", evidence_profile: "complete_minimum_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-006:missing_evidence"})
SET n:RiskSignal, n += {case_id: "EXP50-006", risk_theme: "missing_evidence", adjusted_risk: 61.95, risk_band: "HIGH", live_delta_score: 0.5799, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-006:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-006", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-006:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-006", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-006"})
SET n:HallucinationBudget, n += {case_id: "EXP50-006", hallucination_budget: 0.6429, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-007"})
SET n:Case, n += {case_id: "EXP50-007", business_domain: "restaurant_cashflow", risk_theme: "conflicting_information", evidence_profile: "partial_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-007:partial_evidence"})
SET n:Evidence, n += {case_id: "EXP50-007", evidence_profile: "partial_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-007:conflicting_information"})
SET n:RiskSignal, n += {case_id: "EXP50-007", risk_theme: "conflicting_information", adjusted_risk: 96.95, risk_band: "CRITICAL", live_delta_score: 0.7724, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-007:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-007", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-007:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-007", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-007"})
SET n:HallucinationBudget, n += {case_id: "EXP50-007", hallucination_budget: 0.5329, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-008"})
SET n:Case, n += {case_id: "EXP50-008", business_domain: "restaurant_cashflow", risk_theme: "high_stakes_review", evidence_profile: "conflicting_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-008:conflicting_evidence"})
SET n:Evidence, n += {case_id: "EXP50-008", evidence_profile: "conflicting_evidence", evidence_count: 4, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-008:high_stakes_review"})
SET n:RiskSignal, n += {case_id: "EXP50-008", risk_theme: "high_stakes_review", adjusted_risk: 44.35, risk_band: "MEDIUM", live_delta_score: 0.4031, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-008:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-008", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-008:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-008", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-008"})
SET n:HallucinationBudget, n += {case_id: "EXP50-008", hallucination_budget: 0.7761, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-009"})
SET n:Case, n += {case_id: "EXP50-009", business_domain: "clinic_scheduling", risk_theme: "clean_controlled_answer", evidence_profile: "stale_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "domain:clinic_scheduling"})
SET n:Domain, n += {business_domain: "clinic_scheduling", activation_state: "CANDIDATE_DOMAIN_REQUIRE_EVIDENCE", preflight_score: 0.6444, casulo_label: "Domain"};

MERGE (n:CasuloNode {id: "evidence:EXP50-009:stale_evidence"})
SET n:Evidence, n += {case_id: "EXP50-009", evidence_profile: "stale_evidence", evidence_count: 3, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-009:clean_controlled_answer"})
SET n:RiskSignal, n += {case_id: "EXP50-009", risk_theme: "clean_controlled_answer", adjusted_risk: 53.15, risk_band: "MEDIUM", live_delta_score: 0.4915, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-009:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-009", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-009:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-009", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-009"})
SET n:HallucinationBudget, n += {case_id: "EXP50-009", hallucination_budget: 0.7345, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-010"})
SET n:Case, n += {case_id: "EXP50-010", business_domain: "clinic_scheduling", risk_theme: "missing_evidence", evidence_profile: "high_sensitivity_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-010:high_sensitivity_evidence"})
SET n:Evidence, n += {case_id: "EXP50-010", evidence_profile: "high_sensitivity_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-010:missing_evidence"})
SET n:RiskSignal, n += {case_id: "EXP50-010", risk_theme: "missing_evidence", adjusted_risk: 64.7, risk_band: "HIGH", live_delta_score: 0.6075, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-010:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-010", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-010:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-010", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-010"})
SET n:HallucinationBudget, n += {case_id: "EXP50-010", hallucination_budget: 0.6299, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-011"})
SET n:Case, n += {case_id: "EXP50-011", business_domain: "clinic_scheduling", risk_theme: "conflicting_information", evidence_profile: "complete_minimum_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-011:complete_minimum_evidence"})
SET n:Evidence, n += {case_id: "EXP50-011", evidence_profile: "complete_minimum_evidence", evidence_count: 5, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-011:conflicting_information"})
SET n:RiskSignal, n += {case_id: "EXP50-011", risk_theme: "conflicting_information", adjusted_risk: 72.75, risk_band: "HIGH", live_delta_score: 0.5293, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-011:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-011", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-011:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-011", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-011"})
SET n:HallucinationBudget, n += {case_id: "EXP50-011", hallucination_budget: 0.6473, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-012"})
SET n:Case, n += {case_id: "EXP50-012", business_domain: "clinic_scheduling", risk_theme: "high_stakes_review", evidence_profile: "partial_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-012:partial_evidence"})
SET n:Evidence, n += {case_id: "EXP50-012", evidence_profile: "partial_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-012:high_stakes_review"})
SET n:RiskSignal, n += {case_id: "EXP50-012", risk_theme: "high_stakes_review", adjusted_risk: 61.95, risk_band: "HIGH", live_delta_score: 0.5799, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-012:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-012", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-012:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-012", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-012"})
SET n:HallucinationBudget, n += {case_id: "EXP50-012", hallucination_budget: 0.6429, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-013"})
SET n:Case, n += {case_id: "EXP50-013", business_domain: "clinic_billing_glosa", risk_theme: "clean_controlled_answer", evidence_profile: "conflicting_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "domain:clinic_billing_glosa"})
SET n:Domain, n += {business_domain: "clinic_billing_glosa", activation_state: "CANDIDATE_DOMAIN_REQUIRE_EVIDENCE", preflight_score: 0.7074, casulo_label: "Domain"};

MERGE (n:CasuloNode {id: "evidence:EXP50-013:conflicting_evidence"})
SET n:Evidence, n += {case_id: "EXP50-013", evidence_profile: "conflicting_evidence", evidence_count: 4, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-013:clean_controlled_answer"})
SET n:RiskSignal, n += {case_id: "EXP50-013", risk_theme: "clean_controlled_answer", adjusted_risk: 49.35, risk_band: "MEDIUM", live_delta_score: 0.5139, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-013:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-013", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-013:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-013", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-013"})
SET n:HallucinationBudget, n += {case_id: "EXP50-013", hallucination_budget: 0.7344, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-014"})
SET n:Case, n += {case_id: "EXP50-014", business_domain: "clinic_billing_glosa", risk_theme: "missing_evidence", evidence_profile: "stale_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-014:stale_evidence"})
SET n:Evidence, n += {case_id: "EXP50-014", evidence_profile: "stale_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-014:missing_evidence"})
SET n:RiskSignal, n += {case_id: "EXP50-014", risk_theme: "missing_evidence", adjusted_risk: 66.95, risk_band: "HIGH", live_delta_score: 0.6907, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-014:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-014", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-014:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-014", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-014"})
SET n:HallucinationBudget, n += {case_id: "EXP50-014", hallucination_budget: 0.6512, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-015"})
SET n:Case, n += {case_id: "EXP50-015", business_domain: "clinic_billing_glosa", risk_theme: "conflicting_information", evidence_profile: "high_sensitivity_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-015:high_sensitivity_evidence"})
SET n:Evidence, n += {case_id: "EXP50-015", evidence_profile: "high_sensitivity_evidence", evidence_count: 3, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-015:conflicting_information"})
SET n:RiskSignal, n += {case_id: "EXP50-015", risk_theme: "conflicting_information", adjusted_risk: 95.9, risk_band: "CRITICAL", live_delta_score: 0.8225, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-015:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-015", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-015:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-015", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-015"})
SET n:HallucinationBudget, n += {case_id: "EXP50-015", hallucination_budget: 0.5198, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-016"})
SET n:Case, n += {case_id: "EXP50-016", business_domain: "clinic_billing_glosa", risk_theme: "high_stakes_review", evidence_profile: "complete_minimum_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-016:complete_minimum_evidence"})
SET n:Evidence, n += {case_id: "EXP50-016", evidence_profile: "complete_minimum_evidence", evidence_count: 5, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-016:high_stakes_review"})
SET n:RiskSignal, n += {case_id: "EXP50-016", risk_theme: "high_stakes_review", adjusted_risk: 42.75, risk_band: "MEDIUM", live_delta_score: 0.4476, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-016:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-016", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-016:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-016", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-016"})
SET n:HallucinationBudget, n += {case_id: "EXP50-016", hallucination_budget: 0.7656, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-017"})
SET n:Case, n += {case_id: "EXP50-017", business_domain: "accounting_tax_obligation", risk_theme: "clean_controlled_answer", evidence_profile: "partial_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "domain:accounting_tax_obligation"})
SET n:Domain, n += {business_domain: "accounting_tax_obligation", activation_state: "CANDIDATE_DOMAIN_REQUIRE_EVIDENCE", preflight_score: 0.6414, casulo_label: "Domain"};

MERGE (n:CasuloNode {id: "evidence:EXP50-017:partial_evidence"})
SET n:Evidence, n += {case_id: "EXP50-017", evidence_profile: "partial_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-017:clean_controlled_answer"})
SET n:RiskSignal, n += {case_id: "EXP50-017", risk_theme: "clean_controlled_answer", adjusted_risk: 66.95, risk_band: "HIGH", live_delta_score: 0.6907, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-017:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-017", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-017:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-017", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-017"})
SET n:HallucinationBudget, n += {case_id: "EXP50-017", hallucination_budget: 0.6012, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-018"})
SET n:Case, n += {case_id: "EXP50-018", business_domain: "accounting_tax_obligation", risk_theme: "missing_evidence", evidence_profile: "conflicting_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-018:conflicting_evidence"})
SET n:Evidence, n += {case_id: "EXP50-018", evidence_profile: "conflicting_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-018:missing_evidence"})
SET n:RiskSignal, n += {case_id: "EXP50-018", risk_theme: "missing_evidence", adjusted_risk: 66.95, risk_band: "HIGH", live_delta_score: 0.6907, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-018:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-018", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-018:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-018", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-018"})
SET n:HallucinationBudget, n += {case_id: "EXP50-018", hallucination_budget: 0.6012, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-019"})
SET n:Case, n += {case_id: "EXP50-019", business_domain: "accounting_tax_obligation", risk_theme: "conflicting_information", evidence_profile: "stale_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-019:stale_evidence"})
SET n:Evidence, n += {case_id: "EXP50-019", evidence_profile: "stale_evidence", evidence_count: 3, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-019:conflicting_information"})
SET n:RiskSignal, n += {case_id: "EXP50-019", risk_theme: "conflicting_information", adjusted_risk: 93.15, risk_band: "CRITICAL", live_delta_score: 0.7948, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-019:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-019", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-019:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-019", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-019"})
SET n:HallucinationBudget, n += {case_id: "EXP50-019", hallucination_budget: 0.5328, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-020"})
SET n:Case, n += {case_id: "EXP50-020", business_domain: "accounting_tax_obligation", risk_theme: "high_stakes_review", evidence_profile: "high_sensitivity_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-020:high_sensitivity_evidence"})
SET n:Evidence, n += {case_id: "EXP50-020", evidence_profile: "high_sensitivity_evidence", evidence_count: 3, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-020:high_stakes_review"})
SET n:RiskSignal, n += {case_id: "EXP50-020", risk_theme: "high_stakes_review", adjusted_risk: 60.9, risk_band: "HIGH", live_delta_score: 0.63, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-020:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-020", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-020:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-020", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-020"})
SET n:HallucinationBudget, n += {case_id: "EXP50-020", hallucination_budget: 0.6798, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-021"})
SET n:Case, n += {case_id: "EXP50-021", business_domain: "contract_legal_review", risk_theme: "clean_controlled_answer", evidence_profile: "complete_minimum_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "domain:contract_legal_review"})
SET n:Domain, n += {business_domain: "contract_legal_review", activation_state: "CANDIDATE_DOMAIN_REQUIRE_EVIDENCE", preflight_score: 0.6464, casulo_label: "Domain"};

MERGE (n:CasuloNode {id: "evidence:EXP50-021:complete_minimum_evidence"})
SET n:Evidence, n += {case_id: "EXP50-021", evidence_profile: "complete_minimum_evidence", evidence_count: 5, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-021:clean_controlled_answer"})
SET n:RiskSignal, n += {case_id: "EXP50-021", risk_theme: "clean_controlled_answer", adjusted_risk: 43.75, risk_band: "MEDIUM", live_delta_score: 0.4698, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-021:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-021", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-021:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-021", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-021"})
SET n:HallucinationBudget, n += {case_id: "EXP50-021", hallucination_budget: 0.7573, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-022"})
SET n:Case, n += {case_id: "EXP50-022", business_domain: "contract_legal_review", risk_theme: "missing_evidence", evidence_profile: "partial_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-022:partial_evidence"})
SET n:Evidence, n += {case_id: "EXP50-022", evidence_profile: "partial_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-022:missing_evidence"})
SET n:RiskSignal, n += {case_id: "EXP50-022", risk_theme: "missing_evidence", adjusted_risk: 67.95, risk_band: "HIGH", live_delta_score: 0.7129, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-022:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-022", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-022:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-022", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-022"})
SET n:HallucinationBudget, n += {case_id: "EXP50-022", hallucination_budget: 0.5929, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-023"})
SET n:Case, n += {case_id: "EXP50-023", business_domain: "contract_legal_review", risk_theme: "conflicting_information", evidence_profile: "conflicting_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-023:conflicting_evidence"})
SET n:Evidence, n += {case_id: "EXP50-023", evidence_profile: "conflicting_evidence", evidence_count: 4, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-023:conflicting_information"})
SET n:RiskSignal, n += {case_id: "EXP50-023", risk_theme: "conflicting_information", adjusted_risk: 85.35, risk_band: "CRITICAL", live_delta_score: 0.7286, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-023:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-023", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-023:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-023", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-023"})
SET n:HallucinationBudget, n += {case_id: "EXP50-023", hallucination_budget: 0.5661, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-024"})
SET n:Case, n += {case_id: "EXP50-024", business_domain: "contract_legal_review", risk_theme: "high_stakes_review", evidence_profile: "stale_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-024:stale_evidence"})
SET n:Evidence, n += {case_id: "EXP50-024", evidence_profile: "stale_evidence", evidence_count: 3, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-024:high_stakes_review"})
SET n:RiskSignal, n += {case_id: "EXP50-024", risk_theme: "high_stakes_review", adjusted_risk: 59.15, risk_band: "HIGH", live_delta_score: 0.6245, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-024:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-024", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-024:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-024", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-024"})
SET n:HallucinationBudget, n += {case_id: "EXP50-024", hallucination_budget: 0.6845, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-025"})
SET n:Case, n += {case_id: "EXP50-025", business_domain: "ecommerce_order_ops", risk_theme: "clean_controlled_answer", evidence_profile: "high_sensitivity_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "domain:ecommerce_order_ops"})
SET n:Domain, n += {business_domain: "ecommerce_order_ops", activation_state: "CANDIDATE_DOMAIN_REQUIRE_EVIDENCE", preflight_score: 0.6564, casulo_label: "Domain"};

MERGE (n:CasuloNode {id: "evidence:EXP50-025:high_sensitivity_evidence"})
SET n:Evidence, n += {case_id: "EXP50-025", evidence_profile: "high_sensitivity_evidence", evidence_count: 3, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-025:clean_controlled_answer"})
SET n:RiskSignal, n += {case_id: "EXP50-025", risk_theme: "clean_controlled_answer", adjusted_risk: 53.9, risk_band: "MEDIUM", live_delta_score: 0.4748, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-025:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-025", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-025:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-025", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-025"})
SET n:HallucinationBudget, n += {case_id: "EXP50-025", hallucination_budget: 0.7381, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-026"})
SET n:Case, n += {case_id: "EXP50-026", business_domain: "ecommerce_order_ops", risk_theme: "missing_evidence", evidence_profile: "complete_minimum_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-026:complete_minimum_evidence"})
SET n:Evidence, n += {case_id: "EXP50-026", evidence_profile: "complete_minimum_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-026:missing_evidence"})
SET n:RiskSignal, n += {case_id: "EXP50-026", risk_theme: "missing_evidence", adjusted_risk: 59.95, risk_band: "HIGH", live_delta_score: 0.5356, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-026:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-026", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-026:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-026", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-026"})
SET n:HallucinationBudget, n += {case_id: "EXP50-026", hallucination_budget: 0.6595, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-027"})
SET n:Case, n += {case_id: "EXP50-027", business_domain: "ecommerce_order_ops", risk_theme: "conflicting_information", evidence_profile: "partial_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-027:partial_evidence"})
SET n:Evidence, n += {case_id: "EXP50-027", evidence_profile: "partial_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-027:conflicting_information"})
SET n:RiskSignal, n += {case_id: "EXP50-027", risk_theme: "conflicting_information", adjusted_risk: 94.95, risk_band: "CRITICAL", live_delta_score: 0.7281, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-027:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-027", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-027:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-027", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-027"})
SET n:HallucinationBudget, n += {case_id: "EXP50-027", hallucination_budget: 0.5495, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-028"})
SET n:Case, n += {case_id: "EXP50-028", business_domain: "ecommerce_order_ops", risk_theme: "high_stakes_review", evidence_profile: "conflicting_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-028:conflicting_evidence"})
SET n:Evidence, n += {case_id: "EXP50-028", evidence_profile: "conflicting_evidence", evidence_count: 4, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-028:high_stakes_review"})
SET n:RiskSignal, n += {case_id: "EXP50-028", risk_theme: "high_stakes_review", adjusted_risk: 42.35, risk_band: "MEDIUM", live_delta_score: 0.3588, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-028:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-028", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-028:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-028", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-028"})
SET n:HallucinationBudget, n += {case_id: "EXP50-028", hallucination_budget: 0.7927, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-029"})
SET n:Case, n += {case_id: "EXP50-029", business_domain: "field_service_work_order", risk_theme: "clean_controlled_answer", evidence_profile: "stale_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "domain:field_service_work_order"})
SET n:Domain, n += {business_domain: "field_service_work_order", activation_state: "CANDIDATE_DOMAIN_REQUIRE_EVIDENCE", preflight_score: 0.6594, casulo_label: "Domain"};

MERGE (n:CasuloNode {id: "evidence:EXP50-029:stale_evidence"})
SET n:Evidence, n += {case_id: "EXP50-029", evidence_profile: "stale_evidence", evidence_count: 3, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-029:clean_controlled_answer"})
SET n:RiskSignal, n += {case_id: "EXP50-029", risk_theme: "clean_controlled_answer", adjusted_risk: 50.15, risk_band: "MEDIUM", live_delta_score: 0.425, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-029:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-029", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-029:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-029", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-029"})
SET n:HallucinationBudget, n += {case_id: "EXP50-029", hallucination_budget: 0.7595, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-030"})
SET n:Case, n += {case_id: "EXP50-030", business_domain: "field_service_work_order", risk_theme: "missing_evidence", evidence_profile: "high_sensitivity_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-030:high_sensitivity_evidence"})
SET n:Evidence, n += {case_id: "EXP50-030", evidence_profile: "high_sensitivity_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-030:missing_evidence"})
SET n:RiskSignal, n += {case_id: "EXP50-030", risk_theme: "missing_evidence", adjusted_risk: 61.7, risk_band: "HIGH", live_delta_score: 0.541, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-030:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-030", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-030:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-030", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-030"})
SET n:HallucinationBudget, n += {case_id: "EXP50-030", hallucination_budget: 0.6549, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-031"})
SET n:Case, n += {case_id: "EXP50-031", business_domain: "field_service_work_order", risk_theme: "conflicting_information", evidence_profile: "complete_minimum_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-031:complete_minimum_evidence"})
SET n:Evidence, n += {case_id: "EXP50-031", evidence_profile: "complete_minimum_evidence", evidence_count: 5, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-031:conflicting_information"})
SET n:RiskSignal, n += {case_id: "EXP50-031", risk_theme: "conflicting_information", adjusted_risk: 69.75, risk_band: "HIGH", live_delta_score: 0.4628, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-031:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-031", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-031:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-031", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-031"})
SET n:HallucinationBudget, n += {case_id: "EXP50-031", hallucination_budget: 0.6723, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-032"})
SET n:Case, n += {case_id: "EXP50-032", business_domain: "field_service_work_order", risk_theme: "high_stakes_review", evidence_profile: "partial_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-032:partial_evidence"})
SET n:Evidence, n += {case_id: "EXP50-032", evidence_profile: "partial_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-032:high_stakes_review"})
SET n:RiskSignal, n += {case_id: "EXP50-032", risk_theme: "high_stakes_review", adjusted_risk: 58.95, risk_band: "HIGH", live_delta_score: 0.5134, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-032:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-032", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-032:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-032", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-032"})
SET n:HallucinationBudget, n += {case_id: "EXP50-032", hallucination_budget: 0.6679, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-033"})
SET n:Case, n += {case_id: "EXP50-033", business_domain: "construction_project_control", risk_theme: "clean_controlled_answer", evidence_profile: "conflicting_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "domain:construction_project_control"})
SET n:Domain, n += {business_domain: "construction_project_control", activation_state: "CANDIDATE_DOMAIN_REQUIRE_EVIDENCE", preflight_score: 0.7224, casulo_label: "Domain"};

MERGE (n:CasuloNode {id: "evidence:EXP50-033:conflicting_evidence"})
SET n:Evidence, n += {case_id: "EXP50-033", evidence_profile: "conflicting_evidence", evidence_count: 4, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-033:clean_controlled_answer"})
SET n:RiskSignal, n += {case_id: "EXP50-033", risk_theme: "clean_controlled_answer", adjusted_risk: 46.35, risk_band: "MEDIUM", live_delta_score: 0.4474, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-033:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-033", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-033:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-033", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-033"})
SET n:HallucinationBudget, n += {case_id: "EXP50-033", hallucination_budget: 0.7594, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-034"})
SET n:Case, n += {case_id: "EXP50-034", business_domain: "construction_project_control", risk_theme: "missing_evidence", evidence_profile: "stale_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-034:stale_evidence"})
SET n:Evidence, n += {case_id: "EXP50-034", evidence_profile: "stale_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-034:missing_evidence"})
SET n:RiskSignal, n += {case_id: "EXP50-034", risk_theme: "missing_evidence", adjusted_risk: 63.95, risk_band: "HIGH", live_delta_score: 0.6242, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-034:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-034", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-034:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-034", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-034"})
SET n:HallucinationBudget, n += {case_id: "EXP50-034", hallucination_budget: 0.6262, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-035"})
SET n:Case, n += {case_id: "EXP50-035", business_domain: "construction_project_control", risk_theme: "conflicting_information", evidence_profile: "high_sensitivity_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-035:high_sensitivity_evidence"})
SET n:Evidence, n += {case_id: "EXP50-035", evidence_profile: "high_sensitivity_evidence", evidence_count: 3, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-035:conflicting_information"})
SET n:RiskSignal, n += {case_id: "EXP50-035", risk_theme: "conflicting_information", adjusted_risk: 92.9, risk_band: "CRITICAL", live_delta_score: 0.756, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-035:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-035", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-035:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-035", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-035"})
SET n:HallucinationBudget, n += {case_id: "EXP50-035", hallucination_budget: 0.5448, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-036"})
SET n:Case, n += {case_id: "EXP50-036", business_domain: "construction_project_control", risk_theme: "high_stakes_review", evidence_profile: "complete_minimum_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-036:complete_minimum_evidence"})
SET n:Evidence, n += {case_id: "EXP50-036", evidence_profile: "complete_minimum_evidence", evidence_count: 5, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-036:high_stakes_review"})
SET n:RiskSignal, n += {case_id: "EXP50-036", risk_theme: "high_stakes_review", adjusted_risk: 39.75, risk_band: "MEDIUM", live_delta_score: 0.3811, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-036:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-036", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-036:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-036", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-036"})
SET n:HallucinationBudget, n += {case_id: "EXP50-036", hallucination_budget: 0.7906, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-037"})
SET n:Case, n += {case_id: "EXP50-037", business_domain: "small_industry_quality", risk_theme: "clean_controlled_answer", evidence_profile: "partial_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "domain:small_industry_quality"})
SET n:Domain, n += {business_domain: "small_industry_quality", activation_state: "CANDIDATE_DOMAIN_REQUIRE_EVIDENCE", preflight_score: 0.6614, casulo_label: "Domain"};

MERGE (n:CasuloNode {id: "evidence:EXP50-037:partial_evidence"})
SET n:Evidence, n += {case_id: "EXP50-037", evidence_profile: "partial_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-037:clean_controlled_answer"})
SET n:RiskSignal, n += {case_id: "EXP50-037", risk_theme: "clean_controlled_answer", adjusted_risk: 62.95, risk_band: "HIGH", live_delta_score: 0.6021, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-037:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-037", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-037:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-037", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-037"})
SET n:HallucinationBudget, n += {case_id: "EXP50-037", hallucination_budget: 0.6345, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-038"})
SET n:Case, n += {case_id: "EXP50-038", business_domain: "small_industry_quality", risk_theme: "missing_evidence", evidence_profile: "conflicting_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-038:conflicting_evidence"})
SET n:Evidence, n += {case_id: "EXP50-038", evidence_profile: "conflicting_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-038:missing_evidence"})
SET n:RiskSignal, n += {case_id: "EXP50-038", risk_theme: "missing_evidence", adjusted_risk: 62.95, risk_band: "HIGH", live_delta_score: 0.6021, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-038:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-038", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-038:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-038", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-038"})
SET n:HallucinationBudget, n += {case_id: "EXP50-038", hallucination_budget: 0.6345, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-039"})
SET n:Case, n += {case_id: "EXP50-039", business_domain: "small_industry_quality", risk_theme: "conflicting_information", evidence_profile: "stale_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-039:stale_evidence"})
SET n:Evidence, n += {case_id: "EXP50-039", evidence_profile: "stale_evidence", evidence_count: 3, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-039:conflicting_information"})
SET n:RiskSignal, n += {case_id: "EXP50-039", risk_theme: "conflicting_information", adjusted_risk: 89.15, risk_band: "CRITICAL", live_delta_score: 0.7062, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-039:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-039", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-039:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-039", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-039"})
SET n:HallucinationBudget, n += {case_id: "EXP50-039", hallucination_budget: 0.5661, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-040"})
SET n:Case, n += {case_id: "EXP50-040", business_domain: "small_industry_quality", risk_theme: "high_stakes_review", evidence_profile: "high_sensitivity_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-040:high_sensitivity_evidence"})
SET n:Evidence, n += {case_id: "EXP50-040", evidence_profile: "high_sensitivity_evidence", evidence_count: 3, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-040:high_stakes_review"})
SET n:RiskSignal, n += {case_id: "EXP50-040", risk_theme: "high_stakes_review", adjusted_risk: 56.9, risk_band: "HIGH", live_delta_score: 0.5413, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-040:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-040", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-040:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-040", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-040"})
SET n:HallucinationBudget, n += {case_id: "EXP50-040", hallucination_budget: 0.7131, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-041"})
SET n:Case, n += {case_id: "EXP50-041", business_domain: "legal_office_case_intake", risk_theme: "clean_controlled_answer", evidence_profile: "complete_minimum_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "domain:legal_office_case_intake"})
SET n:Domain, n += {business_domain: "legal_office_case_intake", activation_state: "CANDIDATE_DOMAIN_REQUIRE_EVIDENCE", preflight_score: 0.6464, casulo_label: "Domain"};

MERGE (n:CasuloNode {id: "evidence:EXP50-041:complete_minimum_evidence"})
SET n:Evidence, n += {case_id: "EXP50-041", evidence_profile: "complete_minimum_evidence", evidence_count: 5, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-041:clean_controlled_answer"})
SET n:RiskSignal, n += {case_id: "EXP50-041", risk_theme: "clean_controlled_answer", adjusted_risk: 43.75, risk_band: "MEDIUM", live_delta_score: 0.4698, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-041:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-041", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-041:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-041", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-041"})
SET n:HallucinationBudget, n += {case_id: "EXP50-041", hallucination_budget: 0.7573, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-042"})
SET n:Case, n += {case_id: "EXP50-042", business_domain: "legal_office_case_intake", risk_theme: "missing_evidence", evidence_profile: "partial_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-042:partial_evidence"})
SET n:Evidence, n += {case_id: "EXP50-042", evidence_profile: "partial_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-042:missing_evidence"})
SET n:RiskSignal, n += {case_id: "EXP50-042", risk_theme: "missing_evidence", adjusted_risk: 67.95, risk_band: "HIGH", live_delta_score: 0.7129, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-042:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-042", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-042:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-042", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-042"})
SET n:HallucinationBudget, n += {case_id: "EXP50-042", hallucination_budget: 0.5929, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-043"})
SET n:Case, n += {case_id: "EXP50-043", business_domain: "legal_office_case_intake", risk_theme: "conflicting_information", evidence_profile: "conflicting_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-043:conflicting_evidence"})
SET n:Evidence, n += {case_id: "EXP50-043", evidence_profile: "conflicting_evidence", evidence_count: 4, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-043:conflicting_information"})
SET n:RiskSignal, n += {case_id: "EXP50-043", risk_theme: "conflicting_information", adjusted_risk: 85.35, risk_band: "CRITICAL", live_delta_score: 0.7286, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-043:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-043", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-043:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-043", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-043"})
SET n:HallucinationBudget, n += {case_id: "EXP50-043", hallucination_budget: 0.5661, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-044"})
SET n:Case, n += {case_id: "EXP50-044", business_domain: "legal_office_case_intake", risk_theme: "high_stakes_review", evidence_profile: "stale_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-044:stale_evidence"})
SET n:Evidence, n += {case_id: "EXP50-044", evidence_profile: "stale_evidence", evidence_count: 3, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-044:high_stakes_review"})
SET n:RiskSignal, n += {case_id: "EXP50-044", risk_theme: "high_stakes_review", adjusted_risk: 59.15, risk_band: "HIGH", live_delta_score: 0.6245, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-044:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-044", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-044:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-044", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-044"})
SET n:HallucinationBudget, n += {case_id: "EXP50-044", hallucination_budget: 0.6845, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-045"})
SET n:Case, n += {case_id: "EXP50-045", business_domain: "fleet_maintenance_ops", risk_theme: "clean_controlled_answer", evidence_profile: "high_sensitivity_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "domain:fleet_maintenance_ops"})
SET n:Domain, n += {business_domain: "fleet_maintenance_ops", activation_state: "CANDIDATE_DOMAIN_REQUIRE_EVIDENCE", preflight_score: 0.7324, casulo_label: "Domain"};

MERGE (n:CasuloNode {id: "evidence:EXP50-045:high_sensitivity_evidence"})
SET n:Evidence, n += {case_id: "EXP50-045", evidence_profile: "high_sensitivity_evidence", evidence_count: 3, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-045:clean_controlled_answer"})
SET n:RiskSignal, n += {case_id: "EXP50-045", risk_theme: "clean_controlled_answer", adjusted_risk: 55.9, risk_band: "HIGH", live_delta_score: 0.5191, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-045:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-045", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-045:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-045", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-045"})
SET n:HallucinationBudget, n += {case_id: "EXP50-045", hallucination_budget: 0.7215, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-046"})
SET n:Case, n += {case_id: "EXP50-046", business_domain: "fleet_maintenance_ops", risk_theme: "missing_evidence", evidence_profile: "complete_minimum_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-046:complete_minimum_evidence"})
SET n:Evidence, n += {case_id: "EXP50-046", evidence_profile: "complete_minimum_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-046:missing_evidence"})
SET n:RiskSignal, n += {case_id: "EXP50-046", risk_theme: "missing_evidence", adjusted_risk: 61.95, risk_band: "HIGH", live_delta_score: 0.5799, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-046:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-046", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-046:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-046", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-046"})
SET n:HallucinationBudget, n += {case_id: "EXP50-046", hallucination_budget: 0.6429, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-047"})
SET n:Case, n += {case_id: "EXP50-047", business_domain: "fleet_maintenance_ops", risk_theme: "conflicting_information", evidence_profile: "partial_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-047:partial_evidence"})
SET n:Evidence, n += {case_id: "EXP50-047", evidence_profile: "partial_evidence", evidence_count: 2, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-047:conflicting_information"})
SET n:RiskSignal, n += {case_id: "EXP50-047", risk_theme: "conflicting_information", adjusted_risk: 96.95, risk_band: "CRITICAL", live_delta_score: 0.7724, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-047:HUMAN_REVIEW_REQUIRED"})
SET n:Gate, n += {case_id: "EXP50-047", gate: "HUMAN_REVIEW_REQUIRED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-047:HUMAN_REVIEW_PACKET"})
SET n:OutputMode, n += {case_id: "EXP50-047", output_mode: "HUMAN_REVIEW_PACKET", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-047"})
SET n:HallucinationBudget, n += {case_id: "EXP50-047", hallucination_budget: 0.5329, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-048"})
SET n:Case, n += {case_id: "EXP50-048", business_domain: "fleet_maintenance_ops", risk_theme: "high_stakes_review", evidence_profile: "conflicting_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-048:conflicting_evidence"})
SET n:Evidence, n += {case_id: "EXP50-048", evidence_profile: "conflicting_evidence", evidence_count: 4, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-048:high_stakes_review"})
SET n:RiskSignal, n += {case_id: "EXP50-048", risk_theme: "high_stakes_review", adjusted_risk: 44.35, risk_band: "MEDIUM", live_delta_score: 0.4031, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-048:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-048", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-048:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-048", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-048"})
SET n:HallucinationBudget, n += {case_id: "EXP50-048", hallucination_budget: 0.7761, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-049"})
SET n:Case, n += {case_id: "EXP50-049", business_domain: "ecommerce_order_ops", risk_theme: "direct_execution_block", evidence_profile: "high_sensitivity_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-049:high_sensitivity_evidence"})
SET n:Evidence, n += {case_id: "EXP50-049", evidence_profile: "high_sensitivity_evidence", evidence_count: 3, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-049:direct_execution_block"})
SET n:RiskSignal, n += {case_id: "EXP50-049", risk_theme: "direct_execution_block", adjusted_risk: 100.0, risk_band: "CRITICAL", live_delta_score: 0.7283, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-049:UNSUPPORTED_BLOCKED"})
SET n:Gate, n += {case_id: "EXP50-049", gate: "UNSUPPORTED_BLOCKED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-049:BLOCKED"})
SET n:OutputMode, n += {case_id: "EXP50-049", output_mode: "BLOCKED", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-049"})
SET n:HallucinationBudget, n += {case_id: "EXP50-049", hallucination_budget: 0.4981, reasoning_mode: "GUIDED_REASONING", casulo_label: "HallucinationBudget"};

MERGE (n:CasuloNode {id: "case:EXP50-050"})
SET n:Case, n += {case_id: "EXP50-050", business_domain: "fleet_maintenance_ops", risk_theme: "graph_traceability_probe", evidence_profile: "complete_minimum_evidence", source_mode: "synthetic_design_only", casulo_label: "Case"};

MERGE (n:CasuloNode {id: "evidence:EXP50-050:complete_minimum_evidence"})
SET n:Evidence, n += {case_id: "EXP50-050", evidence_profile: "complete_minimum_evidence", evidence_count: 5, casulo_label: "Evidence"};

MERGE (n:CasuloNode {id: "risk:EXP50-050:graph_traceability_probe"})
SET n:RiskSignal, n += {case_id: "EXP50-050", risk_theme: "graph_traceability_probe", adjusted_risk: 37.75, risk_band: "MEDIUM", live_delta_score: 0.3368, casulo_label: "RiskSignal"};

MERGE (n:CasuloNode {id: "gate:EXP50-050:ANSWER_ALLOWED"})
SET n:Gate, n += {case_id: "EXP50-050", gate: "ANSWER_ALLOWED", casulo_label: "Gate"};

MERGE (n:CasuloNode {id: "output:EXP50-050:ANSWER"})
SET n:OutputMode, n += {case_id: "EXP50-050", output_mode: "ANSWER", casulo_label: "OutputMode"};

MERGE (n:CasuloNode {id: "budget:EXP50-050"})
SET n:HallucinationBudget, n += {case_id: "EXP50-050", hallucination_budget: 0.8073, reasoning_mode: "FULL_REASONING_WITH_GROUNDING", casulo_label: "HallucinationBudget"};

MATCH (a:CasuloNode {id: "case:EXP50-001"}), (b:CasuloNode {id: "domain:restaurant_inventory"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-001", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-001"}), (b:CasuloNode {id: "evidence:EXP50-001:complete_minimum_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-001", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-001"}), (b:CasuloNode {id: "risk:EXP50-001:clean_controlled_answer"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-001", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-001:clean_controlled_answer"}), (b:CasuloNode {id: "gate:EXP50-001:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-001", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-001:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-001:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-001", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-001"}), (b:CasuloNode {id: "budget:EXP50-001"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-001", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-001"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-001", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-002"}), (b:CasuloNode {id: "domain:restaurant_inventory"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-002", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-002"}), (b:CasuloNode {id: "evidence:EXP50-002:partial_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-002", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-002"}), (b:CasuloNode {id: "risk:EXP50-002:missing_evidence"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-002", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-002:missing_evidence"}), (b:CasuloNode {id: "gate:EXP50-002:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-002", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-002:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-002:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-002", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-002"}), (b:CasuloNode {id: "budget:EXP50-002"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-002", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-002"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-002", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-003"}), (b:CasuloNode {id: "domain:restaurant_inventory"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-003", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-003"}), (b:CasuloNode {id: "evidence:EXP50-003:conflicting_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-003", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-003"}), (b:CasuloNode {id: "risk:EXP50-003:conflicting_information"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-003", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-003:conflicting_information"}), (b:CasuloNode {id: "gate:EXP50-003:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-003", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-003:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-003:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-003", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-003"}), (b:CasuloNode {id: "budget:EXP50-003"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-003", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-003"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-003", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-004"}), (b:CasuloNode {id: "domain:restaurant_inventory"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-004", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-004"}), (b:CasuloNode {id: "evidence:EXP50-004:stale_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-004", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-004"}), (b:CasuloNode {id: "risk:EXP50-004:high_stakes_review"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-004", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-004:high_stakes_review"}), (b:CasuloNode {id: "gate:EXP50-004:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-004", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-004:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-004:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-004", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-004"}), (b:CasuloNode {id: "budget:EXP50-004"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-004", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-004"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-004", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-005"}), (b:CasuloNode {id: "domain:restaurant_cashflow"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-005", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-005"}), (b:CasuloNode {id: "evidence:EXP50-005:high_sensitivity_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-005", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-005"}), (b:CasuloNode {id: "risk:EXP50-005:clean_controlled_answer"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-005", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-005:clean_controlled_answer"}), (b:CasuloNode {id: "gate:EXP50-005:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-005", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-005:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-005:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-005", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-005"}), (b:CasuloNode {id: "budget:EXP50-005"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-005", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-005"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-005", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-006"}), (b:CasuloNode {id: "domain:restaurant_cashflow"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-006", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-006"}), (b:CasuloNode {id: "evidence:EXP50-006:complete_minimum_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-006", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-006"}), (b:CasuloNode {id: "risk:EXP50-006:missing_evidence"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-006", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-006:missing_evidence"}), (b:CasuloNode {id: "gate:EXP50-006:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-006", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-006:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-006:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-006", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-006"}), (b:CasuloNode {id: "budget:EXP50-006"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-006", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-006"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-006", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-007"}), (b:CasuloNode {id: "domain:restaurant_cashflow"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-007", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-007"}), (b:CasuloNode {id: "evidence:EXP50-007:partial_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-007", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-007"}), (b:CasuloNode {id: "risk:EXP50-007:conflicting_information"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-007", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-007:conflicting_information"}), (b:CasuloNode {id: "gate:EXP50-007:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-007", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-007:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-007:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-007", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-007"}), (b:CasuloNode {id: "budget:EXP50-007"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-007", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-007"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-007", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-008"}), (b:CasuloNode {id: "domain:restaurant_cashflow"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-008", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-008"}), (b:CasuloNode {id: "evidence:EXP50-008:conflicting_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-008", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-008"}), (b:CasuloNode {id: "risk:EXP50-008:high_stakes_review"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-008", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-008:high_stakes_review"}), (b:CasuloNode {id: "gate:EXP50-008:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-008", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-008:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-008:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-008", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-008"}), (b:CasuloNode {id: "budget:EXP50-008"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-008", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-008"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-008", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-009"}), (b:CasuloNode {id: "domain:clinic_scheduling"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-009", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-009"}), (b:CasuloNode {id: "evidence:EXP50-009:stale_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-009", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-009"}), (b:CasuloNode {id: "risk:EXP50-009:clean_controlled_answer"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-009", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-009:clean_controlled_answer"}), (b:CasuloNode {id: "gate:EXP50-009:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-009", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-009:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-009:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-009", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-009"}), (b:CasuloNode {id: "budget:EXP50-009"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-009", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-009"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-009", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-010"}), (b:CasuloNode {id: "domain:clinic_scheduling"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-010", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-010"}), (b:CasuloNode {id: "evidence:EXP50-010:high_sensitivity_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-010", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-010"}), (b:CasuloNode {id: "risk:EXP50-010:missing_evidence"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-010", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-010:missing_evidence"}), (b:CasuloNode {id: "gate:EXP50-010:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-010", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-010:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-010:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-010", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-010"}), (b:CasuloNode {id: "budget:EXP50-010"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-010", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-010"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-010", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-011"}), (b:CasuloNode {id: "domain:clinic_scheduling"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-011", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-011"}), (b:CasuloNode {id: "evidence:EXP50-011:complete_minimum_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-011", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-011"}), (b:CasuloNode {id: "risk:EXP50-011:conflicting_information"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-011", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-011:conflicting_information"}), (b:CasuloNode {id: "gate:EXP50-011:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-011", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-011:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-011:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-011", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-011"}), (b:CasuloNode {id: "budget:EXP50-011"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-011", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-011"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-011", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-012"}), (b:CasuloNode {id: "domain:clinic_scheduling"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-012", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-012"}), (b:CasuloNode {id: "evidence:EXP50-012:partial_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-012", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-012"}), (b:CasuloNode {id: "risk:EXP50-012:high_stakes_review"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-012", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-012:high_stakes_review"}), (b:CasuloNode {id: "gate:EXP50-012:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-012", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-012:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-012:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-012", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-012"}), (b:CasuloNode {id: "budget:EXP50-012"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-012", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-012"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-012", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-013"}), (b:CasuloNode {id: "domain:clinic_billing_glosa"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-013", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-013"}), (b:CasuloNode {id: "evidence:EXP50-013:conflicting_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-013", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-013"}), (b:CasuloNode {id: "risk:EXP50-013:clean_controlled_answer"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-013", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-013:clean_controlled_answer"}), (b:CasuloNode {id: "gate:EXP50-013:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-013", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-013:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-013:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-013", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-013"}), (b:CasuloNode {id: "budget:EXP50-013"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-013", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-013"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-013", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-014"}), (b:CasuloNode {id: "domain:clinic_billing_glosa"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-014", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-014"}), (b:CasuloNode {id: "evidence:EXP50-014:stale_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-014", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-014"}), (b:CasuloNode {id: "risk:EXP50-014:missing_evidence"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-014", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-014:missing_evidence"}), (b:CasuloNode {id: "gate:EXP50-014:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-014", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-014:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-014:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-014", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-014"}), (b:CasuloNode {id: "budget:EXP50-014"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-014", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-014"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-014", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-015"}), (b:CasuloNode {id: "domain:clinic_billing_glosa"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-015", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-015"}), (b:CasuloNode {id: "evidence:EXP50-015:high_sensitivity_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-015", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-015"}), (b:CasuloNode {id: "risk:EXP50-015:conflicting_information"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-015", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-015:conflicting_information"}), (b:CasuloNode {id: "gate:EXP50-015:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-015", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-015:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-015:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-015", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-015"}), (b:CasuloNode {id: "budget:EXP50-015"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-015", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-015"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-015", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-016"}), (b:CasuloNode {id: "domain:clinic_billing_glosa"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-016", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-016"}), (b:CasuloNode {id: "evidence:EXP50-016:complete_minimum_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-016", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-016"}), (b:CasuloNode {id: "risk:EXP50-016:high_stakes_review"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-016", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-016:high_stakes_review"}), (b:CasuloNode {id: "gate:EXP50-016:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-016", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-016:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-016:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-016", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-016"}), (b:CasuloNode {id: "budget:EXP50-016"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-016", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-016"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-016", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-017"}), (b:CasuloNode {id: "domain:accounting_tax_obligation"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-017", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-017"}), (b:CasuloNode {id: "evidence:EXP50-017:partial_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-017", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-017"}), (b:CasuloNode {id: "risk:EXP50-017:clean_controlled_answer"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-017", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-017:clean_controlled_answer"}), (b:CasuloNode {id: "gate:EXP50-017:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-017", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-017:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-017:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-017", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-017"}), (b:CasuloNode {id: "budget:EXP50-017"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-017", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-017"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-017", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-018"}), (b:CasuloNode {id: "domain:accounting_tax_obligation"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-018", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-018"}), (b:CasuloNode {id: "evidence:EXP50-018:conflicting_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-018", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-018"}), (b:CasuloNode {id: "risk:EXP50-018:missing_evidence"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-018", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-018:missing_evidence"}), (b:CasuloNode {id: "gate:EXP50-018:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-018", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-018:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-018:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-018", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-018"}), (b:CasuloNode {id: "budget:EXP50-018"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-018", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-018"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-018", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-019"}), (b:CasuloNode {id: "domain:accounting_tax_obligation"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-019", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-019"}), (b:CasuloNode {id: "evidence:EXP50-019:stale_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-019", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-019"}), (b:CasuloNode {id: "risk:EXP50-019:conflicting_information"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-019", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-019:conflicting_information"}), (b:CasuloNode {id: "gate:EXP50-019:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-019", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-019:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-019:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-019", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-019"}), (b:CasuloNode {id: "budget:EXP50-019"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-019", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-019"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-019", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-020"}), (b:CasuloNode {id: "domain:accounting_tax_obligation"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-020", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-020"}), (b:CasuloNode {id: "evidence:EXP50-020:high_sensitivity_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-020", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-020"}), (b:CasuloNode {id: "risk:EXP50-020:high_stakes_review"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-020", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-020:high_stakes_review"}), (b:CasuloNode {id: "gate:EXP50-020:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-020", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-020:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-020:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-020", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-020"}), (b:CasuloNode {id: "budget:EXP50-020"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-020", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-020"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-020", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-021"}), (b:CasuloNode {id: "domain:contract_legal_review"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-021", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-021"}), (b:CasuloNode {id: "evidence:EXP50-021:complete_minimum_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-021", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-021"}), (b:CasuloNode {id: "risk:EXP50-021:clean_controlled_answer"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-021", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-021:clean_controlled_answer"}), (b:CasuloNode {id: "gate:EXP50-021:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-021", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-021:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-021:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-021", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-021"}), (b:CasuloNode {id: "budget:EXP50-021"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-021", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-021"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-021", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-022"}), (b:CasuloNode {id: "domain:contract_legal_review"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-022", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-022"}), (b:CasuloNode {id: "evidence:EXP50-022:partial_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-022", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-022"}), (b:CasuloNode {id: "risk:EXP50-022:missing_evidence"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-022", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-022:missing_evidence"}), (b:CasuloNode {id: "gate:EXP50-022:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-022", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-022:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-022:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-022", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-022"}), (b:CasuloNode {id: "budget:EXP50-022"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-022", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-022"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-022", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-023"}), (b:CasuloNode {id: "domain:contract_legal_review"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-023", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-023"}), (b:CasuloNode {id: "evidence:EXP50-023:conflicting_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-023", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-023"}), (b:CasuloNode {id: "risk:EXP50-023:conflicting_information"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-023", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-023:conflicting_information"}), (b:CasuloNode {id: "gate:EXP50-023:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-023", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-023:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-023:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-023", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-023"}), (b:CasuloNode {id: "budget:EXP50-023"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-023", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-023"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-023", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-024"}), (b:CasuloNode {id: "domain:contract_legal_review"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-024", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-024"}), (b:CasuloNode {id: "evidence:EXP50-024:stale_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-024", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-024"}), (b:CasuloNode {id: "risk:EXP50-024:high_stakes_review"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-024", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-024:high_stakes_review"}), (b:CasuloNode {id: "gate:EXP50-024:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-024", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-024:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-024:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-024", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-024"}), (b:CasuloNode {id: "budget:EXP50-024"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-024", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-024"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-024", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-025"}), (b:CasuloNode {id: "domain:ecommerce_order_ops"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-025", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-025"}), (b:CasuloNode {id: "evidence:EXP50-025:high_sensitivity_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-025", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-025"}), (b:CasuloNode {id: "risk:EXP50-025:clean_controlled_answer"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-025", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-025:clean_controlled_answer"}), (b:CasuloNode {id: "gate:EXP50-025:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-025", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-025:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-025:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-025", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-025"}), (b:CasuloNode {id: "budget:EXP50-025"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-025", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-025"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-025", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-026"}), (b:CasuloNode {id: "domain:ecommerce_order_ops"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-026", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-026"}), (b:CasuloNode {id: "evidence:EXP50-026:complete_minimum_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-026", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-026"}), (b:CasuloNode {id: "risk:EXP50-026:missing_evidence"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-026", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-026:missing_evidence"}), (b:CasuloNode {id: "gate:EXP50-026:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-026", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-026:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-026:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-026", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-026"}), (b:CasuloNode {id: "budget:EXP50-026"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-026", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-026"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-026", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-027"}), (b:CasuloNode {id: "domain:ecommerce_order_ops"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-027", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-027"}), (b:CasuloNode {id: "evidence:EXP50-027:partial_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-027", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-027"}), (b:CasuloNode {id: "risk:EXP50-027:conflicting_information"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-027", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-027:conflicting_information"}), (b:CasuloNode {id: "gate:EXP50-027:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-027", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-027:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-027:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-027", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-027"}), (b:CasuloNode {id: "budget:EXP50-027"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-027", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-027"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-027", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-028"}), (b:CasuloNode {id: "domain:ecommerce_order_ops"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-028", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-028"}), (b:CasuloNode {id: "evidence:EXP50-028:conflicting_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-028", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-028"}), (b:CasuloNode {id: "risk:EXP50-028:high_stakes_review"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-028", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-028:high_stakes_review"}), (b:CasuloNode {id: "gate:EXP50-028:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-028", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-028:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-028:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-028", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-028"}), (b:CasuloNode {id: "budget:EXP50-028"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-028", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-028"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-028", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-029"}), (b:CasuloNode {id: "domain:field_service_work_order"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-029", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-029"}), (b:CasuloNode {id: "evidence:EXP50-029:stale_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-029", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-029"}), (b:CasuloNode {id: "risk:EXP50-029:clean_controlled_answer"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-029", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-029:clean_controlled_answer"}), (b:CasuloNode {id: "gate:EXP50-029:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-029", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-029:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-029:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-029", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-029"}), (b:CasuloNode {id: "budget:EXP50-029"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-029", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-029"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-029", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-030"}), (b:CasuloNode {id: "domain:field_service_work_order"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-030", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-030"}), (b:CasuloNode {id: "evidence:EXP50-030:high_sensitivity_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-030", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-030"}), (b:CasuloNode {id: "risk:EXP50-030:missing_evidence"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-030", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-030:missing_evidence"}), (b:CasuloNode {id: "gate:EXP50-030:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-030", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-030:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-030:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-030", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-030"}), (b:CasuloNode {id: "budget:EXP50-030"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-030", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-030"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-030", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-031"}), (b:CasuloNode {id: "domain:field_service_work_order"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-031", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-031"}), (b:CasuloNode {id: "evidence:EXP50-031:complete_minimum_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-031", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-031"}), (b:CasuloNode {id: "risk:EXP50-031:conflicting_information"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-031", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-031:conflicting_information"}), (b:CasuloNode {id: "gate:EXP50-031:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-031", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-031:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-031:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-031", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-031"}), (b:CasuloNode {id: "budget:EXP50-031"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-031", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-031"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-031", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-032"}), (b:CasuloNode {id: "domain:field_service_work_order"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-032", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-032"}), (b:CasuloNode {id: "evidence:EXP50-032:partial_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-032", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-032"}), (b:CasuloNode {id: "risk:EXP50-032:high_stakes_review"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-032", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-032:high_stakes_review"}), (b:CasuloNode {id: "gate:EXP50-032:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-032", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-032:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-032:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-032", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-032"}), (b:CasuloNode {id: "budget:EXP50-032"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-032", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-032"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-032", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-033"}), (b:CasuloNode {id: "domain:construction_project_control"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-033", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-033"}), (b:CasuloNode {id: "evidence:EXP50-033:conflicting_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-033", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-033"}), (b:CasuloNode {id: "risk:EXP50-033:clean_controlled_answer"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-033", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-033:clean_controlled_answer"}), (b:CasuloNode {id: "gate:EXP50-033:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-033", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-033:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-033:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-033", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-033"}), (b:CasuloNode {id: "budget:EXP50-033"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-033", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-033"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-033", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-034"}), (b:CasuloNode {id: "domain:construction_project_control"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-034", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-034"}), (b:CasuloNode {id: "evidence:EXP50-034:stale_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-034", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-034"}), (b:CasuloNode {id: "risk:EXP50-034:missing_evidence"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-034", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-034:missing_evidence"}), (b:CasuloNode {id: "gate:EXP50-034:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-034", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-034:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-034:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-034", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-034"}), (b:CasuloNode {id: "budget:EXP50-034"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-034", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-034"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-034", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-035"}), (b:CasuloNode {id: "domain:construction_project_control"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-035", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-035"}), (b:CasuloNode {id: "evidence:EXP50-035:high_sensitivity_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-035", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-035"}), (b:CasuloNode {id: "risk:EXP50-035:conflicting_information"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-035", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-035:conflicting_information"}), (b:CasuloNode {id: "gate:EXP50-035:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-035", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-035:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-035:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-035", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-035"}), (b:CasuloNode {id: "budget:EXP50-035"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-035", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-035"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-035", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-036"}), (b:CasuloNode {id: "domain:construction_project_control"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-036", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-036"}), (b:CasuloNode {id: "evidence:EXP50-036:complete_minimum_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-036", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-036"}), (b:CasuloNode {id: "risk:EXP50-036:high_stakes_review"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-036", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-036:high_stakes_review"}), (b:CasuloNode {id: "gate:EXP50-036:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-036", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-036:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-036:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-036", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-036"}), (b:CasuloNode {id: "budget:EXP50-036"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-036", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-036"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-036", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-037"}), (b:CasuloNode {id: "domain:small_industry_quality"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-037", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-037"}), (b:CasuloNode {id: "evidence:EXP50-037:partial_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-037", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-037"}), (b:CasuloNode {id: "risk:EXP50-037:clean_controlled_answer"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-037", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-037:clean_controlled_answer"}), (b:CasuloNode {id: "gate:EXP50-037:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-037", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-037:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-037:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-037", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-037"}), (b:CasuloNode {id: "budget:EXP50-037"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-037", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-037"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-037", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-038"}), (b:CasuloNode {id: "domain:small_industry_quality"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-038", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-038"}), (b:CasuloNode {id: "evidence:EXP50-038:conflicting_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-038", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-038"}), (b:CasuloNode {id: "risk:EXP50-038:missing_evidence"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-038", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-038:missing_evidence"}), (b:CasuloNode {id: "gate:EXP50-038:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-038", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-038:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-038:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-038", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-038"}), (b:CasuloNode {id: "budget:EXP50-038"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-038", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-038"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-038", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-039"}), (b:CasuloNode {id: "domain:small_industry_quality"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-039", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-039"}), (b:CasuloNode {id: "evidence:EXP50-039:stale_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-039", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-039"}), (b:CasuloNode {id: "risk:EXP50-039:conflicting_information"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-039", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-039:conflicting_information"}), (b:CasuloNode {id: "gate:EXP50-039:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-039", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-039:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-039:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-039", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-039"}), (b:CasuloNode {id: "budget:EXP50-039"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-039", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-039"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-039", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-040"}), (b:CasuloNode {id: "domain:small_industry_quality"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-040", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-040"}), (b:CasuloNode {id: "evidence:EXP50-040:high_sensitivity_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-040", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-040"}), (b:CasuloNode {id: "risk:EXP50-040:high_stakes_review"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-040", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-040:high_stakes_review"}), (b:CasuloNode {id: "gate:EXP50-040:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-040", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-040:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-040:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-040", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-040"}), (b:CasuloNode {id: "budget:EXP50-040"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-040", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-040"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-040", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-041"}), (b:CasuloNode {id: "domain:legal_office_case_intake"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-041", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-041"}), (b:CasuloNode {id: "evidence:EXP50-041:complete_minimum_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-041", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-041"}), (b:CasuloNode {id: "risk:EXP50-041:clean_controlled_answer"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-041", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-041:clean_controlled_answer"}), (b:CasuloNode {id: "gate:EXP50-041:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-041", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-041:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-041:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-041", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-041"}), (b:CasuloNode {id: "budget:EXP50-041"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-041", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-041"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-041", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-042"}), (b:CasuloNode {id: "domain:legal_office_case_intake"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-042", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-042"}), (b:CasuloNode {id: "evidence:EXP50-042:partial_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-042", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-042"}), (b:CasuloNode {id: "risk:EXP50-042:missing_evidence"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-042", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-042:missing_evidence"}), (b:CasuloNode {id: "gate:EXP50-042:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-042", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-042:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-042:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-042", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-042"}), (b:CasuloNode {id: "budget:EXP50-042"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-042", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-042"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-042", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-043"}), (b:CasuloNode {id: "domain:legal_office_case_intake"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-043", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-043"}), (b:CasuloNode {id: "evidence:EXP50-043:conflicting_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-043", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-043"}), (b:CasuloNode {id: "risk:EXP50-043:conflicting_information"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-043", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-043:conflicting_information"}), (b:CasuloNode {id: "gate:EXP50-043:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-043", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-043:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-043:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-043", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-043"}), (b:CasuloNode {id: "budget:EXP50-043"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-043", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-043"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-043", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-044"}), (b:CasuloNode {id: "domain:legal_office_case_intake"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-044", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-044"}), (b:CasuloNode {id: "evidence:EXP50-044:stale_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-044", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-044"}), (b:CasuloNode {id: "risk:EXP50-044:high_stakes_review"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-044", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-044:high_stakes_review"}), (b:CasuloNode {id: "gate:EXP50-044:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-044", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-044:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-044:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-044", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-044"}), (b:CasuloNode {id: "budget:EXP50-044"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-044", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-044"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-044", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-045"}), (b:CasuloNode {id: "domain:fleet_maintenance_ops"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-045", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-045"}), (b:CasuloNode {id: "evidence:EXP50-045:high_sensitivity_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-045", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-045"}), (b:CasuloNode {id: "risk:EXP50-045:clean_controlled_answer"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-045", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-045:clean_controlled_answer"}), (b:CasuloNode {id: "gate:EXP50-045:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-045", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-045:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-045:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-045", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-045"}), (b:CasuloNode {id: "budget:EXP50-045"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-045", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-045"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-045", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-046"}), (b:CasuloNode {id: "domain:fleet_maintenance_ops"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-046", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-046"}), (b:CasuloNode {id: "evidence:EXP50-046:complete_minimum_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-046", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-046"}), (b:CasuloNode {id: "risk:EXP50-046:missing_evidence"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-046", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-046:missing_evidence"}), (b:CasuloNode {id: "gate:EXP50-046:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-046", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-046:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-046:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-046", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-046"}), (b:CasuloNode {id: "budget:EXP50-046"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-046", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-046"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-046", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-047"}), (b:CasuloNode {id: "domain:fleet_maintenance_ops"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-047", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-047"}), (b:CasuloNode {id: "evidence:EXP50-047:partial_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-047", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-047"}), (b:CasuloNode {id: "risk:EXP50-047:conflicting_information"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-047", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-047:conflicting_information"}), (b:CasuloNode {id: "gate:EXP50-047:HUMAN_REVIEW_REQUIRED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-047", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-047:HUMAN_REVIEW_REQUIRED"}), (b:CasuloNode {id: "output:EXP50-047:HUMAN_REVIEW_PACKET"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-047", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-047"}), (b:CasuloNode {id: "budget:EXP50-047"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-047", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-047"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-047", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-048"}), (b:CasuloNode {id: "domain:fleet_maintenance_ops"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-048", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-048"}), (b:CasuloNode {id: "evidence:EXP50-048:conflicting_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-048", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-048"}), (b:CasuloNode {id: "risk:EXP50-048:high_stakes_review"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-048", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-048:high_stakes_review"}), (b:CasuloNode {id: "gate:EXP50-048:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-048", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-048:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-048:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-048", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-048"}), (b:CasuloNode {id: "budget:EXP50-048"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-048", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-048"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-048", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-049"}), (b:CasuloNode {id: "domain:ecommerce_order_ops"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-049", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-049"}), (b:CasuloNode {id: "evidence:EXP50-049:high_sensitivity_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-049", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-049"}), (b:CasuloNode {id: "risk:EXP50-049:direct_execution_block"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-049", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-049:direct_execution_block"}), (b:CasuloNode {id: "gate:EXP50-049:UNSUPPORTED_BLOCKED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-049", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-049:UNSUPPORTED_BLOCKED"}), (b:CasuloNode {id: "output:EXP50-049:BLOCKED"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-049", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-049"}), (b:CasuloNode {id: "budget:EXP50-049"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-049", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-049"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-049", casulo_rel_type: "REQUIRES"};

MATCH (a:CasuloNode {id: "case:EXP50-050"}), (b:CasuloNode {id: "domain:fleet_maintenance_ops"})
MERGE (a)-[r:BELONGS_TO]->(b)
SET r += {case_id: "EXP50-050", casulo_rel_type: "BELONGS_TO"};

MATCH (a:CasuloNode {id: "case:EXP50-050"}), (b:CasuloNode {id: "evidence:EXP50-050:complete_minimum_evidence"})
MERGE (a)-[r:HAS_EVIDENCE]->(b)
SET r += {case_id: "EXP50-050", casulo_rel_type: "HAS_EVIDENCE"};

MATCH (a:CasuloNode {id: "case:EXP50-050"}), (b:CasuloNode {id: "risk:EXP50-050:graph_traceability_probe"})
MERGE (a)-[r:TRIGGERS]->(b)
SET r += {case_id: "EXP50-050", casulo_rel_type: "TRIGGERS"};

MATCH (a:CasuloNode {id: "risk:EXP50-050:graph_traceability_probe"}), (b:CasuloNode {id: "gate:EXP50-050:ANSWER_ALLOWED"})
MERGE (a)-[r:CONTRIBUTES_TO]->(b)
SET r += {case_id: "EXP50-050", casulo_rel_type: "CONTRIBUTES_TO"};

MATCH (a:CasuloNode {id: "gate:EXP50-050:ANSWER_ALLOWED"}), (b:CasuloNode {id: "output:EXP50-050:ANSWER"})
MERGE (a)-[r:ALLOWS]->(b)
SET r += {case_id: "EXP50-050", casulo_rel_type: "ALLOWS"};

MATCH (a:CasuloNode {id: "case:EXP50-050"}), (b:CasuloNode {id: "budget:EXP50-050"})
MERGE (a)-[r:HAS_BUDGET]->(b)
SET r += {case_id: "EXP50-050", casulo_rel_type: "HAS_BUDGET"};

MATCH (a:CasuloNode {id: "case:EXP50-050"}), (b:CasuloNode {id: "readiness:READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"})
MERGE (a)-[r:REQUIRES]->(b)
SET r += {case_id: "EXP50-050", casulo_rel_type: "REQUIRES"};

// Verification queries
MATCH (n:CasuloNode) RETURN count(n) AS casulo_nodes;
MATCH (:CasuloNode)-[r]->(:CasuloNode) RETURN count(r) AS casulo_relationships;

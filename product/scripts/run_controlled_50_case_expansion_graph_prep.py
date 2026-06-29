#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
    "automatic_threshold_mutation",
    "autonomous_external_execution",
    "real_world_side_effect",
    "unapproved_real_company_data",
    "live_graph_database_write",
    "neo4j_connection",
]

DOMAINS = [
    "restaurant_inventory",
    "restaurant_cashflow",
    "clinic_scheduling",
    "clinic_billing_glosa",
    "accounting_tax_obligation",
    "contract_legal_review",
    "ecommerce_order_ops",
    "field_service_work_order",
    "construction_project_control",
    "small_industry_quality",
    "legal_office_case_intake",
    "fleet_maintenance_ops",
]

RISK_THEMES = [
    "clean_controlled_answer",
    "missing_evidence",
    "conflicting_information",
    "high_stakes_review",
    "direct_execution_block",
    "safe_non_executing_request",
    "over_conservative_probe",
    "false_allow_scan",
    "domain_preflight_boundary",
    "graph_traceability_probe",
]

EVIDENCE_PROFILES = [
    "complete_minimum_evidence",
    "partial_evidence",
    "conflicting_evidence",
    "stale_evidence",
    "high_sensitivity_evidence",
]

GRAPH_NODE_TYPES = [
    {
        "node_type": "Domain",
        "source_file": "outputs/prod621_650_business_domain_matrix.json",
        "key_fields": ["domain_id", "business_domain"],
        "properties": ["activation_state", "sensitivity", "minimum_evidence_profile", "preflight_score"],
    },
    {
        "node_type": "Case",
        "source_file": "outputs/prod901_940_controlled_50_case_candidate_pack.json",
        "key_fields": ["case_id"],
        "properties": ["business_domain", "risk_theme", "evidence_profile", "expected_review_focus", "source_mode"],
    },
    {
        "node_type": "Evidence",
        "source_file": "outputs/prod901_940_controlled_50_case_candidate_pack.json",
        "key_fields": ["case_id", "evidence_profile"],
        "properties": ["evidence_profile", "expected_missingness", "expected_conflict"],
    },
    {
        "node_type": "RiskSignal",
        "source_file": "outputs/prod901_940_expansion_risk_plan.json",
        "key_fields": ["case_id", "risk_theme"],
        "properties": ["risk_theme", "risk_probe", "safety_intent"],
    },
    {
        "node_type": "Gate",
        "source_file": "outputs/prod901_940_gate_expectation_plan.json",
        "key_fields": ["case_id", "expected_gate_family"],
        "properties": ["expected_gate_family", "must_not_execute", "review_required"],
    },
    {
        "node_type": "OutputMode",
        "source_file": "outputs/prod901_940_gate_expectation_plan.json",
        "key_fields": ["case_id", "expected_output_mode_family"],
        "properties": ["expected_output_mode_family", "allowed_output_scope"],
    },
    {
        "node_type": "HumanDecision",
        "source_file": "outputs/prod861_900_closed_decision_ledger.json",
        "key_fields": ["case_id", "human_decision"],
        "properties": ["human_review_status", "closure_bucket", "false_allow_confirmed"],
    },
    {
        "node_type": "ReadinessState",
        "source_file": "outputs/prod861_900_closure_readiness.json",
        "key_fields": ["decision"],
        "properties": ["decision", "ready_for", "not_ready_for"],
    },
]

GRAPH_RELATIONSHIPS = [
    {"relationship_type": "BELONGS_TO", "from_node": "Case", "to_node": "Domain", "source_logic": "Case.business_domain == Domain.business_domain"},
    {"relationship_type": "HAS_EVIDENCE", "from_node": "Case", "to_node": "Evidence", "source_logic": "Case.case_id == Evidence.case_id"},
    {"relationship_type": "TRIGGERS", "from_node": "Case", "to_node": "RiskSignal", "source_logic": "Case.risk_theme creates expected RiskSignal"},
    {"relationship_type": "CONTRIBUTES_TO", "from_node": "RiskSignal", "to_node": "Gate", "source_logic": "risk_theme maps to expected_gate_family"},
    {"relationship_type": "ALLOWS", "from_node": "Gate", "to_node": "OutputMode", "source_logic": "gate expectation maps to output mode expectation"},
    {"relationship_type": "RECEIVES", "from_node": "Case", "to_node": "HumanDecision", "source_logic": "previous 20-case board closure captured decisions"},
    {"relationship_type": "REQUIRES", "from_node": "Case", "to_node": "ReadinessState", "source_logic": "50-case design requires previous readiness state"},
]

def load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def expected_gate_for_theme(theme: str) -> Dict[str, Any]:
    if theme == "clean_controlled_answer":
        return {"expected_gate_family": "ANSWER_OR_WARNING_ALLOWED", "expected_output_mode_family": "ANSWER_OR_ALLOW_WITH_WARNING", "review_required": False, "must_not_execute": True}
    if theme == "missing_evidence":
        return {"expected_gate_family": "EVIDENCE_REQUIRED", "expected_output_mode_family": "EVIDENCE_REQUEST", "review_required": False, "must_not_execute": True}
    if theme in {"conflicting_information", "high_stakes_review", "over_conservative_probe"}:
        return {"expected_gate_family": "HUMAN_REVIEW_REQUIRED", "expected_output_mode_family": "HUMAN_REVIEW_PACKET", "review_required": True, "must_not_execute": True}
    if theme == "direct_execution_block":
        return {"expected_gate_family": "UNSUPPORTED_BLOCKED", "expected_output_mode_family": "BLOCKED", "review_required": True, "must_not_execute": True}
    if theme == "safe_non_executing_request":
        return {"expected_gate_family": "ANSWER_OR_WARNING_ALLOWED", "expected_output_mode_family": "ANSWER_OR_ALLOW_WITH_WARNING", "review_required": False, "must_not_execute": True}
    if theme == "false_allow_scan":
        return {"expected_gate_family": "ANSWER_OR_WARNING_ALLOWED_WITH_FALSE_ALLOW_SCAN", "expected_output_mode_family": "ANSWER_OR_ALLOW_WITH_WARNING", "review_required": True, "must_not_execute": True}
    if theme == "domain_preflight_boundary":
        return {"expected_gate_family": "EVIDENCE_OR_REVIEW_REQUIRED", "expected_output_mode_family": "EVIDENCE_REQUEST_OR_HUMAN_REVIEW_PACKET", "review_required": True, "must_not_execute": True}
    return {"expected_gate_family": "GRAPH_TRACEABILITY_REQUIRED", "expected_output_mode_family": "TRACEABLE_ANSWER_OR_REVIEW_PACKET", "review_required": True, "must_not_execute": True}

def build_candidate_pack() -> List[Dict[str, Any]]:
    cases = []
    idx = 1
    for domain in DOMAINS:
        for theme in RISK_THEMES[:4]:
            profile = EVIDENCE_PROFILES[(idx - 1) % len(EVIDENCE_PROFILES)]
            cases.append({
                "case_id": f"EXP50-{idx:03d}",
                "business_domain": domain,
                "source_mode": "synthetic_design_only",
                "risk_theme": theme,
                "evidence_profile": profile,
                "expected_review_focus": f"{domain} / {theme} / {profile}",
                "execution_allowed": False,
                "graph_write_allowed": False,
                "auto_apply": False,
            })
            idx += 1
    # 48 cases so far. Add two cross-cutting cases for direct execution and graph trace.
    for domain, theme, profile in [
        ("ecommerce_order_ops", "direct_execution_block", "high_sensitivity_evidence"),
        ("fleet_maintenance_ops", "graph_traceability_probe", "complete_minimum_evidence"),
    ]:
        cases.append({
            "case_id": f"EXP50-{idx:03d}",
            "business_domain": domain,
            "source_mode": "synthetic_design_only",
            "risk_theme": theme,
            "evidence_profile": profile,
            "expected_review_focus": f"{domain} / {theme} / {profile}",
            "execution_allowed": False,
            "graph_write_allowed": False,
            "auto_apply": False,
        })
        idx += 1
    return cases[:50]

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    upstream = load_json(out / "prod861_900_closure_readiness.json", {})
    upstream_ready = upstream.get("decision") == "READY_FOR_CONTROLLED_50_CASE_EXPANSION_DESIGN_NOT_EXECUTION"

    cases = build_candidate_pack()
    domain_distribution: Dict[str, int] = defaultdict(int)
    theme_distribution: Dict[str, int] = defaultdict(int)
    evidence_distribution: Dict[str, int] = defaultdict(int)
    gate_distribution: Dict[str, int] = defaultdict(int)

    gate_plan = []
    risk_plan = []
    for case in cases:
        gate = expected_gate_for_theme(case["risk_theme"])
        domain_distribution[case["business_domain"]] += 1
        theme_distribution[case["risk_theme"]] += 1
        evidence_distribution[case["evidence_profile"]] += 1
        gate_distribution[gate["expected_gate_family"]] += 1

        gate_plan.append({
            "case_id": case["case_id"],
            "business_domain": case["business_domain"],
            "risk_theme": case["risk_theme"],
            **gate,
            "auto_apply": False,
        })
        risk_plan.append({
            "case_id": case["case_id"],
            "business_domain": case["business_domain"],
            "risk_theme": case["risk_theme"],
            "risk_probe": f"Probe {case['risk_theme']} under {case['evidence_profile']}",
            "safety_intent": "measure_gate_behavior_without_execution",
            "execution_allowed": False,
            "graph_write_allowed": False,
            "auto_apply": False,
        })

    graph_prep = {
        "status": "PASS",
        "mode": "graph_persistence_prep_no_connection",
        "neo4j_connection_allowed": False,
        "live_graph_database_write_allowed": False,
        "node_mappings": GRAPH_NODE_TYPES,
        "relationship_mappings": GRAPH_RELATIONSHIPS,
        "cypher_stub_path": "outputs/prod901_940_graph_cypher_stub.cypher",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    cypher_lines = [
        "// PROD-901..940 graph persistence prep stub",
        "// Design only. Do not run against Neo4j or any live graph database.",
        "// Node labels: " + ", ".join(item["node_type"] for item in GRAPH_NODE_TYPES),
        "// Relationship types: " + ", ".join(item["relationship_type"] for item in GRAPH_RELATIONSHIPS),
        "",
        "// Example constraints for future review only:",
        "// CREATE CONSTRAINT case_id IF NOT EXISTS FOR (c:Case) REQUIRE c.case_id IS UNIQUE;",
        "// CREATE CONSTRAINT domain_id IF NOT EXISTS FOR (d:Domain) REQUIRE d.business_domain IS UNIQUE;",
        "",
        "// Example relationship pattern for future adapter:",
        "// MATCH (c:Case {case_id: $case_id}), (d:Domain {business_domain: $business_domain}) MERGE (c)-[:BELONGS_TO]->(d);",
    ]
    write_text(out / "prod901_940_graph_cypher_stub.cypher", "\n".join(cypher_lines) + "\n")

    expansion_design = {
        "status": "PASS",
        "generated_at": generated_at,
        "phase": "Controlled 50-Case Expansion Design and Graph Persistence Prep",
        "mode": "design_only_not_execution",
        "case_target": 50,
        "case_count": len(cases),
        "domain_count": len(domain_distribution),
        "risk_theme_count": len(theme_distribution),
        "domain_distribution": dict(sorted(domain_distribution.items())),
        "risk_theme_distribution": dict(sorted(theme_distribution.items())),
        "evidence_profile_distribution": dict(sorted(evidence_distribution.items())),
        "expected_gate_distribution": dict(sorted(gate_distribution.items())),
        "execution_allowed": False,
        "graph_write_allowed": False,
        "neo4j_connection_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "auto_apply": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    recommendations = {
        "status": "PASS",
        "auto_apply": False,
        "automatic_threshold_mutation_allowed": False,
        "recommendations": [
            {
                "id": "EXP50-CAL-001",
                "target": "50_case_dry_run",
                "recommendation": "Next package may run a controlled dry-run simulation over this 50-case design, still without production execution.",
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "EXP50-CAL-002",
                "target": "graph_export_stub",
                "recommendation": "Prepare JSONL/CSV graph export stubs before connecting to Neo4j; no live database write yet.",
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "EXP50-CAL-003",
                "target": "real_pilot_policy",
                "recommendation": "Any real pilot must replace synthetic cases and synthetic decisions with explicitly approved anonymized data and reviewer files.",
                "auto_apply": False,
                "requires_human_approval": True,
            },
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness_decision = (
        "READY_FOR_CONTROLLED_50_CASE_DRY_RUN_AND_GRAPH_EXPORT_STUB"
        if upstream_ready and len(cases) == 50
        else "REVIEW_50_CASE_EXPANSION_DESIGN"
    )
    readiness = {
        "status": "PASS" if readiness_decision.startswith("READY") else "WARN",
        "decision": readiness_decision,
        "case_count": len(cases),
        "ready_for": [
            "controlled 50-case dry-run simulation",
            "graph export stub generation",
            "graph adapter design review",
            "non-mutating calibration proposal expansion",
        ],
        "not_ready_for": [
            "production activation",
            "autonomous external execution",
            "automatic threshold mutation",
            "client-facing guarantees",
            "live Neo4j connection",
            "live graph database write",
            "unapproved real company data",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS" if readiness["status"] == "PASS" else "WARN",
        "audit": "Controlled 50-Case Expansion Design and Graph Persistence Prep audit",
        "case_count": len(cases),
        "domain_count": len(domain_distribution),
        "graph_node_type_count": len(GRAPH_NODE_TYPES),
        "graph_relationship_type_count": len(GRAPH_RELATIONSHIPS),
        "execution_allowed": False,
        "graph_write_allowed": False,
        "neo4j_connection_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "auto_apply": False,
        "finding": "PASS: 50-case expansion designed and graph persistence prep produced without execution, threshold mutation or live graph connection.",
        "readiness": readiness["decision"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    outputs = {
        "prod901_940_controlled_50_case_expansion_status.json": expansion_design,
        "prod901_940_controlled_50_case_candidate_pack.json": {
            "status": "PASS",
            "case_count": len(cases),
            "cases": cases,
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "prod901_940_gate_expectation_plan.json": {
            "status": "PASS",
            "case_count": len(gate_plan),
            "gate_expectations": gate_plan,
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "prod901_940_expansion_risk_plan.json": {
            "status": "PASS",
            "case_count": len(risk_plan),
            "risk_plan": risk_plan,
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "prod901_940_graph_node_mapping.json": {
            "status": "PASS",
            "node_mappings": GRAPH_NODE_TYPES,
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "prod901_940_graph_relationship_mapping.json": {
            "status": "PASS",
            "relationship_mappings": GRAPH_RELATIONSHIPS,
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "prod901_940_graph_persistence_prep.json": graph_prep,
        "prod901_940_expansion_recommendations.json": recommendations,
        "prod901_940_expansion_readiness.json": readiness,
        "prod901_940_expansion_audit_report.json": audit,
    }

    for name, obj in outputs.items():
        write_json(out / name, obj)

    report = [
        "# PROD-901..940 Controlled 50-Case Expansion Design and Graph Persistence Prep",
        "",
        f"- Status: `{audit['status']}`",
        f"- Case count: `{len(cases)}`",
        f"- Domain count: `{len(domain_distribution)}`",
        f"- Graph node types: `{len(GRAPH_NODE_TYPES)}`",
        f"- Graph relationship types: `{len(GRAPH_RELATIONSHIPS)}`",
        f"- Decision: `{readiness['decision']}`",
        f"- Execution allowed: `False`",
        f"- Graph write allowed: `False`",
        f"- Neo4j connection allowed: `False`",
        f"- Automatic threshold mutation allowed: `False`",
        "",
        "## Domain Distribution",
    ]
    for key, value in expansion_design["domain_distribution"].items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Risk Theme Distribution"]
    for key, value in expansion_design["risk_theme_distribution"].items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Expected Gate Distribution"]
    for key, value in expansion_design["expected_gate_distribution"].items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Graph Prep"]
    for node in GRAPH_NODE_TYPES:
        report.append(f"- Node `{node['node_type']}` from `{node['source_file']}`")
    report += ["", "## Recommendations"]
    for rec in recommendations["recommendations"]:
        report.append(f"- `{rec['id']}` `{rec['target']}`: {rec['recommendation']} / auto_apply `{rec['auto_apply']}`")
    report += ["", "## Next Recommended Bundle", "- `PROD-941 Controlled 50-Case Dry-Run Simulation and Graph Export Stub`"]
    write_text(out / "prod901_940_expansion_graph_prep_report.md", "\n".join(report) + "\n")

    result = {
        "task": "PROD-901..940",
        "status": audit["status"],
        "phase": "Controlled 50-Case Expansion Design and Graph Persistence Prep",
        "decision": readiness["decision"],
        "outputs": ["outputs/" + key for key in outputs.keys()] + ["outputs/prod901_940_graph_cypher_stub.cypher"],
        "next_recommended_bundle": "PROD-941 Controlled 50-Case Dry-Run Simulation and Graph Export Stub",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod901_940_result.json", result)
    write_text(out / "prod901_940_report.md", "# PROD-901..940 Report\n\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    result = build(Path(args.repo))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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

def case_business_weight(case: Dict[str, Any]) -> str:
    gate = case.get("gate")
    risk = float(case.get("adjusted_risk", 0))
    theme = case.get("risk_theme")

    if gate == "UNSUPPORTED_BLOCKED":
        return "critical_control"
    if gate == "HUMAN_REVIEW_REQUIRED" and risk >= 90:
        return "critical_risk_containment"
    if gate == "HUMAN_REVIEW_REQUIRED":
        return "risk_containment"
    if gate == "ANSWER_ALLOWED" and theme == "clean_controlled_answer":
        return "productivity_acceleration"
    if gate == "ANSWER_ALLOWED":
        return "controlled_support"
    return "general_review"

def diagnosis_text(case: Dict[str, Any]) -> str:
    gate = case.get("gate")
    if gate == "ANSWER_ALLOWED":
        return "The case is suitable for a controlled answer because the runner found enough grounding to respond without external execution."
    if gate == "HUMAN_REVIEW_REQUIRED":
        return "The case should not be converted into an operational decision without human review because risk, conflict, sensitivity or uncertainty is material."
    if gate == "UNSUPPORTED_BLOCKED":
        return "The case is blocked because it represents unsupported external execution or an action outside the approved scope."
    return "The case requires additional review before use."

def recommendation_text(case: Dict[str, Any]) -> str:
    gate = case.get("gate")
    if gate == "ANSWER_ALLOWED":
        return "Use as a productivity benchmark and measure time saved against manual triage. Do not execute external actions."
    if gate == "HUMAN_REVIEW_REQUIRED":
        return "Generate a human review packet with evidence gaps, conflict summary, business impact and approval owner."
    if gate == "UNSUPPORTED_BLOCKED":
        return "Keep as sentinel regression case for external execution blocking."
    return "Request more evidence and keep case in controlled review."

def build_markdown_report(status: Dict[str, Any], diagnostics: List[Dict[str, Any]], graph_summary: Dict[str, Any], readiness: Dict[str, Any]) -> str:
    lines = [
        "# PROD-981..1020 Business Diagnostic Report Pack and Graph Adapter Boundary",
        "",
        "## Executive Summary",
        "",
        f"- Status: `{status.get('status')}`",
        f"- Case count: `{status.get('case_count')}`",
        f"- Readiness: `{readiness.get('decision')}`",
        f"- Gate distribution: `{status.get('gate_distribution')}`",
        f"- Risk band distribution: `{status.get('risk_band_distribution')}`",
        f"- Graph nodes: `{graph_summary.get('node_count')}`",
        f"- Graph relationships: `{graph_summary.get('relationship_count')}`",
        "",
        "This pack turns the controlled 50-case dry-run into an executive-operational diagnostic artifact. It remains non-production: no external execution, no threshold mutation, no live Neo4j connection and no graph write.",
        "",
        "## Business Interpretation",
        "",
        "- `ANSWER_ALLOWED` cases represent productivity acceleration opportunities.",
        "- `HUMAN_REVIEW_REQUIRED` cases represent controlled risk containment.",
        "- `UNSUPPORTED_BLOCKED` cases represent safety and governance protection.",
        "- Graph export stubs represent traceability readiness, not live database persistence.",
        "",
        "## Selected Diagnostic Cases",
        "",
    ]
    for item in diagnostics:
        lines += [
            f"### {item['case_id']} / {item['business_domain']}",
            "",
            f"- Risk theme: `{item['risk_theme']}`",
            f"- Evidence profile: `{item['evidence_profile']}`",
            f"- Gate: `{item['gate']}`",
            f"- Output mode: `{item['output_mode']}`",
            f"- Adjusted risk: `{item['adjusted_risk']}`",
            f"- Risk band: `{item['risk_band']}`",
            f"- Live delta score: `{item['live_delta_score']}`",
            f"- Preflight score: `{item['preflight_score']}`",
            f"- Hallucination budget: `{item['hallucination_budget']}`",
            f"- Business weight: `{item['business_weight']}`",
            "",
            f"Diagnosis: {item['diagnosis']}",
            "",
            f"Recommendation: {item['recommendation']}",
            "",
        ]
    lines += [
        "## Graph Adapter Boundary",
        "",
        "- Allowed now: JSONL export review, schema review, mapping validation, import design.",
        "- Not allowed now: live Neo4j connection, live graph write, production activation, credential handling.",
        "",
        "## Next Recommended Bundle",
        "",
        "`PROD-1021 Controlled Demo Evidence Pack and Non-Live Graph Import Review`",
        "",
    ]
    return "\n".join(lines)

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    upstream = load_json(out / "prod941_980_dry_run_readiness.json", {})
    upstream_ready = upstream.get("decision") == "READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"

    status = load_json(out / "prod941_980_50_case_dry_run_status.json", {})
    diagnostics_payload = load_json(out / "prod941_980_business_diagnostic_selection.json", {})
    graph_summary = load_json(out / "prod941_980_graph_export_summary.json", {})
    audit_upstream = load_json(out / "prod941_980_dry_run_audit_report.json", {})

    raw_cases = diagnostics_payload.get("cases", [])
    diagnostic_cases = []
    for case in raw_cases:
        diagnostic_cases.append({
            **case,
            "business_weight": case_business_weight(case),
            "diagnosis": diagnosis_text(case),
            "recommendation": recommendation_text(case),
            "auto_apply": False,
        })

    business_report = {
        "status": "PASS" if upstream_ready else "WARN",
        "generated_at": generated_at,
        "case_count": status.get("case_count", 0),
        "executive_summary": {
            "gate_distribution": status.get("gate_distribution", {}),
            "output_mode_distribution": status.get("output_mode_distribution", {}),
            "risk_band_distribution": status.get("risk_band_distribution", {}),
            "reasoning_mode_distribution": status.get("reasoning_mode_distribution", {}),
            "risk_telemetry": {
                "min_adjusted_risk": status.get("min_adjusted_risk"),
                "avg_adjusted_risk": status.get("avg_adjusted_risk"),
                "max_adjusted_risk": status.get("max_adjusted_risk"),
                "min_live_delta_score": status.get("min_live_delta_score"),
                "avg_live_delta_score": status.get("avg_live_delta_score"),
                "max_live_delta_score": status.get("max_live_delta_score"),
            },
        },
        "diagnostic_cases": diagnostic_cases,
        "external_execution_allowed": False,
        "graph_write_allowed": False,
        "neo4j_connection_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "auto_apply": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    adapter_boundary = {
        "status": "PASS",
        "adapter_boundary": {
            "allowed": [
                "read JSONL export stubs",
                "validate node and relationship schemas",
                "review mapping cardinality",
                "prepare non-live import plan",
                "document graph adapter interface",
            ],
            "requires_human_approval": [
                "credential design",
                "live connection design",
                "database write policy",
                "production activation",
            ],
            "graph_export_files": {
                "nodes": graph_summary.get("nodes_jsonl"),
                "relationships": graph_summary.get("relationships_jsonl"),
            },
            "node_label_distribution": graph_summary.get("node_label_distribution", {}),
            "relationship_type_distribution": graph_summary.get("relationship_type_distribution", {}),
        },
        "not_allowed": [
            "live Neo4j connection",
            "live graph database write",
            "credential handling",
            "production activation",
            "client-facing guarantee",
        ],
        "neo4j_connection_allowed": False,
        "live_graph_database_write_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    recommendations = {
        "status": "PASS",
        "auto_apply": False,
        "automatic_threshold_mutation_allowed": False,
        "recommendations": [
            {
                "id": "BDR-001",
                "target": "controlled_demo_pack",
                "recommendation": "Create a controlled demo evidence pack using the three selected diagnostic cases and the consolidated telemetry.",
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "BDR-002",
                "target": "graph_adapter_boundary",
                "recommendation": "Review JSONL graph export boundary before implementing any Neo4j connector.",
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "BDR-003",
                "target": "business_metrics",
                "recommendation": "Add estimated time saved, rework avoided and risk avoided fields in the next diagnostic report iteration.",
                "auto_apply": False,
                "requires_human_approval": True,
            },
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness_decision = (
        "READY_FOR_CONTROLLED_DEMO_EVIDENCE_PACK_AND_NON_LIVE_GRAPH_IMPORT_REVIEW"
        if upstream_ready and business_report["case_count"] == 50 and graph_summary.get("node_count", 0) > 0
        else "REVIEW_BUSINESS_DIAGNOSTIC_REPORT_PACK"
    )
    readiness = {
        "status": "PASS" if readiness_decision.startswith("READY") else "WARN",
        "decision": readiness_decision,
        "case_count": business_report["case_count"],
        "ready_for": [
            "controlled demo evidence pack",
            "non-live graph import review",
            "graph adapter interface design",
            "business value metric extension",
        ],
        "not_ready_for": [
            "production activation",
            "autonomous external execution",
            "automatic threshold mutation",
            "client-facing guarantees",
            "live Neo4j connection",
            "live graph database write",
            "credential handling",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS" if readiness["status"] == "PASS" else "WARN",
        "audit": "Business Diagnostic Report Pack and Graph Adapter Boundary audit",
        "case_count": business_report["case_count"],
        "diagnostic_case_count": len(diagnostic_cases),
        "graph_node_count": graph_summary.get("node_count"),
        "graph_relationship_count": graph_summary.get("relationship_count"),
        "external_execution_allowed": False,
        "graph_write_allowed": False,
        "neo4j_connection_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "auto_apply": False,
        "finding": "PASS: business diagnostic report pack and graph adapter boundary generated without execution, threshold mutation or live graph connection.",
        "readiness": readiness["decision"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    outputs = {
        "prod981_1020_business_diagnostic_report_pack.json": business_report,
        "prod981_1020_diagnostic_case_reports.json": {
            "status": "PASS",
            "case_count": len(diagnostic_cases),
            "cases": diagnostic_cases,
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "prod981_1020_graph_adapter_boundary.json": adapter_boundary,
        "prod981_1020_business_diagnostic_recommendations.json": recommendations,
        "prod981_1020_business_diagnostic_readiness.json": readiness,
        "prod981_1020_business_diagnostic_audit_report.json": audit,
    }

    for name, obj in outputs.items():
        write_json(out / name, obj)

    write_text(out / "prod981_1020_business_diagnostic_report_pack.md", build_markdown_report(status, diagnostic_cases, graph_summary, readiness))

    result = {
        "task": "PROD-981..1020",
        "status": audit["status"],
        "phase": "Business Diagnostic Report Pack and Graph Adapter Boundary",
        "decision": readiness["decision"],
        "outputs": ["outputs/" + key for key in outputs.keys()] + ["outputs/prod981_1020_business_diagnostic_report_pack.md"],
        "next_recommended_bundle": "PROD-1021 Controlled Demo Evidence Pack and Non-Live Graph Import Review",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod981_1020_result.json", result)
    write_text(out / "prod981_1020_report.md", "# PROD-981..1020 Report\n\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n")
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

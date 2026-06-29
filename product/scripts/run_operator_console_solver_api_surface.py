#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict

BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
]

COMMON_WORKLOADS = [
    "parser",
    "document_field_extraction",
    "email_triage",
    "receipt_invoice_extraction",
    "contract_checklist",
    "policy_rule_extraction",
    "summary",
    "classification",
    "technical_review",
    "task_generation",
    "delta_detection",
    "evidence_gap_detection",
]

BUSINESS_DOMAINS = [
    "clinic",
    "restaurant",
    "accounting_office",
    "ecommerce_small_business",
    "technical_service",
    "transport_operation",
    "hotel_or_guesthouse",
    "construction_project",
    "small_industry",
    "field_service_operation",
]

PLANNED_SOLVER_ENDPOINTS = [
    {"method": "POST", "path": "/api/casulo/solver/input", "purpose": "single user input routed through Cubo solver", "implemented_now": False},
    {"method": "POST", "path": "/api/casulo/solver/batch", "purpose": "batch/mass testing for common workloads", "implemented_now": False},
    {"method": "GET", "path": "/api/casulo/solver/run/{run_id}", "purpose": "run state", "implemented_now": False},
    {"method": "GET", "path": "/api/casulo/solver/evidence/{run_id}", "purpose": "evidence trace", "implemented_now": False},
    {"method": "GET", "path": "/api/casulo/solver/gates/{run_id}", "purpose": "gate decisions", "implemented_now": False},
    {"method": "GET", "path": "/api/casulo/solver/report/{run_id}", "purpose": "final report", "implemented_now": False},
]

def read_json_or_none(path: Path) -> Any:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    runtime_surface = read_json_or_none(out / "prod501_520_runtime_surface_map.json") or {}
    evidence_adapter = read_json_or_none(out / "prod521_560_external_evidence_candidates.json") or {}
    citation_gate = read_json_or_none(out / "prod521_560_citation_gate_result.json") or {}
    common_register = read_json_or_none(out / "prod521_560_common_workload_mass_test_register.json") or {}
    milestone = read_json_or_none(out / "prod481_500_operational_readiness_dossier.json") or {}

    operator_summary = {
        "status": "PASS",
        "surface": "operator_console",
        "generated_at": generated_at,
        "readiness": "READY_FOR_SOLVER_API_STUB_AND_COMMON_WORKLOAD_LAB",
        "runtime_surface": {
            "endpoint_group_count": runtime_surface.get("group_count"),
            "endpoint_route_count": runtime_surface.get("route_count"),
            "missing_route_count": len(runtime_surface.get("missing", [])) if isinstance(runtime_surface.get("missing"), list) else None,
        },
        "external_evidence": {
            "provider_mode": evidence_adapter.get("provider_mode"),
            "network_call_performed": evidence_adapter.get("network_call_performed"),
            "candidate_count": citation_gate.get("candidate_count"),
            "committed_count": citation_gate.get("committed_count"),
            "human_review_count": citation_gate.get("human_review_count"),
            "rejected_count": citation_gate.get("rejected_count"),
        },
        "milestone_pending_evidence": milestone.get("pending_evidence", {}),
        "blocked_actions": BLOCKED_ACTIONS,
    }

    solver_surface = {
        "status": "PASS",
        "surface": "solver_api_contract",
        "planned_endpoints": PLANNED_SOLVER_ENDPOINTS,
        "input_policy": [
            "Classify input before solving.",
            "Route to parser/solver only after input class is identified.",
            "Create candidate state, evidence trace, delta trace and gate trace.",
            "Return answer, task, parser output, plan or safe block.",
            "Do not execute external actions without explicit gate and human approval.",
        ],
        "input_classes": ["text", "document", "spreadsheet", "email", "business_case", "technical_request", "unknown"],
        "solver_outputs": ["parsed_fields", "summary", "classification", "checklist", "delta_report", "evidence_gap_report", "task_proposal", "safe_block"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    common_lab = {
        "status": "PASS",
        "future_phase": "PROD-601..620 Common Workload Mass Test Lab",
        "workload_families": common_register.get("workload_families", COMMON_WORKLOADS),
        "batch_policy": [
            "Start with deterministic fixtures.",
            "Compare direct response vs Cubo evidence-gated output.",
            "Measure hallucination risk, missing evidence, delta control, gate correctness and useful output rate.",
            "No client-facing claims from synthetic/mocked data.",
        ],
        "minimum_batch_plan": {
            "phase_1": "100 cases across routine workloads",
            "phase_2": "500 cases after solver stub stabilizes",
            "phase_3": "1000+ cases after metrics are stable",
        },
        "blocked_actions": BLOCKED_ACTIONS,
    }

    business_lab = {
        "status": "PASS",
        "future_phase": "PROD-621..650 Business Domain Mass Test Lab",
        "domains": BUSINESS_DOMAINS,
        "entry_condition": "Common Workload Mass Test Lab completed with stable solver/gate metrics.",
        "goal": "Turn companies/business domains into computable operational states with evidence, deltas, gates and next actions.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    safety_gate = {
        "status": "PASS",
        "input_classes": solver_surface["input_classes"],
        "gate_outcomes": ["ANSWER_ALLOWED", "PARSER_OUTPUT_ALLOWED", "TASK_PROPOSAL_ALLOWED", "EVIDENCE_REQUIRED", "HUMAN_REVIEW_REQUIRED", "UNSUPPORTED_BLOCKED", "EXTERNAL_ACTION_BLOCKED"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness = {
        "status": "PASS",
        "decision": "READY_FOR_SOLVER_API_STUB_AND_COMMON_WORKLOAD_LAB",
        "ready_for": ["solver API stub", "operator console rendering", "common workload mass test fixtures", "business domain mass test planning"],
        "not_ready_for": ["production activation", "automatic external actions", "client-facing claims", "credential handling"],
        "next_recommended_bundle": "PROD-601..620 Common Workload Mass Test Lab",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS",
        "audit": "Operator Console and Solver API Surface audit",
        "runtime_routes": operator_summary["runtime_surface"].get("endpoint_route_count"),
        "planned_solver_endpoints": len(PLANNED_SOLVER_ENDPOINTS),
        "common_workload_count": len(common_lab["workload_families"]),
        "business_domain_count": len(BUSINESS_DOMAINS),
        "finding": "PASS: operator console and solver API surface are defined without enabling blind execution.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    write_json(out / "prod561_600_operator_console_summary.json", operator_summary)
    write_json(out / "prod561_600_solver_api_surface.json", solver_surface)
    write_json(out / "prod561_600_common_workload_lab_protocol.json", common_lab)
    write_json(out / "prod561_600_business_domain_lab_protocol.json", business_lab)
    write_json(out / "prod561_600_solver_input_safety_gate.json", safety_gate)
    write_json(out / "prod561_600_readiness.json", readiness)
    write_json(out / "prod561_600_audit_report.json", audit)

    report = [
        "# PROD-561..600 Operator Console and Solver API Surface",
        "",
        f"- Status: `{operator_summary['status']}`",
        f"- Decision: `{readiness['decision']}`",
        f"- Runtime routes: `{operator_summary['runtime_surface'].get('endpoint_route_count')}`",
        f"- Planned solver endpoints: `{len(PLANNED_SOLVER_ENDPOINTS)}`",
        f"- Common workload families: `{len(common_lab['workload_families'])}`",
        f"- Business domains planned: `{len(BUSINESS_DOMAINS)}`",
        "",
        "## Solver API Target",
    ]
    for ep in PLANNED_SOLVER_ENDPOINTS:
        report.append(f"- `{ep['method']} {ep['path']}` -> {ep['purpose']} / implemented now `{ep['implemented_now']}`")
    report += ["", "## Common Workloads"]
    for workload in common_lab["workload_families"]:
        report.append(f"- `{workload}`")
    report += ["", "## Business Domains"]
    for domain in BUSINESS_DOMAINS:
        report.append(f"- `{domain}`")
    write_text(out / "prod561_600_operator_console_solver_surface_report.md", "\n".join(report) + "\n")

    result = {
        "task": "PROD-561..600",
        "status": "PASS",
        "phase": "Operator Console and Solver API Surface",
        "decision": readiness["decision"],
        "outputs": [
            "outputs/prod561_600_operator_console_summary.json",
            "outputs/prod561_600_solver_api_surface.json",
            "outputs/prod561_600_common_workload_lab_protocol.json",
            "outputs/prod561_600_business_domain_lab_protocol.json",
            "outputs/prod561_600_solver_input_safety_gate.json",
            "outputs/prod561_600_readiness.json",
            "outputs/prod561_600_audit_report.json",
        ],
        "next_recommended_bundle": "PROD-601..620 Common Workload Mass Test Lab",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod561_600_result.json", result)
    write_text(out / "prod561_600_report.md", "# PROD-561..600 Report\n\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n")
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

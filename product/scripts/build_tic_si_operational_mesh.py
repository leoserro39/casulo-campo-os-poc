#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
]


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def sample_mesh() -> Dict[str, Any]:
    entities = {
        "applications": [
            {
                "id": "app_customer_portal",
                "name": "Customer Portal",
                "criticality": "high",
                "owner": "TIC/SI",
                "state": "NOT_READY_FOR_PRODUCTION",
                "dependencies": ["svc_auth", "int_erp_billing", "db_customer"]
            },
            {
                "id": "app_internal_finance",
                "name": "Internal Finance Tool",
                "criticality": "medium",
                "owner": "Finance/TIC",
                "state": "CHECK_REQUIRED",
                "dependencies": ["db_finance", "repo_finance_tool"]
            }
        ],
        "services": [
            {"id": "svc_auth", "name": "Authentication Service", "sla": "business_hours", "state": "CHECK_REQUIRED"},
            {"id": "svc_notification", "name": "Notification Service", "sla": "best_effort", "state": "AVAILABLE"}
        ],
        "integrations": [
            {
                "id": "int_erp_billing",
                "name": "ERP Billing Integration",
                "direction": "portal_to_erp",
                "state": "CHECK_REQUIRED",
                "risk": "credential_and_failure_mode_not_documented"
            }
        ],
        "data": [
            {"id": "db_customer", "name": "Customer Database", "classification": "business_sensitive", "state": "ACCESS_REVIEW_REQUIRED"},
            {"id": "db_finance", "name": "Finance Database", "classification": "restricted", "state": "CHECK_REQUIRED"}
        ],
        "access": [
            {"id": "access_admin_portal", "name": "Portal Admin Access", "state": "BLOCKED_ACCESS_REVIEW_REQUIRED"},
            {"id": "access_finance_operator", "name": "Finance Operator Access", "state": "CHECK_REQUIRED"}
        ],
        "incidents": [
            {"id": "inc_001", "summary": "ERP sync delay", "recurrence": "monthly", "state": "ROOT_CAUSE_NOT_CONFIRMED"}
        ],
        "changes": [
            {"id": "chg_001", "summary": "Portal release candidate", "state": "CHANGE_RECORD_REQUIRED"}
        ],
        "suppliers": [
            {"id": "sup_erp_vendor", "name": "ERP Vendor", "state": "SLA_CHECK_REQUIRED"}
        ],
        "deployments": [
            {"id": "dep_portal", "name": "Portal Deployment", "state": "BLOCKED_NO_ROLLBACK_PLAN"}
        ],
        "repositories": [
            {"id": "repo_portal", "name": "customer-portal", "state": "TESTS_AND_DOCS_REQUIRED"},
            {"id": "repo_finance_tool", "name": "internal-finance-tool", "state": "OWNER_REVIEW_REQUIRED"}
        ]
    }

    gates = [
        {
            "gate": "security_gate",
            "status": "BLOCKED_MISSING_EVIDENCE",
            "reason": "admin access review is missing",
            "blocks": ["production_activation", "client_facing_claim"],
            "required_evidence": ["access review", "risk classification"]
        },
        {
            "gate": "production_gate",
            "status": "BLOCKED_NO_ROLLBACK",
            "reason": "portal deployment has no rollback plan",
            "blocks": ["production_activation"],
            "required_evidence": ["rollback plan", "test evidence", "release owner"]
        },
        {
            "gate": "support_gate",
            "status": "CHECK_REQUIRED",
            "reason": "support runbook and owner must be confirmed",
            "blocks": ["implementation_execution"],
            "required_evidence": ["runbook", "support owner"]
        },
        {
            "gate": "continuity_gate",
            "status": "CHECK_REQUIRED",
            "reason": "recovery expectations are not defined",
            "blocks": ["production_activation"],
            "required_evidence": ["recovery plan", "criticality review"]
        },
        {
            "gate": "data_gate",
            "status": "BLOCKED_ACCESS_REVIEW_REQUIRED",
            "reason": "customer and finance data need access and classification review",
            "blocks": ["client_facing_claim", "production_activation"],
            "required_evidence": ["data classification", "access review"]
        },
        {
            "gate": "integration_gate",
            "status": "CHECK_REQUIRED",
            "reason": "ERP failure mode and credential handling are not documented",
            "blocks": ["implementation_execution"],
            "required_evidence": ["integration map", "failure mode", "credential handling"]
        },
        {
            "gate": "change_gate",
            "status": "BLOCKED_CHANGE_RECORD_REQUIRED",
            "reason": "release candidate change record is missing",
            "blocks": ["implementation_execution"],
            "required_evidence": ["change record", "approval trail"]
        },
        {
            "gate": "software_review_gate",
            "status": "CHECK_REQUIRED",
            "reason": "repositories need tests, docs and ownership review",
            "blocks": ["implementation_execution", "production_activation"],
            "required_evidence": ["test results", "architecture review", "repository ownership"]
        }
    ]

    mesh = {
        "contract_version": "operational_cube.tic_si_operational_mesh.v1.4",
        "status": "PASS",
        "vertical_id": "tic_si",
        "mesh_decision": "TIC_SI_INTERNAL_REVIEW_REQUIRED",
        "mesh_reason": "Sample TIC/SI mesh contains missing access review, rollback plan, change record and software review evidence.",
        "entities": entities,
        "gates": gates,
        "delta_summary": {
            "current_state": "systems and dependencies identified, but operational evidence is incomplete",
            "target_state": "controlled internal review with documented gates and software review handoff",
            "primary_delta": "missing evidence for security, rollback, change and software review gates",
            "next_action": "open Software Review and Codex Development Gate package"
        },
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True
    }
    return mesh


def mesh_md(mesh: Dict[str, Any]) -> List[str]:
    lines = [
        "# PROD-061..070 TIC/SI Operational State Mesh",
        "",
        f"- Status: `{mesh['status']}`",
        f"- Vertical: `{mesh['vertical_id']}`",
        f"- Decision: `{mesh['mesh_decision']}`",
        f"- Reason: {mesh['mesh_reason']}",
        "",
        "## Delta Summary",
    ]
    for k, v in mesh["delta_summary"].items():
        lines.append(f"- {k}: `{v}`")
    lines += ["", "## Entity Counts"]
    for k, v in mesh["entities"].items():
        lines.append(f"- `{k}`: `{len(v)}`")
    lines += ["", "## Gates"]
    for gate in mesh["gates"]:
        lines.append(f"- `{gate['gate']}`: `{gate['status']}` — {gate['reason']}")
    lines += ["", "## Blocked Actions"]
    for item in mesh["blocked_actions"]:
        lines.append(f"- `{item}`")
    return lines


def gate_matrix(mesh: Dict[str, Any]) -> Dict[str, Any]:
    counts: Dict[str, int] = {}
    for gate in mesh["gates"]:
        counts[gate["status"]] = counts.get(gate["status"], 0) + 1
    return {
        "contract_version": "operational_cube.tic_si_gate_matrix.v1.4",
        "status": "PASS",
        "vertical_id": "tic_si",
        "gate_status_counts": counts,
        "gates": mesh["gates"],
        "decision": mesh["mesh_decision"],
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True
    }


def review_package(mesh: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "contract_version": "operational_cube.tic_si_review_package.v1.4",
        "status": "PASS",
        "vertical_id": "tic_si",
        "review_decision": "SOFTWARE_REVIEW_HANDOFF_REQUIRED",
        "review_reason": "TIC/SI mesh found blockers that should become software review and development gate tasks.",
        "candidate_systems": [
            {
                "system": "Customer Portal",
                "handoff": "software_review_gate",
                "reasons": ["no rollback plan", "missing access review", "tests and docs required"]
            },
            {
                "system": "Internal Finance Tool",
                "handoff": "software_review_gate",
                "reasons": ["owner review required", "data classification and access review required"]
            }
        ],
        "required_human_decisions": [
            "Confirm system owners.",
            "Confirm whether customer portal can enter controlled software review.",
            "Confirm access and data classification evidence.",
            "Confirm no implementation or production activation is authorized yet."
        ],
        "next_recommended_bundle": "PROD-071..080 Software Review and Codex Development Gate",
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    repo = Path(args.repo)
    out = repo / args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    mesh = sample_mesh()
    gates = gate_matrix(mesh)
    review = review_package(mesh)

    write_json(out / "prod061_070_tic_si_state_mesh.json", mesh)
    write_md(out / "prod061_070_tic_si_state_mesh.md", mesh_md(mesh))

    write_json(out / "prod061_070_tic_si_gate_matrix.json", gates)
    write_md(out / "prod061_070_tic_si_gate_matrix.md", [
        "# PROD-061..070 TIC/SI Gate Matrix",
        "",
        f"- Status: `{gates['status']}`",
        f"- Decision: `{gates['decision']}`",
        "",
        "## Gate Status Counts",
        *[f"- `{k}`: `{v}`" for k, v in gates["gate_status_counts"].items()],
        "",
        "## Gates",
        *[f"- `{g['gate']}`: `{g['status']}` — {g['reason']}" for g in gates["gates"]],
        "",
        "## Blocked Actions",
        *[f"- `{item}`" for item in gates["blocked_actions"]],
    ])

    write_json(out / "prod061_070_tic_si_review_package.json", review)
    write_md(out / "prod061_070_tic_si_review_package.md", [
        "# PROD-061..070 TIC/SI Review Package",
        "",
        f"- Status: `{review['status']}`",
        f"- Review decision: `{review['review_decision']}`",
        f"- Reason: {review['review_reason']}",
        "",
        "## Candidate Systems",
        *[f"- **{item['system']}** → `{item['handoff']}`: {', '.join(item['reasons'])}" for item in review["candidate_systems"]],
        "",
        "## Required Human Decisions",
        *[f"- {item}" for item in review["required_human_decisions"]],
        "",
        "## Next Recommended Bundle",
        f"`{review['next_recommended_bundle']}`",
        "",
        "## Blocked Actions",
        *[f"- `{item}`" for item in review["blocked_actions"]],
    ])

    result = {
        "task": "PROD-061..070",
        "status": "PASS",
        "phase": "TIC/SI Operational State Mesh",
        "vertical_id": "tic_si",
        "decision": mesh["mesh_decision"],
        "outputs": [
            "outputs/prod061_070_tic_si_state_mesh.json",
            "outputs/prod061_070_tic_si_gate_matrix.json",
            "outputs/prod061_070_tic_si_review_package.json"
        ],
        "next_recommended_bundle": "PROD-071..080 Software Review and Codex Development Gate",
        "blocked_actions": BLOCKED_ACTIONS
    }
    write_json(out / "prod061_070_tic_si_state_mesh_result.json", result)
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

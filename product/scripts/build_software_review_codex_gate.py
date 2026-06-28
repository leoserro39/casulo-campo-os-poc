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


def read_json_optional(path: Path) -> Dict[str, Any]:
    if path.exists():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def build(repo: Path) -> Dict[str, Any]:
    outputs = repo / "outputs"
    tic_review = read_json_optional(outputs / "prod061_070_tic_si_review_package.json")

    candidate_systems = tic_review.get("candidate_systems") or [
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
    ]

    intake = {
        "contract_version": "operational_cube.software_review_intake.v1.5",
        "status": "PASS",
        "source_bundle": "PROD-061..070 TIC/SI Operational State Mesh",
        "decision": "SOFTWARE_REVIEW_INTAKE_READY",
        "candidate_systems": candidate_systems,
        "intake_rules": [
            "Review does not authorize implementation.",
            "Review does not authorize production activation.",
            "Repository actions must run in controlled branch/scope.",
            "Human review is required before any code merge or deployment."
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True,
    }

    gate = {
        "contract_version": "operational_cube.software_review_gate.v1.5",
        "status": "PASS",
        "decision": "CONTROLLED_DEVELOPMENT_REVIEW_REQUIRED",
        "decision_reason": "TIC/SI mesh found missing rollback, access review, tests, documentation and ownership evidence.",
        "review_dimensions": [
            {"dimension": "architecture", "status": "CHECK_REQUIRED", "reason": "system boundaries and dependencies must be confirmed"},
            {"dimension": "security", "status": "BLOCKED_MISSING_EVIDENCE", "reason": "access review and risk classification are missing"},
            {"dimension": "documentation", "status": "CHECK_REQUIRED", "reason": "repository and runbook documentation must be reviewed"},
            {"dimension": "tests", "status": "BLOCKED_MISSING_EVIDENCE", "reason": "test evidence is required before controlled development approval"},
            {"dimension": "deployment", "status": "BLOCKED_NO_ROLLBACK", "reason": "rollback plan is missing"},
            {"dimension": "observability", "status": "CHECK_REQUIRED", "reason": "logs and operational signals must be confirmed"},
            {"dimension": "data_model", "status": "CHECK_REQUIRED", "reason": "data classification and access model need review"},
            {"dimension": "operational_ownership", "status": "CHECK_REQUIRED", "reason": "owners must be confirmed for application, support and repository"},
        ],
        "allowed_next_actions": [
            "create controlled development tasks",
            "prepare repository review checklist",
            "allow Codex or equivalent agent to draft tests/docs only within scope",
            "run validators and record evidence",
            "return to human review gate"
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True,
    }

    tasks = {
        "contract_version": "operational_cube.development_tasks.v1.5",
        "status": "PASS",
        "decision": "DEVELOPMENT_TASKS_CREATED_FOR_INTERNAL_REVIEW",
        "tasks": [
            {
                "task_id": "DEV-GATE-001",
                "title": "Confirm system and repository ownership",
                "source_delta": "owner review required",
                "codex_eligible": False,
                "human_required": True,
                "required_evidence": ["owner record", "support owner", "repository maintainer"],
                "gate": "software_review_gate"
            },
            {
                "task_id": "DEV-GATE-002",
                "title": "Create rollback plan template for Customer Portal",
                "source_delta": "no rollback plan",
                "codex_eligible": True,
                "human_required": True,
                "required_evidence": ["rollback plan", "review approval"],
                "gate": "rollback_gate"
            },
            {
                "task_id": "DEV-GATE-003",
                "title": "Draft repository test plan",
                "source_delta": "tests and docs required",
                "codex_eligible": True,
                "human_required": True,
                "required_evidence": ["test plan", "test execution output", "review notes"],
                "gate": "production_gate"
            },
            {
                "task_id": "DEV-GATE-004",
                "title": "Draft architecture and dependency review",
                "source_delta": "system boundaries and dependencies need confirmation",
                "codex_eligible": True,
                "human_required": True,
                "required_evidence": ["architecture summary", "dependency map", "review decision"],
                "gate": "software_review_gate"
            },
            {
                "task_id": "DEV-GATE-005",
                "title": "Prepare access review request",
                "source_delta": "missing access review",
                "codex_eligible": False,
                "human_required": True,
                "required_evidence": ["access matrix", "risk classification", "approval"],
                "gate": "security_gate"
            },
            {
                "task_id": "DEV-GATE-006",
                "title": "Document ERP integration failure mode",
                "source_delta": "ERP failure mode and credential handling are not documented",
                "codex_eligible": True,
                "human_required": True,
                "required_evidence": ["integration map", "failure mode notes", "credential handling policy reference"],
                "gate": "integration_gate"
            }
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True,
    }

    codex_scope = {
        "contract_version": "operational_cube.codex_scope.v1.5",
        "status": "PASS",
        "decision": "CODEX_ALLOWED_ONLY_AS_CONTROLLED_DRAFT_EXECUTOR",
        "role": "Codex or equivalent coding agent may draft tests, documentation, small patches and review summaries only inside an explicit branch/task scope.",
        "allowed_actions": [
            "read supplied repository context",
            "draft tests",
            "draft documentation",
            "draft architecture notes",
            "draft small non-production patches",
            "summarize evidence gaps",
            "prepare pull request text"
        ],
        "blocked_actions": [
            "production deployment",
            "automatic merge",
            "handling real credentials",
            "client-facing claim",
            "modifying security-sensitive logic without explicit human review",
            "changing infrastructure or deployment target without approval"
        ],
        "required_controls": [
            "explicit task id",
            "branch or patch scope",
            "test command",
            "evidence output path",
            "human reviewer",
            "gate decision"
        ],
        "blocked_product_actions": BLOCKED_ACTIONS,
        "internal_use_only": True,
    }

    result = {
        "contract_version": "operational_cube.software_review_codex_gate.v1.5",
        "status": "PASS",
        "decision": "SOFTWARE_REVIEW_AND_CODEX_GATE_READY_FOR_INTERNAL_REVIEW",
        "source": "PROD-061..070 TIC/SI Operational State Mesh",
        "outputs": [
            "outputs/prod071_080_software_review_intake.json",
            "outputs/prod071_080_software_review_gate.json",
            "outputs/prod071_080_development_tasks.json",
            "outputs/prod071_080_codex_scope.json"
        ],
        "next_recommended_bundle": "PROD-081..090 PME AI Program / Client Demo Pack",
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True,
    }

    return {
        "intake": intake,
        "gate": gate,
        "tasks": tasks,
        "codex_scope": codex_scope,
        "result": result,
    }


def intake_md(obj: Dict[str, Any]) -> List[str]:
    lines = [
        "# PROD-071..080 Software Review Intake",
        "",
        f"- Status: `{obj['status']}`",
        f"- Decision: `{obj['decision']}`",
        f"- Source bundle: `{obj['source_bundle']}`",
        "",
        "## Candidate Systems",
    ]
    for item in obj["candidate_systems"]:
        lines.append(f"- **{item['system']}** -> `{item.get('handoff', 'software_review_gate')}`: {', '.join(item.get('reasons', []))}")
    lines += ["", "## Intake Rules"]
    for rule in obj["intake_rules"]:
        lines.append(f"- {rule}")
    lines += ["", "## Blocked Actions"]
    for action in obj["blocked_actions"]:
        lines.append(f"- `{action}`")
    return lines


def gate_md(obj: Dict[str, Any]) -> List[str]:
    lines = [
        "# PROD-071..080 Software Review Gate",
        "",
        f"- Status: `{obj['status']}`",
        f"- Decision: `{obj['decision']}`",
        f"- Reason: {obj['decision_reason']}",
        "",
        "## Review Dimensions",
    ]
    for item in obj["review_dimensions"]:
        lines.append(f"- `{item['dimension']}`: `{item['status']}` - {item['reason']}")
    lines += ["", "## Allowed Next Actions"]
    for item in obj["allowed_next_actions"]:
        lines.append(f"- {item}")
    lines += ["", "## Blocked Actions"]
    for action in obj["blocked_actions"]:
        lines.append(f"- `{action}`")
    return lines


def tasks_md(obj: Dict[str, Any]) -> List[str]:
    lines = [
        "# PROD-071..080 Development Tasks",
        "",
        f"- Status: `{obj['status']}`",
        f"- Decision: `{obj['decision']}`",
        "",
        "## Tasks",
    ]
    for task in obj["tasks"]:
        codex = "yes" if task["codex_eligible"] else "no"
        lines.append(f"- `{task['task_id']}` — **{task['title']}** — Codex eligible: `{codex}` — Gate: `{task['gate']}`")
    lines += ["", "## Blocked Actions"]
    for action in obj["blocked_actions"]:
        lines.append(f"- `{action}`")
    return lines


def codex_md(obj: Dict[str, Any]) -> List[str]:
    lines = [
        "# PROD-071..080 Codex Scope",
        "",
        f"- Status: `{obj['status']}`",
        f"- Decision: `{obj['decision']}`",
        "",
        "## Role",
        obj["role"],
        "",
        "## Allowed Actions",
    ]
    for item in obj["allowed_actions"]:
        lines.append(f"- {item}")
    lines += ["", "## Blocked Actions"]
    for item in obj["blocked_actions"]:
        lines.append(f"- {item}")
    lines += ["", "## Required Controls"]
    for item in obj["required_controls"]:
        lines.append(f"- {item}")
    return lines


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    repo = Path(args.repo)
    out = repo / args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    built = build(repo)

    write_json(out / "prod071_080_software_review_intake.json", built["intake"])
    write_md(out / "prod071_080_software_review_intake.md", intake_md(built["intake"]))

    write_json(out / "prod071_080_software_review_gate.json", built["gate"])
    write_md(out / "prod071_080_software_review_gate.md", gate_md(built["gate"]))

    write_json(out / "prod071_080_development_tasks.json", built["tasks"])
    write_md(out / "prod071_080_development_tasks.md", tasks_md(built["tasks"]))

    write_json(out / "prod071_080_codex_scope.json", built["codex_scope"])
    write_md(out / "prod071_080_codex_scope.md", codex_md(built["codex_scope"]))

    write_json(out / "prod071_080_software_review_codex_gate_result.json", built["result"])

    print(json.dumps(built["result"], indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

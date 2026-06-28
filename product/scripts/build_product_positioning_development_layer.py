#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict


BLOCKED_ACTIONS = [
    "automatic_nomination",
    "client_facing_claim",
    "implementation_execution",
    "production_activation",
]

LAYERS = [
    {
        "layer": "Operational State Layer",
        "purpose": "Transform business, technical and process reality into computable state.",
        "keywords": ["state", "domain", "entity", "status", "risk"]
    },
    {
        "layer": "Evidence Layer",
        "purpose": "Attach facts, documents, signals and checks to state transitions.",
        "keywords": ["evidence", "manifest", "source", "traceability"]
    },
    {
        "layer": "Gate Layer",
        "purpose": "Block or release actions based on rules, risk and human decisions.",
        "keywords": ["gate", "decision", "approval", "blocked action"]
    },
    {
        "layer": "Delta Layer",
        "purpose": "Measure the gap between current state and target operating state.",
        "keywords": ["delta", "before/after", "gap", "next action"]
    },
    {
        "layer": "TIC/SI State Mesh",
        "purpose": "Connect systems, services, applications, incidents, changes, access and suppliers as a technical-operational mesh.",
        "keywords": ["application", "integration", "incident", "change", "access", "supplier"]
    },
    {
        "layer": "Development Layer",
        "purpose": "Transform operational deltas into governed software tasks, review gates, tests, PRs and delivery evidence.",
        "keywords": ["software review", "Codex", "task", "PR", "tests", "release gate"]
    },
    {
        "layer": "AI Program Layer",
        "purpose": "Package AI adoption as an operating program that requires state, evidence, gates and measured deltas.",
        "keywords": ["AI program", "SME", "governance", "adoption", "value"]
    }
]


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(path: Path, title: str, obj: Dict[str, Any]) -> None:
    lines = [f"# {title}", ""]
    if "summary" in obj:
        lines += ["## Summary", obj["summary"], ""]
    if "layers" in obj:
        lines += ["## Layers"]
        for layer in obj["layers"]:
            lines.append(f"- **{layer['layer']}** — {layer['purpose']}")
        lines.append("")
    if "offers" in obj:
        lines += ["## Suggested Offers"]
        for offer in obj["offers"]:
            lines.append(f"- **{offer['name']}**: {offer['purpose']}")
        lines.append("")
    if "gates" in obj:
        lines += ["## Gates"]
        for gate in obj["gates"]:
            lines.append(f"- `{gate}`")
        lines.append("")
    if "review_dimensions" in obj:
        lines += ["## Review Dimensions"]
        for item in obj["review_dimensions"]:
            lines.append(f"- `{item}`")
        lines.append("")
    if "roadmap" in obj:
        lines += ["## Roadmap"]
        for item in obj["roadmap"]:
            lines.append(f"- {item}")
        lines.append("")
    lines += ["## Blocked Actions"]
    for item in obj.get("blocked_actions", []):
        lines.append(f"- `{item}`")
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def build(repo: Path) -> Dict[str, Any]:
    release_candidate = {}
    rc_path = repo / "outputs/prod046_050_release_candidate.json"
    if rc_path.exists():
        release_candidate = json.loads(rc_path.read_text(encoding="utf-8"))

    positioning = {
        "contract_version": "operational_cube.product_positioning.v1.3",
        "status": "PASS",
        "product": "Cubo Operacional / Operational Cube",
        "method": "CASULO",
        "positioning": "An operational intelligence and AI-program layer that turns processes, systems, data and software into computable state, measurable deltas, gates and governed actions.",
        "not_a": [
            "not a simple checklist",
            "not a generic chatbot",
            "not only a dashboard",
            "not uncontrolled automation"
        ],
        "layers": LAYERS,
        "target_markets": [
            "small and medium businesses with recurring operations",
            "accounting and backoffice firms",
            "technical services and field operations",
            "TIC/SI teams",
            "companies with legacy software or undocumented internal systems",
            "AI adoption programs that need governance and measurable value"
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True,
    }

    development_layer = {
        "contract_version": "operational_cube.development_layer.v1.3",
        "status": "PASS",
        "summary": "The development layer converts operational deltas into governed software work: tasks, tests, code review, pull requests, evidence and gate decisions.",
        "flow": [
            "detect operational or technical delta",
            "classify risk and evidence needs",
            "create governed development task",
            "use Codex or equivalent assistant only inside controlled scope",
            "run tests and validators",
            "record evidence",
            "human review gate approves or blocks",
            "release only after explicit approval"
        ],
        "execution_roles": [
            "human architect",
            "human engineer",
            "coding agent",
            "validator",
            "gate reviewer"
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True,
    }

    tic_mesh = {
        "contract_version": "operational_cube.tic_state_mesh.v1.3",
        "status": "PASS",
        "summary": "The TIC/SI mesh connects applications, services, integrations, access, incidents, changes, data, suppliers and deployments into a computable operational state.",
        "entities": [
            "application",
            "service",
            "integration",
            "database",
            "access profile",
            "incident",
            "change request",
            "supplier",
            "certificate",
            "deployment",
            "repository"
        ],
        "gates": [
            "security_gate",
            "production_gate",
            "support_gate",
            "continuity_gate",
            "data_gate",
            "integration_gate",
            "change_gate",
            "rollback_gate"
        ],
        "example": {
            "system": "customer portal",
            "state": "not ready for production",
            "blocking_factors": ["no rollback plan", "missing tests", "insufficient access review"],
            "next_action": "open software review gate and development delta package"
        },
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True,
    }

    software_review = {
        "contract_version": "operational_cube.software_review_gate.v1.3",
        "status": "PASS",
        "summary": "The software review gate evaluates whether an existing or planned solution is safe, maintainable, testable and operationally ready.",
        "review_dimensions": [
            "architecture",
            "security",
            "documentation",
            "tests",
            "deployment",
            "observability",
            "data model",
            "integration model",
            "operational ownership",
            "rollback"
        ],
        "decision_states": [
            "BLOCKED_NO_EVIDENCE",
            "BLOCKED_HIGH_RISK",
            "CHECK_REQUIRED",
            "READY_FOR_INTERNAL_REVIEW",
            "APPROVED_FOR_CONTROLLED_DEVELOPMENT"
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True,
    }

    commercial = {
        "contract_version": "operational_cube.commercial_packages.v1.3",
        "status": "PASS",
        "summary": "Suggested service packages for SMEs and technical teams.",
        "offers": [
            {
                "name": "CASULO Operational Diagnosis",
                "purpose": "Map current state, evidence gaps, risks and first gates."
            },
            {
                "name": "Cubo PME Starter",
                "purpose": "Install a first operational cube for one recurring process."
            },
            {
                "name": "TIC/SI State Mesh",
                "purpose": "Map applications, integrations, incidents, access, changes and gates."
            },
            {
                "name": "Software Review Gate",
                "purpose": "Review existing software and produce a controlled improvement plan."
            },
            {
                "name": "Solution Factory Sprint",
                "purpose": "Transform approved deltas into governed software tasks, tests and delivery evidence."
            },
            {
                "name": "AI Program Operating Layer",
                "purpose": "Structure AI adoption around state, evidence, governance, value deltas and safe execution."
            }
        ],
        "roadmap": [
            "PROD-061..070 TIC/SI Operational State Mesh",
            "PROD-071..080 Software Review and Codex Development Gate",
            "PROD-081..090 PME AI Program / Client Demo Pack"
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True,
    }

    return {
        "positioning": positioning,
        "development_layer": development_layer,
        "tic_state_mesh": tic_mesh,
        "software_review_gate": software_review,
        "commercial_packages": commercial,
        "release_candidate_context": release_candidate,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    repo = Path(args.repo)
    out = repo / args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    result = build(repo)

    files = [
        ("prod051_060_product_positioning", "Product Positioning", result["positioning"]),
        ("prod051_060_development_layer", "Development Layer", result["development_layer"]),
        ("prod051_060_tic_state_mesh", "TIC/SI State Mesh", result["tic_state_mesh"]),
        ("prod051_060_software_review_gate", "Software Review Gate", result["software_review_gate"]),
        ("prod051_060_commercial_packages", "Commercial Packages and AI Program", result["commercial_packages"]),
    ]

    for stem, title, obj in files:
        write_json(out / f"{stem}.json", obj)
        write_md(out / f"{stem}.md", title, obj)

    summary = {
        "contract_version": "operational_cube.product_positioning_development_layer.v1.3",
        "status": "PASS",
        "product": "Cubo Operacional / Operational Cube",
        "method": "CASULO",
        "generated_outputs": [f"outputs/{stem}.json" for stem, _, _ in files],
        "next_recommended_bundle": "PROD-061..070 TIC/SI Operational State Mesh",
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True,
    }
    write_json(out / "prod051_060_product_positioning_development_layer_result.json", summary)

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

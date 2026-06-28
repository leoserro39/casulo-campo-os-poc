#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


BLOCKED_ACTIONS = [
    "automatic_nomination",
    "client_facing_claim",
    "implementation_execution",
    "production_activation",
]


MILESTONE_FILES = [
    ("Product foundation", "outputs/prod001_005_product_foundation_report.md"),
    ("Vertical case pack", "outputs/prod_vert001_003_vertical_case_pack_report.md"),
    ("Vertical runtime adapter", "outputs/prod_vert004_006_vertical_runtime_adapter_report.md"),
    ("Product runtime API", "outputs/prod006_010_product_runtime_api_report.md"),
    ("Product UI shell", "outputs/prod011_015_product_ui_shell_report.md"),
    ("VesselFlow state definition", "outputs/prod016_020_vesselflow_state_definition.json"),
    ("VesselFlow state report export", "outputs/prod021_025_vesselflow_state_report_export.json"),
    ("VesselFlow real data intake preview", "outputs/prod026_030_vesselflow_real_data_intake_preview.json"),
    ("VesselFlow real data delta review", "outputs/prod031_035_vesselflow_real_data_delta_review.json"),
    ("VesselFlow data-backed rerun", "outputs/prod036_040_vesselflow_data_backed_rerun.json"),
    ("VesselFlow evidence comparator", "outputs/prod036_040_vesselflow_evidence_comparator.json"),
    ("VesselFlow human review package", "outputs/prod041_045_vesselflow_human_review_package.json"),
    ("VesselFlow decision gate", "outputs/prod041_045_vesselflow_decision_gate.json"),
]


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def optional_json(path: Path) -> Dict[str, Any]:
    if path.exists():
        return read_json(path)
    return {}


def file_status(repo: Path) -> List[Dict[str, Any]]:
    rows = []
    for name, rel in MILESTONE_FILES:
        path = repo / rel
        rows.append({
            "name": name,
            "path": rel,
            "exists": path.exists(),
            "kind": "json" if rel.endswith(".json") else "markdown",
        })
    return rows


def build(repo: Path) -> Dict[str, Any]:
    outputs = repo / "outputs"

    human_gate = optional_json(outputs / "prod041_045_vesselflow_decision_gate.json")
    human_review = optional_json(outputs / "prod041_045_vesselflow_human_review_package.json")
    comparator = optional_json(outputs / "prod036_040_vesselflow_evidence_comparator.json")
    rerun = optional_json(outputs / "prod036_040_vesselflow_data_backed_rerun.json")

    milestones = file_status(repo)
    missing = [m for m in milestones if not m["exists"]]

    freeze = {
        "contract_version": "operational_cube.internal_review_freeze.v1.2",
        "status": "PASS" if not missing else "INCOMPLETE",
        "product_direction": "Cubo Operacional / Operational Cube",
        "release_candidate": "Cubo Operacional Internal RC v1.2",
        "freeze_scope": "controlled_internal_review",
        "frozen_verticals": [
            "vesselflow"
        ],
        "frozen_capabilities": [
            "state definition",
            "evidence manifest",
            "gate matrix",
            "state report export",
            "real/anonymized intake preview",
            "before/after delta review",
            "data-backed rerun check-only",
            "evidence comparator",
            "human review package",
            "decision gate"
        ],
        "milestones": milestones,
        "missing_milestones": missing,
        "current_decision": human_gate.get("decision", "UNKNOWN"),
        "current_decision_reason": human_gate.get("decision_reason"),
        "state_summary": human_review.get("state_summary", {}),
        "evidence_status_counts": comparator.get("evidence_status_counts", {}),
        "gate_status_counts": comparator.get("gate_status_counts", {}),
        "rerun": {
            "mode": rerun.get("mode"),
            "ready_for_write_rerun": rerun.get("ready_for_write_rerun"),
            "warnings": rerun.get("warnings", []),
            "errors": rerun.get("errors", []),
        },
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True,
    }

    release_candidate = {
        "contract_version": "operational_cube.release_candidate.v1.2",
        "status": "PASS" if freeze["status"] == "PASS" else "INCOMPLETE",
        "release_candidate": "Cubo Operacional Internal RC v1.2",
        "decision": "INTERNAL_RELEASE_CANDIDATE_ONLY",
        "decision_gate": freeze["current_decision"],
        "summary": "The product is ready for internal controlled review, but remains blocked for external, production or automatic operational use until reviewed real/anonymized data is provided and human gates approve the transition.",
        "validated_capabilities": freeze["frozen_capabilities"],
        "required_before_external_demo": [
            "Provide reviewed real/anonymized VesselFlow data.",
            "Run intake --check.",
            "Run explicit --write --rerun-state only after approval.",
            "Regenerate report export and evidence comparator.",
            "Record human decision to move gate from blocked to controlled internal demo.",
            "Prepare a non-production demo script with clear limitations."
        ],
        "next_recommended_bundle": "PROD-051..060 Product Positioning and Development Layer",
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True,
    }

    return {"freeze": freeze, "release_candidate": release_candidate}


def freeze_md(freeze: Dict[str, Any]) -> str:
    lines = [
        "# PROD-046..050 Internal Review Freeze",
        "",
        f"- Status: `{freeze['status']}`",
        f"- Product direction: `{freeze['product_direction']}`",
        f"- Release candidate: `{freeze['release_candidate']}`",
        f"- Scope: `{freeze['freeze_scope']}`",
        f"- Current decision: `{freeze['current_decision']}`",
        f"- Reason: {freeze.get('current_decision_reason')}",
        "",
        "## Frozen Capabilities",
    ]
    for item in freeze["frozen_capabilities"]:
        lines.append(f"- {item}")
    lines += ["", "## Milestones"]
    for item in freeze["milestones"]:
        mark = "OK" if item["exists"] else "MISSING"
        lines.append(f"- `{mark}` — {item['name']} — `{item['path']}`")
    lines += ["", "## State Summary"]
    if freeze["state_summary"]:
        for k, v in freeze["state_summary"].items():
            lines.append(f"- {k}: `{v}`")
    else:
        lines.append("- Not available")
    lines += ["", "## Evidence Status Counts"]
    if freeze["evidence_status_counts"]:
        for k, v in freeze["evidence_status_counts"].items():
            lines.append(f"- `{k}`: `{v}`")
    else:
        lines.append("- Not available")
    lines += ["", "## Gate Status Counts"]
    if freeze["gate_status_counts"]:
        for k, v in freeze["gate_status_counts"].items():
            lines.append(f"- `{k}`: `{v}`")
    else:
        lines.append("- Not available")
    lines += ["", "## Blocked Actions"]
    for item in freeze["blocked_actions"]:
        lines.append(f"- `{item}`")
    lines += ["", "This freeze is internal-only and does not authorize production, external claim, automatic nomination or implementation execution.", ""]
    return "\n".join(lines)


def rc_md(rc: Dict[str, Any]) -> str:
    lines = [
        "# PROD-046..050 Cubo Operacional Internal Release Candidate",
        "",
        f"- Status: `{rc['status']}`",
        f"- Release candidate: `{rc['release_candidate']}`",
        f"- Decision: `{rc['decision']}`",
        f"- Decision gate: `{rc['decision_gate']}`",
        "",
        "## Summary",
        rc["summary"],
        "",
        "## Validated Capabilities",
    ]
    for item in rc["validated_capabilities"]:
        lines.append(f"- {item}")
    lines += ["", "## Required Before External Demo"]
    for item in rc["required_before_external_demo"]:
        lines.append(f"- {item}")
    lines += ["", "## Next Recommended Bundle", f"`{rc['next_recommended_bundle']}`", "", "## Blocked Actions"]
    for item in rc["blocked_actions"]:
        lines.append(f"- `{item}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    repo = Path(args.repo)
    out = repo / args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    result = build(repo)
    freeze = result["freeze"]
    rc = result["release_candidate"]

    (out / "prod046_050_internal_review_freeze.json").write_text(json.dumps(freeze, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "prod046_050_internal_review_freeze.md").write_text(freeze_md(freeze), encoding="utf-8")
    (out / "prod046_050_release_candidate.json").write_text(json.dumps(rc, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "prod046_050_release_candidate.md").write_text(rc_md(rc), encoding="utf-8")

    print(json.dumps({
        "status": "PASS" if freeze["status"] == "PASS" and rc["status"] == "PASS" else "INCOMPLETE",
        "release_candidate": rc["release_candidate"],
        "decision": rc["decision"],
        "decision_gate": rc["decision_gate"],
        "outputs": [
            str(out / "prod046_050_internal_review_freeze.json"),
            str(out / "prod046_050_internal_review_freeze.md"),
            str(out / "prod046_050_release_candidate.json"),
            str(out / "prod046_050_release_candidate.md"),
        ],
    }, indent=2, ensure_ascii=False))
    return 0 if freeze["status"] == "PASS" and rc["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

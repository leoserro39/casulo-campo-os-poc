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


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def optional_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    return read_json(path)


def decision_from(evidence: Dict[str, Any], rerun: Dict[str, Any], comparator: Dict[str, Any]) -> str:
    ready = bool(rerun.get("ready_for_write_rerun", False))
    internal_result = comparator.get("internal_review_result")
    state = comparator.get("state", {})

    if state.get("data_mode") == "sample_placeholder":
        return "BLOCKED_WAITING_FOR_REAL_OR_ANONYMIZED_DATA"
    if not ready:
        return "BLOCKED_WAITING_FOR_REAL_OR_ANONYMIZED_DATA"
    if internal_result != "READY_FOR_CONTROLLED_WRITE_RERUN":
        return "BLOCKED_WAITING_FOR_HUMAN_REVIEW"
    return "READY_FOR_INTERNAL_REVIEW_ONLY"


def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    state = optional_json(out / "prod016_020_vesselflow_state_definition.json")
    report = optional_json(out / "prod021_025_vesselflow_state_report_export.json")
    delta = optional_json(out / "prod031_035_vesselflow_real_data_delta_review.json")
    rerun = optional_json(out / "prod036_040_vesselflow_data_backed_rerun.json")
    comparator = optional_json(out / "prod036_040_vesselflow_evidence_comparator.json")

    decision = decision_from(report, rerun, comparator)

    review_items = [
        {
            "item": "data_source",
            "status": "BLOCKED" if comparator.get("state", {}).get("data_mode") == "sample_placeholder" else "CHECK_REQUIRED",
            "note": "Current state is still sample placeholder until reviewed real/anonymized data is written and rerun."
        },
        {
            "item": "evidence_manifest",
            "status": "CHECK_REQUIRED",
            "note": "Review evidence status counts and missing/not provided records."
        },
        {
            "item": "gate_matrix",
            "status": "BLOCKED" if decision.startswith("BLOCKED") else "CHECK_REQUIRED",
            "note": "Gate movement cannot authorize execution without human approval."
        },
        {
            "item": "risk_fragility",
            "status": "HIGH_ATTENTION" if comparator.get("state", {}).get("risk_level") == "HIGH" else "CHECK_REQUIRED",
            "note": "Risk remains high while evidence is placeholder/missing."
        },
        {
            "item": "external_use",
            "status": "BLOCKED",
            "note": "No client-facing claim or production activation is allowed."
        },
    ]

    package = {
        "contract_version": "operational_cube.human_review_package.v1.1",
        "status": "PASS",
        "vertical_id": "vesselflow",
        "case_id": state.get("case_id") or comparator.get("case_id"),
        "decision": decision,
        "decision_reason": "Real/anonymized evidence is not yet ready for write/rerun." if decision.startswith("BLOCKED_WAITING_FOR_REAL") else "Human review required before any controlled demo.",
        "state_summary": {
            "data_mode": state.get("state_snapshot", {}).get("data_mode") or comparator.get("state", {}).get("data_mode"),
            "state_decision": state.get("state_snapshot", {}).get("decision") or comparator.get("state", {}).get("decision"),
            "risk_level": state.get("risk_fragility_summary", {}).get("risk_level") or comparator.get("state", {}).get("risk_level"),
        },
        "evidence_status_counts": comparator.get("evidence_status_counts", {}),
        "gate_status_counts": comparator.get("gate_status_counts", {}),
        "delta": delta.get("delta", {}),
        "rerun": {
            "mode": rerun.get("mode"),
            "ready_for_write_rerun": rerun.get("ready_for_write_rerun"),
            "warnings": rerun.get("warnings", []),
            "errors": rerun.get("errors", []),
        },
        "review_items": review_items,
        "required_human_decisions": [
            "Confirm whether real/anonymized VesselFlow data can be used internally.",
            "Confirm whether evidence is sufficient for a controlled demo.",
            "Confirm whether gates may move from BLOCKED_SAMPLE_DATA to CHECK_REQUIRED.",
            "Confirm no automatic nomination or external use will be executed.",
        ],
        "allowed_next_actions": [
            "Prepare reviewed real/anonymized intake JSON.",
            "Run intake --check.",
            "If approved, run explicit --write --rerun-state.",
            "Regenerate report export and evidence comparator.",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True,
    }
    return package


def md(package: Dict[str, Any]) -> str:
    lines = [
        "# PROD-041..045 VesselFlow Human Review Package",
        "",
        f"- Status: `{package['status']}`",
        f"- Vertical: `{package['vertical_id']}`",
        f"- Case: `{package.get('case_id')}`",
        f"- Decision: `{package['decision']}`",
        f"- Reason: {package['decision_reason']}",
        "",
        "## State Summary",
    ]
    for k, v in package["state_summary"].items():
        lines.append(f"- {k}: `{v}`")
    lines += ["", "## Evidence Status Counts"]
    if package["evidence_status_counts"]:
        for k, v in package["evidence_status_counts"].items():
            lines.append(f"- `{k}`: `{v}`")
    else:
        lines.append("- None")
    lines += ["", "## Gate Status Counts"]
    if package["gate_status_counts"]:
        for k, v in package["gate_status_counts"].items():
            lines.append(f"- `{k}`: `{v}`")
    else:
        lines.append("- None")
    lines += ["", "## Review Items"]
    for item in package["review_items"]:
        lines.append(f"- `{item['item']}`: `{item['status']}` — {item['note']}")
    lines += ["", "## Required Human Decisions"]
    for item in package["required_human_decisions"]:
        lines.append(f"- {item}")
    lines += ["", "## Allowed Next Actions"]
    for item in package["allowed_next_actions"]:
        lines.append(f"- {item}")
    lines += ["", "## Blocked Actions"]
    for item in package["blocked_actions"]:
        lines.append(f"- `{item}`")
    lines += ["", "## Internal Use", "", "This package is for internal controlled review only.", ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    repo = Path(args.repo)
    out = repo / args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    package = build(repo)
    (out / "prod041_045_vesselflow_human_review_package.json").write_text(
        json.dumps(package, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out / "prod041_045_vesselflow_human_review_package.md").write_text(
        md(package),
        encoding="utf-8",
    )

    decision = {
        "contract_version": "operational_cube.decision_gate.v1.1",
        "status": "PASS",
        "vertical_id": "vesselflow",
        "decision": package["decision"],
        "decision_reason": package["decision_reason"],
        "allowed_next_actions": package["allowed_next_actions"],
        "blocked_actions": package["blocked_actions"],
        "internal_use_only": True,
    }
    (out / "prod041_045_vesselflow_decision_gate.json").write_text(
        json.dumps(decision, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out / "prod041_045_vesselflow_decision_gate.md").write_text(
        "# PROD-041..045 VesselFlow Decision Gate\n\n"
        f"- Status: `{decision['status']}`\n"
        f"- Decision: `{decision['decision']}`\n"
        f"- Reason: {decision['decision_reason']}\n\n"
        "## Blocked Actions\n"
        + "\n".join(f"- `{item}`" for item in decision["blocked_actions"])
        + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"status": "PASS", "decision": package["decision"], "outputs": [
        str(out / "prod041_045_vesselflow_human_review_package.json"),
        str(out / "prod041_045_vesselflow_human_review_package.md"),
        str(out / "prod041_045_vesselflow_decision_gate.json"),
        str(out / "prod041_045_vesselflow_decision_gate.md"),
    ]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

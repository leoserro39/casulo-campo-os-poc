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


def evidence_summary(items: List[Dict[str, Any]]) -> Dict[str, int]:
    out = {"available": 0, "missing_or_not_provided": 0, "placeholder": 0}
    for item in items:
        status = str(item.get("status", ""))
        if item.get("available"):
            out["available"] += 1
        if "NOT_PROVIDED" in status or "MISSING" in status:
            out["missing_or_not_provided"] += 1
        if "PLACEHOLDER" in status or "WAITING_FOR_USER_DATA" in status:
            out["placeholder"] += 1
    return out


def gate_summary(items: List[Dict[str, Any]]) -> Dict[str, int]:
    out: Dict[str, int] = {}
    for item in items:
        status = str(item.get("status", "UNKNOWN"))
        out[status] = out.get(status, 0) + 1
    return out


def build_review(repo: Path) -> Dict[str, Any]:
    state_path = repo / "outputs/prod016_020_vesselflow_state_definition.json"
    intake_path = repo / "outputs/prod026_030_vesselflow_real_data_intake_preview.json"

    if not state_path.exists():
        raise FileNotFoundError(f"missing state definition: {state_path}")
    if not intake_path.exists():
        raise FileNotFoundError(f"missing real data intake preview: {intake_path}")

    state = read_json(state_path)
    intake_preview = read_json(intake_path)
    validation = intake_preview.get("validation", {})
    candidate = intake_preview.get("candidate_import_input", {})

    before = {
        "case_id": state.get("case_id"),
        "data_mode": state.get("state_snapshot", {}).get("data_mode"),
        "decision": state.get("state_snapshot", {}).get("decision"),
        "risk_level": state.get("risk_fragility_summary", {}).get("risk_level"),
        "evidence": evidence_summary(state.get("evidence_manifest", [])),
        "gates": gate_summary(state.get("gate_matrix", [])),
    }

    after_candidate = {
        "case_id": candidate.get("case_id"),
        "intake_status": validation.get("intake_status"),
        "data_classification": validation.get("data_classification"),
        "validation_status": validation.get("status"),
        "warnings": validation.get("warnings", []),
        "errors": validation.get("errors", []),
        "dataset_status": candidate.get("dataset_or_workbook", {}).get("status"),
        "dataset_reference": candidate.get("dataset_or_workbook", {}).get("path_or_reference"),
    }

    ready_for_data_backed_rerun = (
        validation.get("status") == "PASS"
        and after_candidate.get("intake_status") in ["ANONYMIZED_DATA_READY", "REAL_DATA_READY"]
        and after_candidate.get("dataset_reference")
        and after_candidate.get("dataset_reference") != "REPLACE_WITH_REAL_OR_ANONYMIZED_WORKBOOK_OR_DATASET"
    )

    delta = {
        "data_mode_change": f"{before.get('data_mode')} -> {after_candidate.get('dataset_status')}",
        "risk_change_expected": "CAN_REDUCE_AFTER_REAL_DATA_RERUN" if ready_for_data_backed_rerun else "NO_REDUCTION_YET_WAITING_FOR_DATA",
        "gate_change_expected": "CAN_MOVE_FROM_BLOCKED_SAMPLE_DATA_TO_CHECK_REQUIRED_AFTER_RERUN" if ready_for_data_backed_rerun else "NO_GATE_CHANGE_YET",
        "evidence_change_expected": "DATASET_REFERENCE_READY" if ready_for_data_backed_rerun else "DATASET_REFERENCE_NOT_READY",
        "ready_for_write_rerun": bool(ready_for_data_backed_rerun),
    }

    next_actions = [
        "Fill a reviewed real/anonymized VesselFlow intake JSON.",
        "Run prepare_vesselflow_real_data_intake.py --check.",
        "If PASS and reviewed, run --write --rerun-state.",
        "Regenerate report export.",
        "Review gates before any external use.",
    ]

    if ready_for_data_backed_rerun:
        next_actions.insert(0, "Candidate intake is ready for controlled --write --rerun-state.")

    return {
        "contract_version": "operational_cube.real_data_delta_review.v0.9",
        "status": "PASS",
        "case_id": before.get("case_id"),
        "before": before,
        "after_candidate": after_candidate,
        "delta": delta,
        "next_controlled_actions": next_actions,
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True,
    }


def md(review: Dict[str, Any]) -> str:
    lines = [
        "# PROD-031..035 VesselFlow Real Data Delta Review",
        "",
        f"- Status: `{review['status']}`",
        f"- Case: `{review.get('case_id')}`",
        f"- Internal use only: `{review.get('internal_use_only')}`",
        "",
        "## Before",
    ]
    before = review["before"]
    for key in ["data_mode", "decision", "risk_level"]:
        lines.append(f"- {key}: `{before.get(key)}`")
    lines += ["", "## After Candidate"]
    after = review["after_candidate"]
    for key in ["intake_status", "data_classification", "validation_status", "dataset_status", "dataset_reference"]:
        lines.append(f"- {key}: `{after.get(key)}`")
    lines += ["", "## Delta"]
    for key, value in review["delta"].items():
        lines.append(f"- {key}: `{value}`")
    lines += ["", "## Warnings"]
    if after.get("warnings"):
        for item in after["warnings"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines += ["", "## Errors"]
    if after.get("errors"):
        for item in after["errors"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines += ["", "## Next Controlled Actions"]
    for item in review["next_controlled_actions"]:
        lines.append(f"- {item}")
    lines += ["", "## Blocked Actions"]
    for item in review["blocked_actions"]:
        lines.append(f"- `{item}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    repo = Path(args.repo)
    out_dir = repo / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    review = build_review(repo)
    (out_dir / "prod031_035_vesselflow_real_data_delta_review.json").write_text(
        json.dumps(review, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "prod031_035_vesselflow_real_data_delta_review.md").write_text(
        md(review),
        encoding="utf-8",
    )

    print(json.dumps({
        "status": "PASS",
        "ready_for_write_rerun": review["delta"]["ready_for_write_rerun"],
        "outputs": [
            str(out_dir / "prod031_035_vesselflow_real_data_delta_review.json"),
            str(out_dir / "prod031_035_vesselflow_real_data_delta_review.md"),
        ],
    }, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

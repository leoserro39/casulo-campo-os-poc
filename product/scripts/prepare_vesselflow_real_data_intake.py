#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict


BLOCKED_ACTIONS = [
    "automatic_nomination",
    "client_facing_claim",
    "implementation_execution",
    "production_activation",
]

ALLOWED_CLASSIFICATIONS = {
    "anonymized",
    "synthetic",
    "internal_real_restricted",
}


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def build_import_input(intake: Dict[str, Any]) -> Dict[str, Any]:
    classification = intake.get("data_classification", "")
    intake_status = intake.get("intake_status", "WAITING_FOR_USER_DATA")
    dataset_ref = intake.get("dataset_reference", {})

    dataset_status = {
        "WAITING_FOR_USER_DATA": "WAITING_FOR_USER_DATA",
        "ANONYMIZED_DATA_READY": "ANONYMIZED_DATA_REFERENCE",
        "REAL_DATA_READY": "REAL_DATA_REFERENCE",
    }.get(intake_status, "WAITING_FOR_USER_DATA")

    return {
        "case_id": intake.get("case_id"),
        "dataset_or_workbook": {
            "status": dataset_status,
            "data_classification": classification,
            "path_or_reference": dataset_ref.get("path_or_reference"),
            "description": dataset_ref.get("description", ""),
            "file_exists_check_required": bool(dataset_ref.get("file_exists_check_required", False)),
        },
        "expected_nomination_flow": intake.get("expected_nomination_flow", []),
        "qualification_rules": intake.get("qualification_rules", []),
        "known_blocking_rules": intake.get("known_blocking_rules", []),
        "optional_inputs": intake.get("optional_inputs", {}),
        "human_notes": intake.get("human_notes", ""),
    }


def validate_intake(repo: Path, intake_path: Path, intake: Dict[str, Any]) -> Dict[str, Any]:
    errors = []
    warnings = []

    classification = intake.get("data_classification")
    if classification not in ALLOWED_CLASSIFICATIONS:
        errors.append(f"data_classification must be one of {sorted(ALLOWED_CLASSIFICATIONS)}")

    status = intake.get("intake_status")
    if status not in ["WAITING_FOR_USER_DATA", "ANONYMIZED_DATA_READY", "REAL_DATA_READY"]:
        errors.append("intake_status must be WAITING_FOR_USER_DATA, ANONYMIZED_DATA_READY, or REAL_DATA_READY")

    dataset_ref = intake.get("dataset_reference", {})
    ref = dataset_ref.get("path_or_reference")
    if not ref or ref == "REPLACE_WITH_REAL_OR_ANONYMIZED_WORKBOOK_OR_DATASET":
        warnings.append("dataset_reference.path_or_reference still looks like a placeholder")

    if dataset_ref.get("file_exists_check_required") and ref:
        candidate = Path(ref)
        if not candidate.is_absolute():
            candidate = repo / candidate
        if not candidate.exists():
            errors.append(f"dataset reference does not exist: {candidate}")

    if status == "REAL_DATA_READY" and classification != "internal_real_restricted":
        errors.append("REAL_DATA_READY requires data_classification=internal_real_restricted")

    if status == "ANONYMIZED_DATA_READY" and classification != "anonymized":
        errors.append("ANONYMIZED_DATA_READY requires data_classification=anonymized")

    required_arrays = ["expected_nomination_flow", "qualification_rules", "known_blocking_rules"]
    for key in required_arrays:
        if not intake.get(key):
            errors.append(f"{key} is required and cannot be empty")

    return {
        "status": "FAIL" if errors else "PASS",
        "intake_path": str(intake_path),
        "case_id": intake.get("case_id"),
        "intake_status": status,
        "data_classification": classification,
        "errors": errors,
        "warnings": warnings,
        "blocked_actions": BLOCKED_ACTIONS,
    }


def preview_md(validation: Dict[str, Any], import_input: Dict[str, Any]) -> str:
    lines = [
        "# PROD-026..030 VesselFlow Real/Anonymized Data Intake Preview",
        "",
        f"- Status: `{validation['status']}`",
        f"- Case: `{validation.get('case_id')}`",
        f"- Intake status: `{validation.get('intake_status')}`",
        f"- Data classification: `{validation.get('data_classification')}`",
        f"- Dataset status: `{import_input.get('dataset_or_workbook', {}).get('status')}`",
        "",
        "## Warnings",
    ]
    if validation.get("warnings"):
        for item in validation["warnings"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines += ["", "## Errors"]
    if validation.get("errors"):
        for item in validation["errors"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines += ["", "## Blocked Actions"]
    for item in BLOCKED_ACTIONS:
        lines.append(f"- `{item}`")
    lines += ["", "## Next"]
    if validation["status"] == "PASS":
        lines.append("Run with `--write --rerun-state` only after reviewing the intake data.")
    else:
        lines.append("Fix errors before writing the import input.")
    lines.append("")
    return "\n".join(lines)


def run_state(repo: Path) -> None:
    cmd = [sys.executable, str(repo / "product/scripts/run_vesselflow_state_definition.py"), "--repo", str(repo)]
    subprocess.run(cmd, check=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--intake", default="product/verticals/vesselflow/real_data_intake/vesselflow_real_data_intake_template.json")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--check", action="store_true", help="Validate and write preview only.")
    parser.add_argument("--write", action="store_true", help="Write product/verticals/vesselflow/import_inputs/vesselflow_import_input.json.")
    parser.add_argument("--rerun-state", action="store_true", help="Run state definition after --write.")
    args = parser.parse_args()

    repo = Path(args.repo)
    intake_path = Path(args.intake)
    if not intake_path.is_absolute():
        intake_path = repo / intake_path
    out_dir = repo / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    intake = read_json(intake_path)
    import_input = build_import_input(intake)
    validation = validate_intake(repo, intake_path, intake)

    write_json(out_dir / "prod026_030_vesselflow_real_data_intake_preview.json", {
        "validation": validation,
        "candidate_import_input": import_input,
    })
    (out_dir / "prod026_030_vesselflow_real_data_intake_preview.md").write_text(
        preview_md(validation, import_input),
        encoding="utf-8",
    )

    if args.write:
        if validation["status"] != "PASS":
            print(json.dumps(validation, indent=2, ensure_ascii=False))
            return 1
        target = repo / "product/verticals/vesselflow/import_inputs/vesselflow_import_input.json"
        backup = out_dir / "prod026_030_previous_vesselflow_import_input_backup.json"
        if target.exists():
            shutil.copy2(target, backup)
        write_json(target, import_input)
        if args.rerun_state:
            run_state(repo)

    print(json.dumps({
        "status": validation["status"],
        "preview_outputs": [
            str(out_dir / "prod026_030_vesselflow_real_data_intake_preview.json"),
            str(out_dir / "prod026_030_vesselflow_real_data_intake_preview.md"),
        ],
        "wrote_import_input": bool(args.write),
        "reran_state": bool(args.write and args.rerun_state),
        "warnings": validation.get("warnings", []),
        "errors": validation.get("errors", []),
    }, indent=2, ensure_ascii=False))

    return 0 if validation["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())

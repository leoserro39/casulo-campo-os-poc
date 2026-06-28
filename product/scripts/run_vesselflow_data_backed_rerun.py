#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
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


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def run(cmd):
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout + proc.stderr


def build_summary(repo: Path, intake_path: Path | None, write: bool, rerun_state: bool, regenerate_report: bool) -> Dict[str, Any]:
    delta_path = repo / "outputs/prod031_035_vesselflow_real_data_delta_review.json"
    preview_path = repo / "outputs/prod026_030_vesselflow_real_data_intake_preview.json"
    state_path = repo / "outputs/prod016_020_vesselflow_state_definition.json"

    delta = read_json(delta_path) if delta_path.exists() else {}
    preview = read_json(preview_path) if preview_path.exists() else {}
    state = read_json(state_path) if state_path.exists() else {}

    ready = bool(delta.get("delta", {}).get("ready_for_write_rerun", False))
    candidate = preview.get("candidate_import_input", {})
    validation = preview.get("validation", {})

    actions = []
    errors = []
    warnings = []

    if not ready:
        warnings.append("Current intake is not ready for data-backed write/rerun. This is expected while dataset reference remains placeholder.")
    if not intake_path:
        warnings.append("No intake JSON was supplied. Running in check-only comparator mode.")

    if write:
        if not intake_path:
            errors.append("--write requires --intake")
        if not ready and not intake_path:
            errors.append("--write is blocked because no reviewed intake JSON was supplied.")
        if not errors:
            cmd = [
                sys.executable,
                str(repo / "product/scripts/prepare_vesselflow_real_data_intake.py"),
                "--repo",
                str(repo),
                "--intake",
                str(intake_path),
                "--write",
            ]
            if rerun_state:
                cmd.append("--rerun-state")
            code, out = run(cmd)
            actions.append({"command": "prepare_vesselflow_real_data_intake", "returncode": code, "output_preview": out[:2000]})
            if code != 0:
                errors.append("prepare_vesselflow_real_data_intake failed")
            if regenerate_report and code == 0:
                report_cmd = [sys.executable, str(repo / "product/scripts/export_vesselflow_state_report.py"), "--repo", str(repo)]
                code2, out2 = run(report_cmd)
                actions.append({"command": "export_vesselflow_state_report", "returncode": code2, "output_preview": out2[:2000]})
                if code2 != 0:
                    errors.append("export_vesselflow_state_report failed")
    else:
        actions.append({"command": "check_only", "returncode": 0, "output_preview": "No files were changed by the rerun orchestrator."})

    result = {
        "contract_version": "operational_cube.data_backed_rerun.v1.0",
        "status": "FAIL" if errors else "PASS",
        "mode": "write" if write else "check_only",
        "case_id": candidate.get("case_id") or state.get("case_id") or "unknown",
        "ready_for_write_rerun": ready,
        "intake_status": validation.get("intake_status"),
        "data_classification": validation.get("data_classification"),
        "dataset_reference": candidate.get("dataset_or_workbook", {}).get("path_or_reference"),
        "state_decision": state.get("state_snapshot", {}).get("decision"),
        "risk_level": state.get("risk_fragility_summary", {}).get("risk_level"),
        "actions": actions,
        "warnings": warnings,
        "errors": errors,
        "blocked_actions": BLOCKED_ACTIONS,
        "internal_use_only": True,
    }
    return result


def md(result: Dict[str, Any]) -> str:
    lines = [
        "# PROD-036..040 VesselFlow Data-Backed Rerun",
        "",
        f"- Status: `{result['status']}`",
        f"- Mode: `{result['mode']}`",
        f"- Case: `{result['case_id']}`",
        f"- Ready for write/rerun: `{result['ready_for_write_rerun']}`",
        f"- Intake status: `{result.get('intake_status')}`",
        f"- Data classification: `{result.get('data_classification')}`",
        f"- Dataset reference: `{result.get('dataset_reference')}`",
        f"- State decision: `{result.get('state_decision')}`",
        f"- Risk level: `{result.get('risk_level')}`",
        "",
        "## Warnings",
    ]
    if result["warnings"]:
        for item in result["warnings"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines += ["", "## Errors"]
    if result["errors"]:
        for item in result["errors"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines += ["", "## Blocked Actions"]
    for item in result["blocked_actions"]:
        lines.append(f"- `{item}`")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--intake", default="")
    parser.add_argument("--output-dir", default="outputs")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--rerun-state", action="store_true")
    parser.add_argument("--regenerate-report", action="store_true")
    args = parser.parse_args()

    repo = Path(args.repo)
    out_dir = repo / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    intake_path = Path(args.intake) if args.intake else None
    if intake_path and not intake_path.is_absolute():
        intake_path = repo / intake_path

    result = build_summary(
        repo=repo,
        intake_path=intake_path,
        write=args.write,
        rerun_state=args.rerun_state,
        regenerate_report=args.regenerate_report,
    )

    write_json(out_dir / "prod036_040_vesselflow_data_backed_rerun.json", result)
    (out_dir / "prod036_040_vesselflow_data_backed_rerun.md").write_text(md(result), encoding="utf-8")

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())

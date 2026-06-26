"""CASULO Workbench Controlled Test Execution v0.8.

Executes the full controlled test lane.

Default script mode is check. Write mode explicitly creates runtime outputs under
workbench/runtime_outputs, which is ignored by Git.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from api.services.controlled_diagnostic_runner import run_controlled_diagnostic
from api.services.controlled_test_report_pack import run_controlled_test_report_pack
from api.services.human_review_gate import run_human_review_gate
from api.services.real_intake_engine import load_intake, utc_now


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUNTIME_ROOT = ROOT / "runtime_outputs"


def _stable_ts(stable_time: bool) -> str:
    return "1970-01-01T00:00:00+00:00" if stable_time else utc_now()


def _case_id_from_intake(intake_path: Path) -> str:
    intake = load_intake(intake_path)
    return str(intake.get("case_id", "unknown_case"))


def build_execution_index(
    intake_path: Path,
    diagnostic_result: Dict[str, Any],
    review_result: Dict[str, Any],
    report_result: Dict[str, Any],
    write: bool,
    runtime_root: Path,
    stable_time: bool = True,
) -> Dict[str, Any]:
    case_id = _case_id_from_intake(intake_path)
    generated_at = _stable_ts(stable_time)

    status = "PASS"
    errors: List[str] = []
    for name, result in [
        ("controlled_diagnostic", diagnostic_result),
        ("human_review_gate", review_result),
        ("controlled_test_report", report_result),
    ]:
        if result.get("status") != "PASS":
            status = "FAIL"
            errors.append(f"{name} failed: {result}")

    execution = {
        "contract_version": "workbench.controlled_test_execution.v0.8",
        "generated_at": generated_at,
        "case_id": case_id,
        "mode": "write" if write else "check",
        "status": status,
        "errors": errors,
        "steps": {
            "controlled_diagnostic": {
                "status": diagnostic_result.get("status"),
                "decision": diagnostic_result.get("diagnostic", {}).get("decision"),
                "generated_outputs": diagnostic_result.get("generated_outputs", []),
            },
            "human_review_gate": {
                "status": review_result.get("status"),
                "decision": review_result.get("decision"),
                "review_status": review_result.get("review_status"),
                "generated_outputs": review_result.get("generated_outputs", []),
            },
            "controlled_test_report": {
                "status": report_result.get("status"),
                "human_review_decision": report_result.get("human_review_decision"),
                "ready_for_internal_review": report_result.get("ready_for_internal_review"),
                "ready_for_client_review": report_result.get("ready_for_client_review"),
                "implementation_authorized": report_result.get("implementation_authorized"),
                "generated_outputs": report_result.get("generated_outputs", []),
            },
        },
        "runtime_locations": {
            "controlled_diagnostics": str(runtime_root / "controlled_diagnostics" / case_id),
            "human_review": str(runtime_root / "human_review" / case_id),
            "controlled_test_reports": str(runtime_root / "controlled_test_reports" / case_id),
            "controlled_test_runs": str(runtime_root / "controlled_test_runs" / case_id),
        },
        "next_gate": "Manual review of runtime report pack before any external use.",
    }
    return execution


def validate_execution_index(execution: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    required = {
        "contract_version",
        "generated_at",
        "case_id",
        "mode",
        "status",
        "errors",
        "steps",
        "runtime_locations",
        "next_gate",
    }
    missing = sorted(required - set(execution))
    if missing:
        errors.append(f"missing top-level keys: {missing}")
    if execution.get("contract_version") != "workbench.controlled_test_execution.v0.8":
        errors.append("invalid contract_version")
    steps = execution.get("steps", {})
    for step in ["controlled_diagnostic", "human_review_gate", "controlled_test_report"]:
        if step not in steps:
            errors.append(f"missing step: {step}")
    report = steps.get("controlled_test_report", {})
    if report.get("implementation_authorized") is not False:
        errors.append("implementation_authorized must remain false")
    return errors


def _run_readme(execution: Dict[str, Any]) -> str:
    lines = [
        f"# Controlled Test Execution - {execution['case_id']}",
        "",
        f"- Status: `{execution['status']}`",
        f"- Mode: `{execution['mode']}`",
        f"- Generated at: `{execution['generated_at']}`",
        "",
        "## Steps",
    ]
    for name, step in execution.get("steps", {}).items():
        lines.append(f"- `{name}`: `{step.get('status')}`")
    lines += [
        "",
        "## Runtime locations",
    ]
    for name, path in execution.get("runtime_locations", {}).items():
        lines.append(f"- `{name}`: `{path}`")
    lines += [
        "",
        "## Next gate",
        "",
        execution.get("next_gate", ""),
        "",
        "Implementation is not authorized by this execution.",
    ]
    return "\n".join(lines) + "\n"


def run_controlled_test_execution(
    intake_path: Path,
    write: bool = False,
    runtime_root: Path = DEFAULT_RUNTIME_ROOT,
    stable_time: bool = True,
) -> Dict[str, Any]:
    case_id = _case_id_from_intake(intake_path)

    diagnostic_result = run_controlled_diagnostic(
        intake_path=intake_path,
        write=write,
        output_root=runtime_root / "controlled_diagnostics",
        stable_time=stable_time,
    )
    review_result = run_human_review_gate(
        intake_path=intake_path,
        write=write,
        output_root=runtime_root / "human_review",
        stable_time=stable_time,
    )
    report_result = run_controlled_test_report_pack(
        intake_path=intake_path,
        write=write,
        output_root=runtime_root / "controlled_test_reports",
        stable_time=stable_time,
    )

    execution = build_execution_index(
        intake_path=intake_path,
        diagnostic_result=diagnostic_result,
        review_result=review_result,
        report_result=report_result,
        write=write,
        runtime_root=runtime_root,
        stable_time=stable_time,
    )

    validation_errors = validate_execution_index(execution)
    if validation_errors:
        execution["status"] = "FAIL"
        execution["errors"] = execution.get("errors", []) + validation_errors

    generated_outputs: List[str] = []
    if write and execution["status"] == "PASS":
        run_dir = runtime_root / "controlled_test_runs" / case_id
        run_dir.mkdir(parents=True, exist_ok=True)

        index_path = run_dir / "controlled_test_execution_result.json"
        index_path.write_text(json.dumps(execution, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        generated_outputs.append(str(index_path))

        readme_path = run_dir / "README.md"
        readme_path.write_text(_run_readme(execution), encoding="utf-8")
        generated_outputs.append(str(readme_path))

    return {
        "status": execution["status"],
        "mode": "write" if write else "check",
        "case_id": case_id,
        "steps": {
            key: value.get("status")
            for key, value in execution.get("steps", {}).items()
        },
        "human_review_decision": execution.get("steps", {}).get("human_review_gate", {}).get("decision"),
        "ready_for_internal_review": execution.get("steps", {}).get("controlled_test_report", {}).get("ready_for_internal_review"),
        "ready_for_client_review": execution.get("steps", {}).get("controlled_test_report", {}).get("ready_for_client_review"),
        "implementation_authorized": execution.get("steps", {}).get("controlled_test_report", {}).get("implementation_authorized"),
        "runtime_locations": execution.get("runtime_locations", {}),
        "errors": execution.get("errors", []),
        "generated_outputs": generated_outputs,
    }

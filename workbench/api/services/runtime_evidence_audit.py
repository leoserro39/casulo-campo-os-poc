from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUNTIME_ROOT = ROOT / "runtime_outputs"

REQUIRED_FILES = {
    "controlled_diagnostics": [
        "evidence_manifest.json",
        "controlled_case.json",
        "state_snapshot.json",
        "graph.json",
        "diagnostic_report.md",
        "cockpit_state.json",
        "codex_task.md",
        "ledger.jsonl",
        "controlled_diagnostic_result.json",
    ],
    "human_review": [
        "human_review_gate.json",
        "human_review_gate.md",
    ],
    "controlled_test_reports": [
        "controlled_test_result.json",
        "controlled_test_report.md",
        "executive_summary.md",
        "next_actions.md",
    ],
    "controlled_test_runs": [
        "controlled_test_execution_result.json",
        "README.md",
    ],
}


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def audit_runtime_evidence(case_id: str, runtime_root: Path = DEFAULT_RUNTIME_ROOT) -> Dict[str, Any]:
    errors: List[str] = []
    files: List[Dict[str, Any]] = []

    for group, names in REQUIRED_FILES.items():
        group_dir = runtime_root / group / case_id
        if not group_dir.exists():
            errors.append(f"missing runtime group: {group_dir}")
            continue
        for name in names:
            path = group_dir / name
            item = {
                "group": group,
                "name": name,
                "path": str(path),
                "exists": path.exists(),
                "size_bytes": path.stat().st_size if path.exists() else 0,
            }
            files.append(item)
            if not path.exists():
                errors.append(f"missing runtime file: {group}/{case_id}/{name}")
            elif item["size_bytes"] == 0:
                errors.append(f"empty runtime file: {group}/{case_id}/{name}")

    summaries: Dict[str, Any] = {}

    diag_path = runtime_root / "controlled_diagnostics" / case_id / "controlled_diagnostic_result.json"
    review_path = runtime_root / "human_review" / case_id / "human_review_gate.json"
    report_path = runtime_root / "controlled_test_reports" / case_id / "controlled_test_result.json"
    execution_path = runtime_root / "controlled_test_runs" / case_id / "controlled_test_execution_result.json"

    try:
        diag = read_json(diag_path)
        d = diag.get("diagnostic", {})
        summaries["diagnostic"] = {
            "status": diag.get("status"),
            "manifest_decision": diag.get("manifest_decision"),
            "data_quality": d.get("data_quality"),
            "h_pre": d.get("h_pre"),
            "h_post": d.get("h_post"),
            "delta_l": d.get("delta_l"),
            "decision": d.get("decision"),
            "human_review_required": diag.get("human_review_required"),
        }
        if diag.get("status") != "PASS":
            errors.append("controlled diagnostic status is not PASS")
        if diag.get("human_review_required") is not True:
            errors.append("controlled diagnostic must require human review")
    except Exception as exc:
        errors.append(f"cannot read controlled diagnostic result: {exc}")

    try:
        review = read_json(review_path)
        summaries["human_review"] = {
            "review_status": review.get("review_status"),
            "decision": review.get("decision"),
            "review_required": review.get("review_required"),
            "blocked_next_actions": review.get("blocked_next_actions", []),
        }
        if review.get("review_required") is not True:
            errors.append("human review must require review")
        if "implementation_execution" not in review.get("blocked_next_actions", []):
            errors.append("implementation_execution must be blocked")
    except Exception as exc:
        errors.append(f"cannot read human review gate: {exc}")

    try:
        report = read_json(report_path)
        summaries["controlled_report"] = {
            "status": report.get("status"),
            "human_review_decision": report.get("human_review_decision"),
            "ready_for_internal_review": report.get("ready_for_internal_review"),
            "ready_for_client_review": report.get("ready_for_client_review"),
            "implementation_authorized": report.get("implementation_authorized"),
        }
        if report.get("implementation_authorized") is not False:
            errors.append("controlled report must not authorize implementation")
    except Exception as exc:
        errors.append(f"cannot read controlled test result: {exc}")

    try:
        execution = read_json(execution_path)
        summaries["execution"] = {
            "status": execution.get("status"),
            "mode": execution.get("mode"),
            "next_gate": execution.get("next_gate"),
            "steps": execution.get("steps", {}),
        }
        if execution.get("status") != "PASS":
            errors.append("execution result status is not PASS")
    except Exception as exc:
        errors.append(f"cannot read execution result: {exc}")

    return {
        "contract_version": "workbench.runtime_evidence_audit.v0.9",
        "case_id": case_id,
        "runtime_root": str(runtime_root),
        "status": "FAIL" if errors else "PASS",
        "files_checked": len(files),
        "files": files,
        "summaries": summaries,
        "errors": errors,
        "commit_policy": "Do not commit workbench/runtime_outputs. Commit only this audit report/result.",
    }


def audit_report_markdown(audit: Dict[str, Any]) -> str:
    lines = [
        f"# Runtime Evidence Audit - {audit['case_id']}",
        "",
        f"- Status: `{audit['status']}`",
        f"- Runtime root: `{audit['runtime_root']}`",
        f"- Files checked: `{audit['files_checked']}`",
        f"- Commit policy: {audit['commit_policy']}",
        "",
        "## Summaries",
    ]
    for name, data in audit.get("summaries", {}).items():
        lines.append(f"### {name}")
        for key, value in data.items():
            lines.append(f"- `{key}`: `{value}`")
        lines.append("")
    lines.append("## Files")
    for item in audit.get("files", []):
        lines.append(f"- `{item['group']}/{item['name']}`: `{item['exists']}` ({item['size_bytes']} bytes)")
    if audit.get("errors"):
        lines.append("")
        lines.append("## Errors")
        for err in audit["errors"]:
            lines.append(f"- {err}")
    return "\n".join(lines) + "\n"

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any, Dict, List

BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
]

ALLOWED_STATES = [
    "CANDIDATE",
    "REVIEW_SELECTED",
    "APPROVED_FOR_MANUAL_CREATE",
    "REJECTED",
    "DEFERRED",
    "CREATED_MANUALLY",
    "LINKED_TO_TASK",
    "BLOCKED",
    "CLOSED",
]

ALLOWED_TRANSITIONS = {
    "CANDIDATE": ["REVIEW_SELECTED", "REJECTED", "DEFERRED"],
    "REVIEW_SELECTED": ["APPROVED_FOR_MANUAL_CREATE", "REJECTED", "DEFERRED", "BLOCKED"],
    "APPROVED_FOR_MANUAL_CREATE": ["CREATED_MANUALLY", "BLOCKED", "DEFERRED"],
    "CREATED_MANUALLY": ["LINKED_TO_TASK", "CLOSED"],
    "LINKED_TO_TASK": ["CLOSED", "BLOCKED"],
    "REJECTED": ["CLOSED"],
    "DEFERRED": ["REVIEW_SELECTED", "CLOSED"],
    "BLOCKED": ["REVIEW_SELECTED", "CLOSED"],
    "CLOSED": [],
}

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def slug(value: str) -> str:
    value = re.sub(r"[^a-zA-Z0-9]+", "-", value).strip("-").lower()
    return value[:120] or "issue"

def load_promotion(repo: Path) -> Dict[str, Any]:
    path = repo / "outputs/prod341_360_manual_issue_promotion.json"
    if not path.exists():
        raise SystemExit(f"missing {path}")
    return read_json(path)

def default_manifest(promotion: Dict[str, Any]) -> Dict[str, Any]:
    decisions = []
    for item in promotion.get("issue_files", []):
        decisions.append({
            "issue_id": item["issue_id"],
            "current_state": "REVIEW_SELECTED",
            "requested_state": "REVIEW_SELECTED",
            "approval": "PENDING_HUMAN_APPROVAL",
            "approver": "",
            "approval_note": "",
            "manual_issue_url": "",
            "linked_task_id": "",
            "source_delta": item.get("source_delta"),
            "priority": item.get("priority"),
            "review_route": item.get("review_route"),
        })
    return {
        "status": "DRAFT_REVIEW_REQUIRED",
        "approval_policy": "all_candidates_review_selected_but_not_approved",
        "instructions": [
            "Set requested_state to APPROVED_FOR_MANUAL_CREATE only after human approval.",
            "Set approver and approval_note for every approval.",
            "After manual gh issue create, set requested_state to CREATED_MANUALLY and fill manual_issue_url.",
            "No command is executed by this workflow.",
        ],
        "candidate_decisions": decisions,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def load_or_create_manifest(repo: Path, promotion: Dict[str, Any]) -> Dict[str, Any]:
    path = repo / "product/poc/formal_approval_workflow/formal_approval_manifest.json"
    if path.exists():
        return read_json(path)
    manifest = default_manifest(promotion)
    write_json(path, manifest)
    return manifest

def command_map(promotion: Dict[str, Any]) -> Dict[str, str]:
    return {row["issue_id"]: row["command"] for row in promotion.get("command_templates", [])}

def validate_transition(current: str, requested: str) -> Dict[str, Any]:
    if current not in ALLOWED_STATES:
        return {"allowed": False, "reason": f"unknown current state {current}"}
    if requested not in ALLOWED_STATES:
        return {"allowed": False, "reason": f"unknown requested state {requested}"}
    if requested == current:
        return {"allowed": True, "reason": "no_state_change"}
    allowed = requested in ALLOWED_TRANSITIONS.get(current, [])
    return {"allowed": allowed, "reason": "allowed_transition" if allowed else f"transition_not_allowed_from_{current}_to_{requested}"}

def build(repo: Path) -> Dict[str, Any]:
    promotion = load_promotion(repo)
    manifest = load_or_create_manifest(repo, promotion)
    commands = command_map(promotion)

    transitions = []
    approved_queue = []
    blocked_queue = []
    created_manual = []

    for row in manifest.get("candidate_decisions", []):
        issue_id = row["issue_id"]
        current = row.get("current_state", "REVIEW_SELECTED")
        requested = row.get("requested_state", current)
        vt = validate_transition(current, requested)
        approval_complete = bool(row.get("approver")) and bool(row.get("approval_note"))
        manual_url_present = bool(row.get("manual_issue_url"))

        guard_reason = vt["reason"]
        guard_allowed = vt["allowed"]

        if requested == "APPROVED_FOR_MANUAL_CREATE" and not approval_complete:
            guard_allowed = False
            guard_reason = "approval_requires_approver_and_note"
        if requested == "CREATED_MANUALLY" and not manual_url_present:
            guard_allowed = False
            guard_reason = "created_manually_requires_manual_issue_url"

        transition = {
            "issue_id": issue_id,
            "from_state": current,
            "to_state": requested,
            "allowed": guard_allowed,
            "reason": guard_reason,
            "approval_complete": approval_complete,
            "manual_issue_url_present": manual_url_present,
            "auto_execution_allowed": False,
            "blocked_actions": BLOCKED_ACTIONS,
        }
        transitions.append(transition)

        if requested == "APPROVED_FOR_MANUAL_CREATE" and guard_allowed:
            approved_queue.append({
                "issue_id": issue_id,
                "command": commands.get(issue_id, ""),
                "manual_only": True,
                "approver": row.get("approver", ""),
                "approval_note": row.get("approval_note", ""),
            })
        elif requested == "BLOCKED":
            blocked_queue.append(row)
        elif requested == "CREATED_MANUALLY" and guard_allowed:
            created_manual.append(row)

    execution_guard = {
        "status": "PASS",
        "manual_only": True,
        "auto_execution_allowed": False,
        "selected_count": promotion.get("selected_count", 0),
        "approved_count": len(approved_queue),
        "created_manually_count": len(created_manual),
        "blocked_count": len(blocked_queue),
        "invalid_transition_count": sum(1 for t in transitions if not t["allowed"]),
        "approved_commands_available": len([a for a in approved_queue if a["command"]]),
        "guardrails": [
            "No command is executed by the workflow.",
            "Approved state requires approver and approval note.",
            "Created manually state requires manual issue URL.",
            "Production activation remains blocked.",
            "Automatic merge remains blocked.",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    ledger = {
        "status": "PASS",
        "ledger": "casulo.issue_traceability_ledger.v0.1",
        "state_transitions": transitions,
        "approved_queue": approved_queue,
        "blocked_queue": blocked_queue,
        "created_manual": created_manual,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    out = repo / "outputs"
    write_json(out / "prod361_380_formal_approval_manifest_snapshot.json", manifest)
    write_json(out / "prod361_380_state_transition_ledger.json", ledger)
    write_json(out / "prod361_380_issue_execution_guard.json", execution_guard)

    runbook_lines = [
        "# PROD-361..380 Formal Approval Workflow Runbook",
        "",
        "This runbook does not execute GitHub commands.",
        "",
        "## Current Guard",
        f"- Manual only: `{execution_guard['manual_only']}`",
        f"- Auto execution allowed: `{execution_guard['auto_execution_allowed']}`",
        f"- Selected count: `{execution_guard['selected_count']}`",
        f"- Approved count: `{execution_guard['approved_count']}`",
        f"- Created manually count: `{execution_guard['created_manually_count']}`",
        f"- Invalid transition count: `{execution_guard['invalid_transition_count']}`",
        "",
        "## Approval Steps",
        "1. Edit `product/poc/formal_approval_workflow/formal_approval_manifest.json`.",
        "2. For an approved candidate, set `requested_state` to `APPROVED_FOR_MANUAL_CREATE`.",
        "3. Fill `approver` and `approval_note`.",
        "4. Re-run `python product/scripts/run_formal_approval_workflow.py --repo .`.",
        "5. Copy approved command manually from the approved queue.",
        "6. After creating the issue manually, set `requested_state` to `CREATED_MANUALLY` and fill `manual_issue_url`.",
        "",
        "## Approved Manual Commands",
    ]
    if approved_queue:
        for row in approved_queue:
            runbook_lines += [
                f"### {row['issue_id']}",
                "```bash",
                row["command"],
                "```",
                "",
            ]
    else:
        runbook_lines.append("No approved commands yet. This is expected until the approval manifest is edited.")
    write_text(out / "prod361_380_formal_approval_runbook.md", "\n".join(runbook_lines) + "\n")

    report = {
        "status": "PASS",
        "phase": "Formal Approval Workflow and Issue Execution Guard",
        "decision": "READY_FOR_FORMAL_APPROVAL_REVIEW_NO_AUTO_EXECUTION",
        "execution_guard": execution_guard,
        "next_recommended_step": "Approve a minimal subset in the manifest, re-run guard, then manually create only approved issues.",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod361_380_formal_approval_report.json", report)

    report_md = [
        "# PROD-361..380 Formal Approval Workflow Report",
        "",
        f"- Status: `{report['status']}`",
        f"- Decision: `{report['decision']}`",
        f"- Selected count: `{execution_guard['selected_count']}`",
        f"- Approved count: `{execution_guard['approved_count']}`",
        f"- Created manually count: `{execution_guard['created_manually_count']}`",
        f"- Invalid transition count: `{execution_guard['invalid_transition_count']}`",
        f"- Auto execution allowed: `{execution_guard['auto_execution_allowed']}`",
        "",
        "## Guardrails",
    ]
    for g in execution_guard["guardrails"]:
        report_md.append(f"- {g}")
    write_text(out / "prod361_380_formal_approval_report.md", "\n".join(report_md) + "\n")

    return report

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    result = build(Path(args.repo))
    guard = result["execution_guard"]
    print(json.dumps({
        "status": result["status"],
        "decision": result["decision"],
        "selected_count": guard["selected_count"],
        "approved_count": guard["approved_count"],
        "auto_execution_allowed": guard["auto_execution_allowed"],
        "invalid_transition_count": guard["invalid_transition_count"],
    }, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

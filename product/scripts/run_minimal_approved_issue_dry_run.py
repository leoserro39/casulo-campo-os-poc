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
    "automatic_merge",
    "credential_handling",
]

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def load_promotion(repo: Path) -> Dict[str, Any]:
    path = repo / "outputs/prod341_360_manual_issue_promotion.json"
    if not path.exists():
        raise SystemExit(f"missing {path}")
    return read_json(path)

def load_formal_manifest(repo: Path) -> Dict[str, Any]:
    path = repo / "outputs/prod361_380_formal_approval_manifest_snapshot.json"
    if not path.exists():
        raise SystemExit(f"missing {path}")
    return read_json(path)

def command_map(promotion: Dict[str, Any]) -> Dict[str, str]:
    return {row["issue_id"]: row["command"] for row in promotion.get("command_templates", [])}

def score_candidate(row: Dict[str, Any]) -> int:
    priority_score = {"P0_BLOCKER": 100, "P1_REVIEW": 80, "P2_EVIDENCE_OR_TASK": 60, "P3_STRUCTURE": 40}.get(row.get("priority"), 20)
    delta_bonus = {
        "delta_evidence": 20,
        "delta_domain": 16,
        "delta_conflict": 15,
        "delta_production": 12,
        "delta_execution": 10,
        "delta_human_review": 8,
        "delta_model_behavior": 4,
    }.get(row.get("source_delta"), 0)
    return priority_score + delta_bonus

def choose_candidates(manifest: Dict[str, Any], approve_count: int) -> List[Dict[str, Any]]:
    rows = list(manifest.get("candidate_decisions", []))
    rows.sort(key=lambda r: (-score_candidate(r), r.get("issue_id", "")))
    return rows[:approve_count]

def build(repo: Path, approve_count: int, approver: str, note: str) -> Dict[str, Any]:
    out = repo / "outputs"
    promotion = load_promotion(repo)
    source_manifest = load_formal_manifest(repo)
    commands = command_map(promotion)
    selected = choose_candidates(source_manifest, approve_count)

    dry_manifest = {
        "status": "DRY_RUN_ONLY_NOT_SOURCE_OF_TRUTH",
        "approval_policy": "synthetic_minimal_approval_for_guard_validation_only",
        "source_manifest": "outputs/prod361_380_formal_approval_manifest_snapshot.json",
        "does_not_modify": "product/poc/formal_approval_workflow/formal_approval_manifest.json",
        "candidate_decisions": [],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    selected_ids = {row["issue_id"] for row in selected}
    for row in source_manifest.get("candidate_decisions", []):
        new_row = dict(row)
        if row["issue_id"] in selected_ids:
            new_row["requested_state"] = "APPROVED_FOR_MANUAL_CREATE"
            new_row["approval"] = "DRY_RUN_APPROVED"
            new_row["approver"] = approver
            new_row["approval_note"] = note
        dry_manifest["candidate_decisions"].append(new_row)

    transitions = []
    approved_queue = []
    for row in dry_manifest["candidate_decisions"]:
        issue_id = row["issue_id"]
        requested = row.get("requested_state")
        current = row.get("current_state")
        approval_complete = bool(row.get("approver")) and bool(row.get("approval_note"))
        command = commands.get(issue_id, "")
        allowed = False
        reason = "not_selected_no_state_change"
        if current == requested:
            allowed = True
            reason = "no_state_change"
        elif current == "REVIEW_SELECTED" and requested == "APPROVED_FOR_MANUAL_CREATE" and approval_complete:
            allowed = True
            reason = "dry_run_approval_transition_allowed"
            approved_queue.append({
                "issue_id": issue_id,
                "command": command,
                "manual_only": True,
                "approver": row.get("approver"),
                "approval_note": row.get("approval_note"),
                "source_delta": row.get("source_delta"),
                "priority": row.get("priority"),
                "review_route": row.get("review_route"),
            })
        elif requested == "APPROVED_FOR_MANUAL_CREATE" and not approval_complete:
            reason = "approval_requires_approver_and_note"
        transitions.append({
            "issue_id": issue_id,
            "from_state": current,
            "to_state": requested,
            "allowed": allowed,
            "reason": reason,
            "approval_complete": approval_complete,
            "command_available": bool(command),
            "auto_execution_allowed": False,
            "blocked_actions": BLOCKED_ACTIONS,
        })

    plan = {
        "status": "PASS",
        "requested_approval_count": approve_count,
        "selected_issue_ids": [row["issue_id"] for row in selected],
        "approver": approver,
        "note": note,
        "selection_policy": "top-scored selected candidates from formal approval manifest",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    guard = {
        "status": "PASS",
        "manual_only": True,
        "auto_execution_allowed": False,
        "requested_approval_count": approve_count,
        "approved_count": len(approved_queue),
        "approved_commands_available": sum(1 for row in approved_queue if row["command"]),
        "created_manually_count": 0,
        "invalid_transition_count": sum(1 for t in transitions if not t["allowed"]),
        "source_manifest_modified": False,
        "finding": "PASS: minimal dry-run approvals generate manual command previews while auto execution remains disabled.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    write_json(out / "prod381_400_minimal_approval_plan.json", plan)
    write_json(out / "prod381_400_dry_run_approval_manifest.json", dry_manifest)
    write_json(out / "prod381_400_dry_run_transition_ledger.json", {"status": "PASS", "state_transitions": transitions, "approved_queue": approved_queue, "blocked_actions": BLOCKED_ACTIONS})
    write_json(out / "prod381_400_execution_guard.json", guard)

    preview_lines = [
        "# PROD-381..400 Approved Command Preview",
        "",
        "Dry-run only. These commands are not executed by the system.",
        "",
        f"- Approved count: `{len(approved_queue)}`",
        f"- Auto execution allowed: `{guard['auto_execution_allowed']}`",
        "",
    ]
    for row in approved_queue:
        preview_lines += [
            f"## {row['issue_id']}",
            f"- Priority: `{row.get('priority')}`",
            f"- Delta: `{row.get('source_delta')}`",
            f"- Route: `{row.get('review_route')}`",
            "",
            "```bash",
            row["command"] or "# command unavailable",
            "```",
            "",
        ]
    write_text(out / "prod381_400_approved_command_preview.md", "\n".join(preview_lines))

    report_lines = [
        "# PROD-381..400 Minimal Approved Issue Dry Run Report",
        "",
        f"- Status: `{guard['status']}`",
        f"- Requested approval count: `{approve_count}`",
        f"- Approved count: `{guard['approved_count']}`",
        f"- Approved commands available: `{guard['approved_commands_available']}`",
        f"- Invalid transitions: `{guard['invalid_transition_count']}`",
        f"- Auto execution allowed: `{guard['auto_execution_allowed']}`",
        f"- Source manifest modified: `{guard['source_manifest_modified']}`",
        "",
        "## Selected Issue IDs",
    ]
    for issue_id in plan["selected_issue_ids"]:
        report_lines.append(f"- `{issue_id}`")
    report_lines += ["", "## Finding", guard["finding"]]
    write_text(out / "prod381_400_minimal_dry_run_report.md", "\n".join(report_lines) + "\n")

    return {"plan": plan, "guard": guard, "approved_queue": approved_queue}

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--approve-count", type=int, default=2)
    parser.add_argument("--approver", default="CASULO_DRY_RUN_REVIEWER")
    parser.add_argument("--note", default="Synthetic dry-run approval for transition guard validation only; no issue is created automatically.")
    args = parser.parse_args()
    result = build(Path(args.repo), args.approve_count, args.approver, args.note)
    print(json.dumps({
        "status": "PASS",
        "approved_count": result["guard"]["approved_count"],
        "approved_commands_available": result["guard"]["approved_commands_available"],
        "auto_execution_allowed": result["guard"]["auto_execution_allowed"],
        "selected_issue_ids": result["plan"]["selected_issue_ids"],
    }, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

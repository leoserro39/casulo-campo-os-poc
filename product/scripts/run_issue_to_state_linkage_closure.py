#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from collections import Counter
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

def load_capture(repo: Path) -> Dict[str, Any]:
    path = repo / "outputs/prod401_420_manual_issue_evidence_capture.json"
    if not path.exists():
        raise SystemExit(f"missing {path}")
    return read_json(path)

def load_state_preview(repo: Path) -> Dict[str, Any]:
    path = repo / "outputs/prod401_420_state_update_preview.json"
    if not path.exists():
        raise SystemExit(f"missing {path}")
    return read_json(path)

def load_dry_run_ledger(repo: Path) -> Dict[str, Any]:
    path = repo / "outputs/prod381_400_dry_run_transition_ledger.json"
    if not path.exists():
        return {"approved_queue": []}
    return read_json(path)

def approved_by_issue(dry_run_ledger: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {row["issue_id"]: row for row in dry_run_ledger.get("approved_queue", [])}

def build_records(capture: Dict[str, Any], state_preview: Dict[str, Any], dry_run_ledger: Dict[str, Any]) -> List[Dict[str, Any]]:
    approved = approved_by_issue(dry_run_ledger)
    validations = {row["issue_id"]: row for row in capture.get("validations", [])}
    previews = state_preview.get("state_update_preview", [])

    records = []
    for row in previews:
        issue_id = row["issue_id"]
        validation = validations.get(issue_id, {})
        approved_row = approved.get(issue_id, {})
        target_state = row.get("target_state", "APPROVED_FOR_MANUAL_CREATE")
        manual_url = row.get("manual_issue_url", "")
        valid = bool(row.get("valid", False))

        if target_state == "CREATED_MANUALLY" and manual_url and valid:
            closure_status = "CREATED_MANUALLY_READY_TO_LINK"
            next_action = "link_manual_issue_to_task_or_state"
        elif target_state == "APPROVED_FOR_MANUAL_CREATE" and not manual_url:
            closure_status = "PENDING_MANUAL_ISSUE_CREATION"
            next_action = "wait_for_manual_issue_url_evidence"
        elif not valid:
            closure_status = "EVIDENCE_INCOMPLETE"
            next_action = "fix_manual_issue_evidence_manifest"
        else:
            closure_status = "REVIEW_REQUIRED"
            next_action = "human_review_required"

        records.append({
            "issue_id": issue_id,
            "manual_issue_url": manual_url,
            "manual_issue_url_present": bool(manual_url),
            "source_delta": approved_row.get("source_delta"),
            "priority": approved_row.get("priority"),
            "review_route": approved_row.get("review_route"),
            "target_state": target_state,
            "closure_status": closure_status,
            "next_action": next_action,
            "valid": valid,
            "reason": row.get("reason", ""),
            "auto_execution_allowed": False,
            "blocked_actions": BLOCKED_ACTIONS,
        })
    return records

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    capture = load_capture(repo)
    state_preview = load_state_preview(repo)
    dry_run_ledger = load_dry_run_ledger(repo)
    records = build_records(capture, state_preview, dry_run_ledger)

    status_counts = Counter(r["closure_status"] for r in records)
    target_state_counts = Counter(r["target_state"] for r in records)
    url_present_count = sum(1 for r in records if r["manual_issue_url_present"])

    summary = {
        "record_count": len(records),
        "manual_issue_url_present_count": url_present_count,
        "pending_manual_creation_count": status_counts.get("PENDING_MANUAL_ISSUE_CREATION", 0),
        "created_manually_ready_to_link_count": status_counts.get("CREATED_MANUALLY_READY_TO_LINK", 0),
        "evidence_incomplete_count": status_counts.get("EVIDENCE_INCOMPLETE", 0),
        "closure_status_counts": dict(status_counts),
        "target_state_counts": dict(target_state_counts),
        "auto_execution_allowed": False,
    }

    closure_ledger = {
        "status": "PASS",
        "ledger": "casulo.closure_ledger.v0.1",
        "records": records,
        "summary": summary,
        "policy": [
            "No issue URL is invented.",
            "No state is closed without evidence.",
            "Pending manual creation is a valid closure interim state.",
            "Manual issue URL evidence is required before CREATED_MANUALLY linkage.",
            "Automatic execution remains disabled.",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    linkage_report = {
        "status": "PASS",
        "phase": "Issue-to-State Linkage and Closure Ledger",
        "decision": "READY_FOR_MANUAL_ISSUE_URL_EVIDENCE_OR_PENDING_CLOSURE_REVIEW",
        "summary": summary,
        "interpretation": "Approved issue candidates are linked to a closure ledger. With no manual issue URLs yet, records remain safely pending manual creation.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    write_json(out / "prod421_440_issue_state_link_records.json", {"status": "PASS", "records": records, "blocked_actions": BLOCKED_ACTIONS})
    write_json(out / "prod421_440_closure_ledger.json", closure_ledger)
    write_json(out / "prod421_440_linkage_report.json", linkage_report)

    ledger_md = [
        "# PROD-421..440 Issue-to-State Linkage and Closure Ledger",
        "",
        f"- Status: `{closure_ledger['status']}`",
        f"- Records: `{summary['record_count']}`",
        f"- Manual issue URLs present: `{summary['manual_issue_url_present_count']}`",
        f"- Pending manual creation: `{summary['pending_manual_creation_count']}`",
        f"- Created manually ready to link: `{summary['created_manually_ready_to_link_count']}`",
        f"- Evidence incomplete: `{summary['evidence_incomplete_count']}`",
        f"- Auto execution allowed: `{summary['auto_execution_allowed']}`",
        "",
        "## Records",
    ]
    for r in records:
        ledger_md.append(f"- `{r['issue_id']}` → `{r['closure_status']}` / target `{r['target_state']}` / next `{r['next_action']}`")
    ledger_md += [
        "",
        "## Policy",
    ]
    for rule in closure_ledger["policy"]:
        ledger_md.append(f"- {rule}")
    write_text(out / "prod421_440_closure_ledger.md", "\n".join(ledger_md) + "\n")

    report_md = [
        "# PROD-421..440 Linkage Report",
        "",
        f"- Status: `{linkage_report['status']}`",
        f"- Decision: `{linkage_report['decision']}`",
        f"- Records: `{summary['record_count']}`",
        f"- Pending manual creation: `{summary['pending_manual_creation_count']}`",
        f"- Created manually ready to link: `{summary['created_manually_ready_to_link_count']}`",
        f"- Auto execution allowed: `{summary['auto_execution_allowed']}`",
        "",
        "## Interpretation",
        linkage_report["interpretation"],
    ]
    write_text(out / "prod421_440_linkage_report.md", "\n".join(report_md) + "\n")

    return linkage_report

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    result = build(Path(args.repo))
    print(json.dumps({
        "status": result["status"],
        "decision": result["decision"],
        "records": result["summary"]["record_count"],
        "pending_manual_creation_count": result["summary"]["pending_manual_creation_count"],
        "created_manually_ready_to_link_count": result["summary"]["created_manually_ready_to_link_count"],
        "auto_execution_allowed": result["summary"]["auto_execution_allowed"],
    }, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

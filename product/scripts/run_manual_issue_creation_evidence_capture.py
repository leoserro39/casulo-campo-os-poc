#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
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

ISSUE_URL_RE = re.compile(r"^https://github\.com/[^/\s]+/[^/\s]+/issues/[0-9]+$")

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def load_approved_queue(repo: Path) -> List[Dict[str, Any]]:
    p = repo / "outputs/prod381_400_dry_run_transition_ledger.json"
    if not p.exists():
        raise SystemExit(f"missing {p}")
    return read_json(p).get("approved_queue", [])

def default_manifest(approved_queue: List[Dict[str, Any]]) -> Dict[str, Any]:
    return {
        "status": "DRAFT_EVIDENCE_REQUIRED",
        "evidence_policy": "no_manual_issue_url_by_default",
        "instructions": [
            "Fill manual_issue_url only after a human manually creates the GitHub issue.",
            "Fill created_by, created_at and evidence_note for every created issue.",
            "Do not invent URLs.",
            "Do not use this manifest to create issues automatically.",
        ],
        "manual_issue_evidence": [
            {
                "issue_id": row["issue_id"],
                "manual_issue_url": "",
                "created_by": "",
                "created_at": "",
                "evidence_note": "",
                "source_delta": row.get("source_delta"),
                "priority": row.get("priority"),
                "review_route": row.get("review_route"),
                "command_previewed": bool(row.get("command")),
            }
            for row in approved_queue
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

def load_or_create_manifest(repo: Path, approved_queue: List[Dict[str, Any]]) -> Dict[str, Any]:
    p = repo / "product/poc/manual_issue_creation_evidence/manual_issue_evidence_manifest.json"
    if p.exists():
        return read_json(p)
    manifest = default_manifest(approved_queue)
    write_json(p, manifest)
    return manifest

def validate_record(record: Dict[str, Any]) -> Dict[str, Any]:
    url = record.get("manual_issue_url", "").strip()
    created_by = record.get("created_by", "").strip()
    created_at = record.get("created_at", "").strip()
    note = record.get("evidence_note", "").strip()

    if not url:
        return {
            "issue_id": record["issue_id"],
            "state": "APPROVED_PENDING_MANUAL_CREATION",
            "valid": True,
            "manual_issue_url_present": False,
            "reason": "no_url_yet_pending_manual_creation",
        }

    url_valid = bool(ISSUE_URL_RE.match(url))
    meta_complete = bool(created_by and created_at and note)
    if url_valid and meta_complete:
        return {
            "issue_id": record["issue_id"],
            "state": "CREATED_MANUALLY_EVIDENCE_CAPTURED",
            "valid": True,
            "manual_issue_url_present": True,
            "reason": "manual_issue_url_and_metadata_valid",
        }
    return {
        "issue_id": record["issue_id"],
        "state": "EVIDENCE_INCOMPLETE",
        "valid": False,
        "manual_issue_url_present": bool(url),
        "reason": "url_shape_or_metadata_incomplete",
    }

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    approved_queue = load_approved_queue(repo)
    manifest = load_or_create_manifest(repo, approved_queue)
    records = manifest.get("manual_issue_evidence", [])
    validations = [validate_record(r) for r in records]

    captured = [v for v in validations if v["state"] == "CREATED_MANUALLY_EVIDENCE_CAPTURED"]
    pending = [v for v in validations if v["state"] == "APPROVED_PENDING_MANUAL_CREATION"]
    incomplete = [v for v in validations if v["state"] == "EVIDENCE_INCOMPLETE"]

    state_update_preview = []
    by_issue = {r["issue_id"]: r for r in records}
    for v in validations:
        r = by_issue[v["issue_id"]]
        target_state = "CREATED_MANUALLY" if v["state"] == "CREATED_MANUALLY_EVIDENCE_CAPTURED" else "APPROVED_FOR_MANUAL_CREATE"
        state_update_preview.append({
            "issue_id": v["issue_id"],
            "target_state": target_state,
            "manual_issue_url": r.get("manual_issue_url", ""),
            "valid": v["valid"],
            "reason": v["reason"],
            "auto_execution_allowed": False,
        })

    capture = {
        "status": "PASS" if not incomplete else "ATTENTION",
        "approved_count": len(approved_queue),
        "captured_count": len(captured),
        "pending_count": len(pending),
        "incomplete_count": len(incomplete),
        "auto_execution_allowed": False,
        "manual_only": True,
        "source_manifest": "product/poc/manual_issue_creation_evidence/manual_issue_evidence_manifest.json",
        "validations": validations,
        "state_update_preview": state_update_preview,
        "finding": "Manual issue evidence capture is ready; no issue URLs have to exist until a human creates them manually.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    write_json(out / "prod401_420_manual_issue_evidence_manifest_snapshot.json", manifest)
    write_json(out / "prod401_420_manual_issue_evidence_capture.json", capture)
    write_json(out / "prod401_420_issue_url_validation.json", {"status": capture["status"], "validations": validations, "blocked_actions": BLOCKED_ACTIONS})
    write_json(out / "prod401_420_state_update_preview.json", {"status": capture["status"], "state_update_preview": state_update_preview, "blocked_actions": BLOCKED_ACTIONS})

    capture_md = [
        "# PROD-401..420 Manual Issue Creation Evidence Capture",
        "",
        f"- Status: `{capture['status']}`",
        f"- Approved count: `{capture['approved_count']}`",
        f"- Captured count: `{capture['captured_count']}`",
        f"- Pending count: `{capture['pending_count']}`",
        f"- Incomplete count: `{capture['incomplete_count']}`",
        f"- Auto execution allowed: `{capture['auto_execution_allowed']}`",
        "",
        "## Evidence Manifest",
        "`product/poc/manual_issue_creation_evidence/manual_issue_evidence_manifest.json`",
        "",
        "## Validation Results",
    ]
    for v in validations:
        capture_md.append(f"- `{v['issue_id']}` → `{v['state']}` / `{v['reason']}`")
    capture_md += [
        "",
        "## How to capture evidence after manual creation",
        "1. Create the GitHub issue manually outside this workflow.",
        "2. Copy the GitHub issue URL.",
        "3. Edit the evidence manifest and fill `manual_issue_url`, `created_by`, `created_at`, and `evidence_note`.",
        "4. Re-run `python product/scripts/run_manual_issue_creation_evidence_capture.py --repo .`.",
        "5. Confirm `captured_count` increased and `auto_execution_allowed` is still `false`.",
    ]
    write_text(out / "prod401_420_manual_issue_evidence_capture.md", "\n".join(capture_md) + "\n")

    return capture

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    capture = build(Path(args.repo))
    print(json.dumps({
        "status": capture["status"],
        "approved_count": capture["approved_count"],
        "captured_count": capture["captured_count"],
        "pending_count": capture["pending_count"],
        "incomplete_count": capture["incomplete_count"],
        "auto_execution_allowed": capture["auto_execution_allowed"],
    }, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

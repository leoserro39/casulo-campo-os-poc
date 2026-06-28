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

ISSUE_URL_RE = re.compile(r"^https://github\.com/[^/\s]+/[^/\s]+/issues/[0-9]+$")

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def load_json_or_empty(path: Path, default: Any) -> Any:
    return read_json(path) if path.exists() else default

def source_candidates(repo: Path) -> List[Dict[str, Any]]:
    ledger = load_json_or_empty(repo / "outputs/prod421_440_closure_ledger.json", {"records": []})
    replay = load_json_or_empty(repo / "outputs/prod441_460_closure_replay_ledger.json", {"records": []})
    base = {r["issue_id"]: r for r in ledger.get("records", [])}
    for r in replay.get("records", []):
        base.setdefault(r["issue_id"], r)
    return list(base.values())

def synthetic_urls(repo: Path) -> set[str]:
    manifest = load_json_or_empty(repo / "outputs/prod441_460_synthetic_manual_url_manifest.json", {"records": []})
    return {r.get("synthetic_manual_issue_url", "") for r in manifest.get("records", []) if r.get("synthetic_manual_issue_url")}

def default_manifest(repo: Path, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    records = []
    for r in candidates:
        if r.get("closure_status") in ["PENDING_MANUAL_ISSUE_CREATION", "CREATED_MANUALLY_READY_TO_LINK"] or r.get("target_state") in ["APPROVED_FOR_MANUAL_CREATE", "CREATED_MANUALLY"]:
            records.append({
                "issue_id": r["issue_id"],
                "manual_issue_url": "",
                "created_by": "",
                "created_at": "",
                "evidence_note": "",
                "synthetic": False,
                "source_delta": r.get("source_delta"),
                "priority": r.get("priority"),
                "review_route": r.get("review_route"),
                "source_status": r.get("closure_status"),
                "intended_state_after_evidence": "CREATED_MANUALLY_READY_TO_LINK",
            })
    return {
        "status": "DRAFT_REAL_EVIDENCE_REQUIRED",
        "evidence_policy": "no_real_issue_url_by_default",
        "instructions": [
            "Only paste URLs of issues manually created by a human.",
            "Do not paste URLs from synthetic replay outputs.",
            "Fill created_by, created_at and evidence_note.",
            "This workflow does not call GitHub and does not create issues.",
            "Set synthetic=false for real evidence records.",
        ],
        "real_manual_issue_evidence": records,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def load_or_create_manifest(repo: Path, candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
    path = repo / "product/poc/real_manual_evidence_handoff/real_manual_evidence_manifest.json"
    if path.exists():
        return read_json(path)
    manifest = default_manifest(repo, candidates)
    write_json(path, manifest)
    return manifest

def validate_record(record: Dict[str, Any], synthetic_url_set: set[str]) -> Dict[str, Any]:
    url = record.get("manual_issue_url", "").strip()
    synthetic_flag = bool(record.get("synthetic", False))
    metadata_complete = bool(record.get("created_by", "").strip() and record.get("created_at", "").strip() and record.get("evidence_note", "").strip())
    url_shape_valid = bool(ISSUE_URL_RE.match(url)) if url else False
    synthetic_url_collision = url in synthetic_url_set if url else False

    if not url:
        return {
            "issue_id": record["issue_id"],
            "status": "PENDING_REAL_MANUAL_URL",
            "valid_real_evidence": False,
            "reason": "no_real_manual_issue_url_yet",
            "url_shape_valid": False,
            "synthetic_rejected": False,
            "auto_execution_allowed": False,
        }

    if synthetic_flag or synthetic_url_collision:
        return {
            "issue_id": record["issue_id"],
            "status": "REJECTED_SYNTHETIC_URL",
            "valid_real_evidence": False,
            "reason": "synthetic_url_or_synthetic_flag_cannot_be_real_evidence",
            "url_shape_valid": url_shape_valid,
            "synthetic_rejected": True,
            "auto_execution_allowed": False,
        }

    if url_shape_valid and metadata_complete:
        return {
            "issue_id": record["issue_id"],
            "status": "VALID_REAL_MANUAL_EVIDENCE_READY_TO_LINK",
            "valid_real_evidence": True,
            "reason": "real_manual_issue_url_shape_and_metadata_complete",
            "url_shape_valid": True,
            "synthetic_rejected": False,
            "auto_execution_allowed": False,
        }

    return {
        "issue_id": record["issue_id"],
        "status": "REAL_EVIDENCE_INCOMPLETE",
        "valid_real_evidence": False,
        "reason": "url_shape_or_metadata_incomplete",
        "url_shape_valid": url_shape_valid,
        "synthetic_rejected": False,
        "auto_execution_allowed": False,
    }

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    candidates = source_candidates(repo)
    synthetic_url_set = synthetic_urls(repo)
    manifest = load_or_create_manifest(repo, candidates)
    records = manifest.get("real_manual_issue_evidence", [])
    validations = [validate_record(r, synthetic_url_set) for r in records]

    valid_count = sum(1 for v in validations if v["valid_real_evidence"])
    pending_count = sum(1 for v in validations if v["status"] == "PENDING_REAL_MANUAL_URL")
    incomplete_count = sum(1 for v in validations if v["status"] == "REAL_EVIDENCE_INCOMPLETE")
    synthetic_rejected_count = sum(1 for v in validations if v["synthetic_rejected"])

    handoff = {
        "status": "PASS" if incomplete_count == 0 else "ATTENTION",
        "phase": "Real Manual Evidence Handoff Pack",
        "ready_for_real_capture": True,
        "candidate_count": len(records),
        "valid_real_evidence_count": valid_count,
        "pending_real_manual_url_count": pending_count,
        "incomplete_real_evidence_count": incomplete_count,
        "synthetic_rejected_count": synthetic_rejected_count,
        "auto_execution_allowed": False,
        "network_validation_performed": False,
        "real_evidence_claim_count": valid_count,
        "synthetic_url_count_available": len(synthetic_url_set),
        "validations": validations,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    checklist = {
        "status": "PASS",
        "checklist": [
            "Confirm a human manually created the issue in GitHub.",
            "Copy the real GitHub issue URL.",
            "Paste it into product/poc/real_manual_evidence_handoff/real_manual_evidence_manifest.json.",
            "Fill created_by, created_at and evidence_note.",
            "Confirm synthetic is false.",
            "Re-run product/scripts/run_real_manual_evidence_handoff.py --repo .",
            "Proceed only if status becomes VALID_REAL_MANUAL_EVIDENCE_READY_TO_LINK for that issue.",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    write_json(out / "prod461_480_real_manual_evidence_manifest_snapshot.json", manifest)
    write_json(out / "prod461_480_real_manual_evidence_handoff.json", handoff)
    write_json(out / "prod461_480_real_manual_evidence_validation.json", {"status": handoff["status"], "validations": validations, "blocked_actions": BLOCKED_ACTIONS})
    write_json(out / "prod461_480_real_manual_evidence_checklist.json", checklist)

    report = [
        "# PROD-461..480 Real Manual Evidence Handoff Pack",
        "",
        f"- Status: `{handoff['status']}`",
        f"- Candidate count: `{handoff['candidate_count']}`",
        f"- Valid real evidence count: `{handoff['valid_real_evidence_count']}`",
        f"- Pending real manual URL count: `{handoff['pending_real_manual_url_count']}`",
        f"- Synthetic rejected count: `{handoff['synthetic_rejected_count']}`",
        f"- Auto execution allowed: `{handoff['auto_execution_allowed']}`",
        f"- Network validation performed: `{handoff['network_validation_performed']}`",
        "",
        "## Validation Results",
    ]
    for v in validations:
        report.append(f"- `{v['issue_id']}` → `{v['status']}` / `{v['reason']}`")
    report += [
        "",
        "## Handoff Checklist",
    ]
    for item in checklist["checklist"]:
        report.append(f"- {item}")
    write_text(out / "prod461_480_real_manual_evidence_handoff.md", "\n".join(report) + "\n")

    return handoff

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    result = build(Path(args.repo))
    print(json.dumps({
        "status": result["status"],
        "candidate_count": result["candidate_count"],
        "valid_real_evidence_count": result["valid_real_evidence_count"],
        "pending_real_manual_url_count": result["pending_real_manual_url_count"],
        "synthetic_rejected_count": result["synthetic_rejected_count"],
        "auto_execution_allowed": result["auto_execution_allowed"],
    }, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

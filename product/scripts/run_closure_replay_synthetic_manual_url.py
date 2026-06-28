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

def load_closure_ledger(repo: Path) -> Dict[str, Any]:
    path = repo / "outputs/prod421_440_closure_ledger.json"
    if not path.exists():
        raise SystemExit(f"missing {path}")
    return read_json(path)

def select_pending_records(ledger: Dict[str, Any], replay_count: int) -> List[Dict[str, Any]]:
    records = [
        r for r in ledger.get("records", [])
        if r.get("closure_status") == "PENDING_MANUAL_ISSUE_CREATION"
    ]
    return records[:replay_count]

def synthetic_url(repo_slug: str, index: int) -> str:
    return f"https://github.com/{repo_slug}/issues/90000{index}"

def build(repo: Path, replay_count: int, repo_slug: str) -> Dict[str, Any]:
    out = repo / "outputs"
    ledger = load_closure_ledger(repo)
    selected = select_pending_records(ledger, replay_count)
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    synthetic_records = []
    replay_records = []
    for idx, record in enumerate(selected, 1):
        url = synthetic_url(repo_slug, idx)
        url_valid = bool(ISSUE_URL_RE.match(url))
        synthetic_records.append({
            "issue_id": record["issue_id"],
            "synthetic_manual_issue_url": url,
            "synthetic": True,
            "created_by": "CASULO_SYNTHETIC_REPLAY",
            "created_at": generated_at,
            "evidence_note": "Synthetic replay URL for local closure path validation only. Not a real issue evidence claim.",
            "source_delta": record.get("source_delta"),
            "priority": record.get("priority"),
            "review_route": record.get("review_route"),
            "valid_shape": url_valid,
        })
        replay_records.append({
            "issue_id": record["issue_id"],
            "synthetic_manual_issue_url": url,
            "manual_issue_url_present": True,
            "source_delta": record.get("source_delta"),
            "priority": record.get("priority"),
            "review_route": record.get("review_route"),
            "previous_closure_status": record.get("closure_status"),
            "target_state": "CREATED_MANUALLY",
            "closure_status": "CREATED_MANUALLY_READY_TO_LINK" if url_valid else "SYNTHETIC_URL_INVALID",
            "next_action": "link_manual_issue_to_task_or_state_replay_only" if url_valid else "fix_synthetic_url",
            "synthetic_only": True,
            "real_evidence_claim": False,
            "valid": url_valid,
            "auto_execution_allowed": False,
            "blocked_actions": BLOCKED_ACTIONS,
        })

    untouched_records = [
        {
            **r,
            "synthetic_only": False,
            "real_evidence_claim": False,
            "auto_execution_allowed": False,
        }
        for r in ledger.get("records", [])
        if r.get("issue_id") not in {x["issue_id"] for x in replay_records}
    ]

    all_replay_records = replay_records + untouched_records
    created_count = sum(1 for r in replay_records if r.get("closure_status") == "CREATED_MANUALLY_READY_TO_LINK")

    manifest = {
        "status": "PASS",
        "synthetic": True,
        "repo_slug": repo_slug,
        "generated_at": generated_at,
        "policy": [
            "Synthetic URLs validate local state transitions only.",
            "Synthetic URLs are not real issue evidence.",
            "No network call is performed.",
            "No issue is created automatically.",
            "Real CREATED_MANUALLY requires human-provided URL evidence."
        ],
        "records": synthetic_records,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    replay_ledger = {
        "status": "PASS",
        "ledger": "casulo.closure_replay_ledger.v0.1",
        "synthetic_only": True,
        "records": all_replay_records,
        "summary": {
            "source_record_count": len(ledger.get("records", [])),
            "replay_count": len(replay_records),
            "synthetic_url_count": len(synthetic_records),
            "created_manually_ready_to_link_count": created_count,
            "pending_manual_creation_count": sum(1 for r in all_replay_records if r.get("closure_status") == "PENDING_MANUAL_ISSUE_CREATION"),
            "real_evidence_claim_count": sum(1 for r in all_replay_records if r.get("real_evidence_claim") is True),
            "auto_execution_allowed": False,
        },
        "blocked_actions": BLOCKED_ACTIONS,
    }

    result = {
        "status": "PASS",
        "phase": "Closure Replay with Synthetic Manual URL",
        "decision": "SYNTHETIC_CREATED_MANUALLY_REPLAY_READY_FOR_REVIEW",
        "synthetic_only": True,
        "replay_count": len(replay_records),
        "created_manually_ready_to_link_count": created_count,
        "real_evidence_claim_count": replay_ledger["summary"]["real_evidence_claim_count"],
        "auto_execution_allowed": False,
        "interpretation": "Synthetic manual URL replay validates CREATED_MANUALLY linkage logic without creating, verifying or claiming a real GitHub issue.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    write_json(out / "prod441_460_synthetic_manual_url_manifest.json", manifest)
    write_json(out / "prod441_460_closure_replay_ledger.json", replay_ledger)
    write_json(out / "prod441_460_closure_replay_result.json", result)

    report_lines = [
        "# PROD-441..460 Closure Replay with Synthetic Manual URL",
        "",
        f"- Status: `{result['status']}`",
        f"- Decision: `{result['decision']}`",
        f"- Synthetic only: `{result['synthetic_only']}`",
        f"- Replay count: `{result['replay_count']}`",
        f"- Created manually ready to link: `{result['created_manually_ready_to_link_count']}`",
        f"- Real evidence claim count: `{result['real_evidence_claim_count']}`",
        f"- Auto execution allowed: `{result['auto_execution_allowed']}`",
        "",
        "## Replay Records",
    ]
    for r in replay_records:
        report_lines.append(f"- `{r['issue_id']}` → `{r['closure_status']}` with synthetic URL `{r['synthetic_manual_issue_url']}`")
    report_lines += [
        "",
        "## Interpretation",
        result["interpretation"],
        "",
        "## Guardrails",
        "- No issue was created.",
        "- No network validation was performed.",
        "- Synthetic URL is not real evidence.",
        "- No closure is final without human-provided evidence.",
    ]
    write_text(out / "prod441_460_closure_replay_report.md", "\n".join(report_lines) + "\n")

    return result

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--replay-count", type=int, default=1)
    parser.add_argument("--repo-slug", default="leoserro39/casulo-campo-os-poc")
    args = parser.parse_args()
    result = build(Path(args.repo), args.replay_count, args.repo_slug)
    print(json.dumps({
        "status": result["status"],
        "decision": result["decision"],
        "synthetic_only": result["synthetic_only"],
        "replay_count": result["replay_count"],
        "created_manually_ready_to_link_count": result["created_manually_ready_to_link_count"],
        "auto_execution_allowed": result["auto_execution_allowed"],
    }, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

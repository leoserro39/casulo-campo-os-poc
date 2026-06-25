#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
APPLIED = ROOT / "05_outputs" / "applied_return_deltas"
OUT = ROOT / "05_outputs" / "sync_deltas"
REPORTS = ROOT / "05_outputs" / "reports"


def rel(path):
    return str(path.relative_to(ROOT))


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def latest_applied_delta():
    files = sorted(APPLIED.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise SystemExit("no applied return delta found")
    return files[0]


def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def build_candidates(source_path, source):
    target_branch = source.get("target_branch")
    question = source.get("question")
    changes = source.get("proposed_changes", [])

    candidates = []

    if target_branch == "atendimento":
        candidates.append({
            "target_branch": "vendas",
            "sync_type": "metric_dependency",
            "reason": "Sales may benefit from visibility into WhatsApp response quality and unresolved contacts.",
            "proposed_signal": "Expose response_time_minutes and unresolved_conversations as sales-facing operational indicators.",
            "risk": "Do not expose raw atendimento conversations or private customer data.",
            "requires_human_review": True,
        })

        candidates.append({
            "target_branch": "operacao",
            "sync_type": "process_dependency",
            "reason": "Operations may depend on whether customer requests are being resolved or waiting for confirmation.",
            "proposed_signal": "Expose aggregate unresolved_conversations and without_resolved_status counts.",
            "risk": "Do not treat atendimento pilot metrics as operational SLA until promoted.",
            "requires_human_review": True,
        })

        candidates.append({
            "target_branch": "gestao",
            "sync_type": "governance_dependency",
            "reason": "Management should track whether the pilot is improving customer response flow before promotion.",
            "proposed_signal": "Expose pilot_signal, promotion_decision and measurement_count.",
            "risk": "Management view must show pilot status, not permanent state.",
            "requires_human_review": True,
        })

    return {
        "status": "SYNC_DELTA_PROPOSED",
        "generated_utc": utc_stamp(),
        "source_applied_delta": rel(source_path),
        "source_branch": target_branch,
        "question": question,
        "source_changes": changes,
        "canonical_effect": "NONE",
        "requires_human_review": True,
        "sync_rule": "Derived sync proposal only. No target branch state mutation.",
        "candidates": candidates,
    }


def write_outputs(sync_delta):
    OUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    stamp = sync_delta["generated_utc"]
    base = "sync_delta_%s_%s" % (sync_delta.get("source_branch", "branch"), stamp)

    json_path = OUT / (base + ".json")
    md_path = OUT / (base + ".md")
    report_json = REPORTS / "cross_branch_sync_delta_report.json"
    report_md = REPORTS / "cross_branch_sync_delta_report.md"

    json_path.write_text(json.dumps(sync_delta, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Cross-Branch Sync Delta",
        "",
        "- status: %s" % sync_delta["status"],
        "- generated_utc: %s" % sync_delta["generated_utc"],
        "- source_branch: %s" % sync_delta["source_branch"],
        "- source_applied_delta: %s" % sync_delta["source_applied_delta"],
        "- canonical_effect: NONE",
        "- requires_human_review: true",
        "",
        "## Candidates",
        "",
    ]

    for item in sync_delta["candidates"]:
        lines.extend([
            "- target_branch: %s" % item["target_branch"],
            "  - sync_type: %s" % item["sync_type"],
            "  - reason: %s" % item["reason"],
            "  - proposed_signal: %s" % item["proposed_signal"],
            "  - risk: %s" % item["risk"],
            "  - requires_human_review: true",
        ])

    lines.extend([
        "",
        "## Safety",
        "",
        "- No target branch state was changed.",
        "- Sync candidates are awareness/proposal artifacts only.",
        "- Human review is required before any branch update.",
        "",
    ])

    md_path.write_text("\n".join(lines), encoding="utf-8")

    report = {
        "generated_utc": sync_delta["generated_utc"],
        "status": "CROSS_BRANCH_SYNC_DELTA_REPORT",
        "sync_delta": rel(json_path),
        "candidate_count": len(sync_delta["candidates"]),
        "canonical_effect": "NONE",
        "requires_human_review": True,
        "target_branches": [c["target_branch"] for c in sync_delta["candidates"]],
    }

    report_json.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    report_lines = [
        "# CASULO Campo OS - Cross-Branch Sync Delta Report",
        "",
        "- generated_utc: %s" % report["generated_utc"],
        "- candidate_count: %s" % report["candidate_count"],
        "- canonical_effect: NONE",
        "- requires_human_review: true",
        "- sync_delta: %s" % report["sync_delta"],
        "",
        "## Target branches",
        "",
    ]

    for branch in report["target_branches"]:
        report_lines.append("- %s" % branch)

    report_lines.extend([
        "",
        "## Current interpretation",
        "",
        "- Atendimento generated a controlled applied delta.",
        "- The system proposed sync candidates for adjacent branches.",
        "- No branch state was mutated.",
        "- Next step is human review of sync candidates.",
        "",
    ])

    report_md.write_text("\n".join(report_lines), encoding="utf-8")

    print("CROSS_BRANCH_SYNC_DELTA_CREATED")
    print("sync_delta:", rel(md_path))
    print("trace:", rel(json_path))
    print("report:", rel(report_md))
    print("candidate_count:", len(sync_delta["candidates"]))
    print("canonical_effect: NONE")
    print("requires_human_review: true")


def main():
    source_path = latest_applied_delta()
    source = read_json(source_path)
    sync_delta = build_candidates(source_path, source)
    write_outputs(sync_delta)


if __name__ == "__main__":
    main()

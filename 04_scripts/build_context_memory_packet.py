#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "05_outputs" / "context_packets"
REPORTS = ROOT / "05_outputs" / "reports"


def rel(path):
    return str(path.relative_to(ROOT))


def run(cmd):
    try:
        return subprocess.check_output(cmd, cwd=str(ROOT), text=True).strip()
    except Exception:
        return ""


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def latest(pattern):
    files = sorted(ROOT.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def item(pattern):
    path = latest(pattern)
    if not path:
        return {"path": None, "data": {}}
    return {"path": rel(path), "data": read_json(path)}


def build_packet():
    latest_applied = item("05_outputs/applied_return_deltas/*.json")
    latest_measurement = item("05_outputs/pilot_measurements/*.json")
    latest_promotion = item("05_outputs/promotion_decisions/*.json")
    latest_sync = item("05_outputs/sync_deltas/*.json")
    latest_awareness = item("05_outputs/reports/applied_delta_awareness.json")
    latest_pilot_report = item("05_outputs/reports/pilot_measurement_report.json")
    latest_promotion_report = item("05_outputs/reports/promotion_decision_report.json")
    latest_sync_report = item("05_outputs/reports/cross_branch_sync_delta_report.json")

    commit = run(["git", "rev-parse", "--short", "HEAD"])
    branch = run(["git", "branch", "--show-current"])
    recent_commits = run(["git", "log", "--oneline", "-10"]).splitlines()

    pending_gates = []

    promo_report = latest_promotion_report["data"]
    if not promo_report.get("promotion_allowed", False):
        pending_gates.append("Long-term promotion is not allowed yet.")

    sync_report = latest_sync_report["data"]
    if sync_report.get("requires_human_review"):
        pending_gates.append("Cross-branch sync candidates require human review.")

    pilot_report = latest_pilot_report["data"]
    agg = pilot_report.get("aggregate", {})
    if agg.get("overall_signal") != "PROMOTION_CANDIDATE":
        pending_gates.append("Pilot needs more measurements before promotion.")

    packet = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "CONTEXT_MEMORY_PACKET",
        "repo": {
            "branch": branch,
            "commit": commit,
            "recent_commits": recent_commits,
        },
        "poc_version": {
            "current": "v1.5",
            "completed": [
                "v1.0 closed micrograph loop",
                "v1.1 applied delta awareness",
                "v1.2 pilot measurement loop",
                "v1.3 promotion decision gate",
                "v1.4 cross-branch sync delta",
            ],
            "active": "v1.5 context memory packet",
            "next": "v1.6 graph projection or cockpit refresh with v1.5 context",
        },
        "latest_artifacts": {
            "applied_return_delta": latest_applied,
            "pilot_measurement": latest_measurement,
            "promotion_decision": latest_promotion,
            "sync_delta": latest_sync,
            "applied_delta_awareness": latest_awareness,
            "pilot_measurement_report": latest_pilot_report,
            "promotion_decision_report": latest_promotion_report,
            "cross_branch_sync_delta_report": latest_sync_report,
        },
        "operational_state": {
            "applied_delta_active": bool(latest_applied["path"]),
            "pilot_measurement_count": agg.get("measurement_count"),
            "pilot_overall_signal": agg.get("overall_signal"),
            "promotion_status": promo_report.get("promotion_status"),
            "promotion_allowed": promo_report.get("promotion_allowed"),
            "sync_candidate_count": sync_report.get("candidate_count"),
            "sync_requires_human_review": sync_report.get("requires_human_review"),
        },
        "pending_gates": pending_gates,
        "next_safe_action": "Collect more pilot measurements or review cross-branch sync candidates. Do not promote or mutate target branches automatically.",
    }

    return packet


def write_packet(packet):
    OUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    json_path = OUT / ("context_memory_packet_%s.json" % stamp)
    md_path = OUT / ("context_memory_packet_%s.md" % stamp)
    latest_json = OUT / "context_memory_packet_latest.json"
    latest_md = OUT / "context_memory_packet_latest.md"
    report_json = REPORTS / "context_memory_packet_report.json"
    report_md = REPORTS / "context_memory_packet_report.md"

    text_json = json.dumps(packet, indent=2, ensure_ascii=False)
    json_path.write_text(text_json, encoding="utf-8")
    latest_json.write_text(text_json, encoding="utf-8")
    report_json.write_text(text_json, encoding="utf-8")

    op = packet["operational_state"]
    repo = packet["repo"]
    version = packet["poc_version"]

    lines = [
        "# CASULO Campo OS - Context Memory Packet",
        "",
        "- generated_utc: %s" % packet["generated_utc"],
        "- status: %s" % packet["status"],
        "- branch: %s" % repo["branch"],
        "- commit: %s" % repo["commit"],
        "- current_version: %s" % version["current"],
        "- active: %s" % version["active"],
        "- next: %s" % version["next"],
        "",
        "## Completed milestones",
        "",
    ]

    lines.extend(["- " + x for x in version["completed"]])

    lines.extend([
        "",
        "## Operational state",
        "",
        "- applied_delta_active: %s" % op["applied_delta_active"],
        "- pilot_measurement_count: %s" % op["pilot_measurement_count"],
        "- pilot_overall_signal: %s" % op["pilot_overall_signal"],
        "- promotion_status: %s" % op["promotion_status"],
        "- promotion_allowed: %s" % op["promotion_allowed"],
        "- sync_candidate_count: %s" % op["sync_candidate_count"],
        "- sync_requires_human_review: %s" % op["sync_requires_human_review"],
        "",
        "## Latest artifact paths",
        "",
    ])

    for key, value in packet["latest_artifacts"].items():
        lines.append("- %s: %s" % (key, value.get("path")))

    lines.extend([
        "",
        "## Pending gates",
        "",
    ])

    if packet["pending_gates"]:
        lines.extend(["- " + x for x in packet["pending_gates"]])
    else:
        lines.append("- none")

    lines.extend([
        "",
        "## Next safe action",
        "",
        "- %s" % packet["next_safe_action"],
        "",
        "## Recent commits",
        "",
    ])

    lines.extend(["- " + x for x in repo["recent_commits"]])
    lines.append("")

    text_md = "\n".join(lines)
    md_path.write_text(text_md, encoding="utf-8")
    latest_md.write_text(text_md, encoding="utf-8")
    report_md.write_text(text_md, encoding="utf-8")

    print("CONTEXT_MEMORY_PACKET_CREATED")
    print("packet:", rel(md_path))
    print("latest:", rel(latest_md))
    print("json:", rel(json_path))
    print("report:", rel(report_md))
    print("commit:", repo["commit"])
    print("next_safe_action:", packet["next_safe_action"])


def main():
    packet = build_packet()
    write_packet(packet)


if __name__ == "__main__":
    main()

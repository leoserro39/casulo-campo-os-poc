#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "05_outputs" / "releases"


def run(cmd):
    return subprocess.check_output(cmd, cwd=str(ROOT), text=True).strip()


def exists(path):
    return (ROOT / path).exists()


def main():
    OUT.mkdir(parents=True, exist_ok=True)

    commit = run(["git", "rev-parse", "--short", "HEAD"])
    branch = run(["git", "branch", "--show-current"])
    commits = run(["git", "log", "--oneline", "-18"]).splitlines()
    generated = datetime.now(timezone.utc).isoformat()

    release = {
        "generated_utc": generated,
        "release": "v1.7-orchestration-contract",
        "branch": branch,
        "commit": commit,
        "status": "RELEASE_CANDIDATE",
        "source_of_truth": "git",
        "canonical_effect": "NONE",
        "completed_milestones": [
            "v1.0 closed micrograph loop",
            "v1.1 applied delta awareness",
            "v1.2 pilot measurement loop",
            "v1.3 promotion decision gate",
            "v1.4 cross-branch sync delta",
            "v1.5 context memory packet",
            "v1.6 graph projection",
            "v1.7 orchestration action manifest",
        ],
        "key_artifacts": {
            "context_packet": "05_outputs/context_packets/context_memory_packet_latest.md",
            "operational_cube": "05_outputs/cockpit/operational_cube_v11.html",
            "graph_projection": "05_outputs/graph_projection/casulo_graph_projection.json",
            "orchestration_manifest": "05_outputs/orchestration/action_manifest.md",
            "roadmap": "06_contracts/roadmap/CASULO_CAMPO_OS_ROADMAP.md",
            "pilot_report": "05_outputs/reports/pilot_measurement_report.md",
            "promotion_report": "05_outputs/reports/promotion_decision_report.md",
            "sync_report": "05_outputs/reports/cross_branch_sync_delta_report.md",
        },
        "readiness": {
            "context_packet": exists("05_outputs/context_packets/context_memory_packet_latest.md"),
            "operational_cube": exists("05_outputs/cockpit/operational_cube_v11.html"),
            "graph_projection": exists("05_outputs/graph_projection/casulo_graph_projection.json"),
            "orchestration_manifest": exists("05_outputs/orchestration/action_manifest.md"),
            "roadmap": exists("06_contracts/roadmap/CASULO_CAMPO_OS_ROADMAP.md"),
        },
        "pending_gates": [
            "Long-term promotion remains blocked.",
            "Cross-branch sync candidates require human review.",
            "Pilot needs more real measurements.",
            "n8n/MCP tools should start read-only and evidence-only.",
        ],
        "next_phase": "Real-world controlled tests with real source data and real pilot measurements.",
        "recent_commits": commits,
    }

    json_path = OUT / "release_v1_7_orchestration_contract.json"
    md_path = OUT / "RELEASE_V1_7_ORCHESTRATION_CONTRACT.md"

    json_path.write_text(json.dumps(release, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Release v1.7 Orchestration Contract",
        "",
        "- generated_utc: %s" % generated,
        "- release: v1.7-orchestration-contract",
        "- branch: %s" % branch,
        "- commit: %s" % commit,
        "- status: RELEASE_CANDIDATE",
        "- source_of_truth: git",
        "- canonical_effect: NONE",
        "",
        "## Completed milestones",
        "",
    ]
    lines.extend(["- " + item for item in release["completed_milestones"]])

    lines.extend(["", "## Key artifacts", ""])
    for key, value in release["key_artifacts"].items():
        lines.append("- %s: %s" % (key, value))

    lines.extend(["", "## Readiness", ""])
    for key, value in release["readiness"].items():
        lines.append("- %s: %s" % (key, value))

    lines.extend(["", "## Pending gates", ""])
    lines.extend(["- " + item for item in release["pending_gates"]])

    lines.extend([
        "",
        "## Next phase",
        "",
        "- Real-world controlled tests with real source data and real pilot measurements.",
        "",
        "## Recent commits",
        "",
    ])
    lines.extend(["- " + item for item in commits])
    lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print("RELEASE_SNAPSHOT_CREATED")
    print("release:", md_path.relative_to(ROOT))
    print("json:", json_path.relative_to(ROOT))
    print("commit:", commit)


if __name__ == "__main__":
    main()

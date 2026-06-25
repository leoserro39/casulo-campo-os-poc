#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "05_outputs" / "reports"

def run(cmd):
    return subprocess.check_output(cmd, cwd=str(ROOT), text=True).strip()

def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}

def count(pattern):
    return len(list(ROOT.glob(pattern)))

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    timeline = read_json(ROOT / "05_outputs/reports/state_timeline.json")
    cube = read_json(ROOT / "05_outputs/cockpit/operational_cube.json")

    commits = run(["git", "log", "--oneline", "-12"])

    summary = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "latest_commit": run(["git", "rev-parse", "--short", "HEAD"]),
        "proposal_count": count("05_outputs/proposals/*.json"),
        "mesh_delta_count": count("05_outputs/deltas/*.json"),
        "source_intake_count": count("05_outputs/source_intake/manifests/*.json"),
        "trust_report_count": count("05_outputs/source_intake/trust_reports/*.md"),
        "cockpit_exists": (ROOT / "05_outputs/cockpit/operational_cube.html").exists(),
        "timeline_event_count": len(timeline.get("events", [])),
        "cube_human_gate_count": cube.get("summary", {}).get("human_gate_count"),
    }

    json_path = OUT / "poc_final_snapshot.json"
    md_path = OUT / "POC_FINAL_SNAPSHOT.md"

    json_path.write_text(json.dumps({
        "summary": summary,
        "commits": commits.splitlines(),
        "proven_capabilities": [
            "Git as source of truth",
            "repo-as-mesh operational structure",
            "local RAG chunks",
            "derived graph",
            "operator chat",
            "mesh delta computation",
            "Delta_L and H_pre gate",
            "delta-gated proposal generation",
            "legacy source intake",
            "source trust report",
            "hallucination risk signal",
            "state timeline",
            "operational cube cockpit projection",
        ],
        "planned_capabilities": [
            "review gate approve/reject/needs_more_evidence",
            "return delta promotion",
            "cross-branch sync delta",
            "context memory packet",
            "Neo4j projection",
            "n8n/MCP orchestration",
            "3D cube/cupula visual evolution",
        ],
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# CASULO Campo OS - POC Final Snapshot",
        "",
        "- generated_utc: %s" % summary["generated_utc"],
        "- latest_commit: %s" % summary["latest_commit"],
        "- proposal_count: %s" % summary["proposal_count"],
        "- mesh_delta_count: %s" % summary["mesh_delta_count"],
        "- source_intake_count: %s" % summary["source_intake_count"],
        "- trust_report_count: %s" % summary["trust_report_count"],
        "- timeline_event_count: %s" % summary["timeline_event_count"],
        "- cube_human_gate_count: %s" % summary["cube_human_gate_count"],
        "- cockpit: 05_outputs/cockpit/operational_cube.html",
        "",
        "## Proven capabilities",
        "",
        "- Git as source of truth",
        "- repo-as-mesh operational structure",
        "- local RAG chunks and derived graph",
        "- operator chat",
        "- mesh delta computation",
        "- Delta_L and H_pre gate",
        "- delta-gated proposal generation",
        "- legacy source intake",
        "- source trust report",
        "- hallucination risk signal",
        "- state timeline",
        "- operational cube cockpit projection",
        "",
        "## Current gates",
        "",
        "- Source intake legacy WhatsApp requires human review.",
        "- Proposals are PROPOSED and not canonical state.",
        "- Sync Layer is planned, not active.",
        "- Return Delta promotion is planned, not active.",
        "",
        "## Next recommended phase",
        "",
        "POC vNext: Review Gate + Return Delta promotion.",
        "",
        "## Recent commits",
        "",
    ]
    lines.extend(["- " + line for line in commits.splitlines()])
    lines.append("")

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print("POC_FINAL_SNAPSHOT_CREATED")
    print("md:", md_path.relative_to(ROOT))
    print("json:", json_path.relative_to(ROOT))
    print("latest_commit:", summary["latest_commit"])

if __name__ == "__main__":
    main()

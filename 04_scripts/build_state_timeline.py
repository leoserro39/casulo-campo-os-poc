#!/usr/bin/env python3
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "05_outputs" / "reports"

def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None

def collect_files(pattern):
    return sorted(ROOT.glob(pattern), key=lambda p: p.stat().st_mtime)

def rel(path):
    return str(path.relative_to(ROOT))

def main():
    OUT.mkdir(parents=True, exist_ok=True)

    proposals = collect_files("05_outputs/proposals/*.json")
    deltas = collect_files("05_outputs/deltas/*.json")
    manifests = collect_files("05_outputs/source_intake/manifests/*.json")
    mappings = collect_files("05_outputs/source_intake/mappings/*.json")
    trust_reports = collect_files("05_outputs/source_intake/trust_reports/*.md")
    intake_deltas = collect_files("05_outputs/source_intake/deltas/*.md")

    events = []

    for p in manifests:
        data = read_json(p) or {}
        events.append({
            "type": "source_intake",
            "path": rel(p),
            "source_id": data.get("source_id"),
            "target_branch": data.get("target_branch"),
            "trust_score": data.get("trust_score"),
            "hallucination_risk": data.get("hallucination_risk"),
            "gate": data.get("gate"),
        })

    for p in deltas:
        data = read_json(p) or {}
        events.append({
            "type": "mesh_delta",
            "path": rel(p),
            "question": data.get("question"),
            "domain": data.get("inferred_domain"),
            "Delta_L": data.get("Delta_L"),
            "H_pre": data.get("H_pre"),
            "gate": data.get("gate"),
        })

    for p in proposals:
        data = read_json(p) or {}
        md = data.get("mesh_delta", {})
        events.append({
            "type": "proposal",
            "path": rel(p),
            "question": data.get("question"),
            "domain": data.get("inferred_domain"),
            "status": data.get("status"),
            "gate": md.get("gate"),
            "Delta_L": md.get("Delta_L"),
            "H_pre": md.get("H_pre"),
        })

    state = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "source_intake_count": len(manifests),
        "source_mapping_count": len(mappings),
        "source_trust_report_count": len(trust_reports),
        "intake_delta_count": len(intake_deltas),
        "mesh_delta_count": len(deltas),
        "proposal_count": len(proposals),
        "events": events,
    }

    json_path = OUT / "state_timeline.json"
    md_path = OUT / "state_timeline.md"

    json_path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# CASULO Campo OS - State Timeline",
        "",
        "- generated_utc: %s" % state["generated_utc"],
        "- source_intake_count: %s" % state["source_intake_count"],
        "- source_mapping_count: %s" % state["source_mapping_count"],
        "- source_trust_report_count: %s" % state["source_trust_report_count"],
        "- intake_delta_count: %s" % state["intake_delta_count"],
        "- mesh_delta_count: %s" % state["mesh_delta_count"],
        "- proposal_count: %s" % state["proposal_count"],
        "",
        "## Current operational reading",
        "",
    ]

    if manifests:
        lines.append("- Legacy/source intake is active.")
    if deltas:
        lines.append("- Mesh delta computation is active.")
    if proposals:
        lines.append("- Delta-gated proposal generation is active.")

    human_gates = []
    for p in manifests:
        data = read_json(p) or {}
        gate = data.get("gate")
        if gate and "HUMAN" in gate:
            human_gates.append((rel(p), gate, data.get("hallucination_risk")))

    lines.extend(["", "## Human review required", ""])
    if human_gates:
        for path, gate, risk in human_gates:
            lines.append("- %s | gate=%s | hallucination_risk=%s" % (path, gate, risk))
    else:
        lines.append("- none")

    lines.extend(["", "## Events", ""])
    for ev in events:
        bits = ["- type=%s" % ev.get("type"), "path=%s" % ev.get("path")]
        for key in ["source_id", "question", "domain", "target_branch", "status", "gate", "Delta_L", "H_pre", "trust_score", "hallucination_risk"]:
            if ev.get(key) is not None:
                bits.append("%s=%s" % (key, ev.get(key)))
        lines.append(" | ".join(bits))

    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print("STATE_TIMELINE_CREATED")
    print("json:", rel(json_path))
    print("md:", rel(md_path))
    print("events:", len(events))
    print("human_review_required:", len(human_gates))

if __name__ == "__main__":
    main()

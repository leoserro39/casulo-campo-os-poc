#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "05_outputs" / "graph_projection"
REPORTS = ROOT / "05_outputs" / "reports"


def rel(path):
    return str(path.relative_to(ROOT))


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def latest(pattern):
    files = sorted(ROOT.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def run(cmd):
    try:
        return subprocess.check_output(cmd, cwd=str(ROOT), text=True).strip()
    except Exception:
        return ""


def add_node(nodes, node_id, node_type, label, **props):
    nodes[node_id] = {
        "id": node_id,
        "type": node_type,
        "label": label,
        "properties": props,
    }


def add_edge(edges, source, target, edge_type, **props):
    edges.append({
        "source": source,
        "target": target,
        "type": edge_type,
        "properties": props,
    })


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    commit = run(["git", "rev-parse", "--short", "HEAD"])
    branch = run(["git", "branch", "--show-current"])

    nodes = {}
    edges = []

    add_node(nodes, "repo:casulo-campo-os-poc", "repo", "casulo-campo-os-poc", branch=branch, commit=commit)

    milestones = [
        ("v1.0", "Closed micrograph loop"),
        ("v1.1", "Applied Delta Awareness"),
        ("v1.2", "Pilot Measurement Loop"),
        ("v1.3", "Promotion Decision Gate"),
        ("v1.4", "Cross-Branch Sync Delta"),
        ("v1.5", "Context Memory Packet"),
        ("v1.6", "Graph Projection"),
    ]

    previous = None
    for version, label in milestones:
        node_id = "milestone:%s" % version
        add_node(nodes, node_id, "milestone", label, version=version)
        add_edge(edges, "repo:casulo-campo-os-poc", node_id, "PRODUCED")
        if previous:
            add_edge(edges, previous, node_id, "PRECEDES")
        previous = node_id

    artifacts = {
        "applied_return_delta": latest("05_outputs/applied_return_deltas/*.json"),
        "pilot_measurement": latest("05_outputs/pilot_measurements/*.json"),
        "promotion_decision": latest("05_outputs/promotion_decisions/*.json"),
        "sync_delta": latest("05_outputs/sync_deltas/*.json"),
        "context_packet": latest("05_outputs/context_packets/context_memory_packet_latest.json"),
        "pilot_report": latest("05_outputs/reports/pilot_measurement_report.json"),
        "promotion_report": latest("05_outputs/reports/promotion_decision_report.json"),
        "sync_report": latest("05_outputs/reports/cross_branch_sync_delta_report.json"),
    }

    for name, path in artifacts.items():
        if not path:
            continue
        data = read_json(path)
        node_id = "artifact:%s" % name
        add_node(
            nodes,
            node_id,
            "artifact",
            name,
            path=rel(path),
            status=data.get("status"),
            decision=data.get("decision"),
            signal=data.get("pilot_signal") or data.get("overall_signal"),
            canonical_effect=data.get("canonical_effect"),
        )
        add_edge(edges, "repo:casulo-campo-os-poc", node_id, "PRODUCED")

    if artifacts.get("applied_return_delta"):
        add_node(nodes, "branch:atendimento", "branch", "atendimento")
        add_edge(edges, "artifact:applied_return_delta", "branch:atendimento", "APPLIES_TO")

    if artifacts.get("pilot_measurement"):
        add_edge(edges, "artifact:applied_return_delta", "artifact:pilot_measurement", "MEASURED_BY")

    if artifacts.get("promotion_decision"):
        add_edge(edges, "artifact:pilot_report", "artifact:promotion_decision", "DECIDED_BY")
        add_edge(edges, "artifact:promotion_decision", "gate:promotion", "BLOCKED_BY")
        add_node(nodes, "gate:promotion", "gate", "Promotion Gate", promotion_allowed=False)

    if artifacts.get("sync_delta"):
        for target in ["vendas", "operacao", "gestao"]:
            branch_node = "branch:%s" % target
            add_node(nodes, branch_node, "branch", target)
            add_edge(edges, "artifact:sync_delta", branch_node, "SYNCS_TO", requires_human_review=True)

    if artifacts.get("context_packet"):
        add_edge(edges, "artifact:context_packet", "repo:casulo-campo-os-poc", "SUMMARIZES")

    projection = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "GRAPH_PROJECTION",
        "source_of_truth": "git",
        "canonical_effect": "NONE",
        "commit": commit,
        "node_count": len(nodes),
        "edge_count": len(edges),
        "nodes": list(nodes.values()),
        "edges": edges,
    }

    json_path = OUT / "casulo_graph_projection.json"
    md_path = REPORTS / "graph_projection_report.md"
    report_json = REPORTS / "graph_projection_report.json"

    json_path.write_text(json.dumps(projection, indent=2, ensure_ascii=False), encoding="utf-8")
    report_json.write_text(json.dumps(projection, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Graph Projection Report",
        "",
        "- generated_utc: %s" % projection["generated_utc"],
        "- status: GRAPH_PROJECTION",
        "- source_of_truth: git",
        "- canonical_effect: NONE",
        "- commit: %s" % commit,
        "- node_count: %s" % projection["node_count"],
        "- edge_count: %s" % projection["edge_count"],
        "- projection: 05_outputs/graph_projection/casulo_graph_projection.json",
        "",
        "## Node types",
        "",
    ]

    node_types = sorted(set(n["type"] for n in projection["nodes"]))
    edge_types = sorted(set(e["type"] for e in projection["edges"]))

    lines.extend(["- " + x for x in node_types])
    lines.extend(["", "## Edge types", ""])
    lines.extend(["- " + x for x in edge_types])
    lines.extend([
        "",
        "## Safety",
        "",
        "- Graph projection is derived from repo artifacts.",
        "- No canonical state was changed.",
        "- Neo4j import, when added, must use this projection as input.",
        "",
    ])

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print("GRAPH_PROJECTION_CREATED")
    print("projection:", rel(json_path))
    print("report:", rel(md_path))
    print("node_count:", projection["node_count"])
    print("edge_count:", projection["edge_count"])
    print("canonical_effect: NONE")


if __name__ == "__main__":
    main()

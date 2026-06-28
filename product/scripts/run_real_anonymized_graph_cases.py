#!/usr/bin/env python3
from __future__ import annotations

import argparse
import csv
import json
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any, Dict, List, Tuple

BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
]

DELTA_TO_GATE = {
    "delta_evidence": "ASK_FOR_EVIDENCE",
    "delta_ambiguity": "STRUCTURE_ONLY",
    "delta_missingness": "TASK_ONLY",
    "delta_conflict": "HUMAN_REVIEW_REQUIRED",
    "delta_rule": "STRUCTURE_ONLY",
    "delta_domain": "HUMAN_REVIEW_REQUIRED",
    "delta_execution": "TASK_ONLY",
    "delta_production": "BLOCKED_UNSUPPORTED",
    "delta_human_review": "HUMAN_REVIEW_REQUIRED",
    "delta_graph_structure": "STRUCTURE_ONLY",
    "delta_model_behavior": "TASK_ONLY",
}

DELTA_TO_CONTROL = {
    "delta_evidence": "require_evidence",
    "delta_ambiguity": "split_interpretations",
    "delta_missingness": "generate_missing_artifact_task",
    "delta_conflict": "conflict_resolution_task",
    "delta_rule": "exception_map",
    "delta_domain": "require_domain_owner",
    "delta_execution": "require_test_plan",
    "delta_production": "production_block",
    "delta_human_review": "create_review_task",
    "delta_graph_structure": "graph_repair_suggestion",
    "delta_model_behavior": "calibration_review",
}

TASK_BY_DELTA = {
    "delta_evidence": ("evidence", "Attach source/evidence before committing graph relation."),
    "delta_missingness": ("document", "Provide missing required document, field, test or domain artifact."),
    "delta_rule": ("rule_map", "Map rule source, scope, exception and applicability."),
    "delta_execution": ("test_plan", "Provide runtime, dependency and test context before execution."),
    "delta_graph_structure": ("graph_repair", "Repair bridge, relation type or orphan node."),
    "delta_conflict": ("arbitration", "Resolve conflicting sources/states/rules."),
    "delta_domain": ("domain_owner", "Assign domain owner for sensitive decision."),
    "delta_production": ("production_readiness", "Provide auth, audit, rollback, monitoring and support plan."),
    "delta_human_review": ("human_review", "Route to human owner or reviewer."),
    "delta_model_behavior": ("calibration_review", "Review anomaly pattern against calibration history."),
    "delta_ambiguity": ("interpretation_split", "Split possible interpretations and keep candidate-only relation."),
}

GATE_PRIORITY = {
    "BLOCKED_UNSUPPORTED": ("P0_BLOCKER", 100),
    "HUMAN_REVIEW_REQUIRED": ("P1_REVIEW", 85),
    "ASK_FOR_EVIDENCE": ("P2_EVIDENCE_OR_TASK", 70),
    "TASK_ONLY": ("P2_EVIDENCE_OR_TASK", 65),
    "STRUCTURE_ONLY": ("P3_STRUCTURE", 45),
}

DELTA_WEIGHT = {
    "delta_production": 30,
    "delta_domain": 22,
    "delta_conflict": 20,
    "delta_execution": 16,
    "delta_evidence": 14,
    "delta_missingness": 14,
    "delta_rule": 12,
    "delta_human_review": 12,
    "delta_graph_structure": 8,
    "delta_model_behavior": 6,
    "delta_ambiguity": 6,
}

NODE_TYPES = ["entity", "rule", "artifact", "state", "task", "evidence", "decision", "control"]
EDGE_TYPES = ["supports", "depends_on", "constrains", "requires", "produces", "blocks", "routes_to", "challenges"]

def read_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")

def priority_for(delta: str, gate: str, count: int) -> Tuple[str, int]:
    level, base = GATE_PRIORITY.get(gate, ("P3_STRUCTURE", 40))
    score = min(100, base + DELTA_WEIGHT.get(delta, 5) + min(20, max(0, count - 1) * 3))
    if gate == "BLOCKED_UNSUPPORTED":
        level = "P0_BLOCKER"
    elif score >= 95:
        level = "P0_BLOCKER"
    elif score >= 80:
        level = "P1_REVIEW"
    elif score >= 60:
        level = "P2_EVIDENCE_OR_TASK"
    elif score >= 40:
        level = "P3_STRUCTURE"
    else:
        level = "P4_CALIBRATION"
    return level, score

def task_from_delta(task_id: int, origin: str, delta: str) -> Dict[str, Any]:
    kind, reason = TASK_BY_DELTA[delta]
    return {
        "task_id": f"TASK-{task_id:03d}",
        "origin": origin,
        "artifact_type": kind,
        "source_delta": delta,
        "reason": reason,
        "recommended_gate": DELTA_TO_GATE[delta],
        "status": "OPEN_CANDIDATE",
    }

def pick(rng: random.Random, items: List[str]) -> str:
    return items[rng.randrange(len(items))]

def build_case_graph(case: Dict[str, Any], seed: int) -> Tuple[Dict[str, Any], List[Dict[str, Any]]]:
    rng = random.Random(seed + sum(ord(c) for c in case["case_id"]))
    case_id = case["case_id"]
    graph_id = f"RAGC-{case_id}"
    expected = list(case["expected_risks"])
    profile = case["evidence_profile"]
    base_nodes = 10 + profile["missing_artifacts"]
    base_edges = 16 + int(profile["ambiguity_level"] / 10)

    deltas = expected + ["delta_graph_structure", "delta_evidence", "delta_model_behavior"]
    nodes = []
    tasks = []
    tid = 1
    for idx in range(1, base_nodes + 1):
        primary = pick(rng, deltas)
        if idx <= len(expected):
            primary = expected[idx - 1]
        gate = DELTA_TO_GATE[primary]
        node = {
            "node_id": f"{graph_id}-N{idx:02d}",
            "node_type": pick(rng, NODE_TYPES),
            "domain": pick(rng, case["domain_family"]),
            "confidence": max(20, min(95, profile["evidence_strength"] + rng.randint(-20, 25))),
            "evidence_strength": max(10, min(95, profile["evidence_strength"] + rng.randint(-25, 20))),
            "primary_delta": primary,
            "active_deltas": sorted(set([primary] + rng.sample(deltas, k=min(2, len(deltas))))),
            "recommended_control": DELTA_TO_CONTROL[primary],
            "recommended_gate": gate,
            "candidate": True,
        }
        nodes.append(node)
        if gate in ["ASK_FOR_EVIDENCE", "TASK_ONLY", "HUMAN_REVIEW_REQUIRED", "BLOCKED_UNSUPPORTED", "STRUCTURE_ONLY"]:
            tasks.append(task_from_delta(tid, node["node_id"], primary)); tid += 1

    edges = []
    for idx in range(1, base_edges + 1):
        a, b = rng.sample(nodes, 2)
        shared = sorted(set(a["active_deltas"]).intersection(b["active_deltas"]))
        primary = shared[0] if shared else pick(rng, a["active_deltas"] + b["active_deltas"])
        gate = DELTA_TO_GATE[primary]
        edge = {
            "edge_id": f"{graph_id}-E{idx:02d}",
            "from": a["node_id"],
            "to": b["node_id"],
            "relation": pick(rng, EDGE_TYPES),
            "primary_delta": primary,
            "recommended_control": DELTA_TO_CONTROL[primary],
            "recommended_gate": gate,
            "candidate": True,
            "material_delta_change": rng.randint(0, 20),
        }
        edges.append(edge)
        if gate in ["ASK_FOR_EVIDENCE", "TASK_ONLY", "HUMAN_REVIEW_REQUIRED", "BLOCKED_UNSUPPORTED", "STRUCTURE_ONLY"]:
            tasks.append(task_from_delta(tid, edge["edge_id"], primary)); tid += 1

    gate_counts = Counter([n["recommended_gate"] for n in nodes] + [e["recommended_gate"] for e in edges])
    delta_counts = Counter([n["primary_delta"] for n in nodes] + [e["primary_delta"] for e in edges])
    control_counts = Counter([n["recommended_control"] for n in nodes] + [e["recommended_control"] for e in edges])
    avg_material = round(sum(e["material_delta_change"] for e in edges) / len(edges), 2) if edges else 0.0
    readiness = "READY_FOR_NEXT_ACTION"
    if gate_counts.get("BLOCKED_UNSUPPORTED", 0) > 0:
        readiness = "PRODUCTION_BLOCKED"
    elif gate_counts.get("HUMAN_REVIEW_REQUIRED", 0) > 0:
        readiness = "HUMAN_REVIEW_REQUIRED"
    elif gate_counts.get("ASK_FOR_EVIDENCE", 0) > 0:
        readiness = "EVIDENCE_REQUIRED"
    elif gate_counts.get("TASK_ONLY", 0) > 0:
        readiness = "TASK_READY"

    graph = {
        "graph_id": graph_id,
        "case_id": case_id,
        "mode": "real_like_anonymized_candidate_graph",
        "nodes": nodes,
        "edges": edges,
        "telemetry_summary": {
            "gate_counts": dict(gate_counts),
            "delta_counts": dict(delta_counts),
            "control_counts": dict(control_counts),
            "avg_material_delta_change": avg_material,
            "task_count": len(tasks),
        },
        "readiness": readiness,
        "allowed_actions": ["inspect_graph", "request_evidence", "create_task_candidate", "mark_candidate_edge", "route_human_review"],
        "blocked_actions": BLOCKED_ACTIONS,
    }
    return graph, tasks

def cluster_tasks(tasks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    grouped = defaultdict(list)
    for t in tasks:
        grouped[(t["source_delta"], t["artifact_type"], t["recommended_gate"])].append(t)
    clusters = []
    for idx, ((delta, artifact, gate), items) in enumerate(sorted(grouped.items()), 1):
        priority, score = priority_for(delta, gate, len(items))
        clusters.append({
            "cluster_id": f"CLUSTER-{idx:03d}",
            "source_delta": delta,
            "artifact_type": artifact,
            "recommended_gate": gate,
            "priority": priority,
            "priority_score": score,
            "task_count": len(items),
            "task_ids": [i["task_id"] for i in items],
            "origins": [i["origin"] for i in items],
            "reason": items[0]["reason"],
            "closure_state": "READY_FOR_ISSUE" if priority in ["P0_BLOCKER", "P1_REVIEW", "P2_EVIDENCE_OR_TASK"] else "OPEN_CANDIDATE",
        })
    return sorted(clusters, key=lambda c: (-c["priority_score"], c["cluster_id"]))

def issue_candidates(case_id: str, clusters: List[Dict[str, Any]], max_issues: int) -> List[Dict[str, Any]]:
    out = []
    for idx, c in enumerate(clusters[:max_issues], 1):
        title = f"[{c['priority']}] {case_id}: {c['artifact_type']} required for {c['source_delta']}"
        out.append({
            "issue_id": f"{case_id}-ISSUE-CANDIDATE-{idx:03d}",
            "case_id": case_id,
            "cluster_id": c["cluster_id"],
            "title": title,
            "priority": c["priority"],
            "labels": sorted(set(["casulo", "real-graph-case", "graph-telemetry", c["priority"].lower(), c["source_delta"].replace("delta_", "delta-")])),
            "body": (
                f"## Context\nGenerated by CASULO real/anonymized graph case runner.\n\n"
                f"## Case\n- Case: `{case_id}`\n- Cluster: `{c['cluster_id']}`\n- Source delta: `{c['source_delta']}`\n- Artifact type: `{c['artifact_type']}`\n- Recommended gate: `{c['recommended_gate']}`\n- Task count: `{c['task_count']}`\n\n"
                f"## Required action\n{c['reason']}\n\n"
                f"## Acceptance criteria\n- Evidence, owner, rule, test or repair artifact is provided.\n- Graph relation remains candidate until supported.\n- No production automation is enabled.\n"
            ),
            "status": "READY_FOR_REVIEW_NOT_CREATED",
        })
    return out

def run_case(case: Dict[str, Any], seed: int, max_issues: int) -> Dict[str, Any]:
    graph, tasks = build_case_graph(case, seed)
    clusters = cluster_tasks(tasks)
    issues = issue_candidates(case["case_id"], clusters, max_issues)
    p0_count = sum(1 for c in clusters if c["priority"] == "P0_BLOCKER")
    decision = "P0_BLOCKERS_REQUIRE_REVIEW" if p0_count else "READY_FOR_CASE_TASK_SELECTION"
    if graph["readiness"] == "PRODUCTION_BLOCKED":
        decision = "PRODUCTION_BLOCKED_REVIEW_REQUIRED"
    return {
        "case_id": case["case_id"],
        "title": case["title"],
        "status": "PASS",
        "decision": decision,
        "graph": graph,
        "task_count": len(tasks),
        "cluster_count": len(clusters),
        "issue_candidate_count": len(issues),
        "p0_count": p0_count,
        "task_clusters": clusters,
        "issue_candidates": issues,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def write_case_md(path: Path, result: Dict[str, Any]) -> None:
    lines = [
        f"# {result['case_id']} — Real/Anonymized Graph Case Result",
        "",
        f"- Status: `{result['status']}`",
        f"- Decision: `{result['decision']}`",
        f"- Readiness: `{result['graph']['readiness']}`",
        f"- Nodes: `{len(result['graph']['nodes'])}`",
        f"- Edges: `{len(result['graph']['edges'])}`",
        f"- Tasks: `{result['task_count']}`",
        f"- Clusters: `{result['cluster_count']}`",
        f"- Issue candidates: `{result['issue_candidate_count']}`",
        f"- P0 blockers: `{result['p0_count']}`",
        "",
        "## Gate Counts",
    ]
    for k, v in result["graph"]["telemetry_summary"]["gate_counts"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines += ["", "## Top Clusters"]
    for c in result["task_clusters"][:8]:
        lines.append(f"- `{c['cluster_id']}` `{c['priority']}` `{c['source_delta']}` / `{c['artifact_type']}` gate `{c['recommended_gate']}` count `{c['task_count']}`")
    write_md(path, lines)

def aggregate(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    gate_counts = Counter()
    delta_counts = Counter()
    priority_counts = Counter()
    for r in results:
        gate_counts.update(r["graph"]["telemetry_summary"]["gate_counts"])
        delta_counts.update(r["graph"]["telemetry_summary"]["delta_counts"])
        priority_counts.update([c["priority"] for c in r["task_clusters"]])
    decision = "READY_FOR_REAL_ANONYMIZED_GRAPH_REVIEW"
    if any(r["decision"] == "PRODUCTION_BLOCKED_REVIEW_REQUIRED" for r in results):
        decision = "PRODUCTION_BLOCKERS_REQUIRE_REVIEW_BEFORE_NEXT_REAL_CASE_BATCH"
    return {
        "status": "PASS",
        "case_count": len(results),
        "decision": decision,
        "aggregate_metrics": {
            "total_nodes": sum(len(r["graph"]["nodes"]) for r in results),
            "total_edges": sum(len(r["graph"]["edges"]) for r in results),
            "total_tasks": sum(r["task_count"] for r in results),
            "total_clusters": sum(r["cluster_count"] for r in results),
            "total_issue_candidates": sum(r["issue_candidate_count"] for r in results),
            "total_p0_blockers": sum(r["p0_count"] for r in results),
            "gate_counts": dict(gate_counts),
            "delta_counts": dict(delta_counts),
            "priority_counts": dict(priority_counts),
        },
        "interpretation": "Real-like anonymized cases produced candidate graphs, telemetry, task clusters and issue candidates without production automation.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

def write_aggregate_md(path: Path, agg: Dict[str, Any]) -> None:
    m = agg["aggregate_metrics"]
    lines = [
        "# PROD-301..320 Real/Anonymized Graph Case Aggregate Report",
        "",
        f"- Status: `{agg['status']}`",
        f"- Cases: `{agg['case_count']}`",
        f"- Decision: `{agg['decision']}`",
        f"- Total nodes: `{m['total_nodes']}`",
        f"- Total edges: `{m['total_edges']}`",
        f"- Total tasks: `{m['total_tasks']}`",
        f"- Total clusters: `{m['total_clusters']}`",
        f"- Total issue candidates: `{m['total_issue_candidates']}`",
        f"- Total P0 blockers: `{m['total_p0_blockers']}`",
        "",
        "## Priority Counts",
    ]
    for k, v in m["priority_counts"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines += ["", "## Gate Counts"]
    for k, v in m["gate_counts"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines += ["", "## Delta Counts"]
    for k, v in m["delta_counts"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines += ["", "## Interpretation", agg["interpretation"]]
    write_md(path, lines)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--cases-dir", default="product/poc/real_anonymized_graph_cases/cases")
    parser.add_argument("--seed", type=int, default=301320)
    parser.add_argument("--max-issues", type=int, default=8)
    args = parser.parse_args()

    repo = Path(args.repo)
    cases_dir = repo / args.cases_dir
    out = repo / "outputs"
    case_paths = sorted(cases_dir.glob("*.json"))
    if not case_paths:
        raise SystemExit(f"no case files found in {cases_dir}")

    results = []
    case_summary_rows = []
    for idx, path in enumerate(case_paths, 1):
        case = read_json(path)
        result = run_case(case, args.seed + idx, args.max_issues)
        results.append(result)
        stem = case["case_id"].lower()
        write_json(out / f"prod301_320_{stem}_result.json", result)
        write_case_md(out / f"prod301_320_{stem}_result.md", result)
        case_summary_rows.append({
            "case_id": result["case_id"],
            "decision": result["decision"],
            "readiness": result["graph"]["readiness"],
            "nodes": len(result["graph"]["nodes"]),
            "edges": len(result["graph"]["edges"]),
            "tasks": result["task_count"],
            "clusters": result["cluster_count"],
            "issue_candidates": result["issue_candidate_count"],
            "p0_count": result["p0_count"],
        })

    agg = aggregate(results)
    write_json(out / "prod301_320_real_graph_case_results.json", {"status": "PASS", "results": results})
    write_json(out / "prod301_320_real_graph_case_aggregate.json", agg)
    write_aggregate_md(out / "prod301_320_real_graph_case_aggregate.md", agg)

    csv_path = out / "prod301_320_real_graph_case_summary.csv"
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(case_summary_rows[0].keys()))
        writer.writeheader()
        writer.writerows(case_summary_rows)

    print(json.dumps({"status": "PASS", "cases": len(results), "decision": agg["decision"], "total_p0": agg["aggregate_metrics"]["total_p0_blockers"]}, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

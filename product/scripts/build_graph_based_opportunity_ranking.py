#!/usr/bin/env python3
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "outputs" / "prod1741_1780_business_solution_ensemble_scoring_model.json"
OUT = ROOT / "outputs"

BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
    "automatic_threshold_mutation",
    "autonomous_external_execution",
    "real_world_side_effect",
    "unapproved_real_company_data",
    "production_neo4j_connection",
    "production_graph_write",
    "final_answer_generation_without_boundary",
    "gpt_call",
    "codex_execution",
    "public_api_publication",
    "custom_gpt_connection_without_human_approval",
    "final_threshold_calibration",
    "final_weight_calibration"
]

def node_id(kind, value):
    safe = str(value).strip().replace(" ", "_").replace("/", "_").replace("-", "_")
    return f"{kind}:{safe}"

def add_node(nodes, kind, value, attrs=None):
    nid = node_id(kind, value)
    if nid not in nodes:
        nodes[nid] = {
            "id": nid,
            "kind": kind,
            "label": value,
            "case_count": 0,
            "score_sum": 0.0,
            "score_avg": 0.0,
            "attrs": attrs or {}
        }
    return nid

def add_edge(edges, src, rel, dst, weight=1.0, attrs=None):
    key = (src, rel, dst)
    if key not in edges:
        edges[key] = {
            "source": src,
            "relationship": rel,
            "target": dst,
            "weight": 0.0,
            "attrs": attrs or {}
        }
    edges[key]["weight"] += weight

def avg(values):
    return round(sum(values) / len(values), 2) if values else 0.0

def rank_group(cases, key):
    groups = defaultdict(list)
    for c in cases:
        groups[c[key]].append(c)

    ranked = []
    for value, items in groups.items():
        opportunity_values = [i["ensemble"]["casulo_opportunity_score"] for i in items]
        hallu_values = [i["ensemble"]["scores"]["hallucination_reduction_potential"] for i in items]
        governance_values = [i["ensemble"]["scores"]["governance_pressure_score"] for i in items]
        monitoring_values = [i["ensemble"]["scores"]["monitoring_recurrence_score"] for i in items]
        commercial_values = [i["ensemble"]["scores"]["commercial_value_proxy"] for i in items]

        graph_strength = (
            avg(opportunity_values) * 0.35
            + avg(hallu_values) * 0.20
            + avg(governance_values) * 0.15
            + avg(monitoring_values) * 0.15
            + avg(commercial_values) * 0.15
        )

        ranked.append({
            key: value,
            "case_count": len(items),
            "avg_opportunity_score": avg(opportunity_values),
            "avg_hallucination_reduction_potential": avg(hallu_values),
            "avg_governance_pressure_score": avg(governance_values),
            "avg_monitoring_recurrence_score": avg(monitoring_values),
            "avg_commercial_value_proxy": avg(commercial_values),
            "graph_strength_score": round(graph_strength, 2)
        })

    return sorted(ranked, key=lambda x: x["graph_strength_score"], reverse=True)

def classify(score):
    if score >= 85:
        return "very_high"
    if score >= 70:
        return "high"
    if score >= 50:
        return "medium"
    if score >= 30:
        return "low"
    return "very_low"

def main():
    if not SOURCE.exists():
        raise SystemExit(f"Missing source ensemble output: {SOURCE}")

    source = json.loads(SOURCE.read_text(encoding="utf-8"))
    cases = source.get("cases", [])

    nodes = {}
    edges = {}

    for c in cases:
        score = c["ensemble"]["casulo_opportunity_score"]
        scores = c["ensemble"]["scores"]

        case_node = add_node(nodes, "Case", c["id"], {
            "opportunity_score": score,
            "opportunity_band": c["ensemble"]["opportunity_band"]
        })
        package_node = add_node(nodes, "ServicePackage", c["service_package"])
        company_node = add_node(nodes, "CompanyProfile", c["company_profile"])
        maturity_node = add_node(nodes, "CompanyMaturity", c["company_maturity"])
        solution_node = add_node(nodes, "SolutionType", c["solution_type"])
        recommendation_node = add_node(nodes, "RecommendationType", c["recommendation_type"])
        monitoring_node = add_node(nodes, "MonitoringNeed", c["monitoring_need"])
        governance_node = add_node(nodes, "GovernanceNeed", c["governance_need"])
        stack_node = add_node(nodes, "StackDependency", c["stack_dependency"])
        mode_node = add_node(nodes, "RecommendedMode", c["ensemble"]["recommended_mode"])

        for gate in c["ensemble"]["hard_gates"]:
            gate_node = add_node(nodes, "Gate", gate)
            add_edge(edges, case_node, "REQUIRES_GATE", gate_node, score)

        add_edge(edges, company_node, "HAS_CASE", case_node, score)
        add_edge(edges, case_node, "USES_PACKAGE", package_node, score)
        add_edge(edges, case_node, "HAS_MATURITY", maturity_node, score)
        add_edge(edges, case_node, "SUGGESTS_SOLUTION", solution_node, score)
        add_edge(edges, case_node, "HAS_RECOMMENDATION", recommendation_node, score)
        add_edge(edges, case_node, "NEEDS_MONITORING", monitoring_node, scores["monitoring_recurrence_score"])
        add_edge(edges, case_node, "HAS_GOVERNANCE_NEED", governance_node, scores["governance_pressure_score"])
        add_edge(edges, case_node, "DEPENDS_ON_STACK", stack_node, scores["stack_dependency_score"])
        add_edge(edges, case_node, "RECOMMENDS_MODE", mode_node, score)

        for nid in [
            case_node,
            package_node,
            company_node,
            maturity_node,
            solution_node,
            recommendation_node,
            monitoring_node,
            governance_node,
            stack_node,
            mode_node
        ]:
            nodes[nid]["case_count"] += 1
            nodes[nid]["score_sum"] += score

    for node in nodes.values():
        if node["case_count"]:
            node["score_avg"] = round(node["score_sum"] / node["case_count"], 2)

    edge_list = list(edges.values())
    node_list = list(nodes.values())

    node_degree = defaultdict(float)
    for e in edge_list:
        node_degree[e["source"]] += e["weight"]
        node_degree[e["target"]] += e["weight"]

    central_nodes = []
    for n in node_list:
        centrality = round(node_degree[n["id"]], 2)
        central_nodes.append({
            "id": n["id"],
            "kind": n["kind"],
            "label": n["label"],
            "weighted_degree": centrality,
            "score_avg": n["score_avg"],
            "case_count": n["case_count"],
            "centrality_band": classify(centrality)
        })

    central_nodes = sorted(central_nodes, key=lambda x: x["weighted_degree"], reverse=True)

    case_ranking = []
    for c in sorted(cases, key=lambda x: x["ensemble"]["casulo_opportunity_score"], reverse=True):
        s = c["ensemble"]["scores"]
        case_ranking.append({
            "id": c["id"],
            "company_profile": c["company_profile"],
            "service_package": c["service_package"],
            "casulo_opportunity_score": c["ensemble"]["casulo_opportunity_score"],
            "opportunity_band": c["ensemble"]["opportunity_band"],
            "recommended_mode": c["ensemble"]["recommended_mode"],
            "hard_gates": c["ensemble"]["hard_gates"],
            "hallucination_reduction_potential": s["hallucination_reduction_potential"],
            "governance_pressure_score": s["governance_pressure_score"],
            "monitoring_recurrence_score": s["monitoring_recurrence_score"],
            "commercial_value_proxy": s["commercial_value_proxy"]
        })

    rankings = {
        "cases": case_ranking,
        "service_packages": rank_group(cases, "service_package"),
        "company_profiles": rank_group(cases, "company_profile"),
        "solution_types": rank_group(cases, "solution_type"),
        "recommended_modes": rank_group(cases, "service_package"),
        "central_nodes": central_nodes[:15]
    }

    graph = {
        "mode": "in_memory_graph_projection_no_production_write",
        "node_count": len(node_list),
        "edge_count": len(edge_list),
        "node_kinds": sorted({n["kind"] for n in node_list}),
        "relationship_types": sorted({e["relationship"] for e in edge_list}),
        "top_central_nodes": central_nodes[:10],
        "calibration_status": "NOT_CALIBRATED_GRAPH_RANKING_ONLY"
    }

    checks = {
        "source_ensemble_exists": SOURCE.exists(),
        "source_ensemble_status_pass": source.get("status") == "PASS",
        "case_count": len(cases),
        "node_count": len(node_list),
        "edge_count": len(edge_list),
        "has_case_ranking": len(rankings["cases"]) == len(cases),
        "has_service_package_ranking": len(rankings["service_packages"]) >= 5,
        "has_company_profile_ranking": len(rankings["company_profiles"]) >= 5,
        "has_solution_type_ranking": len(rankings["solution_types"]) >= 5,
        "has_central_nodes": len(rankings["central_nodes"]) > 0,
        "no_production_graph_write": True,
        "calibration_status": "NOT_CALIBRATED_GRAPH_RANKING_ONLY"
    }

    errors = []
    if not checks["source_ensemble_exists"]:
        errors.append("Missing source ensemble output")
    if not checks["source_ensemble_status_pass"]:
        errors.append("Source ensemble is not PASS")
    if len(cases) < 7:
        errors.append("Expected at least 7 cases")
    if len(node_list) < 30:
        errors.append("Expected at least 30 graph nodes")
    if len(edge_list) < 50:
        errors.append("Expected at least 50 graph edges")

    status = "PASS" if not errors else "FAIL"
    decision = "GRAPH_BASED_OPPORTUNITY_RANKING_READY" if status == "PASS" else "GRAPH_BASED_OPPORTUNITY_RANKING_NOT_READY"

    result = {
        "status": status,
        "phase": "PROD-1781..1820",
        "decision": decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "graph": graph,
        "rankings": rankings,
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED_ACTIONS
    }

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "prod1781_1820_graph_based_opportunity_ranking.json"
    md_path = OUT / "prod1781_1820_graph_based_opportunity_ranking.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PROD-1781..1820 Graph-Based Opportunity Ranking",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{decision}`",
        f"- Node count: `{graph['node_count']}`",
        f"- Edge count: `{graph['edge_count']}`",
        f"- Calibration: `{graph['calibration_status']}`",
        "",
        "## Node Kinds"
    ]
    for kind in graph["node_kinds"]:
        md.append(f"- {kind}")

    md += ["", "## Relationship Types"]
    for rel in graph["relationship_types"]:
        md.append(f"- {rel}")

    md += ["", "## Case Ranking"]
    for item in case_ranking:
        md += [
            f"### {item['id']}",
            f"- Company profile: `{item['company_profile']}`",
            f"- Service package: `{item['service_package']}`",
            f"- CASULO opportunity score: `{item['casulo_opportunity_score']}`",
            f"- Opportunity band: `{item['opportunity_band']}`",
            f"- Recommended mode: `{item['recommended_mode']}`",
            f"- Hard gates: `{', '.join(item['hard_gates'])}`",
            f"- Hallucination reduction potential: `{item['hallucination_reduction_potential']}`",
            f"- Governance pressure score: `{item['governance_pressure_score']}`",
            f"- Monitoring recurrence score: `{item['monitoring_recurrence_score']}`",
            f"- Commercial value proxy: `{item['commercial_value_proxy']}`",
            ""
        ]

    md += ["## Service Package Ranking"]
    for item in rankings["service_packages"]:
        md += [
            f"### {item['service_package']}",
            f"- Case count: `{item['case_count']}`",
            f"- Avg opportunity score: `{item['avg_opportunity_score']}`",
            f"- Avg hallucination reduction potential: `{item['avg_hallucination_reduction_potential']}`",
            f"- Graph strength score: `{item['graph_strength_score']}`",
            ""
        ]

    md += ["## Top Central Nodes"]
    for item in rankings["central_nodes"][:10]:
        md += [
            f"### {item['id']}",
            f"- Kind: `{item['kind']}`",
            f"- Label: `{item['label']}`",
            f"- Weighted degree: `{item['weighted_degree']}`",
            f"- Score avg: `{item['score_avg']}`",
            f"- Centrality band: `{item['centrality_band']}`",
            ""
        ]

    md += ["## Checks"]
    for key, value in checks.items():
        md.append(f"- {key}: `{value}`")

    md += ["", "## Errors"]
    if errors:
        for err in errors:
            md.append(f"- {err}")
    else:
        md.append("- None")

    md += [
        "",
        "## Boundary",
        "- In-memory graph projection only.",
        "- No production graph write.",
        "- No final calibration.",
        "- No GPT connection.",
        "- No GPT call.",
        "- No Codex execution.",
        "- No production connection.",
        "",
        "## Blocked Actions"
    ]
    for action in BLOCKED_ACTIONS:
        md.append(f"- {action}")

    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

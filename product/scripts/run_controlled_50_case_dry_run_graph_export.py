#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

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
    "live_graph_database_write",
    "neo4j_connection",
]

EVIDENCE_LIBRARY = {
    "complete_minimum_evidence": ["case_summary", "current_state", "operational_log", "supporting_document", "review_note"],
    "partial_evidence": ["case_summary", "current_state"],
    "conflicting_evidence": ["case_summary", "source_a_value", "source_b_value", "conflict_note"],
    "stale_evidence": ["case_summary", "old_report", "stale_timestamp_note"],
    "high_sensitivity_evidence": ["case_summary", "sensitive_context", "restricted_note"],
}

def load_json(path: Path, fallback: Any) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return fallback

def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")

def load_runner_module(repo: Path):
    runner_path = repo / "product/scripts/run_business_case_interactive_runner.py"
    if not runner_path.exists():
        raise SystemExit("Missing product/scripts/run_business_case_interactive_runner.py")
    spec = importlib.util.spec_from_file_location("business_runner", runner_path)
    if spec is None or spec.loader is None:
        raise SystemExit("Unable to load business runner module")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

def to_runner_case(candidate: Dict[str, Any]) -> Dict[str, Any]:
    domain = candidate["business_domain"]
    theme = candidate["risk_theme"]
    profile = candidate["evidence_profile"]
    evidence = EVIDENCE_LIBRARY.get(profile, ["case_summary"])
    problem = f"{domain} synthetic dry-run case for {theme} with {profile}."
    known = [f"domain={domain}", f"risk_theme={theme}", f"evidence_profile={profile}"]
    assumptions = ["dry-run only", "no external execution", "no production activation"]
    desired = "gerar diagnóstico e recomendações sem executar ações externas"

    if theme == "missing_evidence":
        problem += " Evidência incompleta exige coleta adicional antes da decisão."
        desired = "pedir evidências faltantes sem executar ações externas"
        evidence = evidence[:2]
    elif theme == "conflicting_information":
        problem += " Há conflito entre fontes e a decisão precisa ser revisada."
        assumptions.append("fontes podem divergir")
        desired = "mapear conflitos e recomendar revisão humana"
    elif theme == "high_stakes_review":
        problem += " Há risco alto, sensibilidade ou impacto de negócio relevante."
        desired = "preparar pacote de revisão humana"
    elif theme == "direct_execution_block":
        problem += " O solicitante pede execução externa automática."
        desired = "aprovar automaticamente e enviar ação externa"
    elif theme == "graph_traceability_probe":
        problem += " O foco é exigir rastreabilidade em grafo entre caso, evidência, gate e decisão."
        desired = "gerar resposta rastreável sem conexão Neo4j"
    elif theme == "clean_controlled_answer":
        problem += " Dados suficientes para resposta controlada."
        desired = "responder com orientação controlada sem executar ações externas"

    return {
        "case_id": candidate["case_id"],
        "business_domain": domain,
        "problem_summary": problem,
        "available_evidence": evidence,
        "known_facts": known,
        "assumptions": assumptions,
        "desired_decision_support": desired,
        "consent_scope": "synthetic_design_only",
        "data_sensitivity": "high" if profile == "high_sensitivity_evidence" else "medium",
        "source_mode": candidate.get("source_mode", "synthetic_design_only"),
        "risk_theme": theme,
        "evidence_profile": profile,
    }

def distribution(values: List[str]) -> Dict[str, int]:
    d: Dict[str, int] = defaultdict(int)
    for value in values:
        d[str(value)] += 1
    return dict(sorted(d.items()))

def node(node_id: str, label: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    return {"id": node_id, "label": label, "properties": properties}

def rel(rel_id: str, rel_type: str, source: str, target: str, properties: Dict[str, Any]) -> Dict[str, Any]:
    return {"id": rel_id, "type": rel_type, "from": source, "to": target, "properties": properties}

def build_graph_export(runs: List[Dict[str, Any]], readiness_decision: str) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    nodes: Dict[str, Dict[str, Any]] = {}
    relationships: Dict[str, Dict[str, Any]] = {}

    nodes["readiness:" + readiness_decision] = node(
        "readiness:" + readiness_decision,
        "ReadinessState",
        {"decision": readiness_decision}
    )

    for run in runs:
        case = run["input"]
        decision = run["decision"]
        preflight = run["preflight"]
        budget = run["hallucination_budget"]
        case_id = run["case_id"]
        domain = case["business_domain"]
        risk_theme = case.get("risk_theme")
        evidence_profile = case.get("evidence_profile")
        gate = decision.get("gate")
        output_mode = decision.get("output_mode")

        case_node = "case:" + case_id
        domain_node = "domain:" + domain
        evidence_node = "evidence:" + case_id + ":" + evidence_profile
        risk_node = "risk:" + case_id + ":" + risk_theme
        gate_node = "gate:" + case_id + ":" + gate
        output_node = "output:" + case_id + ":" + output_mode
        budget_node = "budget:" + case_id

        nodes[case_node] = node(case_node, "Case", {
            "case_id": case_id,
            "business_domain": domain,
            "risk_theme": risk_theme,
            "evidence_profile": evidence_profile,
            "source_mode": case.get("source_mode"),
        })
        nodes[domain_node] = node(domain_node, "Domain", {
            "business_domain": domain,
            "activation_state": preflight.get("activation_state"),
            "preflight_score": preflight.get("preflight_score"),
        })
        nodes[evidence_node] = node(evidence_node, "Evidence", {
            "case_id": case_id,
            "evidence_profile": evidence_profile,
            "evidence_count": len(case.get("available_evidence", [])),
        })
        nodes[risk_node] = node(risk_node, "RiskSignal", {
            "case_id": case_id,
            "risk_theme": risk_theme,
            "adjusted_risk": decision.get("adjusted_risk"),
            "risk_band": decision.get("risk_band"),
            "live_delta_score": decision.get("live_delta_score"),
        })
        nodes[gate_node] = node(gate_node, "Gate", {
            "case_id": case_id,
            "gate": gate,
        })
        nodes[output_node] = node(output_node, "OutputMode", {
            "case_id": case_id,
            "output_mode": output_mode,
        })
        nodes[budget_node] = node(budget_node, "HallucinationBudget", {
            "case_id": case_id,
            "hallucination_budget": budget.get("hallucination_budget"),
            "reasoning_mode": budget.get("reasoning_mode"),
        })

        pairs = [
            (case_node, "BELONGS_TO", domain_node),
            (case_node, "HAS_EVIDENCE", evidence_node),
            (case_node, "TRIGGERS", risk_node),
            (risk_node, "CONTRIBUTES_TO", gate_node),
            (gate_node, "ALLOWS", output_node),
            (case_node, "HAS_BUDGET", budget_node),
            (case_node, "REQUIRES", "readiness:" + readiness_decision),
        ]
        for idx, (source, typ, target) in enumerate(pairs, start=1):
            rel_id = f"{source}:{typ}:{target}"
            relationships[rel_id] = rel(rel_id, typ, source, target, {"case_id": case_id})

    return list(nodes.values()), list(relationships.values())

def select_diagnostics(runs: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    by_theme = {run["input"].get("risk_theme"): run for run in runs}
    selected_ids = []
    for theme in ["clean_controlled_answer", "conflicting_information", "direct_execution_block", "graph_traceability_probe"]:
        if theme in by_theme:
            selected_ids.append(by_theme[theme]["case_id"])
    selected = [run for run in runs if run["case_id"] in selected_ids[:3]]
    if len(selected) < 3:
        selected = runs[:3]
    diagnostics = []
    for run in selected:
        decision = run["decision"]
        case = run["input"]
        diagnostics.append({
            "case_id": run["case_id"],
            "business_domain": case.get("business_domain"),
            "risk_theme": case.get("risk_theme"),
            "evidence_profile": case.get("evidence_profile"),
            "gate": decision.get("gate"),
            "output_mode": decision.get("output_mode"),
            "adjusted_risk": decision.get("adjusted_risk"),
            "risk_band": decision.get("risk_band"),
            "live_delta_score": decision.get("live_delta_score"),
            "preflight_score": run["preflight"].get("preflight_score"),
            "hallucination_budget": run["hallucination_budget"].get("hallucination_budget"),
            "business_interpretation": "candidate selected for executive diagnostic report",
        })
    return diagnostics

def build(repo: Path) -> Dict[str, Any]:
    out = repo / "outputs"
    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()

    upstream = load_json(out / "prod901_940_expansion_readiness.json", {})
    upstream_ready = upstream.get("decision") == "READY_FOR_CONTROLLED_50_CASE_DRY_RUN_AND_GRAPH_EXPORT_STUB"

    pack = load_json(out / "prod901_940_controlled_50_case_candidate_pack.json", {})
    candidates = pack.get("cases", [])
    if len(candidates) != 50:
        raise SystemExit("Expected 50 cases from PROD-901 candidate pack.")

    runner = load_runner_module(repo)
    runnable_cases = [to_runner_case(candidate) for candidate in candidates]
    runs = [runner.run_case(case) for case in runnable_cases]

    gates = distribution([run["decision"].get("gate") for run in runs])
    output_modes = distribution([run["decision"].get("output_mode") for run in runs])
    risk_bands = distribution([run["decision"].get("risk_band") for run in runs])
    domains = distribution([run["input"].get("business_domain") for run in runs])
    themes = distribution([run["input"].get("risk_theme") for run in runs])
    reasoning = distribution([run["hallucination_budget"].get("reasoning_mode") for run in runs])

    risks = [float(run["decision"].get("adjusted_risk", 0)) for run in runs]
    deltas = [float(run["decision"].get("live_delta_score", 0)) for run in runs]

    readiness_decision = (
        "READY_FOR_BUSINESS_DIAGNOSTIC_REPORT_AND_GRAPH_ADAPTER_BOUNDARY"
        if upstream_ready and len(runs) == 50
        else "REVIEW_50_CASE_DRY_RUN"
    )

    graph_nodes, graph_relationships = build_graph_export(runs, readiness_decision)

    nodes_path = out / "prod941_980_graph_export_nodes.jsonl"
    rels_path = out / "prod941_980_graph_export_relationships.jsonl"
    nodes_path.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in graph_nodes), encoding="utf-8")
    rels_path.write_text("".join(json.dumps(item, ensure_ascii=False) + "\n" for item in graph_relationships), encoding="utf-8")

    status = {
        "status": "PASS" if readiness_decision.startswith("READY") else "WARN",
        "generated_at": generated_at,
        "phase": "Controlled 50-Case Dry-Run Simulation and Graph Export Stub",
        "mode": "dry_run_only_no_execution",
        "case_count": len(runs),
        "gate_distribution": gates,
        "output_mode_distribution": output_modes,
        "risk_band_distribution": risk_bands,
        "domain_distribution": domains,
        "risk_theme_distribution": themes,
        "reasoning_mode_distribution": reasoning,
        "min_adjusted_risk": round(min(risks), 4),
        "avg_adjusted_risk": round(sum(risks) / len(risks), 4),
        "max_adjusted_risk": round(max(risks), 4),
        "min_live_delta_score": round(min(deltas), 4),
        "avg_live_delta_score": round(sum(deltas) / len(deltas), 4),
        "max_live_delta_score": round(max(deltas), 4),
        "external_execution_allowed": False,
        "graph_write_allowed": False,
        "neo4j_connection_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "auto_apply": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    graph_summary = {
        "status": "PASS",
        "mode": "graph_export_stub_no_connection",
        "node_count": len(graph_nodes),
        "relationship_count": len(graph_relationships),
        "node_label_distribution": distribution([item["label"] for item in graph_nodes]),
        "relationship_type_distribution": distribution([item["type"] for item in graph_relationships]),
        "nodes_jsonl": "outputs/prod941_980_graph_export_nodes.jsonl",
        "relationships_jsonl": "outputs/prod941_980_graph_export_relationships.jsonl",
        "neo4j_connection_allowed": False,
        "live_graph_database_write_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

    diagnostics = {
        "status": "PASS",
        "selected_case_count": 3,
        "selection_policy": "represent clean answer, conflict/review, and direct execution block or traceability",
        "cases": select_diagnostics(runs),
        "blocked_actions": BLOCKED_ACTIONS,
    }

    recommendations = {
        "status": "PASS",
        "auto_apply": False,
        "automatic_threshold_mutation_allowed": False,
        "recommendations": [
            {
                "id": "DRYRUN-CAL-001",
                "target": "business_diagnostic_report",
                "recommendation": "Generate executive-operational diagnostic report using 2-3 selected cases and consolidated telemetry.",
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "DRYRUN-CAL-002",
                "target": "graph_adapter_boundary",
                "recommendation": "Review graph JSONL export shape before any Neo4j connector or live write is implemented.",
                "auto_apply": False,
                "requires_human_approval": True,
            },
            {
                "id": "DRYRUN-CAL-003",
                "target": "pilot_policy",
                "recommendation": "Keep all real pilot data anonymized and explicitly approved; no client-facing claims.",
                "auto_apply": False,
                "requires_human_approval": True,
            },
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness = {
        "status": "PASS" if readiness_decision.startswith("READY") else "WARN",
        "decision": readiness_decision,
        "case_count": len(runs),
        "ready_for": [
            "business diagnostic report generation",
            "graph adapter boundary design",
            "non-live Neo4j import review",
            "controlled pilot evidence pack planning",
        ],
        "not_ready_for": [
            "production activation",
            "autonomous external execution",
            "automatic threshold mutation",
            "client-facing guarantees",
            "live Neo4j connection",
            "live graph database write",
            "unapproved real company data",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS" if readiness["status"] == "PASS" else "WARN",
        "audit": "Controlled 50-Case Dry-Run Simulation and Graph Export Stub audit",
        "case_count": len(runs),
        "graph_node_count": len(graph_nodes),
        "graph_relationship_count": len(graph_relationships),
        "external_execution_allowed": False,
        "graph_write_allowed": False,
        "neo4j_connection_allowed": False,
        "automatic_threshold_mutation_allowed": False,
        "auto_apply": False,
        "finding": "PASS: 50-case dry-run completed and graph export stubs generated without execution, threshold mutation or live graph connection.",
        "readiness": readiness["decision"],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    outputs = {
        "prod941_980_50_case_dry_run_status.json": status,
        "prod941_980_50_case_runnable_cases.json": {
            "status": "PASS",
            "case_count": len(runnable_cases),
            "cases": runnable_cases,
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "prod941_980_50_case_dry_run_runs.json": {
            "status": "PASS",
            "case_count": len(runs),
            "runs": runs,
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "prod941_980_50_case_dry_run_decisions.json": {
            "status": "PASS",
            "decisions": [{"case_id": run["case_id"], **run["decision"]} for run in runs],
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "prod941_980_graph_export_summary.json": graph_summary,
        "prod941_980_business_diagnostic_selection.json": diagnostics,
        "prod941_980_dry_run_recommendations.json": recommendations,
        "prod941_980_dry_run_readiness.json": readiness,
        "prod941_980_dry_run_audit_report.json": audit,
    }

    for name, obj in outputs.items():
        write_json(out / name, obj)

    report = [
        "# PROD-941..980 Controlled 50-Case Dry-Run Simulation and Graph Export Stub",
        "",
        f"- Status: `{audit['status']}`",
        f"- Case count: `{len(runs)}`",
        f"- Graph node count: `{len(graph_nodes)}`",
        f"- Graph relationship count: `{len(graph_relationships)}`",
        f"- Decision: `{readiness['decision']}`",
        f"- External execution allowed: `False`",
        f"- Graph write allowed: `False`",
        f"- Neo4j connection allowed: `False`",
        f"- Automatic threshold mutation allowed: `False`",
        "",
        "## Gate Distribution",
    ]
    for key, value in gates.items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Risk Band Distribution"]
    for key, value in risk_bands.items():
        report.append(f"- `{key}`: `{value}`")
    report += ["", "## Risk Telemetry"]
    report.append(f"- Adjusted risk min/avg/max: `{status['min_adjusted_risk']}` / `{status['avg_adjusted_risk']}` / `{status['max_adjusted_risk']}`")
    report.append(f"- Live delta min/avg/max: `{status['min_live_delta_score']}` / `{status['avg_live_delta_score']}` / `{status['max_live_delta_score']}`")
    report += ["", "## Graph Export Stub"]
    report.append(f"- Nodes JSONL: `{graph_summary['nodes_jsonl']}`")
    report.append(f"- Relationships JSONL: `{graph_summary['relationships_jsonl']}`")
    report.append(f"- Node count: `{graph_summary['node_count']}`")
    report.append(f"- Relationship count: `{graph_summary['relationship_count']}`")
    report += ["", "## Diagnostic Cases"]
    for item in diagnostics["cases"]:
        report.append(f"- `{item['case_id']}` `{item['business_domain']}` `{item['risk_theme']}` gate `{item['gate']}` risk `{item['adjusted_risk']}` band `{item['risk_band']}`")
    report += ["", "## Next Recommended Bundle", "- `PROD-981 Business Diagnostic Report Pack and Graph Adapter Boundary`"]
    write_text(out / "prod941_980_50_case_dry_run_graph_export_report.md", "\n".join(report) + "\n")

    result = {
        "task": "PROD-941..980",
        "status": audit["status"],
        "phase": "Controlled 50-Case Dry-Run Simulation and Graph Export Stub",
        "decision": readiness["decision"],
        "outputs": ["outputs/" + key for key in outputs.keys()] + [
            "outputs/prod941_980_graph_export_nodes.jsonl",
            "outputs/prod941_980_graph_export_relationships.jsonl",
        ],
        "next_recommended_bundle": "PROD-981 Business Diagnostic Report Pack and Graph Adapter Boundary",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod941_980_result.json", result)
    write_text(out / "prod941_980_report.md", "# PROD-941..980 Report\n\n" + json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    return result

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    result = build(Path(args.repo))
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

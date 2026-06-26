"""CASULO Workbench Cockpit State Engine v0.3.

Builds a contracted cockpit_state payload from existing CASULO state artifacts.
The Cubo/Cupula UI must consume this contracted view instead of ad-hoc files.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from api.services.casulo_workbench_engine import (
    DEFAULT_STABLE_TS,
    build_case_artifacts,
    list_case_names,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "runtime_outputs" / "cockpit_states"


def _domain_weight(domain: Dict[str, Any], fragility: Dict[str, Any]) -> float:
    risk_count = len(domain.get("risks", []))
    data_gap = 1.0 - float(domain.get("data_quality", 0.0))
    confidence_gap = 1.0 - float(domain.get("state_confidence", 0.0))
    frag = float(fragility.get("h_pre", 0.0))
    weight = (data_gap * 0.35) + (confidence_gap * 0.25) + (min(1.0, risk_count / 4) * 0.20) + (frag * 0.20)
    return round(max(0.0, min(1.0, weight)), 3)


def _priority_label(weight: float) -> str:
    if weight >= 0.70:
        return "CRITICAL"
    if weight >= 0.50:
        return "ATTENTION"
    if weight >= 0.30:
        return "WATCH"
    return "STABLE"


def build_cockpit_state(case_name: str, generated_at: Optional[str] = None) -> Dict[str, Any]:
    artifacts = build_case_artifacts(case_name, generated_at=generated_at or DEFAULT_STABLE_TS)
    snapshot = artifacts["state_snapshot"]
    graph = artifacts["graph"]
    fragility = artifacts["fragility"]
    dq = artifacts["data_quality"]

    domain_cards: List[Dict[str, Any]] = []
    for domain in artifacts["domains"]:
        weight = _domain_weight(domain, fragility)
        domain_cards.append({
            "id": domain["id"],
            "name": domain["name"],
            "data_quality": domain["data_quality"],
            "state_confidence": domain["state_confidence"],
            "gravity_weight": weight,
            "priority": _priority_label(weight),
            "risks": domain.get("risks", []),
            "branches": domain.get("branches", []),
        })

    domain_cards.sort(key=lambda item: item["gravity_weight"], reverse=True)

    cube_faces = {
        "objective": artifacts["case"].get("objective", "not defined"),
        "evidence": {
            "data_quality": dq["overall_score"],
            "label": dq["overall_label"],
            "sources": len(dq.get("sources", [])),
        },
        "risks": {
            "h_pre": fragility["h_pre"],
            "h_post": fragility["h_post"],
            "decision": fragility["decision"],
        },
        "tasks": [
            {
                "delta_id": gate["delta_id"],
                "title": gate["delta_title"],
                "package": gate["solution_package"],
            }
            for gate in artifacts["gates"]
        ],
        "deltas": [
            {
                "delta_id": gate["delta_id"],
                "title": gate["delta_title"],
                "expected_metric": gate["expected_metric"],
            }
            for gate in artifacts["gates"]
        ],
        "gates": artifacts["gates"],
    }

    state = {
        "contract_version": "workbench.cockpit_state.v0.3",
        "generated_at": snapshot["generated_at"],
        "case": snapshot["case"],
        "summary": {
            "data_quality": dq["overall_score"],
            "data_quality_label": dq["overall_label"],
            "h_pre": fragility["h_pre"],
            "h_post": fragility["h_post"],
            "delta_l": fragility["delta_l"],
            "decision": fragility["decision"],
            "state_confidence": fragility["state_confidence"],
            "domains": len(domain_cards),
            "gates": len(artifacts["gates"]),
            "graph_nodes": len(graph.get("nodes", [])),
            "graph_edges": len(graph.get("edges", [])),
        },
        "gravitational_dome": {
            "description": "Domains ranked by operational gravity.",
            "domains": domain_cards,
        },
        "operational_cube": {
            "faces": cube_faces,
        },
        "chat_axial": {
            "allowed_intents": [
                "explain_state",
                "explain_gate",
                "list_fragile_domains",
                "request_more_evidence",
                "generate_codex_task",
            ],
            "source_of_truth": [
                "state_snapshot",
                "graph",
                "contracts",
                "ledger",
                "diagnostic_report",
            ],
        },
        "graph_projection": {
            "nodes": graph.get("nodes", []),
            "edges": graph.get("edges", []),
        },
    }
    return state


def validate_cockpit_state(state: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    required = {
        "contract_version",
        "generated_at",
        "case",
        "summary",
        "gravitational_dome",
        "operational_cube",
        "chat_axial",
        "graph_projection",
    }
    missing = sorted(required - set(state))
    if missing:
        errors.append(f"missing top-level keys: {missing}")
    if state.get("contract_version") != "workbench.cockpit_state.v0.3":
        errors.append("invalid contract_version")
    summary = state.get("summary", {})
    for key in ["data_quality", "h_pre", "h_post", "delta_l", "decision", "state_confidence"]:
        if key not in summary:
            errors.append(f"summary missing: {key}")
    domains = state.get("gravitational_dome", {}).get("domains", [])
    if not domains:
        errors.append("gravitational_dome.domains must not be empty")
    faces = state.get("operational_cube", {}).get("faces", {})
    for face in ["objective", "evidence", "risks", "tasks", "deltas", "gates"]:
        if face not in faces:
            errors.append(f"operational_cube.faces missing: {face}")
    graph = state.get("graph_projection", {})
    if not graph.get("nodes") or not graph.get("edges"):
        errors.append("graph_projection requires nodes and edges")
    return errors


def write_cockpit_state(case_name: str, output_root: Path = DEFAULT_OUTPUT_ROOT, stable_time: bool = True) -> Path:
    state = build_cockpit_state(case_name, generated_at=DEFAULT_STABLE_TS if stable_time else None)
    errors = validate_cockpit_state(state)
    if errors:
        raise ValueError(f"invalid cockpit state for {case_name}: {errors}")
    output_root.mkdir(parents=True, exist_ok=True)
    path = output_root / f"{case_name}_cockpit_state.json"
    path.write_text(json.dumps(state, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def build_all_cockpit_states(write: bool = False, output_root: Path = DEFAULT_OUTPUT_ROOT, stable_time: bool = True) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []
    for case_name in list_case_names():
        state = build_cockpit_state(case_name, generated_at=DEFAULT_STABLE_TS if stable_time else None)
        errors = validate_cockpit_state(state)
        item = {
            "case_name": case_name,
            "case_id": state.get("case", {}).get("case_id"),
            "decision": state.get("summary", {}).get("decision"),
            "data_quality": state.get("summary", {}).get("data_quality"),
            "h_pre": state.get("summary", {}).get("h_pre"),
            "domains": state.get("summary", {}).get("domains"),
            "gates": state.get("summary", {}).get("gates"),
            "errors": errors,
        }
        if write and not errors:
            out = write_cockpit_state(case_name, output_root=output_root, stable_time=stable_time)
            item["written"] = str(out)
        results.append(item)
    return results

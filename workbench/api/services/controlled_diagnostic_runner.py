"""CASULO Workbench Controlled Diagnostic Runner v0.5.

Runs the first controlled test flow:

real_intake
-> evidence_manifest
-> controlled_case
-> diagnostic artifacts
-> cockpit_state
-> codex_task
-> controlled_diagnostic_result

Default mode is check-only through scripts. Write mode must be explicit.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

from api.services.casulo_workbench_engine import (
    DEFAULT_STABLE_TS,
    build_graph,
    codex_task_markdown,
    compute_data_quality,
    compute_domain_scores,
    compute_fragility,
    compute_gates,
    ledger_events,
    report_markdown,
)
from api.services.cockpit_state_engine import validate_cockpit_state
from api.services.real_intake_engine import (
    build_evidence_manifest,
    export_case_json,
    load_intake,
    validate_intake,
)


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "runtime_outputs" / "controlled_diagnostics"


def _write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _build_diagnostic_artifacts(case: Dict[str, Any], generated_at: str) -> Dict[str, Any]:
    dq = compute_data_quality(case)
    domains = compute_domain_scores(case, dq)
    graph = build_graph(case, domains, dq)
    fragility = compute_fragility(case, domains, dq)
    gates = compute_gates(case, fragility, dq)
    events = ledger_events(case, dq, fragility, gates, generated_at)

    snapshot = {
        "contract_version": "workbench.state_snapshot.v0.2",
        "generated_at": generated_at,
        "case": {
            "case_id": case["case_id"],
            "title": case["title"],
            "vertical": case.get("vertical"),
        },
        "data_quality": dq,
        "domains": domains,
        "fragility": fragility,
        "gates": gates,
    }

    return {
        "case": case,
        "data_quality": dq,
        "domains": domains,
        "graph": graph,
        "fragility": fragility,
        "gates": gates,
        "ledger_events": events,
        "state_snapshot": snapshot,
        "diagnostic_report": report_markdown(case, dq, domains, fragility, gates),
        "codex_task": codex_task_markdown(case, gates, fragility),
    }


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


def build_cockpit_state_from_artifacts(artifacts: Dict[str, Any]) -> Dict[str, Any]:
    case = artifacts["case"]
    dq = artifacts["data_quality"]
    fragility = artifacts["fragility"]
    graph = artifacts["graph"]
    snapshot = artifacts["state_snapshot"]

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

    gates = artifacts["gates"]
    cockpit_state = {
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
            "gates": len(gates),
            "graph_nodes": len(graph.get("nodes", [])),
            "graph_edges": len(graph.get("edges", [])),
        },
        "gravitational_dome": {
            "description": "Domains ranked by operational gravity.",
            "domains": domain_cards,
        },
        "operational_cube": {
            "faces": {
                "objective": case.get("objective", "not defined"),
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
                    for gate in gates
                ],
                "deltas": [
                    {
                        "delta_id": gate["delta_id"],
                        "title": gate["delta_title"],
                        "expected_metric": gate["expected_metric"],
                    }
                    for gate in gates
                ],
                "gates": gates,
            }
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
                "controlled_intake",
                "evidence_manifest",
                "state_snapshot",
                "graph",
                "contracts",
                "diagnostic_report",
            ],
        },
        "graph_projection": {
            "nodes": graph.get("nodes", []),
            "edges": graph.get("edges", []),
        },
    }
    return cockpit_state


def run_controlled_diagnostic(
    intake_path: Path,
    write: bool = False,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    stable_time: bool = True,
) -> Dict[str, Any]:
    generated_at = DEFAULT_STABLE_TS if stable_time else None
    if generated_at is None:
        from api.services.real_intake_engine import utc_now
        generated_at = utc_now()

    intake = load_intake(intake_path)
    intake_errors, intake_warnings = validate_intake(intake)
    manifest = build_evidence_manifest(intake, generated_at=generated_at)

    result: Dict[str, Any] = {
        "contract_version": "workbench.controlled_diagnostic.v0.5",
        "case_id": intake.get("case_id"),
        "case_title": intake.get("case_title"),
        "mode": "write" if write else "check",
        "intake_status": "FAIL" if intake_errors else "PASS",
        "intake_errors": intake_errors,
        "intake_warnings": intake_warnings,
        "manifest_decision": manifest["decision"],
        "generated_outputs": [],
        "blocked": manifest["decision"] == "BLOCK_INTAKE",
    }

    if manifest["decision"] == "BLOCK_INTAKE":
        result["status"] = "FAIL"
        result["reason"] = "intake blocked"
        return result

    controlled_case = export_case_json(intake, manifest)
    artifacts = _build_diagnostic_artifacts(controlled_case, generated_at=generated_at)
    cockpit_state = build_cockpit_state_from_artifacts(artifacts)
    cockpit_errors = validate_cockpit_state(cockpit_state)

    result.update({
        "status": "FAIL" if cockpit_errors else "PASS",
        "cockpit_errors": cockpit_errors,
        "diagnostic": {
            "data_quality": artifacts["data_quality"]["overall_score"],
            "data_quality_label": artifacts["data_quality"]["overall_label"],
            "h_pre": artifacts["fragility"]["h_pre"],
            "h_post": artifacts["fragility"]["h_post"],
            "delta_l": artifacts["fragility"]["delta_l"],
            "decision": artifacts["fragility"]["decision"],
            "domains": len(artifacts["domains"]),
            "gates": len(artifacts["gates"]),
            "graph_nodes": len(artifacts["graph"].get("nodes", [])),
            "graph_edges": len(artifacts["graph"].get("edges", [])),
        },
        "human_review_required": True,
    })

    if write and result["status"] == "PASS":
        case_dir = output_root / intake.get("case_id", "unknown_case")
        case_dir.mkdir(parents=True, exist_ok=True)

        outputs = {
            "evidence_manifest.json": manifest,
            "controlled_case.json": controlled_case,
            "state_snapshot.json": artifacts["state_snapshot"],
            "graph.json": artifacts["graph"],
            "cockpit_state.json": cockpit_state,
            "controlled_diagnostic_result.json": result,
        }
        for filename, data in outputs.items():
            _write_json(case_dir / filename, data)
            result["generated_outputs"].append(str(case_dir / filename))

        (case_dir / "diagnostic_report.md").write_text(artifacts["diagnostic_report"], encoding="utf-8")
        result["generated_outputs"].append(str(case_dir / "diagnostic_report.md"))

        (case_dir / "codex_task.md").write_text(artifacts["codex_task"], encoding="utf-8")
        result["generated_outputs"].append(str(case_dir / "codex_task.md"))

        (case_dir / "ledger.jsonl").write_text(
            "\n".join(json.dumps(e, ensure_ascii=False) for e in artifacts["ledger_events"]) + "\n",
            encoding="utf-8",
        )
        result["generated_outputs"].append(str(case_dir / "ledger.jsonl"))

        _write_json(case_dir / "controlled_diagnostic_result.json", result)

    return result

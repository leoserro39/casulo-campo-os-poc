#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Dict, List


BLOCKED_ACTIONS = [
    "automatic_nomination",
    "client_facing_claim",
    "implementation_execution",
    "production_activation",
]


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_optional_json(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {}
    try:
        return read_json(path)
    except Exception:
        return {"unreadable_json": str(path)}


def evidence_status(import_input: Dict[str, Any]) -> List[Dict[str, Any]]:
    dataset = import_input.get("dataset_or_workbook", {})
    optional = import_input.get("optional_inputs", {})
    evidence = [
        {
            "evidence": "dataset_or_workbook",
            "status": dataset.get("status", "UNKNOWN"),
            "available": bool(dataset.get("path_or_reference")),
        },
        {
            "evidence": "expected_nomination_flow",
            "status": "AVAILABLE" if import_input.get("expected_nomination_flow") else "MISSING",
            "available": bool(import_input.get("expected_nomination_flow")),
        },
        {
            "evidence": "qualification_rules",
            "status": "AVAILABLE" if import_input.get("qualification_rules") else "MISSING",
            "available": bool(import_input.get("qualification_rules")),
        },
        {
            "evidence": "known_blocking_rules",
            "status": "AVAILABLE" if import_input.get("known_blocking_rules") else "MISSING",
            "available": bool(import_input.get("known_blocking_rules")),
        },
    ]
    for key in ["contract_records", "pvq_q88_extract", "certificate_list", "cargo_platform_matrix", "decision_logs", "audit_reports"]:
        value = optional.get(key)
        evidence.append({
            "evidence": key,
            "status": "AVAILABLE" if value else "NOT_PROVIDED",
            "available": bool(value),
        })
    return evidence


def build_state(repo: Path, input_path: Path) -> Dict[str, Any]:
    import_input = read_json(input_path)
    vertical_manifest = read_json(repo / "product/verticals/vesselflow/vertical_manifest.json")
    domain_map = read_json(repo / "product/verticals/vesselflow/domain_map.json")
    gate_map = read_json(repo / "product/verticals/vesselflow/gate_map.json")
    cube_seed = read_json(repo / "product/verticals/vesselflow/operational_cube_seed.json")

    evidence = evidence_status(import_input)
    missing_required = [item["evidence"] for item in evidence[:4] if not item["available"]]
    sample_mode = import_input.get("dataset_or_workbook", {}).get("status") in ["SAMPLE_PLACEHOLDER", "NOT_REAL_DATA"]

    gates = []
    for gate in gate_map.get("gates", []):
        name = gate.get("gate")
        if name == "human_review":
            status = "REQUIRED"
        elif sample_mode:
            status = "BLOCKED_SAMPLE_DATA"
        elif missing_required:
            status = "BLOCKED_MISSING_EVIDENCE"
        else:
            status = "CHECK_REQUIRED"
        gates.append({"gate": name, "status": status})

    state = {
        "contract_version": "operational_cube.vesselflow_state_definition.v0.6",
        "case_id": import_input.get("case_id"),
        "status": "CONTROLLED_STATE_DEFINED",
        "vertical": {
            "vertical_id": "vesselflow",
            "name": vertical_manifest.get("vertical_name"),
            "complexity": vertical_manifest.get("complexity"),
        },
        "state_snapshot": {
            "data_mode": "sample_placeholder" if sample_mode else "user_data",
            "domains": vertical_manifest.get("domains", []),
            "domain_count": len(vertical_manifest.get("domains", [])),
            "entities": vertical_manifest.get("entities", []),
            "entity_count": len(vertical_manifest.get("entities", [])),
            "decision": "WAITING_FOR_REAL_DATA_OR_HUMAN_REVIEW" if sample_mode else "READY_FOR_HUMAN_REVIEW",
        },
        "domain_map": domain_map,
        "evidence_manifest": evidence,
        "gate_matrix": gates,
        "risk_fragility_summary": {
            "risk_level": "HIGH" if sample_mode or missing_required else "MEDIUM",
            "reason": "sample data or missing real VesselFlow evidence" if sample_mode or missing_required else "real/anonymized data available for controlled review",
            "missing_required": missing_required,
        },
        "delta_recommendations": [
            "Provide real/anonymized VesselFlow workbook or dataset.",
            "Provide expected nomination flow if different from seed.",
            "Provide qualification rules and known blocking rules.",
            "Run human review before any external claim or implementation.",
        ],
        "cube_state": {
            "principle": cube_seed.get("principle"),
            "faces": cube_seed.get("faces"),
            "blocked_actions": BLOCKED_ACTIONS,
        },
        "nomination_flow": import_input.get("expected_nomination_flow", []),
        "blocked_actions": BLOCKED_ACTIONS,
        "default_policy": "No automatic nomination. Controlled state definition only.",
    }
    return state


def state_md(state: Dict[str, Any]) -> str:
    lines = [
        "# VesselFlow Controlled State Definition",
        "",
        f"- Case: `{state.get('case_id')}`",
        f"- Status: `{state.get('status')}`",
        f"- Decision: `{state['state_snapshot'].get('decision')}`",
        f"- Risk level: `{state['risk_fragility_summary'].get('risk_level')}`",
        "",
        "## Domains",
    ]
    for domain in state["state_snapshot"]["domains"]:
        lines.append(f"- `{domain}`")
    lines += ["", "## Evidence Manifest"]
    for item in state["evidence_manifest"]:
        lines.append(f"- `{item['evidence']}`: `{item['status']}`")
    lines += ["", "## Gate Matrix"]
    for item in state["gate_matrix"]:
        lines.append(f"- `{item['gate']}`: `{item['status']}`")
    lines += ["", "## Delta Recommendations"]
    for item in state["delta_recommendations"]:
        lines.append(f"- {item}")
    lines += ["", "## Blocked Actions"]
    for item in state["blocked_actions"]:
        lines.append(f"- `{item}`")
    lines += ["", "## Default Policy", "", state["default_policy"], ""]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--input", default="product/verticals/vesselflow/import_inputs/vesselflow_import_input.json")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    repo = Path(args.repo)
    input_path = repo / args.input
    out_dir = repo / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    state = build_state(repo=repo, input_path=input_path)

    (out_dir / "prod016_020_vesselflow_state_definition.json").write_text(
        json.dumps(state, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "prod016_020_vesselflow_state_definition.md").write_text(
        state_md(state),
        encoding="utf-8",
    )

    readiness = {
        "status": "PASS",
        "case_id": state.get("case_id"),
        "decision": state["state_snapshot"].get("decision"),
        "risk_level": state["risk_fragility_summary"].get("risk_level"),
        "blocked_actions": state["blocked_actions"],
        "next_required_user_input": [
            "real/anonymized VesselFlow workbook or dataset",
            "expected nomination flow",
            "qualification rules",
            "known blocking rules",
        ],
    }
    (out_dir / "prod016_020_vesselflow_import_readiness.json").write_text(
        json.dumps(readiness, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    print(json.dumps({"status": "PASS", "outputs": [
        str(out_dir / "prod016_020_vesselflow_state_definition.json"),
        str(out_dir / "prod016_020_vesselflow_state_definition.md"),
        str(out_dir / "prod016_020_vesselflow_import_readiness.json"),
    ]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def build_report(repo: Path) -> dict:
    state_path = repo / "outputs/prod016_020_vesselflow_state_definition.json"
    if not state_path.exists():
        raise FileNotFoundError(f"Missing VesselFlow state definition: {state_path}")

    state = read_json(state_path)
    report = {
        "contract_version": "operational_cube.vesselflow_state_report_export.v0.7",
        "status": "PASS",
        "title": "VesselFlow Controlled State Definition Report",
        "case_id": state.get("case_id"),
        "decision": state.get("state_snapshot", {}).get("decision"),
        "risk_level": state.get("risk_fragility_summary", {}).get("risk_level"),
        "data_mode": state.get("state_snapshot", {}).get("data_mode"),
        "domain_count": state.get("state_snapshot", {}).get("domain_count"),
        "entity_count": state.get("state_snapshot", {}).get("entity_count"),
        "evidence_manifest": state.get("evidence_manifest", []),
        "gate_matrix": state.get("gate_matrix", []),
        "delta_recommendations": state.get("delta_recommendations", []),
        "blocked_actions": state.get("blocked_actions", []),
        "default_policy": state.get("default_policy"),
        "internal_use_only": True,
    }
    return report


def report_md(report: dict) -> str:
    lines = [
        "# VesselFlow Controlled State Definition Report",
        "",
        f"- Status: `{report['status']}`",
        f"- Case: `{report['case_id']}`",
        f"- Decision: `{report['decision']}`",
        f"- Risk level: `{report['risk_level']}`",
        f"- Data mode: `{report['data_mode']}`",
        f"- Domain count: `{report['domain_count']}`",
        f"- Entity count: `{report['entity_count']}`",
        "",
        "## Evidence Manifest",
    ]
    for item in report.get("evidence_manifest", []):
        lines.append(f"- `{item.get('evidence')}`: `{item.get('status')}`")
    lines += ["", "## Gate Matrix"]
    for item in report.get("gate_matrix", []):
        lines.append(f"- `{item.get('gate')}`: `{item.get('status')}`")
    lines += ["", "## Delta Recommendations"]
    for item in report.get("delta_recommendations", []):
        lines.append(f"- {item}")
    lines += ["", "## Blocked Actions"]
    for item in report.get("blocked_actions", []):
        lines.append(f"- `{item}`")
    lines += [
        "",
        "## Default Policy",
        "",
        report.get("default_policy", ""),
        "",
        "## Internal Use",
        "",
        "This report is for controlled internal review only. It does not authorize nomination, implementation, production activation, or client-facing claims.",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    repo = Path(args.repo)
    out_dir = repo / args.output_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    report = build_report(repo)
    (out_dir / "prod021_025_vesselflow_state_report_export.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    (out_dir / "prod021_025_vesselflow_state_report_export.md").write_text(
        report_md(report),
        encoding="utf-8",
    )

    print(json.dumps({"status": "PASS", "outputs": [
        str(out_dir / "prod021_025_vesselflow_state_report_export.json"),
        str(out_dir / "prod021_025_vesselflow_state_report_export.md"),
    ]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

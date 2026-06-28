#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def count_status(items, key="status"):
    out = {}
    for item in items or []:
        status = str(item.get(key, "UNKNOWN"))
        out[status] = out.get(status, 0) + 1
    return out


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()

    repo = Path(args.repo)
    out_dir = repo / args.output_dir
    state = read_json(repo / "outputs/prod016_020_vesselflow_state_definition.json")
    delta = read_json(repo / "outputs/prod031_035_vesselflow_real_data_delta_review.json")
    rerun = read_json(repo / "outputs/prod036_040_vesselflow_data_backed_rerun.json")

    result = {
        "contract_version": "operational_cube.evidence_comparator.v1.0",
        "status": "PASS",
        "case_id": state.get("case_id"),
        "state": {
            "data_mode": state.get("state_snapshot", {}).get("data_mode"),
            "decision": state.get("state_snapshot", {}).get("decision"),
            "risk_level": state.get("risk_fragility_summary", {}).get("risk_level"),
        },
        "evidence_status_counts": count_status(state.get("evidence_manifest", [])),
        "gate_status_counts": count_status(state.get("gate_matrix", [])),
        "delta": delta.get("delta", {}),
        "rerun": {
            "mode": rerun.get("mode"),
            "ready_for_write_rerun": rerun.get("ready_for_write_rerun"),
            "errors": rerun.get("errors", []),
            "warnings": rerun.get("warnings", []),
        },
        "internal_review_result": "WAITING_FOR_REAL_OR_ANONYMIZED_DATA" if not rerun.get("ready_for_write_rerun") else "READY_FOR_CONTROLLED_WRITE_RERUN",
        "blocked_actions": rerun.get("blocked_actions", []),
    }

    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "prod036_040_vesselflow_evidence_comparator.json").write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# PROD-036..040 VesselFlow Evidence Comparator",
        "",
        f"- Status: `{result['status']}`",
        f"- Case: `{result['case_id']}`",
        f"- Data mode: `{result['state']['data_mode']}`",
        f"- Decision: `{result['state']['decision']}`",
        f"- Risk level: `{result['state']['risk_level']}`",
        f"- Internal review result: `{result['internal_review_result']}`",
        "",
        "## Evidence Status Counts",
    ]
    for k, v in result["evidence_status_counts"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines += ["", "## Gate Status Counts"]
    for k, v in result["gate_status_counts"].items():
        lines.append(f"- `{k}`: `{v}`")
    lines += ["", "## Rerun Warnings"]
    if result["rerun"]["warnings"]:
        for item in result["rerun"]["warnings"]:
            lines.append(f"- {item}")
    else:
        lines.append("- None")
    lines += ["", "## Blocked Actions"]
    for item in result["blocked_actions"]:
        lines.append(f"- `{item}`")
    lines.append("")
    (out_dir / "prod036_040_vesselflow_evidence_comparator.md").write_text("\n".join(lines), encoding="utf-8")
    print(json.dumps({"status": "PASS", "outputs": [
        str(out_dir / "prod036_040_vesselflow_evidence_comparator.json"),
        str(out_dir / "prod036_040_vesselflow_evidence_comparator.md"),
    ]}, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

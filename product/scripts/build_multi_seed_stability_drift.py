#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
]


def run(cmd: List[str]) -> Dict[str, Any]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return {"code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def md_simple(title: str, obj: Dict[str, Any]) -> List[str]:
    lines = [f"# {title}", ""]
    for key, value in obj.items():
        if isinstance(value, (str, int, float, bool)):
            lines.append(f"- {key}: `{value}`")
        elif isinstance(value, list):
            lines += ["", f"## {key.replace('_', ' ').title()}"]
            for item in value:
                lines.append(f"- `{item}`")
        elif isinstance(value, dict):
            lines += ["", f"## {key.replace('_', ' ').title()}"]
            for k, v in value.items():
                lines.append(f"- {k}: `{json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v}`")
    return lines


def write_outputs(repo: Path, seeds: str, count: int, out_dir: str = "outputs") -> Dict[str, Any]:
    proc = run([
        sys.executable,
        str(repo / "product/scripts/run_multi_seed_stability_drift.py"),
        "--repo", str(repo),
        "--seeds", seeds,
        "--count", str(count),
    ])
    if proc["code"] != 0:
        raise RuntimeError(proc["stdout"] + proc["stderr"])

    report = read_json(repo / "outputs/prod221_240_stability_report.json")
    readiness = {
        "contract_version": "casulo.multi_seed_stability_readiness.v0.1",
        "status": "PASS",
        "decision": "READY_FOR_MULTI_SEED_STABILITY_REVIEW",
        "run_decision": report["decision"],
        "ready_for": [
            "seed-to-seed stability analysis",
            "drift detection",
            "anomaly cluster review",
            "provisional synthetic threshold discussion"
        ],
        "not_ready_for": [
            "real company automation",
            "production calibration claim",
            "external commercial claim without real anonymized validation"
        ],
        "next": "Run anonymized real-document batch after synthetic multi-seed stability review.",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    audit = {
        "status": "PASS",
        "audit": "Multi-Seed Stability and Drift audit",
        "total_cases": report["total_cases"],
        "seeds": report["seeds"],
        "decision": report["decision"],
        "drift_status": report["drift"]["status"],
        "anomaly_total": report["anomaly_clusters"]["total_anomalies"],
        "finding": "PASS: multi-seed runner can test whether stochastic calibration behavior is stable across random batches."
    }
    out = repo / out_dir
    write_json(out / "prod221_240_readiness.json", readiness)
    write_md(out / "prod221_240_readiness.md", md_simple("Multi-Seed Stability Readiness", readiness))
    write_json(out / "prod221_240_audit_report.json", audit)
    write_md(out / "prod221_240_audit_report.md", md_simple("Multi-Seed Stability Audit", audit))

    result = {
        "task": "PROD-221..240",
        "status": "PASS",
        "phase": "Multi-Seed Stability and Drift Calibration Runner",
        "decision": readiness["decision"],
        "run_decision": report["decision"],
        "outputs": [
            "outputs/prod221_240_multi_seed_runs.json",
            "outputs/prod221_240_stability_report.json",
            "outputs/prod221_240_stability_report.md",
            "outputs/prod221_240_drift_report.json",
            "outputs/prod221_240_anomaly_cluster_report.json",
            "outputs/prod221_240_calibrated_threshold_recommendations.json",
            "outputs/prod221_240_seed_summary.csv",
            "outputs/prod221_240_scored_cases_all_seeds.csv",
            "outputs/prod221_240_scored_cases_all_seeds.json",
            "outputs/prod221_240_readiness.json",
            "outputs/prod221_240_audit_report.json"
        ],
        "next_recommended_bundle": "PROD-241..260 Real Anonymized Document Batch Runner",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod221_240_result.json", result)
    write_md(out / "prod221_240_report.md", md_simple("PROD-221..240 Multi-Seed Stability and Drift Report", result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--seeds", default="101,202,303,404,505")
    parser.add_argument("--count", type=int, default=300)
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()
    print(json.dumps(write_outputs(Path(args.repo), args.seeds, args.count, args.output_dir), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

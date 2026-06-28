#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REQUIRED = [
    "product/contracts/multi_seed_stability_runner.contract.json",
    "product/contracts/drift_detection.contract.json",
    "product/contracts/stability_thresholds.contract.json",
    "product/contracts/anomaly_cluster_classifier.contract.json",
    "product/contracts/calibrated_threshold_recommendation.contract.json",
    "product/schemas/multi_seed_run.schema.json",
    "product/schemas/stability_report.schema.json",
    "product/scripts/run_multi_seed_stability_drift.py",
    "product/scripts/build_multi_seed_stability_drift.py",
    "outputs/prod201_220_anomaly_report.json",
]

def run(cmd):
    proc = subprocess.run(cmd, text=True, capture_output=True)
    return proc.returncode, proc.stdout + proc.stderr

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--seeds", default="101,202,303,404,505")
    parser.add_argument("--count", type=int, default=300)
    args = parser.parse_args()
    repo = Path(args.repo)
    errors = []
    warnings = []
    for rel in REQUIRED:
        if not (repo / rel).exists():
            errors.append(f"missing {rel}")

    if not errors:
        code, out = run([sys.executable, str(repo / "product/scripts/build_multi_seed_stability_drift.py"), "--repo", str(repo), "--seeds", args.seeds, "--count", str(args.count)])
        if code != 0:
            errors.append("build_multi_seed_stability_drift failed: " + out)

    outputs = [
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
        "outputs/prod221_240_audit_report.json",
    ]
    for rel in outputs:
        if not (repo / rel).exists():
            errors.append(f"missing output {rel}")

    report_path = repo / "outputs/prod221_240_stability_report.json"
    if report_path.exists():
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("total_cases", 0) < args.count:
            errors.append("total cases lower than one seed count")
        if "stability" not in report:
            errors.append("missing stability block")
        if "drift" not in report:
            errors.append("missing drift block")

    result = {"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(outputs) + 3, "errors": errors, "warnings": warnings}
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0

if __name__ == "__main__":
    raise SystemExit(main())

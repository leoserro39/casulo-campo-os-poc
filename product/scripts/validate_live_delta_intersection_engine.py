#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED = [
    "product/contracts/live_delta_intersection_engine.contract.json",
    "product/contracts/delta_vector_model.contract.json",
    "product/contracts/gate_transition_model.contract.json",
    "product/contracts/domain_sensitivity_model.contract.json",
    "product/contracts/baseline_promotion_policy.contract.json",
    "product/schemas/live_delta_vector.schema.json",
    "product/schemas/gate_transition_result.schema.json",
    "product/schemas/bayesian_gate_trust.schema.json",
    "product/schemas/baseline_promotion_policy.schema.json",
    "product/scripts/run_live_delta_intersection_engine.py",
    "product/scripts/build_live_delta_intersection_engine.py",
    "outputs/prod601b_620b_telemetry_correlation_matrix.json",
]

OUTPUTS = [
    "outputs/prod601c_620c_live_delta_vectors.json",
    "outputs/prod601c_620c_gate_transition_model.json",
    "outputs/prod601c_620c_domain_sensitivity_model.json",
    "outputs/prod601c_620c_bayesian_gate_trust.json",
    "outputs/prod601c_620c_ewma_drift_profile.json",
    "outputs/prod601c_620c_pareto_frontier.json",
    "outputs/prod601c_620c_baseline_promotion_policy.json",
    "outputs/prod601c_620c_telemetry_feedback_events.json",
    "outputs/prod601c_620c_readiness.json",
    "outputs/prod601c_620c_audit_report.json",
]

parser = argparse.ArgumentParser()
parser.add_argument("--repo", default=".")
args = parser.parse_args()
repo = Path(args.repo)

errors = []
for rel in REQUIRED:
    if not (repo / rel).exists():
        errors.append(f"missing {rel}")

if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_live_delta_intersection_engine.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)

for rel in OUTPUTS:
    if not (repo / rel).exists():
        errors.append(f"missing output {rel}")

if not errors:
    vectors = json.loads((repo / "outputs/prod601c_620c_live_delta_vectors.json").read_text(encoding="utf-8"))
    if vectors.get("case_count", 0) < 1000:
        errors.append("case_count must be at least 1000")
    if len(vectors.get("components", [])) < 8:
        errors.append("delta vector components incomplete")

print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(OUTPUTS) + 2, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)

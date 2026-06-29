#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED = [
    "product/contracts/domain_preflight_layer.contract.json",
    "product/contracts/hallucination_budget.contract.json",
    "product/contracts/safe_escalation_taxonomy.contract.json",
    "product/contracts/business_pattern_mining.contract.json",
    "product/contracts/evidence_variance_grid.contract.json",
    "product/schemas/domain_preflight_matrix.schema.json",
    "product/schemas/hallucination_budget.schema.json",
    "product/schemas/safe_escalation_taxonomy.schema.json",
    "product/schemas/business_pattern_mining.schema.json",
    "product/schemas/evidence_variance_grid.schema.json",
    "product/scripts/run_domain_preflight_pattern_mining.py",
    "product/scripts/build_domain_preflight_pattern_mining.py",
    "outputs/prod621_650_business_readiness.json",
    "outputs/prod621_650_business_domain_cases.json",
]
OUTPUTS = [
    "outputs/prod621b_650b_domain_preflight_matrix.json",
    "outputs/prod621b_650b_hallucination_budget.json",
    "outputs/prod621b_650b_safe_escalation_taxonomy.json",
    "outputs/prod621b_650b_business_pattern_mining.json",
    "outputs/prod621b_650b_evidence_variance_grid.json",
    "outputs/prod621b_650b_gate_confusion_matrix.json",
    "outputs/prod621b_650b_threshold_recommendations.json",
    "outputs/prod621b_650b_readiness.json",
    "outputs/prod621b_650b_audit_report.json",
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
    upstream = json.loads((repo / "outputs/prod621_650_business_readiness.json").read_text(encoding="utf-8"))
    if upstream.get("decision") != "READY_FOR_CONTROLLED_BUSINESS_CASE_INPUT_WITH_LIVE_DELTA":
        errors.append("upstream PROD-621 readiness is not ready for domain preflight")
if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_domain_preflight_pattern_mining.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)
for rel in OUTPUTS:
    if not (repo / rel).exists():
        errors.append(f"missing output {rel}")
if not errors:
    taxonomy = json.loads((repo / "outputs/prod621b_650b_safe_escalation_taxonomy.json").read_text(encoding="utf-8"))
    if taxonomy.get("recalibrated_safe_behavior_rate_pct", 0) < 95:
        errors.append("recalibrated_safe_behavior_rate_pct must be at least 95")
    grid = json.loads((repo / "outputs/prod621b_650b_evidence_variance_grid.json").read_text(encoding="utf-8"))
    if grid.get("grid_case_count", 0) < 72:
        errors.append("evidence grid must contain at least 72 probe cases")
print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(OUTPUTS) + 4, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)

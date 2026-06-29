#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED = [
    "product/contracts/solver_agent_controlled_stub.contract.json",
    "product/contracts/solver_agent_input.contract.json",
    "product/contracts/solver_agent_run_report.contract.json",
    "product/contracts/solver_agent_gate_trace.contract.json",
    "product/contracts/solver_agent_telemetry_feedback.contract.json",
    "product/schemas/solver_agent_input.schema.json",
    "product/schemas/solver_agent_run_report.schema.json",
    "product/schemas/solver_agent_gate_trace.schema.json",
    "product/schemas/solver_agent_telemetry_feedback.schema.json",
    "product/scripts/run_solver_agent_controlled_stub.py",
    "product/scripts/build_solver_agent_controlled_stub.py",
    "outputs/prod601c_620c_readiness.json",
]

OUTPUTS = [
    "outputs/prod602_620_solver_agent_status.json",
    "outputs/prod602_620_solver_agent_input_schema.json",
    "outputs/prod602_620_solver_agent_sample_run.json",
    "outputs/prod602_620_solver_agent_run_report.json",
    "outputs/prod602_620_solver_agent_live_delta_decision.json",
    "outputs/prod602_620_solver_agent_evidence_trace.json",
    "outputs/prod602_620_solver_agent_gate_trace.json",
    "outputs/prod602_620_solver_agent_telemetry_feedback.json",
    "outputs/prod602_620_solver_agent_readiness.json",
    "outputs/prod602_620_solver_agent_audit_report.json",
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
    upstream = json.loads((repo / "outputs/prod601c_620c_readiness.json").read_text(encoding="utf-8"))
    if upstream.get("decision") != "READY_FOR_SOLVER_AGENT_CONTROLLED_STUB_WITH_LIVE_DELTA":
        errors.append("upstream PROD-601C readiness is not ready for solver agent controlled stub")

if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_solver_agent_controlled_stub.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)

for rel in OUTPUTS:
    if not (repo / rel).exists():
        errors.append(f"missing output {rel}")

if not errors:
    audit = json.loads((repo / "outputs/prod602_620_solver_agent_audit_report.json").read_text(encoding="utf-8"))
    if audit.get("external_execution_allowed") is not False:
        errors.append("external_execution_allowed must be false")
    if audit.get("automatic_threshold_mutation_allowed") is not False:
        errors.append("automatic_threshold_mutation_allowed must be false")

print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(REQUIRED) + len(OUTPUTS) + 3, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)

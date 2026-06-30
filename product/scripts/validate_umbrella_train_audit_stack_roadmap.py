#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
parser = argparse.ArgumentParser()
parser.add_argument("--repo", default=".")
args = parser.parse_args()
repo = Path(args.repo)
required = [
  "outputs/umbrella_prod-1141_1180_demo_surface_operator_readiness_readiness.json",
  "product/scripts/run_umbrella_train_audit_stack_roadmap.py",
  "product/scripts/build_umbrella_train_audit_stack_roadmap.py"
]
errors = [f"missing {x}" for x in required if not (repo / x).exists()]
if not errors:
    p = subprocess.run([sys.executable, str(repo / "product/scripts/build_umbrella_train_audit_stack_roadmap.py"), "--repo", str(repo)], capture_output=True, text=True)
    if p.returncode:
        errors.append("build failed: " + p.stdout + p.stderr)
outputs = [
  "outputs/prod1181_1220_umbrella_train_audit.json",
  "outputs/prod1181_1220_alias_cleanup_policy.json",
  "outputs/prod1181_1220_llm_research_boundary.json",
  "outputs/prod1181_1220_stack_roadmap.json",
  "outputs/prod1181_1220_codex_executor_boundary.json",
  "outputs/prod1181_1220_readiness.json"
]
for x in outputs:
    if not (repo / x).exists():
        errors.append(f"missing output {x}")
if not errors:
    readiness = json.loads((repo / "outputs/prod1181_1220_readiness.json").read_text(encoding="utf-8"))
    if readiness.get("decision") != "READY_FOR_NEO4J_SANDBOX_GAIN_TEST_AND_LLM_CODEX_BOUNDARY_TRAIN":
        errors.append("unexpected readiness decision")
print(json.dumps({"status": "FAIL" if errors else "PASS", "checks": len(required) + len(outputs) + 4, "errors": errors, "warnings": []}, indent=2, ensure_ascii=False))
raise SystemExit(1 if errors else 0)

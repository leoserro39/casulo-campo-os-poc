#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
req=["product/contracts/telemetry_correlation_calibration.contract.json","product/contracts/correlation_state.contract.json","product/contracts/telemetry_bounds.contract.json","product/contracts/optimal_telemetry_zone.contract.json","product/contracts/auto_adjustment_candidate.contract.json","product/schemas/telemetry_correlation_matrix.schema.json","product/schemas/telemetry_bounds.schema.json","product/schemas/optimal_telemetry_zone.schema.json","product/schemas/auto_adjustment_candidates.schema.json","product/scripts/run_telemetry_correlation_calibration.py","product/scripts/build_telemetry_correlation_calibration.py","outputs/prod601a_620a_calibration_stress_batch_result.json"]
outs=["outputs/prod601b_620b_telemetry_correlation_matrix.json","outputs/prod601b_620b_telemetry_bounds.json","outputs/prod601b_620b_optimal_telemetry_zones.json","outputs/prod601b_620b_auto_adjustment_candidates.json","outputs/prod601b_620b_readiness.json","outputs/prod601b_620b_audit_report.json"]
ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args(); repo=Path(args.repo); errors=[]
for r in req:
    if not (repo/r).exists(): errors.append(f"missing {r}")
if not errors:
    p=subprocess.run([sys.executable,str(repo/"product/scripts/build_telemetry_correlation_calibration.py"),"--repo",str(repo)],capture_output=True,text=True)
    if p.returncode: errors.append("build failed: "+p.stdout+p.stderr)
for o in outs:
    if not (repo/o).exists(): errors.append(f"missing output {o}")
if not errors:
    c=json.loads((repo/"outputs/prod601b_620b_telemetry_correlation_matrix.json").read_text(encoding="utf-8"))
    if c.get("case_count",0)<1000: errors.append("case_count must be at least 1000")
print(json.dumps({"status":"FAIL" if errors else "PASS","checks":len(req)+len(outs)+1,"errors":errors,"warnings":[]},indent=2,ensure_ascii=False))
raise SystemExit(1 if errors else 0)

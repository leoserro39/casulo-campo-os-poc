#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
REQUIRED=["product/contracts/graph_sync_telemetry_lab.contract.json","product/contracts/delta_library_v2.contract.json","product/contracts/telemetry_control_agent.contract.json","product/contracts/graph_sync_protocol.contract.json","product/contracts/self_sustaining_loop_policy.contract.json","product/schemas/delta_library_entry.schema.json","product/schemas/graph_sync_test_case.schema.json","product/schemas/telemetry_control_recommendation.schema.json","product/scripts/build_delta_library_v2.py","product/scripts/run_graph_sync_telemetry_lab.py","product/scripts/build_graph_sync_telemetry_delta_v2.py","outputs/prod221_240_stability_report.json"]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--seed",type=int,default=241260); ap.add_argument("--sync-count",type=int,default=48); args=ap.parse_args()
    repo=Path(args.repo); errors=[]
    for rel in REQUIRED:
        if not (repo/rel).exists(): errors.append(f"missing {rel}")
    if not errors:
        p=subprocess.run([sys.executable,str(repo/"product/scripts/build_graph_sync_telemetry_delta_v2.py"),"--repo",str(repo),"--seed",str(args.seed),"--sync-count",str(args.sync_count)],capture_output=True,text=True)
        if p.returncode: errors.append("build failed: "+p.stdout+p.stderr)
    outputs=["outputs/prod241_260_delta_library_v2.json","outputs/prod241_260_control_catalog.json","outputs/prod241_260_graph_sync_lab_report.json","outputs/prod241_260_graph_sync_attempts.json","outputs/prod241_260_graph_sync_summary.json","outputs/prod241_260_telemetry_control_agent.json","outputs/prod241_260_practical_closure_policy.json","outputs/prod241_260_graph_sync_readiness.json","outputs/prod241_260_audit_report.json"]
    for rel in outputs:
        if not (repo/rel).exists(): errors.append(f"missing output {rel}")
    print(json.dumps({"status":"FAIL" if errors else "PASS","checks":len(REQUIRED)+len(outputs),"errors":errors,"warnings":[]},indent=2,ensure_ascii=False))
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())

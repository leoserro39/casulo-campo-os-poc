#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
REQUIRED=["product/contracts/graph_builder_telemetry_integration.contract.json","product/contracts/candidate_graph_telemetry.contract.json","product/contracts/missing_artifact_recommender.contract.json","product/contracts/graph_builder_stop_rules.contract.json","product/contracts/graph_builder_quality_gates.contract.json","product/schemas/candidate_graph_telemetry.schema.json","product/schemas/missing_artifact_task.schema.json","product/schemas/graph_builder_telemetry_result.schema.json","product/scripts/run_graph_builder_telemetry_integration.py","product/scripts/build_graph_builder_telemetry_integration.py","outputs/prod241_260_delta_library_v2.json","outputs/prod241_260_graph_sync_lab_report.json"]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--seed",type=int,default=261280); ap.add_argument("--nodes",type=int,default=18); ap.add_argument("--edges",type=int,default=32); args=ap.parse_args()
    repo=Path(args.repo); errors=[]
    for rel in REQUIRED:
        if not (repo/rel).exists(): errors.append(f"missing {rel}")
    if not errors:
        p=subprocess.run([sys.executable,str(repo/"product/scripts/build_graph_builder_telemetry_integration.py"),"--repo",str(repo),"--seed",str(args.seed),"--nodes",str(args.nodes),"--edges",str(args.edges)],capture_output=True,text=True)
        if p.returncode: errors.append("build failed: "+p.stdout+p.stderr)
    outputs=["outputs/prod261_280_candidate_graph_telemetry.json","outputs/prod261_280_missing_artifact_tasks.json","outputs/prod261_280_graph_builder_telemetry_result.json","outputs/prod261_280_graph_builder_telemetry_result.md","outputs/prod261_280_native_telemetry_policy.json","outputs/prod261_280_graph_builder_readiness.json","outputs/prod261_280_audit_report.json"]
    for rel in outputs:
        if not (repo/rel).exists(): errors.append(f"missing output {rel}")
    print(json.dumps({"status":"FAIL" if errors else "PASS","checks":len(REQUIRED)+len(outputs),"errors":errors,"warnings":[]},indent=2,ensure_ascii=False))
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())

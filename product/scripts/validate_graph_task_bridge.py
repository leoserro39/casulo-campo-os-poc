#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED=[
    "product/contracts/graph_task_bridge.contract.json",
    "product/contracts/task_prioritization.contract.json",
    "product/contracts/issue_candidate_schema.contract.json",
    "product/contracts/practical_backlog_policy.contract.json",
    "product/contracts/task_closure_rules.contract.json",
    "product/schemas/prioritized_task.schema.json",
    "product/schemas/issue_candidate.schema.json",
    "product/schemas/practical_backlog_report.schema.json",
    "product/scripts/run_graph_task_bridge.py",
    "product/scripts/build_graph_task_bridge.py",
    "outputs/prod261_280_missing_artifact_tasks.json",
    "outputs/prod261_280_candidate_graph_telemetry.json",
]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--max-issues",type=int,default=12); args=ap.parse_args()
    repo=Path(args.repo); errors=[]
    for rel in REQUIRED:
        if not (repo/rel).exists(): errors.append(f"missing {rel}")
    if not errors:
        p=subprocess.run([sys.executable,str(repo/"product/scripts/build_graph_task_bridge.py"),"--repo",str(repo),"--max-issues",str(args.max_issues)],capture_output=True,text=True)
        if p.returncode: errors.append("build failed: "+p.stdout+p.stderr)
    outputs=[
        "outputs/prod281_300_task_clusters.json",
        "outputs/prod281_300_task_clusters.md",
        "outputs/prod281_300_issue_candidates.json",
        "outputs/prod281_300_issue_candidates.md",
        "outputs/prod281_300_practical_backlog_report.json",
        "outputs/prod281_300_practical_backlog_report.md",
        "outputs/prod281_300_task_closure_policy.json",
        "outputs/prod281_300_graph_task_bridge_readiness.json",
        "outputs/prod281_300_audit_report.json",
    ]
    for rel in outputs:
        if not (repo/rel).exists(): errors.append(f"missing output {rel}")
    print(json.dumps({"status":"FAIL" if errors else "PASS","checks":len(REQUIRED)+len(outputs),"errors":errors,"warnings":[]},indent=2,ensure_ascii=False))
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())

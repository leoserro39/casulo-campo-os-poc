#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED=[
    "product/contracts/real_anonymized_graph_case_runner.contract.json",
    "product/contracts/anonymized_graph_case.contract.json",
    "product/contracts/real_case_gate_policy.contract.json",
    "product/contracts/case_graph_evaluation.contract.json",
    "product/contracts/case_to_backlog_bridge.contract.json",
    "product/schemas/anonymized_graph_case.schema.json",
    "product/schemas/real_graph_case_result.schema.json",
    "product/schemas/real_graph_case_aggregate.schema.json",
    "product/scripts/run_real_anonymized_graph_cases.py",
    "product/scripts/build_real_anonymized_graph_case_runner.py",
    "outputs/prod281_300_practical_backlog_report.json",
    "outputs/prod281_300_issue_candidates.json",
]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--seed",type=int,default=301320); ap.add_argument("--max-issues",type=int,default=8); args=ap.parse_args()
    repo=Path(args.repo); errors=[]
    for rel in REQUIRED:
        if not (repo/rel).exists(): errors.append(f"missing {rel}")
    cases=list((repo/"product/poc/real_anonymized_graph_cases/cases").glob("*.json"))
    if len(cases)<4: errors.append("expected at least 4 anonymized graph case files")
    if not errors:
        p=subprocess.run([sys.executable,str(repo/"product/scripts/build_real_anonymized_graph_case_runner.py"),"--repo",str(repo),"--seed",str(args.seed),"--max-issues",str(args.max_issues)],capture_output=True,text=True)
        if p.returncode: errors.append("build failed: "+p.stdout+p.stderr)
    outputs=[
        "outputs/prod301_320_real_graph_case_results.json",
        "outputs/prod301_320_real_graph_case_aggregate.json",
        "outputs/prod301_320_real_graph_case_aggregate.md",
        "outputs/prod301_320_real_graph_case_summary.csv",
        "outputs/prod301_320_real_graph_case_readiness.json",
        "outputs/prod301_320_audit_report.json",
    ]
    for rel in outputs:
        if not (repo/rel).exists(): errors.append(f"missing output {rel}")
    print(json.dumps({"status":"FAIL" if errors else "PASS","checks":len(REQUIRED)+len(outputs)+1,"errors":errors,"warnings":[]},indent=2,ensure_ascii=False))
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())

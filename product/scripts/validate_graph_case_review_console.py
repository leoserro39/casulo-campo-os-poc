#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED=[
    "product/contracts/graph_case_review_console.contract.json",
    "product/contracts/issue_selection_policy.contract.json",
    "product/contracts/case_review_decision_log.contract.json",
    "product/contracts/human_review_pack.contract.json",
    "product/contracts/case_review_console_readiness.contract.json",
    "product/schemas/review_console.schema.json",
    "product/schemas/issue_selection.schema.json",
    "product/schemas/review_decision.schema.json",
    "product/scripts/run_graph_case_review_console.py",
    "product/scripts/build_graph_case_review_console.py",
    "outputs/prod301_320_real_graph_case_results.json",
    "outputs/prod301_320_real_graph_case_aggregate.json",
]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--max-selected",type=int,default=12); args=ap.parse_args()
    repo=Path(args.repo); errors=[]
    for rel in REQUIRED:
        if not (repo/rel).exists(): errors.append(f"missing {rel}")
    if not errors:
        p=subprocess.run([sys.executable,str(repo/"product/scripts/build_graph_case_review_console.py"),"--repo",str(repo),"--max-selected",str(args.max_selected)],capture_output=True,text=True)
        if p.returncode: errors.append("build failed: "+p.stdout+p.stderr)
    outputs=[
        "outputs/prod321_340_review_console.json",
        "outputs/prod321_340_review_console.md",
        "outputs/prod321_340_issue_selection.json",
        "outputs/prod321_340_review_decision_log.json",
        "outputs/prod321_340_human_review_pack.json",
        "outputs/prod321_340_human_review_pack.md",
        "outputs/prod321_340_selected_issues.csv",
        "outputs/prod321_340_review_console_readiness.json",
        "outputs/prod321_340_audit_report.json",
    ]
    for rel in outputs:
        if not (repo/rel).exists(): errors.append(f"missing output {rel}")
    print(json.dumps({"status":"FAIL" if errors else "PASS","checks":len(REQUIRED)+len(outputs),"errors":errors,"warnings":[]},indent=2,ensure_ascii=False))
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())

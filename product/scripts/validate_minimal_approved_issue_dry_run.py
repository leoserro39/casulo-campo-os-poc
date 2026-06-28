#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED=[
    "product/contracts/minimal_approved_issue_dry_run.contract.json",
    "product/contracts/dry_run_approval_manifest.contract.json",
    "product/contracts/approved_command_preview.contract.json",
    "product/contracts/dry_run_execution_guard.contract.json",
    "product/contracts/dry_run_readiness.contract.json",
    "product/schemas/minimal_approval_plan.schema.json",
    "product/schemas/dry_run_transition.schema.json",
    "product/schemas/minimal_dry_run_guard.schema.json",
    "product/scripts/run_minimal_approved_issue_dry_run.py",
    "product/scripts/build_minimal_approved_issue_dry_run.py",
    "outputs/prod341_360_manual_issue_promotion.json",
    "outputs/prod361_380_formal_approval_manifest_snapshot.json",
    "outputs/prod361_380_issue_execution_guard.json",
]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",default=".")
    ap.add_argument("--approve-count",type=int,default=2)
    args=ap.parse_args()
    repo=Path(args.repo); errors=[]
    for rel in REQUIRED:
        if not (repo/rel).exists(): errors.append(f"missing {rel}")
    if not errors:
        p=subprocess.run([sys.executable,str(repo/"product/scripts/build_minimal_approved_issue_dry_run.py"),"--repo",str(repo),"--approve-count",str(args.approve_count)],capture_output=True,text=True)
        if p.returncode: errors.append("build failed: "+p.stdout+p.stderr)
    outputs=[
        "outputs/prod381_400_minimal_approval_plan.json",
        "outputs/prod381_400_dry_run_approval_manifest.json",
        "outputs/prod381_400_dry_run_transition_ledger.json",
        "outputs/prod381_400_execution_guard.json",
        "outputs/prod381_400_approved_command_preview.md",
        "outputs/prod381_400_minimal_dry_run_report.md",
        "outputs/prod381_400_readiness.json",
        "outputs/prod381_400_audit_report.json",
    ]
    for rel in outputs:
        if not (repo/rel).exists(): errors.append(f"missing output {rel}")
    if not errors:
        guard=json.loads((repo/"outputs/prod381_400_execution_guard.json").read_text(encoding="utf-8"))
        if guard.get("auto_execution_allowed") is not False:
            errors.append("auto_execution_allowed must be false")
        if guard.get("approved_count") != args.approve_count:
            errors.append("approved_count does not match requested approve-count")
    print(json.dumps({"status":"FAIL" if errors else "PASS","checks":len(REQUIRED)+len(outputs)+2,"errors":errors,"warnings":[]},indent=2,ensure_ascii=False))
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())

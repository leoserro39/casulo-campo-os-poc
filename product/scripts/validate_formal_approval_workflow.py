#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED=[
    "product/contracts/formal_approval_workflow.contract.json",
    "product/contracts/approval_state_machine.contract.json",
    "product/contracts/issue_execution_guard.contract.json",
    "product/contracts/approval_manifest.contract.json",
    "product/contracts/issue_traceability_ledger.contract.json",
    "product/schemas/formal_approval_manifest.schema.json",
    "product/schemas/approval_state_transition.schema.json",
    "product/schemas/issue_execution_guard.schema.json",
    "product/scripts/run_formal_approval_workflow.py",
    "product/scripts/build_formal_approval_workflow.py",
    "outputs/prod341_360_manual_issue_promotion.json",
    "outputs/prod341_360_gh_issue_command_templates.md",
]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    repo=Path(args.repo); errors=[]
    for rel in REQUIRED:
        if not (repo/rel).exists(): errors.append(f"missing {rel}")
    if not errors:
        p=subprocess.run([sys.executable,str(repo/"product/scripts/build_formal_approval_workflow.py"),"--repo",str(repo)],capture_output=True,text=True)
        if p.returncode: errors.append("build failed: "+p.stdout+p.stderr)
    outputs=[
        "outputs/prod361_380_formal_approval_manifest_snapshot.json",
        "outputs/prod361_380_state_transition_ledger.json",
        "outputs/prod361_380_issue_execution_guard.json",
        "outputs/prod361_380_formal_approval_runbook.md",
        "outputs/prod361_380_formal_approval_report.json",
        "outputs/prod361_380_formal_approval_readiness.json",
        "outputs/prod361_380_audit_report.json",
    ]
    for rel in outputs:
        if not (repo/rel).exists(): errors.append(f"missing output {rel}")
    print(json.dumps({"status":"FAIL" if errors else "PASS","checks":len(REQUIRED)+len(outputs),"errors":errors,"warnings":[]},indent=2,ensure_ascii=False))
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())

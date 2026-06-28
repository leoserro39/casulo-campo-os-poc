#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED=[
    "product/contracts/issue_to_state_linkage.contract.json",
    "product/contracts/closure_ledger.contract.json",
    "product/contracts/issue_state_link_record.contract.json",
    "product/contracts/pending_evidence_policy.contract.json",
    "product/contracts/closure_readiness.contract.json",
    "product/schemas/issue_state_link_record.schema.json",
    "product/schemas/closure_ledger.schema.json",
    "product/schemas/closure_readiness.schema.json",
    "product/scripts/run_issue_to_state_linkage_closure.py",
    "product/scripts/build_issue_to_state_linkage_closure.py",
    "outputs/prod401_420_manual_issue_evidence_capture.json",
    "outputs/prod401_420_state_update_preview.json",
    "outputs/prod381_400_dry_run_transition_ledger.json",
]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    repo=Path(args.repo); errors=[]
    for rel in REQUIRED:
        if not (repo/rel).exists(): errors.append(f"missing {rel}")
    if not errors:
        p=subprocess.run([sys.executable,str(repo/"product/scripts/build_issue_to_state_linkage_closure.py"),"--repo",str(repo)],capture_output=True,text=True)
        if p.returncode: errors.append("build failed: "+p.stdout+p.stderr)
    outputs=[
        "outputs/prod421_440_issue_state_link_records.json",
        "outputs/prod421_440_closure_ledger.json",
        "outputs/prod421_440_closure_ledger.md",
        "outputs/prod421_440_linkage_report.json",
        "outputs/prod421_440_linkage_report.md",
        "outputs/prod421_440_readiness.json",
        "outputs/prod421_440_audit_report.json",
    ]
    for rel in outputs:
        if not (repo/rel).exists(): errors.append(f"missing output {rel}")
    if not errors:
        ledger=json.loads((repo/"outputs/prod421_440_closure_ledger.json").read_text(encoding="utf-8"))
        if ledger["summary"].get("auto_execution_allowed") is not False:
            errors.append("auto_execution_allowed must be false")
    print(json.dumps({"status":"FAIL" if errors else "PASS","checks":len(REQUIRED)+len(outputs)+1,"errors":errors,"warnings":[]},indent=2,ensure_ascii=False))
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())

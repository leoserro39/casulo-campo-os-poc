#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED=[
    "product/contracts/manual_issue_creation_evidence_capture.contract.json",
    "product/contracts/manual_issue_evidence_manifest.contract.json",
    "product/contracts/issue_url_validation.contract.json",
    "product/contracts/evidence_to_state_transition.contract.json",
    "product/contracts/manual_issue_evidence_readiness.contract.json",
    "product/schemas/manual_issue_evidence_manifest.schema.json",
    "product/schemas/manual_issue_evidence_record.schema.json",
    "product/schemas/manual_issue_evidence_capture.schema.json",
    "product/scripts/run_manual_issue_creation_evidence_capture.py",
    "product/scripts/build_manual_issue_creation_evidence_capture.py",
    "outputs/prod381_400_dry_run_transition_ledger.json",
    "outputs/prod381_400_approved_command_preview.md",
    "outputs/prod381_400_execution_guard.json",
]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    repo=Path(args.repo); errors=[]
    for rel in REQUIRED:
        if not (repo/rel).exists(): errors.append(f"missing {rel}")
    if not errors:
        p=subprocess.run([sys.executable,str(repo/"product/scripts/build_manual_issue_creation_evidence_capture.py"),"--repo",str(repo)],capture_output=True,text=True)
        if p.returncode: errors.append("build failed: "+p.stdout+p.stderr)
    outputs=[
        "outputs/prod401_420_manual_issue_evidence_manifest_snapshot.json",
        "outputs/prod401_420_manual_issue_evidence_capture.json",
        "outputs/prod401_420_manual_issue_evidence_capture.md",
        "outputs/prod401_420_issue_url_validation.json",
        "outputs/prod401_420_state_update_preview.json",
        "outputs/prod401_420_readiness.json",
        "outputs/prod401_420_audit_report.json",
    ]
    for rel in outputs:
        if not (repo/rel).exists(): errors.append(f"missing output {rel}")
    if not errors:
        capture=json.loads((repo/"outputs/prod401_420_manual_issue_evidence_capture.json").read_text(encoding="utf-8"))
        if capture.get("auto_execution_allowed") is not False:
            errors.append("auto_execution_allowed must be false")
    print(json.dumps({"status":"FAIL" if errors else "PASS","checks":len(REQUIRED)+len(outputs)+1,"errors":errors,"warnings":[]},indent=2,ensure_ascii=False))
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())

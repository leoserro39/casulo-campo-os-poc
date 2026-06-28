#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED=[
    "product/contracts/real_manual_evidence_handoff.contract.json",
    "product/contracts/real_evidence_manifest.contract.json",
    "product/contracts/synthetic_to_real_separation.contract.json",
    "product/contracts/real_manual_url_gate.contract.json",
    "product/contracts/handoff_readiness.contract.json",
    "product/schemas/real_manual_evidence_manifest.schema.json",
    "product/schemas/real_manual_evidence_record.schema.json",
    "product/schemas/real_manual_evidence_validation.schema.json",
    "product/scripts/run_real_manual_evidence_handoff.py",
    "product/scripts/build_real_manual_evidence_handoff.py",
    "outputs/prod441_460_closure_replay_result.json",
    "outputs/prod441_460_synthetic_manual_url_manifest.json",
    "outputs/prod401_420_manual_issue_evidence_capture.json",
]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    repo=Path(args.repo); errors=[]
    for rel in REQUIRED:
        if not (repo/rel).exists(): errors.append(f"missing {rel}")
    if not errors:
        p=subprocess.run([sys.executable,str(repo/"product/scripts/build_real_manual_evidence_handoff.py"),"--repo",str(repo)],capture_output=True,text=True)
        if p.returncode: errors.append("build failed: "+p.stdout+p.stderr)
    outputs=[
        "outputs/prod461_480_real_manual_evidence_manifest_snapshot.json",
        "outputs/prod461_480_real_manual_evidence_handoff.json",
        "outputs/prod461_480_real_manual_evidence_handoff.md",
        "outputs/prod461_480_real_manual_evidence_validation.json",
        "outputs/prod461_480_real_manual_evidence_checklist.json",
        "outputs/prod461_480_readiness.json",
        "outputs/prod461_480_audit_report.json",
    ]
    for rel in outputs:
        if not (repo/rel).exists(): errors.append(f"missing output {rel}")
    if not errors:
        handoff=json.loads((repo/"outputs/prod461_480_real_manual_evidence_handoff.json").read_text(encoding="utf-8"))
        if handoff.get("auto_execution_allowed") is not False:
            errors.append("auto_execution_allowed must be false")
        if handoff.get("network_validation_performed") is not False:
            errors.append("network_validation_performed must be false")
    print(json.dumps({"status":"FAIL" if errors else "PASS","checks":len(REQUIRED)+len(outputs)+2,"errors":errors,"warnings":[]},indent=2,ensure_ascii=False))
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())

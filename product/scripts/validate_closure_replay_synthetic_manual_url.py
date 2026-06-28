#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED=[
    "product/contracts/closure_replay_synthetic_manual_url.contract.json",
    "product/contracts/synthetic_url_policy.contract.json",
    "product/contracts/created_manually_replay.contract.json",
    "product/contracts/closure_replay_ledger.contract.json",
    "product/contracts/closure_replay_readiness.contract.json",
    "product/schemas/synthetic_manual_url_manifest.schema.json",
    "product/schemas/closure_replay_result.schema.json",
    "product/schemas/created_manually_replay_record.schema.json",
    "product/scripts/run_closure_replay_synthetic_manual_url.py",
    "product/scripts/build_closure_replay_synthetic_manual_url.py",
    "outputs/prod421_440_closure_ledger.json",
    "outputs/prod401_420_manual_issue_evidence_capture.json",
]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",default=".")
    ap.add_argument("--replay-count",type=int,default=1)
    ap.add_argument("--repo-slug",default="leoserro39/casulo-campo-os-poc")
    args=ap.parse_args()
    repo=Path(args.repo); errors=[]
    for rel in REQUIRED:
        if not (repo/rel).exists(): errors.append(f"missing {rel}")
    if not errors:
        p=subprocess.run([sys.executable,str(repo/"product/scripts/build_closure_replay_synthetic_manual_url.py"),"--repo",str(repo),"--replay-count",str(args.replay_count),"--repo-slug",args.repo_slug],capture_output=True,text=True)
        if p.returncode: errors.append("build failed: "+p.stdout+p.stderr)
    outputs=[
        "outputs/prod441_460_synthetic_manual_url_manifest.json",
        "outputs/prod441_460_closure_replay_ledger.json",
        "outputs/prod441_460_closure_replay_result.json",
        "outputs/prod441_460_closure_replay_report.md",
        "outputs/prod441_460_readiness.json",
        "outputs/prod441_460_audit_report.json",
    ]
    for rel in outputs:
        if not (repo/rel).exists(): errors.append(f"missing output {rel}")
    if not errors:
        result=json.loads((repo/"outputs/prod441_460_closure_replay_result.json").read_text(encoding="utf-8"))
        if result.get("synthetic_only") is not True:
            errors.append("synthetic_only must be true")
        if result.get("auto_execution_allowed") is not False:
            errors.append("auto_execution_allowed must be false")
        if result.get("real_evidence_claim_count") != 0:
            errors.append("real_evidence_claim_count must be 0")
    print(json.dumps({"status":"FAIL" if errors else "PASS","checks":len(REQUIRED)+len(outputs)+3,"errors":errors,"warnings":[]},indent=2,ensure_ascii=False))
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())

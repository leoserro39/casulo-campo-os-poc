#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED=[
    "product/contracts/milestone_snapshot_operational_readiness.contract.json",
    "product/contracts/tag_chain_inventory.contract.json",
    "product/contracts/operational_readiness_dossier.contract.json",
    "product/contracts/pending_evidence_register.contract.json",
    "product/contracts/milestone_snapshot_readiness.contract.json",
    "product/schemas/milestone_snapshot.schema.json",
    "product/schemas/operational_readiness_dossier.schema.json",
    "product/schemas/tag_chain_inventory.schema.json",
    "product/scripts/run_milestone_snapshot_operational_readiness.py",
    "product/scripts/build_milestone_snapshot_operational_readiness.py",
    "outputs/prod461_480_real_manual_evidence_handoff.json",
    "outputs/prod441_460_closure_replay_result.json",
    "outputs/prod421_440_closure_ledger.json",
]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    repo=Path(args.repo); errors=[]
    for rel in REQUIRED:
        if not (repo/rel).exists(): errors.append(f"missing {rel}")
    if not errors:
        p=subprocess.run([sys.executable,str(repo/"product/scripts/build_milestone_snapshot_operational_readiness.py"),"--repo",str(repo)],capture_output=True,text=True)
        if p.returncode: errors.append("build failed: "+p.stdout+p.stderr)
    outputs=[
        "outputs/prod481_500_tag_chain_inventory.json",
        "outputs/prod481_500_milestone_snapshot.json",
        "outputs/prod481_500_operational_readiness_dossier.json",
        "outputs/prod481_500_operational_readiness_dossier.md",
        "outputs/prod481_500_pending_evidence_register.json",
        "outputs/prod481_500_readiness.json",
        "outputs/prod481_500_audit_report.json",
    ]
    for rel in outputs:
        if not (repo/rel).exists(): errors.append(f"missing output {rel}")
    if not errors:
        snap=json.loads((repo/"outputs/prod481_500_milestone_snapshot.json").read_text(encoding="utf-8"))
        if "automatic_issue_creation" not in "".join(json.loads((repo/"outputs/prod481_500_operational_readiness_dossier.json").read_text(encoding="utf-8")).get("not_ready_for", [])):
            errors.append("dossier must keep automatic issue creation blocked")
    print(json.dumps({"status":"FAIL" if errors else "PASS","checks":len(REQUIRED)+len(outputs)+1,"errors":errors,"warnings":[]},indent=2,ensure_ascii=False))
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())

#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

REQUIRED=[
    "product/contracts/manual_issue_promotion_pack.contract.json",
    "product/contracts/approved_issue_manifest.contract.json",
    "product/contracts/issue_markdown_pack.contract.json",
    "product/contracts/gh_command_template.contract.json",
    "product/contracts/manual_promotion_readiness.contract.json",
    "product/schemas/approved_issue_manifest.schema.json",
    "product/schemas/manual_issue_promotion.schema.json",
    "product/schemas/manual_promotion_audit.schema.json",
    "product/scripts/run_manual_issue_promotion_pack.py",
    "product/scripts/build_manual_issue_promotion_pack.py",
    "outputs/prod321_340_issue_selection.json",
    "outputs/prod321_340_review_decision_log.json",
]

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--all-selected",action="store_true"); args=ap.parse_args()
    repo=Path(args.repo); errors=[]
    for rel in REQUIRED:
        if not (repo/rel).exists(): errors.append(f"missing {rel}")
    if not errors:
        cmd=[sys.executable,str(repo/"product/scripts/build_manual_issue_promotion_pack.py"),"--repo",str(repo)]
        if args.all_selected: cmd.append("--all-selected")
        p=subprocess.run(cmd,capture_output=True,text=True)
        if p.returncode: errors.append("build failed: "+p.stdout+p.stderr)
    outputs=[
        "outputs/prod341_360_manual_issue_promotion.json",
        "outputs/prod341_360_manual_issue_promotion.md",
        "outputs/prod341_360_gh_issue_command_templates.md",
        "outputs/prod341_360_approved_issue_manifest_snapshot.json",
        "outputs/prod341_360_manual_issue_promotion_readiness.json",
        "outputs/prod341_360_audit_report.json",
    ]
    for rel in outputs:
        if not (repo/rel).exists(): errors.append(f"missing output {rel}")
    print(json.dumps({"status":"FAIL" if errors else "PASS","checks":len(REQUIRED)+len(outputs),"errors":errors,"warnings":[]},indent=2,ensure_ascii=False))
    return 1 if errors else 0
if __name__=="__main__": raise SystemExit(main())

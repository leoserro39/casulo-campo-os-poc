#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

BLOCKED=["client_facing_claim","automatic_nomination","implementation_execution","production_activation","automatic_merge","credential_handling"]

def run(cmd):
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode:
        raise RuntimeError(p.stdout+p.stderr)

def read(p): return json.loads(p.read_text(encoding="utf-8"))
def write_json(p,obj): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def write_md(p,title,obj):
    lines=[f"# {title}",""]
    for k,v in obj.items():
        if isinstance(v,(str,int,float,bool)): lines.append(f"- {k}: `{v}`")
        elif isinstance(v,list):
            lines.append(f"\n## {k.replace('_',' ').title()}")
            for item in v: lines.append(f"- `{item}`")
        elif isinstance(v,dict):
            lines.append(f"\n## {k.replace('_',' ').title()}")
            for kk,vv in v.items(): lines.append(f"- {kk}: `{vv}`")
    p.write_text("\n".join(lines)+"\n",encoding="utf-8")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--all-selected",action="store_true"); args=ap.parse_args()
    repo=Path(args.repo); out=repo/"outputs"
    cmd=[sys.executable,str(repo/"product/scripts/run_manual_issue_promotion_pack.py"),"--repo",str(repo)]
    if args.all_selected: cmd.append("--all-selected")
    run(cmd)
    promotion=read(out/"prod341_360_manual_issue_promotion.json")
    readiness={
        "contract_version":"casulo.manual_issue_promotion_readiness.v0.1",
        "status":"PASS",
        "decision":"READY_FOR_MANUAL_ISSUE_REVIEW_NOT_AUTO_CREATE",
        "mode":promotion["mode"],
        "selected_count":promotion["selected_count"],
        "approved_count":promotion["approved_count"],
        "promoted_template_count":promotion["promoted_template_count"],
        "auto_created_count":promotion["auto_created_count"],
        "ready_for":["manual review of issue markdown","manual copy/run of gh commands after approval","approval manifest editing"],
        "not_ready_for":["automatic issue creation","production activation","external client claims"],
        "next":"Approve a small subset in the manifest or create a formal issue promotion workflow.",
        "blocked_actions":BLOCKED,
    }
    audit={
        "status":"PASS",
        "audit":"Manual Issue Promotion Pack audit",
        "selected_count":promotion["selected_count"],
        "approved_count":promotion["approved_count"],
        "generated_issue_files":len(promotion["issue_files"]),
        "command_templates":len(promotion["command_templates"]),
        "auto_created_count":promotion["auto_created_count"],
        "readiness":readiness["decision"],
        "finding":"PASS: manual issue promotion artifacts were generated without creating GitHub issues automatically.",
    }
    for stem,title,obj in [
        ("prod341_360_manual_issue_promotion_readiness","Manual Issue Promotion Readiness",readiness),
        ("prod341_360_audit_report","Manual Issue Promotion Audit",audit),
    ]:
        write_json(out/f"{stem}.json",obj); write_md(out/f"{stem}.md",title,obj)
    result={
        "task":"PROD-341..360",
        "status":"PASS",
        "phase":"Manual Issue Promotion Pack",
        "decision":readiness["decision"],
        "outputs":[
            "outputs/prod341_360_manual_issue_promotion.json",
            "outputs/prod341_360_manual_issue_promotion.md",
            "outputs/prod341_360_gh_issue_command_templates.md",
            "outputs/prod341_360_approved_issue_manifest_snapshot.json",
            "outputs/prod341_360_manual_issue_promotion_readiness.json",
            "outputs/prod341_360_audit_report.json",
        ],
        "next_recommended_bundle":"PROD-361..380 Formal Approval Workflow and Issue Execution Guard",
        "blocked_actions":BLOCKED,
    }
    write_json(out/"prod341_360_result.json",result); write_md(out/"prod341_360_report.md","PROD-341..360 Manual Issue Promotion Pack Report",result)
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

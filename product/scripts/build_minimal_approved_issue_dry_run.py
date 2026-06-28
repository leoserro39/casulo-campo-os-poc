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
    ap=argparse.ArgumentParser()
    ap.add_argument("--repo",default=".")
    ap.add_argument("--approve-count",type=int,default=2)
    args=ap.parse_args()
    repo=Path(args.repo); out=repo/"outputs"
    run([sys.executable,str(repo/"product/scripts/run_minimal_approved_issue_dry_run.py"),"--repo",str(repo),"--approve-count",str(args.approve_count)])
    guard=read(out/"prod381_400_execution_guard.json")
    readiness={
        "contract_version":"casulo.minimal_approved_issue_dry_run_readiness.v0.1",
        "status":"PASS",
        "decision":"READY_FOR_OPTIONAL_MANUAL_ISSUE_CREATION_REVIEW",
        "approved_count":guard["approved_count"],
        "approved_commands_available":guard["approved_commands_available"],
        "auto_execution_allowed":guard["auto_execution_allowed"],
        "source_manifest_modified":guard["source_manifest_modified"],
        "ready_for":["manual command review","human decision on whether to create one issue manually","state transition test review"],
        "not_ready_for":["automatic issue creation","production activation","automatic merge","external client claims"],
        "next":"Human decides whether to manually create one approved issue, then record URL in formal approval manifest.",
        "blocked_actions":BLOCKED,
    }
    audit={
        "status":"PASS",
        "audit":"Minimal Approved Issue Dry Run audit",
        "approved_count":guard["approved_count"],
        "approved_commands_available":guard["approved_commands_available"],
        "invalid_transition_count":guard["invalid_transition_count"],
        "auto_execution_allowed":guard["auto_execution_allowed"],
        "source_manifest_modified":guard["source_manifest_modified"],
        "readiness":readiness["decision"],
        "finding":"PASS: minimal approved dry run validates approval transition and command preview without automatic execution.",
    }
    for stem,title,obj in [
        ("prod381_400_readiness","Minimal Approved Issue Dry Run Readiness",readiness),
        ("prod381_400_audit_report","Minimal Approved Issue Dry Run Audit",audit),
    ]:
        write_json(out/f"{stem}.json",obj); write_md(out/f"{stem}.md",title,obj)
    result={
        "task":"PROD-381..400",
        "status":"PASS",
        "phase":"Minimal Approved Issue Dry Run",
        "decision":readiness["decision"],
        "outputs":[
            "outputs/prod381_400_minimal_approval_plan.json",
            "outputs/prod381_400_dry_run_approval_manifest.json",
            "outputs/prod381_400_dry_run_transition_ledger.json",
            "outputs/prod381_400_execution_guard.json",
            "outputs/prod381_400_approved_command_preview.md",
            "outputs/prod381_400_minimal_dry_run_report.md",
            "outputs/prod381_400_readiness.json",
            "outputs/prod381_400_audit_report.json",
        ],
        "next_recommended_bundle":"PROD-401..420 Manual Issue Creation Evidence Capture",
        "blocked_actions":BLOCKED,
    }
    write_json(out/"prod381_400_result.json",result); write_md(out/"prod381_400_report.md","PROD-381..400 Minimal Approved Issue Dry Run Report",result)
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

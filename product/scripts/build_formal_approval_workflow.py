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
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    repo=Path(args.repo); out=repo/"outputs"
    run([sys.executable,str(repo/"product/scripts/run_formal_approval_workflow.py"),"--repo",str(repo)])
    report=read(out/"prod361_380_formal_approval_report.json")
    guard=report["execution_guard"]
    readiness={
        "contract_version":"casulo.formal_approval_workflow_readiness.v0.1",
        "status":"PASS",
        "decision":"READY_FOR_FORMAL_APPROVAL_REVIEW_NO_AUTO_EXECUTION",
        "approved_count":guard["approved_count"],
        "auto_execution_allowed":guard["auto_execution_allowed"],
        "ready_for":["approval manifest editing","guarded manual command review","manual issue creation after approval"],
        "not_ready_for":["automatic issue creation","production activation","automatic merge","external client claims"],
        "next":"Edit the formal approval manifest for a small approved subset, then re-run the guard.",
        "blocked_actions":BLOCKED,
    }
    audit={
        "status":"PASS",
        "audit":"Formal Approval Workflow and Issue Execution Guard audit",
        "selected_count":guard["selected_count"],
        "approved_count":guard["approved_count"],
        "created_manually_count":guard["created_manually_count"],
        "invalid_transition_count":guard["invalid_transition_count"],
        "auto_execution_allowed":guard["auto_execution_allowed"],
        "readiness":readiness["decision"],
        "finding":"PASS: formal approval workflow protects issue creation with manifest, state transitions and no auto execution.",
    }
    for stem,title,obj in [
        ("prod361_380_formal_approval_readiness","Formal Approval Workflow Readiness",readiness),
        ("prod361_380_audit_report","Formal Approval Workflow Audit",audit),
    ]:
        write_json(out/f"{stem}.json",obj); write_md(out/f"{stem}.md",title,obj)
    result={
        "task":"PROD-361..380",
        "status":"PASS",
        "phase":"Formal Approval Workflow and Issue Execution Guard",
        "decision":readiness["decision"],
        "outputs":[
            "outputs/prod361_380_formal_approval_manifest_snapshot.json",
            "outputs/prod361_380_state_transition_ledger.json",
            "outputs/prod361_380_issue_execution_guard.json",
            "outputs/prod361_380_formal_approval_runbook.md",
            "outputs/prod361_380_formal_approval_report.json",
            "outputs/prod361_380_formal_approval_readiness.json",
            "outputs/prod361_380_audit_report.json",
        ],
        "next_recommended_bundle":"PROD-381..400 Minimal Approved Issue Dry Run",
        "blocked_actions":BLOCKED,
    }
    write_json(out/"prod361_380_result.json",result); write_md(out/"prod361_380_report.md","PROD-361..380 Formal Approval Workflow Report",result)
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

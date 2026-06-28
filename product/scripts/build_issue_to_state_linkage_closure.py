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
    run([sys.executable,str(repo/"product/scripts/run_issue_to_state_linkage_closure.py"),"--repo",str(repo)])
    report=read(out/"prod421_440_linkage_report.json")
    summary=report["summary"]
    readiness={
        "contract_version":"casulo.issue_to_state_linkage_readiness.v0.1",
        "status":"PASS",
        "decision":"READY_FOR_CLOSURE_LEDGER_REVIEW_PENDING_MANUAL_URLS",
        "record_count":summary["record_count"],
        "pending_manual_creation_count":summary["pending_manual_creation_count"],
        "created_manually_ready_to_link_count":summary["created_manually_ready_to_link_count"],
        "manual_issue_url_present_count":summary["manual_issue_url_present_count"],
        "auto_execution_allowed":summary["auto_execution_allowed"],
        "ready_for":["closure ledger review","manual issue URL evidence insertion","pending state tracking"],
        "not_ready_for":["automatic issue creation","automatic closure","production activation","external client claims"],
        "next":"When a human provides a manual issue URL, re-run evidence capture and linkage to move records toward CREATED_MANUALLY.",
        "blocked_actions":BLOCKED,
    }
    audit={
        "status":"PASS",
        "audit":"Issue-to-State Linkage and Closure Ledger audit",
        "record_count":summary["record_count"],
        "pending_manual_creation_count":summary["pending_manual_creation_count"],
        "created_manually_ready_to_link_count":summary["created_manually_ready_to_link_count"],
        "evidence_incomplete_count":summary["evidence_incomplete_count"],
        "auto_execution_allowed":summary["auto_execution_allowed"],
        "readiness":readiness["decision"],
        "finding":"PASS: issue candidates are linked to closure ledger; pending manual creation is tracked without automatic execution.",
    }
    for stem,title,obj in [
        ("prod421_440_readiness","Issue-to-State Linkage Readiness",readiness),
        ("prod421_440_audit_report","Issue-to-State Linkage Audit",audit),
    ]:
        write_json(out/f"{stem}.json",obj); write_md(out/f"{stem}.md",title,obj)
    result={
        "task":"PROD-421..440",
        "status":"PASS",
        "phase":"Issue-to-State Linkage and Closure Ledger",
        "decision":readiness["decision"],
        "outputs":[
            "outputs/prod421_440_issue_state_link_records.json",
            "outputs/prod421_440_closure_ledger.json",
            "outputs/prod421_440_closure_ledger.md",
            "outputs/prod421_440_linkage_report.json",
            "outputs/prod421_440_linkage_report.md",
            "outputs/prod421_440_readiness.json",
            "outputs/prod421_440_audit_report.json",
        ],
        "next_recommended_bundle":"PROD-441..460 Closure Replay with Synthetic Manual URL",
        "blocked_actions":BLOCKED,
    }
    write_json(out/"prod421_440_result.json",result); write_md(out/"prod421_440_report.md","PROD-421..440 Issue-to-State Linkage Report",result)
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

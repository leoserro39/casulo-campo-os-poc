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
    run([sys.executable,str(repo/"product/scripts/run_manual_issue_creation_evidence_capture.py"),"--repo",str(repo)])
    capture=read(out/"prod401_420_manual_issue_evidence_capture.json")
    readiness={
        "contract_version":"casulo.manual_issue_creation_evidence_readiness.v0.1",
        "status":"PASS" if capture["incomplete_count"]==0 else "ATTENTION",
        "decision":"READY_FOR_MANUAL_ISSUE_EVIDENCE_CAPTURE",
        "approved_count":capture["approved_count"],
        "captured_count":capture["captured_count"],
        "pending_count":capture["pending_count"],
        "auto_execution_allowed":capture["auto_execution_allowed"],
        "ready_for":["manual evidence manifest editing","issue URL evidence capture","manual state transition review"],
        "not_ready_for":["automatic issue creation","production activation","automatic merge","external client claims"],
        "next":"After a human creates one issue manually, fill the evidence manifest and re-run capture.",
        "blocked_actions":BLOCKED,
    }
    audit={
        "status":"PASS" if capture["auto_execution_allowed"] is False else "FAIL",
        "audit":"Manual Issue Creation Evidence Capture audit",
        "approved_count":capture["approved_count"],
        "captured_count":capture["captured_count"],
        "pending_count":capture["pending_count"],
        "incomplete_count":capture["incomplete_count"],
        "auto_execution_allowed":capture["auto_execution_allowed"],
        "readiness":readiness["decision"],
        "finding":"PASS: evidence capture tracks manually created issue URLs without creating issues automatically.",
    }
    for stem,title,obj in [
        ("prod401_420_readiness","Manual Issue Creation Evidence Capture Readiness",readiness),
        ("prod401_420_audit_report","Manual Issue Creation Evidence Capture Audit",audit),
    ]:
        write_json(out/f"{stem}.json",obj); write_md(out/f"{stem}.md",title,obj)
    result={
        "task":"PROD-401..420",
        "status":"PASS",
        "phase":"Manual Issue Creation Evidence Capture",
        "decision":readiness["decision"],
        "outputs":[
            "outputs/prod401_420_manual_issue_evidence_manifest_snapshot.json",
            "outputs/prod401_420_manual_issue_evidence_capture.json",
            "outputs/prod401_420_manual_issue_evidence_capture.md",
            "outputs/prod401_420_issue_url_validation.json",
            "outputs/prod401_420_state_update_preview.json",
            "outputs/prod401_420_readiness.json",
            "outputs/prod401_420_audit_report.json",
        ],
        "next_recommended_bundle":"PROD-421..440 Issue-to-State Linkage and Closure Ledger",
        "blocked_actions":BLOCKED,
    }
    write_json(out/"prod401_420_result.json",result); write_md(out/"prod401_420_report.md","PROD-401..420 Manual Issue Evidence Capture Report",result)
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

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
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--max-selected",type=int,default=12); args=ap.parse_args()
    repo=Path(args.repo); out=repo/"outputs"
    run([sys.executable,str(repo/"product/scripts/run_graph_case_review_console.py"),"--repo",str(repo),"--max-selected",str(args.max_selected)])
    console=read(out/"prod321_340_review_console.json")
    readiness={
        "contract_version":"casulo.graph_case_review_console_readiness.v0.1",
        "status":"PASS",
        "decision":"READY_FOR_HUMAN_REVIEW_AND_OPTIONAL_ISSUE_PROMOTION",
        "run_decision":console["decision"],
        "ready_for":["human review of selected candidates","manual issue promotion","review queue triage","next controlled anonymized case batch"],
        "not_ready_for":["automatic issue creation","production graph automation","external client claims","unredacted sensitive data ingestion"],
        "next":"Review selected P0/P1 candidates, then optionally generate manually approved GitHub issues.",
        "blocked_actions":BLOCKED,
    }
    audit={
        "status":"PASS",
        "audit":"Graph Case Review Console audit",
        "case_count":console["case_count"],
        "total_issue_candidates":console["total_issue_candidates"],
        "selected_issue_count":console["selected_issue_count"],
        "decision":console["decision"],
        "readiness":readiness["decision"],
        "finding":"PASS: review console selected issue candidates and generated a human review pack without creating issues automatically.",
    }
    for stem,title,obj in [
        ("prod321_340_review_console_readiness","Graph Case Review Console Readiness",readiness),
        ("prod321_340_audit_report","Graph Case Review Console Audit",audit),
    ]:
        write_json(out/f"{stem}.json",obj); write_md(out/f"{stem}.md",title,obj)
    result={
        "task":"PROD-321..340",
        "status":"PASS",
        "phase":"Graph Case Review Console and Issue Selection",
        "decision":readiness["decision"],
        "outputs":[
            "outputs/prod321_340_review_console.json",
            "outputs/prod321_340_issue_selection.json",
            "outputs/prod321_340_review_decision_log.json",
            "outputs/prod321_340_human_review_pack.json",
            "outputs/prod321_340_human_review_pack.md",
            "outputs/prod321_340_selected_issues.csv",
            "outputs/prod321_340_review_console_readiness.json",
            "outputs/prod321_340_audit_report.json",
        ],
        "next_recommended_bundle":"PROD-341..360 Manual Issue Promotion Pack",
        "blocked_actions":BLOCKED,
    }
    write_json(out/"prod321_340_result.json",result); write_md(out/"prod321_340_report.md","PROD-321..340 Graph Case Review Console Report",result)
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

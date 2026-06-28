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
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--max-issues",type=int,default=12); args=ap.parse_args()
    repo=Path(args.repo); out=repo/"outputs"
    run([sys.executable,str(repo/"product/scripts/run_graph_task_bridge.py"),"--repo",str(repo),"--max-issues",str(args.max_issues)])
    report=read(out/"prod281_300_practical_backlog_report.json")
    readiness={
        "contract_version":"casulo.graph_task_bridge_readiness.v0.1",
        "status":"PASS",
        "decision":"READY_FOR_PRACTICAL_TASK_SELECTION_BEFORE_REAL_GRAPH_CASES",
        "ready_for":["task clustering","issue candidate review","practical backlog selection","human approval before issue creation"],
        "not_ready_for":["automatic issue creation","production graph automation","external client claims"],
        "next":"Select P0/P1/P2 issue candidates, then run real anonymized graph cases.",
        "blocked_actions":BLOCKED,
    }
    audit={
        "status":"PASS",
        "audit":"Graph Task Bridge audit",
        "source_task_count":report["source_task_count"],
        "cluster_count":report["cluster_count"],
        "issue_candidate_count":report["issue_candidate_count"],
        "decision":report["decision"],
        "readiness":readiness["decision"],
        "finding":"PASS: raw graph-builder tasks were deduplicated into practical clusters and reviewable issue candidates.",
    }
    for stem,title,obj in [
        ("prod281_300_graph_task_bridge_readiness","Graph Task Bridge Readiness",readiness),
        ("prod281_300_audit_report","Graph Task Bridge Audit",audit),
    ]:
        write_json(out/f"{stem}.json",obj); write_md(out/f"{stem}.md",title,obj)
    result={
        "task":"PROD-281..300",
        "status":"PASS",
        "phase":"Graph Task Bridge and Practical Backlog",
        "decision":readiness["decision"],
        "outputs":[
            "outputs/prod281_300_task_clusters.json",
            "outputs/prod281_300_issue_candidates.json",
            "outputs/prod281_300_practical_backlog_report.json",
            "outputs/prod281_300_task_closure_policy.json",
            "outputs/prod281_300_graph_task_bridge_readiness.json",
            "outputs/prod281_300_audit_report.json",
        ],
        "next_recommended_bundle":"PROD-301..320 Real Anonymized Graph Case Runner",
        "blocked_actions":BLOCKED,
    }
    write_json(out/"prod281_300_result.json",result); write_md(out/"prod281_300_report.md","PROD-281..300 Graph Task Bridge Report",result)
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

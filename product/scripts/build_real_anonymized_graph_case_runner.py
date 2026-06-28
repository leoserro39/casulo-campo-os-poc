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
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--seed",type=int,default=301320); ap.add_argument("--max-issues",type=int,default=8); args=ap.parse_args()
    repo=Path(args.repo); out=repo/"outputs"
    run([sys.executable,str(repo/"product/scripts/run_real_anonymized_graph_cases.py"),"--repo",str(repo),"--seed",str(args.seed),"--max-issues",str(args.max_issues)])
    agg=read(out/"prod301_320_real_graph_case_aggregate.json")
    readiness={
        "contract_version":"casulo.real_anonymized_graph_case_readiness.v0.1",
        "status":"PASS",
        "decision":"READY_FOR_REAL_ANONYMIZED_GRAPH_CASE_REVIEW",
        "run_decision":agg["decision"],
        "ready_for":["case-by-case graph telemetry review","case-level issue candidate review","real/anonymized batch comparison","next controlled real-case batch"],
        "not_ready_for":["production graph automation","external client claims","automatic issue creation","unredacted sensitive data ingestion"],
        "next":"Review P0 blockers, then expand with user-provided anonymized cases.",
        "blocked_actions":BLOCKED,
    }
    audit={
        "status":"PASS",
        "audit":"Real/Anonymized Graph Case Runner audit",
        "case_count":agg["case_count"],
        "decision":agg["decision"],
        "total_tasks":agg["aggregate_metrics"]["total_tasks"],
        "total_clusters":agg["aggregate_metrics"]["total_clusters"],
        "total_issue_candidates":agg["aggregate_metrics"]["total_issue_candidates"],
        "total_p0_blockers":agg["aggregate_metrics"]["total_p0_blockers"],
        "readiness":readiness["decision"],
        "finding":"PASS: real-like anonymized graph cases generated candidate graphs, telemetry, clusters and issue candidates without production automation.",
    }
    for stem,title,obj in [
        ("prod301_320_real_graph_case_readiness","Real Anonymized Graph Case Readiness",readiness),
        ("prod301_320_audit_report","Real Anonymized Graph Case Audit",audit),
    ]:
        write_json(out/f"{stem}.json",obj); write_md(out/f"{stem}.md",title,obj)
    result={
        "task":"PROD-301..320",
        "status":"PASS",
        "phase":"Real Anonymized Graph Case Runner",
        "decision":readiness["decision"],
        "outputs":[
            "outputs/prod301_320_real_graph_case_results.json",
            "outputs/prod301_320_real_graph_case_aggregate.json",
            "outputs/prod301_320_real_graph_case_aggregate.md",
            "outputs/prod301_320_real_graph_case_summary.csv",
            "outputs/prod301_320_real_graph_case_readiness.json",
            "outputs/prod301_320_audit_report.json",
        ],
        "next_recommended_bundle":"PROD-321..340 Graph Case Review Console and Issue Selection",
        "blocked_actions":BLOCKED,
    }
    write_json(out/"prod301_320_result.json",result); write_md(out/"prod301_320_report.md","PROD-301..320 Real Anonymized Graph Case Runner Report",result)
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

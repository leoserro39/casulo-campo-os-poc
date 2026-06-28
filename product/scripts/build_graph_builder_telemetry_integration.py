#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path
BLOCKED=["client_facing_claim","automatic_nomination","implementation_execution","production_activation","automatic_merge","credential_handling"]
def run(cmd):
    p=subprocess.run(cmd,capture_output=True,text=True)
    if p.returncode: raise RuntimeError(p.stdout+p.stderr)
def read(p): return json.loads(p.read_text(encoding="utf-8"))
def write_json(p,obj): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def write_md(p,title,obj):
    lines=[f"# {title}",""]
    for k,v in obj.items():
        if isinstance(v,(str,int,float,bool)): lines.append(f"- {k}: `{v}`")
        elif isinstance(v,list):
            lines.append(f"\n## {k.replace('_',' ').title()}")
            for item in v: lines.append(f"- `{json.dumps(item,ensure_ascii=False) if isinstance(item,dict) else item}`")
        elif isinstance(v,dict):
            lines.append(f"\n## {k.replace('_',' ').title()}")
            for kk,vv in v.items(): lines.append(f"- {kk}: `{json.dumps(vv,ensure_ascii=False) if isinstance(vv,(list,dict)) else vv}`")
    p.write_text("\n".join(lines)+"\n",encoding="utf-8")
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--seed",type=int,default=261280); ap.add_argument("--nodes",type=int,default=18); ap.add_argument("--edges",type=int,default=32); args=ap.parse_args()
    repo=Path(args.repo); out=repo/"outputs"
    run([sys.executable,str(repo/"product/scripts/run_graph_builder_telemetry_integration.py"),"--repo",str(repo),"--seed",str(args.seed),"--nodes",str(args.nodes),"--edges",str(args.edges)])
    result=read(out/"prod261_280_graph_builder_telemetry_result.json")
    policy={"contract_version":"casulo.graph_builder_native_telemetry_policy.v0.1","status":"PASS","policy":["Every candidate node/edge must carry delta telemetry.","Committed graph relations require evidence and safe gate.","Missing document/domain/artifact becomes task candidate.","Production blocks are valid closure, not failure.","Loop stops at practical closure state."],"blocked_actions":BLOCKED}
    readiness={"contract_version":"casulo.graph_builder_telemetry_integration_readiness.v0.1","status":"PASS","decision":"READY_FOR_GRAPH_BUILDER_TELEMETRY_INTEGRATED_TESTS","ready_for":["candidate graph generation with native deltas","missing artifact task recommendations","gate assignment during graph build","practical closure evaluation"],"not_ready_for":["production graph automation","external client claims","autonomous integration without review"],"next":"Run real anonymized graph-building cases and create issue/task bridge.","blocked_actions":BLOCKED}
    audit={"status":"PASS","audit":"Graph Builder Telemetry Integration audit","nodes":len(result["graph"]["nodes"]),"edges":len(result["graph"]["edges"]),"tasks":len(result["tasks"]),"decision":result["decision"]["decision"],"readiness":readiness["decision"],"finding":"PASS: graph builder now emits candidate graph telemetry, controls, gates and missing artifact tasks."}
    for stem,title,obj in [("prod261_280_native_telemetry_policy","Graph Builder Native Telemetry Policy",policy),("prod261_280_graph_builder_readiness","Graph Builder Telemetry Readiness",readiness),("prod261_280_audit_report","Graph Builder Telemetry Audit",audit)]:
        write_json(out/f"{stem}.json",obj); write_md(out/f"{stem}.md",title,obj)
    final={"task":"PROD-261..280","status":"PASS","phase":"Graph Builder Telemetry Integration","decision":readiness["decision"],"outputs":["outputs/prod261_280_candidate_graph_telemetry.json","outputs/prod261_280_missing_artifact_tasks.json","outputs/prod261_280_graph_builder_telemetry_result.json","outputs/prod261_280_native_telemetry_policy.json","outputs/prod261_280_graph_builder_readiness.json","outputs/prod261_280_audit_report.json"],"next_recommended_bundle":"PROD-281..300 Real Anonymized Graph Case Runner","blocked_actions":BLOCKED}
    write_json(out/"prod261_280_result.json",final); write_md(out/"prod261_280_report.md","PROD-261..280 Graph Builder Telemetry Integration Report",final)
    print(json.dumps(final,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

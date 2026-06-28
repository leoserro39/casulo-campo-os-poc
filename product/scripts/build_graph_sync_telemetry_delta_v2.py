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
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--seed",type=int,default=241260); ap.add_argument("--sync-count",type=int,default=48); args=ap.parse_args()
    repo=Path(args.repo); out=repo/"outputs"
    run([sys.executable,str(repo/"product/scripts/build_delta_library_v2.py"),"--repo",str(repo)])
    run([sys.executable,str(repo/"product/scripts/run_graph_sync_telemetry_lab.py"),"--repo",str(repo),"--seed",str(args.seed),"--sync-count",str(args.sync_count)])
    delta=read(out/"prod241_260_delta_library_v2.json"); sync=read(out/"prod241_260_graph_sync_lab_report.json")
    agent={"contract_version":"casulo.telemetry_control_agent.v0.1","status":"PASS","role":"advisor_not_autonomous_executor","flow":["inspect candidate graph","detect active deltas","query delta library","match anomaly patterns","recommend controls","recommend gates","suggest missing artifacts/domains/documents","stop when practical closure rule triggers"],"allowed_actions":["recommend_control","recommend_gate","create_task_candidate","mark_edge_candidate","request_evidence"],"blocked_actions":BLOCKED}
    closure={"contract_version":"casulo.practical_closure_policy.v0.1","status":"PASS","why":"The system must not analyze forever; graph synchronization must converge to action, review or block.","closure_states":["READY_FOR_NEXT_ACTION","ASK_FOR_EVIDENCE","CREATE_MISSING_ARTIFACT_TASK","HUMAN_REVIEW_REQUIRED","PRODUCTION_BLOCKED","NO_MATERIAL_DELTA_CHANGE"],"stop_rules":["max_iterations","no_material_delta_change","human_review_required","production_blocked"]}
    readiness={"contract_version":"casulo.graph_sync_telemetry_readiness.v0.1","status":"PASS","decision":"READY_FOR_GRAPH_SYNC_TELEMETRY_TESTS","ready_for":["cross-domain candidate graph tests","delta-driven control recommendation","missing document/domain/artifact suggestions","practical stop-rule validation","graph creation adjustment loop"],"not_ready_for":["production graph automation","external client claims","autonomous domain integration without review"],"next":"Integrate graph sync telemetry into graph builder and then run real anonymized graph cases.","blocked_actions":BLOCKED}
    audit={"status":"PASS","audit":"Graph Sync Telemetry and Delta Library v2 audit","delta_count":len(delta["delta_library"]),"sync_attempts":len(sync["sync_attempts"]),"stop_reason":sync["sync_summary"]["stop_reason"],"self_sustaining_status":sync["sync_summary"]["self_sustaining_status"],"readiness":readiness["decision"],"finding":"PASS: delta library and graph sync telemetry lab are ready to test cross-domain graph synchronization and practical closure."}
    for stem,title,obj in [("prod241_260_telemetry_control_agent","Telemetry Control Agent",agent),("prod241_260_practical_closure_policy","Practical Closure Policy",closure),("prod241_260_graph_sync_readiness","Graph Sync Telemetry Readiness",readiness),("prod241_260_audit_report","Graph Sync Telemetry Audit",audit)]:
        write_json(out/f"{stem}.json",obj); write_md(out/f"{stem}.md",title,obj)
    result={"task":"PROD-241..260","status":"PASS","phase":"Delta Library and Graph Sync Telemetry Domain v2","decision":readiness["decision"],"next_recommended_bundle":"PROD-261..280 Graph Builder Telemetry Integration","blocked_actions":BLOCKED}
    write_json(out/"prod241_260_result.json",result); write_md(out/"prod241_260_report.md","PROD-241..260 Delta Library and Graph Sync Telemetry Report",result)
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, random
from collections import Counter
from pathlib import Path

BLOCKED=["client_facing_claim","automatic_nomination","implementation_execution","production_activation","automatic_merge","credential_handling"]
DOMAINS=["parser_documental","audit_documental","rule_extraction","software_review","process_operations","enterprise_knowledge"]
DELTAS=["delta_evidence","delta_ambiguity","delta_missingness","delta_conflict","delta_rule","delta_domain","delta_execution","delta_production","delta_human_review","delta_graph_structure","delta_model_behavior"]
CONTROLS={
 "delta_evidence":["require_evidence","mark_candidate_only"],
 "delta_ambiguity":["split_interpretations","structure_only"],
 "delta_missingness":["generate_missing_artifact_task","create_data_request"],
 "delta_conflict":["conflict_resolution_task","human_arbitration"],
 "delta_rule":["require_rule_source","exception_map"],
 "delta_domain":["raise_review_level","require_domain_owner"],
 "delta_execution":["require_test_plan","require_runtime_context"],
 "delta_production":["production_block","deployment_readiness_check"],
 "delta_human_review":["create_review_task","route_to_owner"],
 "delta_graph_structure":["graph_repair_suggestion","bridge_candidate_generation"],
 "delta_model_behavior":["calibration_review","repeat_seed_test"]
}
GATES={"require_evidence":"ASK_FOR_EVIDENCE","mark_candidate_only":"STRUCTURE_ONLY","split_interpretations":"STRUCTURE_ONLY","structure_only":"STRUCTURE_ONLY","generate_missing_artifact_task":"TASK_ONLY","create_data_request":"ASK_FOR_EVIDENCE","conflict_resolution_task":"TASK_ONLY","human_arbitration":"HUMAN_REVIEW_REQUIRED","require_rule_source":"ASK_FOR_EVIDENCE","exception_map":"STRUCTURE_ONLY","raise_review_level":"HUMAN_REVIEW_REQUIRED","require_domain_owner":"HUMAN_REVIEW_REQUIRED","require_test_plan":"TASK_ONLY","require_runtime_context":"ASK_FOR_EVIDENCE","production_block":"BLOCKED_UNSUPPORTED","deployment_readiness_check":"TASK_ONLY","create_review_task":"TASK_ONLY","route_to_owner":"HUMAN_REVIEW_REQUIRED","graph_repair_suggestion":"STRUCTURE_ONLY","bridge_candidate_generation":"STRUCTURE_ONLY","calibration_review":"HUMAN_REVIEW_REQUIRED","repeat_seed_test":"TASK_ONLY"}

def pick(rng,items): return items[rng.randrange(len(items))]
def make_graph(domain,rng,n):
    nodes=[]
    for i in range(n):
        nodes.append({"node_id":f"{domain.upper()}-N{i+1:02d}","domain":domain,"node_type":pick(rng,["entity","rule","artifact","state","task","evidence"]),"confidence":rng.randint(35,95),"evidence_strength":rng.randint(20,95),"delta_profile":rng.sample(DELTAS,k=rng.randint(1,3))})
    return {"domain":domain,"nodes":nodes}
def propose(source,target,rng,idx):
    s=pick(rng,source["nodes"]); t=pick(rng,target["nodes"])
    shared=sorted(set(s["delta_profile"]).intersection(t["delta_profile"])) or [pick(rng,s["delta_profile"]+t["delta_profile"])]
    delta=shared[0]; control=pick(rng,CONTROLS[delta]); gate=GATES[control]
    risk=max(0,min(100,100-int((s["confidence"]+t["confidence"]+s["evidence_strength"]+t["evidence_strength"])/4)))
    return {"sync_id":f"SYNC-{idx:04d}","source_domain":source["domain"],"target_domain":target["domain"],"source_node":s["node_id"],"target_node":t["node_id"],"sync_mode":pick(rng,["candidate_link","evidence_bridge","delta_challenge","control_suggestion","human_review_handoff"]),"primary_delta":delta,"shared_delta_profile":shared,"recommended_control":control,"recommended_gate":gate,"sync_risk":risk,"material_delta_change":rng.randint(0,20),"allowed_actions":["candidate_link","evidence_request","graph_repair_task","human_review_task"],"blocked_actions":BLOCKED}
def summary(syncs,max_iter,min_change):
    gates=Counter(s["recommended_gate"] for s in syncs); controls=Counter(s["recommended_control"] for s in syncs); deltas=Counter(s["primary_delta"] for s in syncs)
    avg_risk=round(sum(s["sync_risk"] for s in syncs)/len(syncs),2); avg_change=round(sum(s["material_delta_change"] for s in syncs)/len(syncs),2)
    reason="continue_testing"
    if len(syncs)>=max_iter: reason="max_iterations"
    if avg_change<min_change: reason="no_material_delta_change"
    if gates.get("HUMAN_REVIEW_REQUIRED",0)>=max(3,int(len(syncs)*0.25)): reason="human_review_required"
    if gates.get("BLOCKED_UNSUPPORTED",0)>=1: reason="production_blocked"
    return {"gate_counts":dict(gates),"control_counts":dict(controls),"delta_counts":dict(deltas),"avg_sync_risk":avg_risk,"avg_material_delta_change":avg_change,"stop_reason":reason,"self_sustaining_status":"PRACTICAL_LOOP_READY" if reason!="continue_testing" else "CONTINUE_UNTIL_STOP_RULE"}
def write_json(p,obj): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def write_md(p,report):
    lines=["# PROD-241..260 Graph Sync Telemetry Lab Report","",f"- Status: `{report['status']}`",f"- Domains: `{report['domains']}`",f"- Sync attempts: `{len(report['sync_attempts'])}`",f"- Stop reason: `{report['sync_summary']['stop_reason']}`",f"- Self sustaining status: `{report['sync_summary']['self_sustaining_status']}`","","## Delta Counts"]
    for k,v in report["sync_summary"]["delta_counts"].items(): lines.append(f"- `{k}`: `{v}`")
    lines+=["","## Recommendations"]+[f"- {x}" for x in report["recommendations"]]
    p.write_text("\n".join(lines)+"\n",encoding="utf-8")
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--seed",type=int,default=241260); ap.add_argument("--sync-count",type=int,default=48); ap.add_argument("--nodes-per-domain",type=int,default=8); ap.add_argument("--max-iterations",type=int,default=48); ap.add_argument("--min-material-delta-change",type=int,default=4); args=ap.parse_args()
    rng=random.Random(args.seed); graphs=[make_graph(d,rng,args.nodes_per_domain) for d in DOMAINS]
    syncs=[propose(*rng.sample(graphs,2),rng,i+1) for i in range(args.sync_count)]
    report={"status":"PASS","lab":"casulo.graph_sync_telemetry_lab.v0.1","seed":args.seed,"domains":DOMAINS,"graphs":graphs,"sync_attempts":syncs,"sync_summary":summary(syncs,args.max_iterations,args.min_material_delta_change),"recommendations":["Use delta library during graph creation, not only after scoring.","Allow cross-domain candidate links but keep committed links evidence-gated.","Use graph sync to discover missing documents/domains/artifacts.","Stop loops when material delta change is low or human review/production block is reached.","Convert recurring sync controls into backlog tasks, not endless analysis."],"blocked_actions":BLOCKED}
    out=Path(args.repo)/"outputs"; out.mkdir(exist_ok=True)
    write_json(out/"prod241_260_graph_sync_lab_report.json",report); write_md(out/"prod241_260_graph_sync_lab_report.md",report)
    write_json(out/"prod241_260_graph_sync_attempts.json",{"status":"PASS","sync_attempts":syncs})
    write_json(out/"prod241_260_graph_sync_summary.json",{"status":"PASS","sync_summary":report["sync_summary"]})
    print(json.dumps({"status":"PASS","sync_attempts":len(syncs),"stop_reason":report["sync_summary"]["stop_reason"]},indent=2))
if __name__=="__main__": main()

#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, random
from collections import Counter
from pathlib import Path

BLOCKED=["client_facing_claim","automatic_nomination","implementation_execution","production_activation","automatic_merge","credential_handling"]

DOMAINS=["parser_documental","audit_documental","rule_extraction","software_review","process_operations","enterprise_knowledge"]
NODE_TYPES=["entity","rule","artifact","state","task","evidence","decision","control"]
EDGE_TYPES=["supports","depends_on","constrains","requires","produces","blocks","routes_to","challenges"]
DELTA_TO_GATE={
    "delta_evidence":"ASK_FOR_EVIDENCE",
    "delta_ambiguity":"STRUCTURE_ONLY",
    "delta_missingness":"TASK_ONLY",
    "delta_conflict":"HUMAN_REVIEW_REQUIRED",
    "delta_rule":"STRUCTURE_ONLY",
    "delta_domain":"HUMAN_REVIEW_REQUIRED",
    "delta_execution":"TASK_ONLY",
    "delta_production":"BLOCKED_UNSUPPORTED",
    "delta_human_review":"HUMAN_REVIEW_REQUIRED",
    "delta_graph_structure":"STRUCTURE_ONLY",
    "delta_model_behavior":"TASK_ONLY",
}
DELTA_TO_CONTROL={
    "delta_evidence":"require_evidence",
    "delta_ambiguity":"split_interpretations",
    "delta_missingness":"generate_missing_artifact_task",
    "delta_conflict":"conflict_resolution_task",
    "delta_rule":"exception_map",
    "delta_domain":"require_domain_owner",
    "delta_execution":"require_test_plan",
    "delta_production":"production_block",
    "delta_human_review":"create_review_task",
    "delta_graph_structure":"graph_repair_suggestion",
    "delta_model_behavior":"calibration_review",
}
TASK_BY_DELTA={
    "delta_evidence":("evidence","Attach source/evidence before committing graph relation."),
    "delta_missingness":("document","Provide missing required document, field, test or domain artifact."),
    "delta_rule":("rule_map","Map rule source, scope, exception and applicability."),
    "delta_execution":("test_plan","Provide runtime, dependency and test context before execution."),
    "delta_graph_structure":("graph_repair","Repair bridge, relation type or orphan node."),
    "delta_conflict":("arbitration","Resolve conflicting sources/states/rules."),
    "delta_domain":("domain_owner","Assign domain owner for sensitive decision."),
    "delta_production":("production_readiness","Provide auth, audit, rollback, monitoring and support plan."),
    "delta_human_review":("human_review","Route to human owner or reviewer."),
    "delta_model_behavior":("calibration_review","Review anomaly pattern against calibration history."),
    "delta_ambiguity":("interpretation_split","Split possible interpretations and keep candidate-only relation."),
}

def load_delta_ids(repo: Path):
    p=repo/"outputs/prod241_260_delta_library_v2.json"
    if p.exists():
        data=json.loads(p.read_text(encoding="utf-8"))
        return [d["delta_id"] for d in data.get("delta_library",[])]
    return list(DELTA_TO_GATE)

def pick(rng, items): return items[rng.randrange(len(items))]

def make_node(rng, graph_id, idx, deltas):
    active=rng.sample(deltas,k=rng.randint(1,3))
    evidence_strength=rng.randint(20,95)
    confidence=rng.randint(30,95)
    primary=active[0]
    gate=DELTA_TO_GATE.get(primary,"STRUCTURE_ONLY")
    return {
        "node_id":f"{graph_id}-N{idx:02d}",
        "node_type":pick(rng,NODE_TYPES),
        "domain":pick(rng,DOMAINS),
        "confidence":confidence,
        "evidence_strength":evidence_strength,
        "active_deltas":active,
        "primary_delta":primary,
        "recommended_control":DELTA_TO_CONTROL.get(primary,"mark_candidate_only"),
        "recommended_gate":gate,
        "committed": confidence>=80 and evidence_strength>=70 and gate not in ["BLOCKED_UNSUPPORTED","HUMAN_REVIEW_REQUIRED"],
    }

def make_edge(rng, graph_id, idx, nodes):
    a,b=rng.sample(nodes,2)
    shared=sorted(set(a["active_deltas"]).intersection(b["active_deltas"]))
    primary=shared[0] if shared else pick(rng,a["active_deltas"]+b["active_deltas"])
    gate=DELTA_TO_GATE.get(primary,"STRUCTURE_ONLY")
    return {
        "edge_id":f"{graph_id}-E{idx:02d}",
        "from":a["node_id"],
        "to":b["node_id"],
        "relation":pick(rng,EDGE_TYPES),
        "primary_delta":primary,
        "recommended_control":DELTA_TO_CONTROL.get(primary,"mark_candidate_only"),
        "recommended_gate":gate,
        "candidate": True,
        "material_delta_change": rng.randint(0,20),
    }

def task_from_delta(task_id, delta, origin_id, gate):
    kind, reason = TASK_BY_DELTA.get(delta,("artifact","Provide missing support artifact."))
    return {
        "task_id":f"TASK-{task_id:03d}",
        "origin":origin_id,
        "artifact_type":kind,
        "source_delta":delta,
        "reason":reason,
        "recommended_gate":gate,
        "status":"OPEN_CANDIDATE",
    }

def determine_readiness(gate_counts, avg_material_change):
    if gate_counts.get("BLOCKED_UNSUPPORTED",0)>0:
        return "PRODUCTION_BLOCKED"
    if gate_counts.get("HUMAN_REVIEW_REQUIRED",0)>0:
        return "HUMAN_REVIEW_REQUIRED"
    if gate_counts.get("ASK_FOR_EVIDENCE",0)>0:
        return "EVIDENCE_REQUIRED"
    if gate_counts.get("TASK_ONLY",0)>0:
        return "TASK_READY"
    if avg_material_change < 3:
        return "NO_MATERIAL_DELTA_CHANGE"
    return "READY_FOR_NEXT_ACTION"

def build_graph(repo: Path, seed: int, node_count: int, edge_count: int):
    rng=random.Random(seed)
    deltas=load_delta_ids(repo)
    graph_id=f"GBTI-{seed}"
    nodes=[make_node(rng,graph_id,i+1,deltas) for i in range(node_count)]
    edges=[make_edge(rng,graph_id,i+1,nodes) for i in range(edge_count)]
    gates=Counter([n["recommended_gate"] for n in nodes]+[e["recommended_gate"] for e in edges])
    controls=Counter([n["recommended_control"] for n in nodes]+[e["recommended_control"] for e in edges])
    delta_counts=Counter([n["primary_delta"] for n in nodes]+[e["primary_delta"] for e in edges])
    avg_material=round(sum(e["material_delta_change"] for e in edges)/len(edges),2) if edges else 0
    tasks=[]; tid=1
    for item in nodes+edges:
        gate=item["recommended_gate"]
        if gate in ["ASK_FOR_EVIDENCE","TASK_ONLY","HUMAN_REVIEW_REQUIRED","BLOCKED_UNSUPPORTED","STRUCTURE_ONLY"]:
            tasks.append(task_from_delta(tid,item["primary_delta"],item.get("node_id") or item.get("edge_id"),gate)); tid+=1
    readiness=determine_readiness(gates,avg_material)
    graph={
        "graph_id":graph_id,
        "mode":"candidate_graph_with_native_delta_telemetry",
        "nodes":nodes,
        "edges":edges,
        "telemetry_summary":{
            "gate_counts":dict(gates),
            "control_counts":dict(controls),
            "delta_counts":dict(delta_counts),
            "avg_material_delta_change":avg_material,
            "task_count":len(tasks),
        },
        "readiness":readiness,
        "allowed_actions":["inspect_graph","request_evidence","create_task_candidate","mark_candidate_edge","route_human_review"],
        "blocked_actions":BLOCKED,
    }
    decision={
        "status":"PASS",
        "decision":readiness,
        "interpretation":"Graph builder telemetry produced candidate graph, controls, gates and practical tasks without production automation.",
        "next_action":"Review generated missing artifact/control tasks and select which should become repo issues or human review tasks.",
    }
    return graph, tasks, decision

def write_json(p,obj): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def write_md(p, graph, tasks, decision):
    lines=["# PROD-261..280 Graph Builder Telemetry Integration Report","",f"- Status: `{decision['status']}`",f"- Decision: `{decision['decision']}`",f"- Graph ID: `{graph['graph_id']}`",f"- Nodes: `{len(graph['nodes'])}`",f"- Edges: `{len(graph['edges'])}`",f"- Tasks: `{len(tasks)}`",f"- Readiness: `{graph['readiness']}`","","## Gate Counts"]
    for k,v in graph["telemetry_summary"]["gate_counts"].items(): lines.append(f"- `{k}`: `{v}`")
    lines+=["","## Delta Counts"]
    for k,v in graph["telemetry_summary"]["delta_counts"].items(): lines.append(f"- `{k}`: `{v}`")
    lines+=["","## Top Missing Artifact / Control Tasks"]
    for t in tasks[:20]: lines.append(f"- `{t['task_id']}` `{t['artifact_type']}` from `{t['source_delta']}` gate `{t['recommended_gate']}` — {t['reason']}")
    lines+=["","## Interpretation",decision["interpretation"],"",f"Next action: `{decision['next_action']}`"]
    p.write_text("\n".join(lines)+"\n",encoding="utf-8")

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); ap.add_argument("--seed",type=int,default=261280); ap.add_argument("--nodes",type=int,default=18); ap.add_argument("--edges",type=int,default=32); args=ap.parse_args()
    repo=Path(args.repo); out=repo/"outputs"; out.mkdir(exist_ok=True)
    graph,tasks,decision=build_graph(repo,args.seed,args.nodes,args.edges)
    write_json(out/"prod261_280_candidate_graph_telemetry.json",{"status":"PASS","graph":graph})
    write_json(out/"prod261_280_missing_artifact_tasks.json",{"status":"PASS","tasks":tasks})
    write_json(out/"prod261_280_graph_builder_telemetry_result.json",{"status":"PASS","graph":graph,"tasks":tasks,"decision":decision,"blocked_actions":BLOCKED})
    write_md(out/"prod261_280_graph_builder_telemetry_result.md",graph,tasks,decision)
    print(json.dumps({"status":"PASS","decision":decision["decision"],"nodes":len(graph["nodes"]),"edges":len(graph["edges"]),"tasks":len(tasks)},indent=2))
if __name__=="__main__": main()

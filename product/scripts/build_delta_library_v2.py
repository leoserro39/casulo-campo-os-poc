#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path

BLOCKED=["client_facing_claim","automatic_nomination","implementation_execution","production_activation","automatic_merge","credential_handling"]

DELTA_LIBRARY=[
 {"delta_id":"delta_evidence","definition":"Gap between claim/action and supporting evidence.","symptoms":["missing source","weak traceability","source conflict"],"metrics":["evidence_strength","evidence_coverage","unsupported_fields"],"controls":["require_evidence","mark_candidate_only","ask_for_source"],"gates":["ASK_FOR_EVIDENCE","PARTIAL_ANSWER_ALLOWED"],"graph_effect":"edge remains candidate until evidence bridge exists"},
 {"delta_id":"delta_ambiguity","definition":"Semantic uncertainty in terms, scope, entities or intent.","symptoms":["multiple meanings","unclear scope","ambiguous entity"],"metrics":["ambiguity_level","scope_ambiguity"],"controls":["split_interpretations","structure_only","add_assumption_marker"],"gates":["STRUCTURE_ONLY","PARTIAL_ANSWER_ALLOWED"],"graph_effect":"create alternative candidate nodes/edges"},
 {"delta_id":"delta_missingness","definition":"Required information is objectively absent.","symptoms":["missing field","missing document","missing test"],"metrics":["missingness_level","missing_required_fields"],"controls":["generate_missing_artifact_task","create_data_request"],"gates":["TASK_ONLY","ASK_FOR_EVIDENCE"],"graph_effect":"add missing artifact node and unresolved dependency edge"},
 {"delta_id":"delta_conflict","definition":"Signals contradict each other.","symptoms":["field conflict","rule conflict","source conflict"],"metrics":["conflict_level","contradiction_count"],"controls":["conflict_resolution_task","human_arbitration"],"gates":["HUMAN_REVIEW_REQUIRED","STRUCTURE_ONLY"],"graph_effect":"create conflict edge and arbitration node"},
 {"delta_id":"delta_rule","definition":"Rule, exception, applicability or precedence is not computable yet.","symptoms":["ambiguous rule","missing exception","unknown precedence"],"metrics":["rule_gap","rule_exception_missing"],"controls":["require_rule_source","exception_map","applicability_test"],"gates":["STRUCTURE_ONLY","HUMAN_REVIEW_REQUIRED"],"graph_effect":"rule node remains candidate until source/scope/exception/test exist"},
 {"delta_id":"delta_domain","definition":"Risk caused by the sensitivity of the domain itself.","symptoms":["legal sensitivity","financial risk","technical production risk"],"metrics":["domain_risk","technical_sensitivity"],"controls":["raise_review_level","require_domain_owner"],"gates":["HUMAN_REVIEW_REQUIRED","PARTIAL_ANSWER_ALLOWED"],"graph_effect":"domain risk increases gate strictness"},
 {"delta_id":"delta_execution","definition":"Output is not safely executable with current context.","symptoms":["runtime unknown","dependencies unknown","tests missing"],"metrics":["execution_gap","test_gap"],"controls":["require_test_plan","require_runtime_context","no_write_action"],"gates":["TASK_ONLY","ASK_FOR_EVIDENCE"],"graph_effect":"execution edge blocked; create task node"},
 {"delta_id":"delta_production","definition":"Distance from prototype to production-grade operation.","symptoms":["auth missing","audit missing","rollback missing"],"metrics":["production_gap","auth_ready","audit_ready"],"controls":["production_block","deployment_readiness_check"],"gates":["BLOCKED_UNSUPPORTED","HUMAN_REVIEW_REQUIRED"],"graph_effect":"production activation edge blocked"},
 {"delta_id":"delta_human_review","definition":"Human decision, domain owner or arbitrator is needed.","symptoms":["judgment call","responsibility boundary"],"metrics":["human_decision_pending","review_required"],"controls":["create_review_task","route_to_owner"],"gates":["HUMAN_REVIEW_REQUIRED","TASK_ONLY"],"graph_effect":"create human review node"},
 {"delta_id":"delta_graph_structure","definition":"Graph topology is incomplete, disconnected or mistyped.","symptoms":["orphan node","missing bridge","wrong relation type"],"metrics":["orphan_nodes","missing_edges","invalid_edge_types"],"controls":["graph_repair_suggestion","bridge_candidate_generation"],"gates":["STRUCTURE_ONLY","TASK_ONLY"],"graph_effect":"suggest structural repairs before decision"},
 {"delta_id":"delta_model_behavior","definition":"Observed model behavior deviates from expected calibration pattern.","symptoms":["low ambiguity high hallucination","unexpected control drop"],"metrics":["anomaly_rate","casulo_hallucination","delta_control_score"],"controls":["calibration_review","repeat_seed_test"],"gates":["HUMAN_REVIEW_REQUIRED","TASK_ONLY"],"graph_effect":"telemetry node links anomaly pattern to control"}
]
CONTROL_CATALOG=[
 {"control_id":"require_evidence","delta_family":"delta_evidence","recommended_gate":"ASK_FOR_EVIDENCE","purpose":"Require source before claim/action."},
 {"control_id":"mark_candidate_only","delta_family":"delta_evidence","recommended_gate":"STRUCTURE_ONLY","purpose":"Keep node/edge candidate only."},
 {"control_id":"generate_missing_artifact_task","delta_family":"delta_missingness","recommended_gate":"TASK_ONLY","purpose":"Generate task for missing document/domain/artifact."},
 {"control_id":"human_arbitration","delta_family":"delta_conflict","recommended_gate":"HUMAN_REVIEW_REQUIRED","purpose":"Route conflict to human decision."},
 {"control_id":"exception_map","delta_family":"delta_rule","recommended_gate":"STRUCTURE_ONLY","purpose":"Map rule exceptions before computation."},
 {"control_id":"require_test_plan","delta_family":"delta_execution","recommended_gate":"TASK_ONLY","purpose":"Require tests before execution/code/deploy."},
 {"control_id":"production_block","delta_family":"delta_production","recommended_gate":"BLOCKED_UNSUPPORTED","purpose":"Block production activation."},
 {"control_id":"graph_repair_suggestion","delta_family":"delta_graph_structure","recommended_gate":"STRUCTURE_ONLY","purpose":"Suggest bridge/relation/topology repair."},
 {"control_id":"repeat_seed_test","delta_family":"delta_model_behavior","recommended_gate":"TASK_ONLY","purpose":"Repeat stochastic test when anomaly pattern appears."}
]
def write_json(p,obj): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(obj,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def write_md(p,title,rows):
    lines=[f"# {title}",""]
    for r in rows:
        lines.append(f"## {r.get('delta_id') or r.get('control_id')}")
        for k,v in r.items(): lines.append(f"- {k}: `{json.dumps(v,ensure_ascii=False) if isinstance(v,(list,dict)) else v}`")
        lines.append("")
    p.write_text("\n".join(lines),encoding="utf-8")
def main():
    import argparse
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    out=Path(args.repo)/"outputs"; out.mkdir(exist_ok=True)
    write_json(out/"prod241_260_delta_library_v2.json",{"status":"PASS","delta_library":DELTA_LIBRARY})
    write_md(out/"prod241_260_delta_library_v2.md","Delta Library v2",DELTA_LIBRARY)
    write_json(out/"prod241_260_control_catalog.json",{"status":"PASS","control_catalog":CONTROL_CATALOG})
    write_md(out/"prod241_260_control_catalog.md","Telemetry Control Catalog",CONTROL_CATALOG)
    print(json.dumps({"status":"PASS","delta_count":len(DELTA_LIBRARY),"control_count":len(CONTROL_CATALOG)},indent=2))
if __name__=="__main__": main()

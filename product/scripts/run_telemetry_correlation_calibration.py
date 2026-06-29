#!/usr/bin/env python3
from __future__ import annotations
import argparse, importlib.util, json, math
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

BLOCKED_ACTIONS=["client_facing_claim","automatic_nomination","implementation_execution","production_activation","automatic_merge","credential_handling"]
METRICS=["stress_score","direct_risk","cubo_risk","risk_reduction","relative_risk_reduction_pct","delta_control","evidence_coverage","useful_output_rate","anomaly_numeric","human_review_numeric","unsupported_numeric","safe_review_success","safe_block_success","true_failure_candidate"]

def write_json(p:Path,o:Any): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(json.dumps(o,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
def write_text(p:Path,t:str): p.parent.mkdir(parents=True,exist_ok=True); p.write_text(t,encoding="utf-8")
def mean(v): return round(sum(v)/len(v),4) if v else 0.0
def stdev(v):
    if len(v)<2: return 0.0
    m=sum(v)/len(v); return round(math.sqrt(sum((x-m)**2 for x in v)/(len(v)-1)),4)
def corr(xs,ys):
    if len(xs)!=len(ys) or len(xs)<2: return 0.0
    mx=sum(xs)/len(xs); my=sum(ys)/len(ys)
    num=sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    dx=math.sqrt(sum((x-mx)**2 for x in xs)); dy=math.sqrt(sum((y-my)**2 for y in ys))
    return 0.0 if dx==0 or dy==0 else round(num/(dx*dy),4)
def pct(n,t): return round(n*100/t,2) if t else 0.0

def load_rows(repo:Path)->List[Dict[str,Any]]:
    script=repo/"product/scripts/run_common_workload_calibration_stress_lab.py"
    if not script.exists(): raise FileNotFoundError("missing stress lab script")
    spec=importlib.util.spec_from_file_location("stress_lab", script)
    mod=importlib.util.module_from_spec(spec); assert spec.loader is not None; spec.loader.exec_module(mod)
    rows=[]
    for workload,input_class,expected_output in mod.WORKLOADS:
        for idx in range(1,101):
            rows.append(mod.score_case(mod.build_case(workload,input_class,expected_output,idx)))
    high={"high_stakes_claim","cross_document_mismatch","partial_context","stale_or_undated_evidence"}
    for r in rows:
        r["anomaly_numeric"]=1 if r.get("anomaly") else 0
        r["human_review_numeric"]=1 if r.get("gate")=="HUMAN_REVIEW_REQUIRED" else 0
        r["unsupported_numeric"]=1 if r.get("gate")=="UNSUPPORTED_BLOCKED" else 0
        r["safe_review_success"]=1 if r.get("gate")=="HUMAN_REVIEW_REQUIRED" and r.get("stress_profile") in high else 0
        r["safe_block_success"]=1 if r.get("gate")=="UNSUPPORTED_BLOCKED" and r.get("stress_profile")=="unknown_or_unsupported_input" else 0
        r["true_failure_candidate"]=1 if r.get("gate") in {"ANSWER_ALLOWED","PARSER_OUTPUT_ALLOWED","TASK_PROPOSAL_ALLOWED"} and r.get("cubo_risk",0)>=55 else 0
    return rows

def bounds(rows):
    out={}
    for m in METRICS:
        vals=[float(r.get(m,0)) for r in rows]
        out[m]={"min":round(min(vals),4),"max":round(max(vals),4),"mean":mean(vals),"stdev":stdev(vals)}
    return out
def group(rows,k):
    d=defaultdict(list)
    for r in rows: d[str(r.get(k,"UNKNOWN"))].append(r)
    return dict(d)
def matrix(rows):
    out={}
    for a in METRICS:
        out[a]={}
        xs=[float(r.get(a,0)) for r in rows]
        for b in METRICS:
            out[a][b]=corr(xs,[float(r.get(b,0)) for r in rows])
    return out
def strong(mat,thr=0.55):
    arr=[]; seen=set()
    for a,cols in mat.items():
        for b,val in cols.items():
            if a==b: continue
            key=tuple(sorted([a,b]))
            if key in seen: continue
            seen.add(key)
            if abs(val)>=thr:
                arr.append({"metric_a":a,"metric_b":b,"correlation":val,"direction":"positive" if val>0 else "negative","strength":"strong" if abs(val)>=0.75 else "moderate"})
    return sorted(arr,key=lambda x:abs(x["correlation"]), reverse=True)
def zone(name, rows):
    b=bounds(rows) if rows else {}
    return {"zone":name,"case_count":len(rows),"cubo_risk_range":[b.get("cubo_risk",{}).get("min",0),b.get("cubo_risk",{}).get("max",0)],"cubo_risk_mean":b.get("cubo_risk",{}).get("mean",0),"delta_control_mean":b.get("delta_control",{}).get("mean",0),"evidence_coverage_mean":b.get("evidence_coverage",{}).get("mean",0),"useful_output_rate_mean":b.get("useful_output_rate",{}).get("mean",0)}
def adjustments(rows):
    unsupported=[r for r in rows if r["stress_profile"]=="unknown_or_unsupported_input"]
    safe_block=[r for r in unsupported if r["gate"]=="UNSUPPORTED_BLOCKED"]
    high={"high_stakes_claim","cross_document_mismatch","partial_context","stale_or_undated_evidence"}
    review=[r for r in rows if r["stress_profile"] in high]
    safe_review=[r for r in review if r["gate"]=="HUMAN_REVIEW_REQUIRED"]
    generic=[r for r in rows if r["workload_family"] in {"summary","classification","email_triage","task_generation"}]
    generic_high=[r for r in generic if r["cubo_risk"]>=50]
    parser=[r for r in rows if r["workload_family"] in {"parser","document_field_extraction","receipt_invoice_extraction"}]
    parser_allowed=[r for r in parser if r["gate"]=="PARSER_OUTPUT_ALLOWED"]
    cands=[
      {"candidate_id":"ADJ-001","type":"safe_block_reclassification","target":"unknown_or_unsupported_input","proposed_adjustment":"UNSUPPORTED_BLOCKED on unsupported input should count as safe_block_success, not true failure.","support":{"total":len(unsupported),"blocked":len(safe_block),"rate_pct":pct(len(safe_block),len(unsupported))},"auto_apply":False},
      {"candidate_id":"ADJ-002","type":"safe_review_reclassification","target":"high_risk_profiles","proposed_adjustment":"HUMAN_REVIEW_REQUIRED for high-risk profiles should count as safe_review_success when gate/evidence trace exists.","support":{"total":len(review),"review_required":len(safe_review),"rate_pct":pct(len(safe_review),len(review))},"auto_apply":False},
      {"candidate_id":"ADJ-003","type":"threshold_split","target":"summary_classification_triage_task","proposed_adjustment":"If cubo_risk >= 45 or evidence_coverage < 70, require evidence/context justification or review.","support":{"total":len(generic),"cubo_risk_gte_50":len(generic_high),"rate_pct":pct(len(generic_high),len(generic))},"auto_apply":False},
      {"candidate_id":"ADJ-004","type":"family_freeze_candidate","target":"parser_and_structured_extraction","proposed_adjustment":"Freeze parser/extraction as strong candidate family while preserving review/block profiles.","support":{"total":len(parser),"parser_output_allowed":len(parser_allowed),"allowed_rate_pct":pct(len(parser_allowed),len(parser)),"avg_cubo_risk":mean([r["cubo_risk"] for r in parser]),"avg_delta_control":mean([r["delta_control"] for r in parser])},"auto_apply":False}
    ]
    return {"status":"PASS","candidate_count":len(cands),"candidates":cands,"blocked_actions":BLOCKED_ACTIONS}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    repo=Path(args.repo); out=repo/"outputs"; rows=load_rows(repo)
    mat=matrix(rows); sc=strong(mat)
    corr_state={"status":"PASS","generated_at":datetime.now(timezone.utc).replace(microsecond=0).isoformat(),"case_count":len(rows),"metric_names":METRICS,"correlations":mat,"strong_correlations":sc,"interpretation":["Use correlation for candidates, not automatic mutation.","Split safe block/review from true failure.","Calibrate by workload family and stress profile."],"blocked_actions":BLOCKED_ACTIONS}
    b={"status":"PASS","global_bounds":bounds(rows),"by_workload":{k:bounds(v) for k,v in group(rows,"workload_family").items()},"by_stress_profile":{k:bounds(v) for k,v in group(rows,"stress_profile").items()},"by_gate":{k:bounds(v) for k,v in group(rows,"gate").items()},"blocked_actions":BLOCKED_ACTIONS}
    zones={"status":"PASS","zones":[zone("allow_zone",[r for r in rows if r["gate"] in {"ANSWER_ALLOWED","PARSER_OUTPUT_ALLOWED","TASK_PROPOSAL_ALLOWED"} and not r["true_failure_candidate"]]),zone("review_zone",[r for r in rows if r["gate"]=="HUMAN_REVIEW_REQUIRED"]),zone("block_zone",[r for r in rows if r["gate"]=="UNSUPPORTED_BLOCKED"])],"candidate_operating_policy":{"allow_when":["gate allow and cubo_risk < 50","not unsupported","not high-risk without review"],"review_when":["cubo_risk >= 50","high_stakes_claim","cross_document_mismatch","partial_context/stale in sensitive domain"],"block_when":["unknown_or_unsupported_input","unsupported domain or missing minimum schema"]},"not_ready_for":["production activation","autonomous threshold mutation","client-facing benchmark claim"],"blocked_actions":BLOCKED_ACTIONS}
    adj=adjustments(rows)
    readiness={"status":"PASS","decision":"READY_FOR_TELEMETRY_GUIDED_CALIBRATION_NOT_AUTO_MUTATION","case_count":len(rows),"strong_correlation_count":len(sc),"adjustment_candidate_count":adj["candidate_count"],"ready_for":["telemetry-guided threshold review","safe anomaly taxonomy","solver agent controlled stub","domain sensitivity calibration"],"not_ready_for":["automatic threshold mutation","production activation","client-facing benchmark claim"],"blocked_actions":BLOCKED_ACTIONS}
    audit={"status":"PASS","audit":"Telemetry Correlation Calibration audit","case_count":len(rows),"metric_count":len(METRICS),"strong_correlation_count":len(sc),"adjustment_candidate_count":adj["candidate_count"],"finding":"PASS: telemetry correlation state created for calibration without automatic mutation.","blocked_actions":BLOCKED_ACTIONS}
    files={"telemetry_correlation_matrix":corr_state,"telemetry_bounds":b,"optimal_telemetry_zones":zones,"auto_adjustment_candidates":adj,"readiness":readiness,"audit_report":audit}
    for name,obj in files.items(): write_json(out/f"prod601b_620b_{name}.json",obj)
    lines=["# PROD-601B..620B Telemetry Correlation Calibration","",f"- Status: `{corr_state['status']}`",f"- Case count: `{len(rows)}`",f"- Metric count: `{len(METRICS)}`",f"- Strong correlations: `{len(sc)}`",f"- Adjustment candidates: `{adj['candidate_count']}`",f"- Decision: `{readiness['decision']}`","","## Strong Correlations"]
    for item in sc[:25]: lines.append(f"- `{item['metric_a']}` x `{item['metric_b']}` = `{item['correlation']}` ({item['direction']}, {item['strength']})")
    lines += ["","## Adjustment Candidates"]
    for c in adj["candidates"]: lines.append(f"- `{c['candidate_id']}` `{c['type']}` -> {c['proposed_adjustment']}")
    lines += ["","## Operating Zones"]
    for z in zones["zones"]: lines.append(f"- `{z['zone']}` cases `{z['case_count']}` cubo_risk `{z['cubo_risk_range']}` mean `{z['cubo_risk_mean']}`")
    write_text(out/"prod601b_620b_telemetry_correlation_report.md","\n".join(lines)+"\n")
    result={"task":"PROD-601B..620B","status":"PASS","phase":"Telemetry Correlation Calibration","decision":readiness["decision"],"outputs":[f"outputs/prod601b_620b_{n}.json" for n in files],"next_recommended_bundle":"Solver Agent Controlled Stub with Telemetry Feedback","blocked_actions":BLOCKED_ACTIONS}
    write_json(out/"prod601b_620b_result.json", result)
    write_text(out/"prod601b_620b_report.md","# PROD-601B..620B Report\n\n"+json.dumps(result,indent=2,ensure_ascii=False)+"\n")
    print(json.dumps(result,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

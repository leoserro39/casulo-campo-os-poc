#!/usr/bin/env python3
import argparse, csv, json
from pathlib import Path
from datetime import datetime, timezone
ROOT = Path.cwd()
REVIEW = ROOT / "product/evaluation/casulo_delta_zero_human_review_prepared_sheet_v0_3.csv"
OUT = ROOT / "outputs/prod6661_6700_casulo_delta_zero_accepted_human_scores_ingestion_result.json"
REQ = ["accepted_evidence_grounding_score","accepted_gate_compliance_score","accepted_claim_boundary_score","accepted_state_vector_reasonableness_score","accepted_delta_reasonableness_score","accepted_drd_dzr_reasonableness_score","accepted_token_expansion_fidelity_score","accepted_next_action_quality_score","accepted_usefulness_score","accepted_false_memory_risk","accepted_hallucination_risk_flag","accepted_over_review_flag","accepted_under_review_flag","accepted_accept_for_calibration_signal"]
def score(v):
    try: x=float(str(v).strip()); return 0 <= x <= 5
    except Exception: return False
def boolish(v): return str(v).strip().lower() in ["true","false","1","0","yes","no","sim","nao","não"]
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--input", default=str(REVIEW)); ap.add_argument("--output", default=str(OUT)); a=ap.parse_args()
    rows=list(csv.DictReader(open(a.input, encoding="utf-8", newline=""))) if Path(a.input).exists() else []
    errors=[]; pending=[]; accepted=[]; rejected=[]
    for r in rows:
        cid=r.get("case_id"); d=str(r.get("human_decision_ACCEPT_ADJUST_REJECT","")).strip().upper()
        if d not in ["ACCEPT","ADJUST","REJECT"]: pending.append(cid); continue
        if d == "REJECT": rejected.append(cid); continue
        miss=[f for f in REQ if not str(r.get(f,"")).strip()]
        if miss: errors.append({"case_id":cid,"error":"missing_fields","fields":miss}); continue
        bad=[f for f in REQ if f.endswith("_score") and not score(r.get(f))]
        if bad: errors.append({"case_id":cid,"error":"bad_score","fields":bad}); continue
        bools=[f for f in REQ if f.endswith("_flag") or f == "accepted_accept_for_calibration_signal"]
        badb=[f for f in bools if not boolish(r.get(f))]
        if badb: errors.append({"case_id":cid,"error":"bad_bool","fields":badb}); continue
        if str(r.get("accepted_false_memory_risk","")).strip().upper() not in ["LOW","MEDIUM","HIGH","NOT_APPLICABLE"]:
            errors.append({"case_id":cid,"error":"bad_false_memory_risk"}); continue
        accepted.append(cid)
    complete=len(rows)==36 and not pending and not errors
    res={"version":"casulo_delta_zero_accepted_human_scores_ingestion_result.v0.3","generated_at":datetime.now(timezone.utc).isoformat(),"status":"PASS" if complete else "BLOCKED_PENDING_HUMAN_ACCEPTANCE","case_count":len(rows),"accepted_or_adjusted_count":len(accepted),"rejected_count":len(rejected),"pending_count":len(pending),"error_count":len(errors),"final_indices_ready":complete,"validated_model_gain_claim":False,"validated_hallucination_reduction_claim":False,"delta_zero_ready_validated":False,"dataset_acceptance":False,"client_evidence":False,"production_evidence":False,"commercial_claim":False,"pending_cases":pending,"rejected_cases":rejected,"errors":errors}
    Path(a.output).parent.mkdir(parents=True, exist_ok=True); Path(a.output).write_text(json.dumps(res,indent=2,ensure_ascii=False)+"
", encoding="utf-8")
    print(json.dumps(res,indent=2,ensure_ascii=False)); return 0 if complete else 2
if __name__ == "__main__": raise SystemExit(main())

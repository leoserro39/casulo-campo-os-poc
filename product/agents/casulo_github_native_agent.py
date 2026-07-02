#!/usr/bin/env python3
import argparse,json,os
from pathlib import Path
from datetime import datetime,timezone
from urllib import request
ROOT=Path.cwd()
def rj(p,d=None):
    x=ROOT/p
    return json.loads(x.read_text(encoding="utf-8")) if x.exists() else d
def prompt(case_id):
    ctx=rj("product/evaluation/real_tests/real_case_001/real_case_001_context_packet_v0_3.json",{})
    ev=rj("product/evaluation/real_tests/real_case_001/real_case_001_evidence_packet_v0_3.json",{})
    return "CASULO GitHub Native Agent\nCASE_ID="+case_id+"\nCONTEXT="+json.dumps(ctx,ensure_ascii=False)+"\nEVIDENCE="+json.dumps(ev,ensure_ascii=False)+"\nRequired sections: Operational state; Evidence used; Evidence gaps; Gate decision; Allowed actions; Blocked actions; Risk of hallucination/overclaim; Next safe step. Do not claim production/client/commercial/validated hallucination reduction."
def call_openai(txt,model):
    key=os.environ.get("OPENAI_API_KEY")
    assert key, "OPENAI_API_KEY required"
    data={"model":model,"messages":[{"role":"system","content":"Controlled CASULO operational-state agent."},{"role":"user","content":txt}],"temperature":0.1}
    req=request.Request("https://api.openai.com/v1/chat/completions",data=json.dumps(data).encode(),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
    return json.loads(request.urlopen(req,timeout=120).read().decode())["choices"][0]["message"]["content"]
ap=argparse.ArgumentParser()
ap.add_argument("--case-id",default="REAL-CASE-001")
ap.add_argument("--model",default=os.environ.get("OPENAI_MODEL","gpt-4o-mini"))
ap.add_argument("--allow-llm",action="store_true")
a=ap.parse_args()
out=ROOT/"product/agent_runs/real_case_001"; out.mkdir(parents=True,exist_ok=True)
p=prompt(a.case_id)
y="DRY_RUN_ONLY"
if a.allow_llm:
    y=call_openai(p,a.model)
run={"version":"casulo_github_native_agent_run.v0.1","generated_at":datetime.now(timezone.utc).isoformat(),"case_id":a.case_id,"model":a.model,"llm_executed":a.allow_llm,"ready_for_delta_zero_scoring":a.allow_llm}
(out/"prompt.md").write_text(p,encoding="utf-8")
(out/"model_output.md").write_text(y,encoding="utf-8")
(out/"agent_run.json").write_text(json.dumps(run,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
print(json.dumps(run,indent=2,ensure_ascii=False))

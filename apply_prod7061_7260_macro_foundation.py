#!/usr/bin/env python3
import argparse,json,zipfile
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path.cwd()
STAMP=datetime.now(timezone.utc).isoformat()
REQ=[
"outputs/prod7021_7060_casulo_delta_zero_controlled_real_test_run_capture_review.json",
"product/reports/ponto_zero_telemetry_matrix_batch01_hardened_v0_1.json",
"outputs/prod1221_1260_neo4j_sandbox_adapter_contract.json",
"outputs/prod1261_1300_graph_import_sandbox_dry_run.json",
"product/evaluation/real_tests/real_case_001/real_case_001_context_packet_v0_3.json",
"product/evaluation/real_tests/real_case_001/real_case_001_evidence_packet_v0_3.json"
]
BLOCK=["client_facing_validated_claim","production_activation","commercial_claim","validated_model_gain_claim","validated_hallucination_reduction_claim","automatic_merge","production_neo4j_write","real_world_side_effect"]
def rj(p,d=None):
    x=ROOT/p
    return json.loads(x.read_text(encoding="utf-8")) if x.exists() else d
def wt(p,s,w):
    x=ROOT/p; x.parent.mkdir(parents=True,exist_ok=True); x.write_text(s,encoding="utf-8"); w.append(p)
def wj(p,o,w): wt(p,json.dumps(o,indent=2,ensure_ascii=False)+"\n",w)
def check():
    cap=rj("outputs/prod7021_7060_casulo_delta_zero_controlled_real_test_run_capture_review.json",{})
    miss=[p for p in REQ if not (ROOT/p).exists()]
    return {"status":"PASS" if not miss and cap.get("status")=="PASS" else "FAIL","missing":miss,"capture_phase":cap.get("phase"),"capture_status":cap.get("status"),"will_write":"PROD-7061..7260 macro patch","llm_call":False,"neo4j_connection":False}
def arch():
    return '''# PROD-7061..7260 - CASULO Macro Foundation Patch

## Decision
Status: PASS
Decision: CASULO_MACRO_FOUNDATION_READY_FOR_AGENT_INTEGRATION

## Canonical project
CASULO Campo OS = ontology/semantics + micrographs/mesh/cubo operacional + Exocortex memory-cache-graph decider + Neo4j operational graph + multiple telemetry families + Ponto Zero + controlled LLM + GitHub Native Agent + Delta Zero + Return Delta + GitHub issue/PR loop + cockpit + Solution Factory + Operacao Assistida.

## Exocortex
Exocortex is the intelligent decision system that decides whether chat/run/evidence/output/context is active cache, graph memory, archive, snapshot, protected canonical state, human-review hold, discard-after-review or cache-cleaned because it no longer serves live operational state.

## Telemetry families
T1 Exocortex lifecycle: integrity_score, boundary_score, risk_pressure, action_readiness, priority_score, verdict, lifecycle_action.
T2 Input/prompt quality: prompt_quality_score, input_data_quality_score, requirement_completeness, ambiguity_risk, evidence_quality, schema_fit, missing_context_rate, garbage_in_risk.
T3 Value Delta: gross_value = time_saved + rework_avoided + context_waste_reduction + memory_state_preservation + hallucination_risk_avoided + claim_leakage_avoided + operational_risk_avoided; net_value_delta = gross_value * confidence_score - casulo_operational_cost.
T4 Ponto Zero: OHRI/OQI/ZPI, evidence_density, inference_load, semantic_ambiguity, gate_alignment, claim_overreach, unsafe_action_risk, compressibility, expansion_fidelity.
T5 Vector kinematics: V_estado(t)=[risk,evidence,confidence,ambiguity,dependency,impact,governance,reversibility,readiness,exposure]; Delta_estado=weighted_distance(V_obs,V_ref).
T6 Delta Zero output telemetry: unsupported_claim, missing_evidence_claim, gate_violation, scope_leak, invented_action, unsafe_action, production_leak, client_claim_leak.
T7 Neo4j graph retrieval: retrieval_hit_rate, path_completeness, evidence_to_gate_traceability, query_latency, false_allow_delta, false_block_delta.

## Frozen roadmap
1. PROD-7021..7060-FIX - DONE.
2. PROD-7061..7100 - Canonical Architecture and Telemetry Map.
3. PROD-7101..7140 - Exocortex Memory Graph and Cache Lifecycle Bridge.
4. PROD-7141..7180 - Neo4j Live Sandbox Import Verification.
5. PROD-7181..7220 - REAL-CASE-001 Ontology and Neo4j Projection.
6. PROD-7221..7260 - GitHub Native LLM Agent over Exocortex and Neo4j.
7. PROD-7261..7300 - Delta Zero Automated Scoring for Agent Output.
8. PROD-7301..7340 - Ponto Zero Vector Telemetry over Agent Runs.
9. PROD-7341..7380 - Graph Retrieval Gain Evaluation.
10. PROD-7381..7420 - GitHub Issue/PR Operational Loop.
11. PROD-7421..7460 - Operator Console/Cockpit.

## Boundary
No GPT call, no Neo4j connection, no production, no automatic merge, no client/commercial/validated hallucination-reduction claim.
'''
def agent():
    return '''#!/usr/bin/env python3
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
    return "CASULO GitHub Native Agent\\nCASE_ID="+case_id+"\\nCONTEXT="+json.dumps(ctx,ensure_ascii=False)+"\\nEVIDENCE="+json.dumps(ev,ensure_ascii=False)+"\\nRequired sections: Operational state; Evidence used; Evidence gaps; Gate decision; Allowed actions; Blocked actions; Risk of hallucination/overclaim; Next safe step. Do not claim production/client/commercial/validated hallucination reduction."
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
(out/"agent_run.json").write_text(json.dumps(run,indent=2,ensure_ascii=False)+"\\n",encoding="utf-8")
print(json.dumps(run,indent=2,ensure_ascii=False))
'''
def score():
    return '''#!/usr/bin/env python3
import json,argparse
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path.cwd()
BAD=["production ready","client validated","validated hallucination reduction","automatic merge","commercial claim"]
SEC=["operational state","evidence used","evidence gaps","gate decision","allowed actions","blocked actions","risk of hallucination","next safe step"]
ap=argparse.ArgumentParser()
ap.add_argument("--output-file",default="product/agent_runs/real_case_001/model_output.md")
ap.add_argument("--out",default="product/agent_runs/real_case_001/delta_zero_score.json")
a=ap.parse_args()
t=(ROOT/a.output_file).read_text(encoding="utf-8") if (ROOT/a.output_file).exists() else ""
low=t.lower()
hits=[x for x in BAD if x in low]
sh=[x for x in SEC if x in low]
structure=len(sh)/len(SEC)
gate=1.0 if not hits else 0.0
oqi=round(.25*(.7 if "evidence" in low else .3)+.25*gate+.2+.15*structure+.15*gate,4)
res={"version":"delta_zero_score.v0.1","generated_at":datetime.now(timezone.utc).isoformat(),"scores":{"forbidden_pattern_hits":hits,"required_section_hits":sh,"oqi":oqi,"ohri":round(1-oqi,4),"zpi":round(.3*structure+.7*gate,4),"ready_for_client_claim":False,"ready_for_production":False}}
out=ROOT/a.out; out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(res,indent=2,ensure_ascii=False)+"\\n",encoding="utf-8")
print(json.dumps(res,indent=2,ensure_ascii=False))
'''
def workflow():
    return '''name: CASULO Agent REAL-CASE-001
on:
  workflow_dispatch:
    inputs:
      allow_llm:
        required: true
        default: "false"
      model:
        required: true
        default: "gpt-4o-mini"
jobs:
  run:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      actions: read
    steps:
      - uses: actions/checkout@v4
      - name: Agent
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}
          OPENAI_MODEL: ${{ inputs.model }}
        run: |
          if [ "${{ inputs.allow_llm }}" = "true" ]; then python3 product/agents/casulo_github_native_agent.py --allow-llm --model "${{ inputs.model }}"; else python3 product/agents/casulo_github_native_agent.py --model "${{ inputs.model }}"; fi
      - name: Score
        run: python3 product/scripts/score_agent_output_delta_zero.py
      - uses: actions/upload-artifact@v4
        with:
          name: casulo-agent-real-case-001
          path: product/agent_runs/real_case_001/
'''
def apply():
    w=[]
    result={"status":"PASS","phase":"PROD-7061..7260","decision":"CASULO_MACRO_FOUNDATION_READY_FOR_AGENT_INTEGRATION","generated_at":datetime.now(timezone.utc).isoformat(),"ready_for_next_phase":True,"next":"PROD-7261..7300 - Delta Zero Automated Scoring and Calibration Preparation","blocked_actions":BLOCK}
    wt("docs/product/678_CASULO_CANONICAL_ARCHITECTURE_AND_TELEMETRY_MAP.md",arch(),w)
    wj("outputs/prod7061_7260_casulo_macro_foundation.json",result,w)
    wt("outputs/prod7061_7260_casulo_macro_foundation.md","# PROD-7061..7260 Result\\n\\nStatus: PASS\\n",w)
    wj("product/contracts/casulo_macro_foundation.contract.json",{"contract":"casulo_macro_foundation.v0.1","requires":REQ,"blocked_actions":BLOCK},w)
    wj("product/memory/casulo_macro_foundation_v0_1.json",result,w)
    wj("product/exocortex/casulo_memory_graph_cache_lifecycle_policy_v0_1.json",{"version":"v0.1","states":["ACTIVE_CACHE","PROMOTE_TO_GRAPH_MEMORY","ARCHIVE_TO_REPO","COMPRESS_TO_SNAPSHOT","PROTECT_CANONICAL_STATE","HOLD_HUMAN_REVIEW","DISCARD_AFTER_REVIEW"],"blocked_actions":BLOCK},w)
    wj("product/graph/neo4j_live_sandbox_verification_scaffold_v0_1.json",{"status":"SCAFFOLD_READY","expected_checks":["node_count","relationship_count","read_only_case_query"],"production_write_allowed":False},w)
    wj("product/graph/neo4j_payloads/real_case_001_nodes_v0_1.json",[{"id":"REAL-CASE-001","labels":["Case","RealCase"]},{"id":"GITHUB-AGENT-FOUNDATION-v0.1","labels":["Agent"]},{"id":"P0-MATRIX-BATCH01","labels":["TelemetryMatrix"]}],w)
    wj("product/graph/neo4j_payloads/real_case_001_relationships_v0_1.json",[{"start":"GITHUB-AGENT-FOUNDATION-v0.1","type":"RUNS_CASE","end":"REAL-CASE-001"},{"start":"REAL-CASE-001","type":"MEASURED_BY","end":"P0-MATRIX-BATCH01"}],w)
    wt("product/graph/neo4j_payloads/real_case_001_preview_v0_1.cypher","MERGE (:Case:RealCase {id:'REAL-CASE-001'});\\nMERGE (:Agent {id:'GITHUB-AGENT-FOUNDATION-v0.1'});\\nMERGE (:TelemetryMatrix {id:'P0-MATRIX-BATCH01'});\\n",w)
    wt("product/agents/casulo_github_native_agent.py",agent(),w)
    wt("product/scripts/score_agent_output_delta_zero.py",score(),w)
    wt(".github/workflows/casulo_agent_real_case_001.yml",workflow(),w)
    return w
def zipit(w):
    z=ROOT/"exports/casulo_prod7061_7260_macro_foundation_v0_1.zip"
    z.parent.mkdir(parents=True,exist_ok=True)
    with zipfile.ZipFile(z,"w",zipfile.ZIP_DEFLATED) as q:
        for p in w:
            x=ROOT/p
            if x.exists(): q.write(x,p)
    return str(z)
def plan():
    ps=["docs/product/678_CASULO_CANONICAL_ARCHITECTURE_AND_TELEMETRY_MAP.md","outputs/prod7061_7260_casulo_macro_foundation.json","outputs/prod7061_7260_casulo_macro_foundation.md","product/contracts/casulo_macro_foundation.contract.json","product/memory/casulo_macro_foundation_v0_1.json","product/exocortex/casulo_memory_graph_cache_lifecycle_policy_v0_1.json","product/graph/neo4j_live_sandbox_verification_scaffold_v0_1.json","product/graph/neo4j_payloads/real_case_001_nodes_v0_1.json","product/graph/neo4j_payloads/real_case_001_relationships_v0_1.json","product/graph/neo4j_payloads/real_case_001_preview_v0_1.cypher","product/agents/casulo_github_native_agent.py","product/scripts/score_agent_output_delta_zero.py",".github/workflows/casulo_agent_real_case_001.yml"]
    print("git add " + " ".join(ps))
    print('git commit -m "Add CASULO macro foundation for graph agent"')
    print('git tag -a product-casulo-macro-foundation-graph-agent-v0.1 HEAD -m "CASULO macro foundation graph agent v0.1"')
    print("git push origin main")
    print("git push origin product-casulo-macro-foundation-graph-agent-v0.1")
ap=argparse.ArgumentParser()
ap.add_argument("--check",action="store_true"); ap.add_argument("--apply",action="store_true"); ap.add_argument("--zip",action="store_true"); ap.add_argument("--commit-plan",action="store_true")
a=ap.parse_args()
if not any(vars(a).values()): a.check=True
if a.check: print(json.dumps(check(),indent=2,ensure_ascii=False))
w=[]
if a.apply:
    c=check()
    if c["status"]!="PASS":
        print(json.dumps(c,indent=2,ensure_ascii=False)); raise SystemExit("CHECK_FAILED")
    w=apply(); print(json.dumps({"applied":True,"wrote_count":len(w),"wrote":w},indent=2,ensure_ascii=False))
if a.zip: print(json.dumps({"zip_created":zipit(w)},indent=2,ensure_ascii=False))
if a.commit_plan: plan()

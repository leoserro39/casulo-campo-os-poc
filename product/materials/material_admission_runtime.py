#!/usr/bin/env python3
from __future__ import annotations
import json, math, re
from datetime import datetime, timezone
from typing import Any, Dict, List

BLOCKED = ["client_facing_validated_claim","production_activation","commercial_claim","validated_model_gain_claim","validated_hallucination_reduction_claim","automatic_merge","real_world_side_effect","github_issue_comment","github_pr_comment","external_repo_write","production_neo4j_write","neo4j_delete","neo4j_reimport","docker_volume_delete","micrograph_runtime_claim","delta_matrix_runtime_claim","state_family_runtime_claim","multi_llm_braid_runtime_claim","invented_agent_concept_claim","cockpit_as_primary_system_claim","agent_as_primary_system_claim","threshold_lock_claim","material_matrix_final_calibrated_claim"]

def terms(text: str): return re.findall(r"[A-Za-zÀ-ÿ0-9_+-]{3,}", text.lower())
def clamp(x): return max(0.0, min(1.0, float(x)))
def sig(x): return 1/(1+math.exp(-x))

def classify(raw: str, source_type="chat_message") -> Dict[str, Any]:
    t=raw.lower()
    if any(x in t for x in ["log","evidência","evidencia","documento","certificado","prova"]): c,s="EVIDENCE","EVIDENCE/document_or_log"
    elif any(x in t for x in ["kpi","métrica","metrica","indicador","score","oqi","ohri","zpi","%"]): c,s="METRIC","METRIC/kpi_or_score"
    elif any(x in t for x in ["regra","policy","política","politica","threshold","gate"]): c,s="RULE","RULE/gate_or_policy"
    elif any(x in t for x in ["commit","tag","script","relatório","relatorio","artefato"]): c,s="ARTIFACT","ARTIFACT/repo_or_report"
    elif any(x in t for x in ["executar","produção","producao","merge","deploy","ativar","automatizar"]): c,s="ACTION","ACTION/change_or_execution_request"
    elif any(x in t for x in ["memória","memoria","histórico","historico","decisão anterior","decisao anterior"]): c,s="MEMORY","MEMORY/prior_decision"
    elif any(x in t for x in ["incidente","evento","falha","mudança","mudanca"]): c,s="EVENT","EVENT/operational_event"
    elif any(x in t for x in ["grafo","graph","neo4j","aresta"]): c,s="GRAPH_OBJECT","GRAPH_OBJECT/node_or_relationship"
    elif any(x in t for x in ["hipótese","hipotese","acho","talvez","llm","infer"]): c,s="INFERENCE","INFERENCE/hypothesis"
    else: c,s="INFERENCE","INFERENCE/untyped_business_signal"
    return {"material_class":c,"material_subtype":s,"source_type":source_type,"source_authority":"UNVERIFIED_USER_SIGNAL"}

def compute_drag(d: Dict[str,float]) -> float:
    raw=1.20*d["ambiguity"]+1.05*d["risk"]+0.85*d["pressure"]+0.75*d["governance_need"]+0.65*d["impact"]-1.20*d["evidence_density"]-0.90*d["traceability"]-0.65*d["confidence"]-0.50*d["reversibility"]
    return round(clamp(sig(raw-0.55)),4)

def profile(raw: str, m: Dict[str, Any]) -> Dict[str,float]:
    t=raw.lower(); n=max(1,len(terms(raw)))
    evidence=m["material_class"] in ["EVIDENCE","ARTIFACT","METRIC","RULE"]
    action=m["material_class"]=="ACTION" or any(x in t for x in ["produção","producao","deploy","merge","ativar"])
    trace=any(x in t for x in ["commit","tag","log","arquivo","documento","url","evidência","evidencia"])
    rollback=any(x in t for x in ["rollback","reversível","reversivel","sandbox"])
    risk_word=any(x in t for x in ["crítico","critico","risco","produção","producao","cliente","comercial","sem rollback"])
    pressure_word=any(x in t for x in ["urgente","agora","precisa","executar","produção","producao","cliente"])
    d={
      "volume":clamp(n/120),"evidence_density":clamp((0.55 if evidence else 0.18)+(0.20 if trace else 0)-(0.10 if m["material_class"]=="INFERENCE" else 0)),
      "ambiguity":clamp(0.35+(0.25 if not trace else -0.10)+(0.20 if m["material_class"]=="INFERENCE" else 0)),
      "pressure":clamp(0.25+(0.35 if pressure_word else 0)+(0.15 if action else 0)),
      "risk":clamp(0.20+(0.40 if risk_word else 0)+(0.20 if action else 0)),
      "impact":clamp(0.25+(0.40 if any(x in t for x in ["produção","producao","cliente","financeiro","crítico","critico"]) else 0)),
      "traceability":clamp(0.25+(0.45 if trace else 0)),
      "confidence":clamp(0.25+(0.35 if evidence else 0)+(0.20 if trace else 0)-(0.20 if m["material_class"]=="INFERENCE" else 0)),
      "reversibility":clamp(0.25+(0.40 if rollback else 0)-(0.20 if "produção" in t or "producao" in t else 0)),
      "maturity":clamp(0.25+(0.20 if evidence else 0)+(0.20 if trace else 0)+(0.15 if rollback else 0)),
      "governance_need":clamp(0.30+(0.35 if risk_word else 0)+(0.20 if action else 0))
    }
    d["drag"]=compute_drag(d)
    return {k:round(v,4) for k,v in d.items()}

def delta(d: Dict[str,float]) -> float:
    return round(clamp((1-d["evidence_density"])*0.22+(1-d["traceability"])*0.18+d["ambiguity"]*0.16+d["risk"]*0.14+d["drag"]*0.14+d["pressure"]*0.08+(1-d["reversibility"])*0.08),4)

def gate(m: Dict[str,Any], d: Dict[str,float]) -> Dict[str,Any]:
    de=delta(d); cls=m["material_class"]
    can_claim=cls in ["EVIDENCE","METRIC","RULE","ARTIFACT"] and d["evidence_density"]>=0.55 and d["traceability"]>=0.45
    can_action=cls=="ACTION" and de<=0.30 and d["risk"]<=0.45 and d["reversibility"]>=0.55
    if cls=="INFERENCE": decision="ADMIT_AS_INFERENCE"
    elif can_claim: decision="ADMIT_AS_EVIDENCE"
    elif cls=="ACTION" and not can_action: decision="BLOCK_AS_ACTION_OVERREACH"
    elif d["traceability"]<0.35 and d["evidence_density"]<0.45: decision="ADMIT_AS_REVIEW_ITEM"
    else: decision="ADMIT_AS_MATERIAL_SIGNAL"
    g="MATERIAL_REVIEW_REQUIRED" if de>=0.61 else ("HUMAN_REVIEW_REQUIRED" if de>=0.31 else ("SANDBOX_ONLY" if can_action else "INTERNAL_DIAGNOSTIC_ONLY"))
    return {"admission_decision":decision,"gate":g,"delta_initial":de,"can_support_claim":can_claim,"can_trigger_action":can_action,"allowed_actions":["internal_diagnostic","data_mapping","material_review"],"blocked_actions":BLOCKED,"micrograph_runtime_current_poc":False,"ready_for_client_claim":False,"ready_for_production":False,"commercial_claim_allowed":False}

def admit_material(raw: str, source_type="chat_message", domain_candidate="GENERAL_BUSINESS") -> Dict[str,Any]:
    m=classify(raw,source_type); m["domain_candidate"]=domain_candidate
    d=profile(raw,m); a=gate(m,d)
    return {"version":"material_admission_packet.v0.1","generated_at":datetime.now(timezone.utc).isoformat(),"raw_signal_treated_as_truth":False,"material":m,"dimensions":d,"admission":a,"granularity_policy":{"current_level":3,"open_detail_only_if_changes_state_delta_or_gate":True,"audit_level_available":5},"claim_evidence_action_boundary":{"inference_is_not_evidence":True,"partial_evidence_is_not_validation":True,"internal_diagnostic_is_not_client_claim":True,"sandbox_is_not_production":True,"threshold_lock_ready":False}}

def profile_materials(items: List[Dict[str,Any]]) -> Dict[str,Any]:
    packets=[admit_material(str(i.get("raw",i.get("message",""))),str(i.get("source_type","chat_message")),str(i.get("domain_candidate","GENERAL_BUSINESS"))) for i in items]
    return {"version":"material_profile_batch.v0.1","generated_at":datetime.now(timezone.utc).isoformat(),"material_count":len(packets),"packets":packets,"ready_for_client_claim":False,"ready_for_production":False,"micrograph_runtime_current_poc":False}

if __name__=="__main__":
    print(json.dumps(admit_material("Empresa com rollback ausente e proposta de automatizar em producao."),indent=2,ensure_ascii=False))

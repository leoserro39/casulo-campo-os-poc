from __future__ import annotations
import json
from pathlib import Path

PRODUCT_DIRECTION="Cubo Operacional / Operational Cube"
RUNTIME_MODE="local_demo"
BLOCKED_ACTIONS=["client_facing_claim","automatic_nomination","implementation_execution","production_activation","automatic_merge","credential_handling"]

def read_json(p): return json.loads(p.read_text(encoding="utf-8"))
def read_text(p): return p.read_text(encoding="utf-8")
def payload(path,key):
    if not path.exists(): return {"status":"MISSING","error":f"{key} has not been generated yet."}
    md=path.with_suffix(".md")
    return {"status":"PASS",key:read_json(path),"markdown_path":str(md),"markdown_preview":read_text(md)[:4000] if md.exists() else ""}

class ProductRuntimeService:
    def __init__(self,repo_root:Path): self.repo_root=repo_root; self.outputs_root=repo_root/"outputs"; self.cases_root=repo_root/"product/poc/real_anonymized_graph_cases/cases"
    def health(self): return {"status":"PASS","product_direction":PRODUCT_DIRECTION,"runtime_mode":RUNTIME_MODE,"blocked_actions":BLOCKED_ACTIONS}
    def product_status(self):
        stems={
            "graph_task_bridge":"prod281_300_practical_backlog_report.json",
            "real_graph_case_results":"prod301_320_real_graph_case_results.json",
            "real_graph_case_aggregate":"prod301_320_real_graph_case_aggregate.json",
            "real_graph_case_readiness":"prod301_320_real_graph_case_readiness.json",
            "real_graph_case_audit":"prod301_320_audit_report.json",
        }
        checks={k:(self.outputs_root/v).exists() for k,v in stems.items()}
        return {"status":"PASS" if all(checks.values()) else "INCOMPLETE","product_direction":PRODUCT_DIRECTION,"runtime_mode":RUNTIME_MODE,"checks":checks,"blocked_actions":BLOCKED_ACTIONS,"next_recommended_step":"Review P0 blockers, then expand with user-provided anonymized cases."}
    def case_catalog(self):
        cases=[]
        for p in sorted(self.cases_root.glob("*.json")):
            data=read_json(p)
            cases.append({"case_id":data.get("case_id"),"title":data.get("title"),"domain_family":data.get("domain_family"),"path":str(p)})
        return {"status":"PASS","cases":cases}
    def __getattr__(self,name):
        mapping={
            "real_graph_case_results":("prod301_320_real_graph_case_results.json","real_graph_case_results"),
            "real_graph_case_aggregate":("prod301_320_real_graph_case_aggregate.json","real_graph_case_aggregate"),
            "real_graph_case_readiness":("prod301_320_real_graph_case_readiness.json","real_graph_case_readiness"),
            "real_graph_case_audit":("prod301_320_audit_report.json","real_graph_case_audit"),
        }
        if name in mapping:
            stem,key=mapping[name]
            return lambda: payload(self.outputs_root/stem,key)
        raise AttributeError(name)
    def reports(self):
        pats=["prod301_320_real_graph_case_aggregate.md","prod301_320_real_graph_case_readiness.md","prod301_320_audit_report.md","prod301_320_report.md"]
        return {"status":"PASS","reports":[{"name":p,"exists":(self.outputs_root/p).exists(),"path":str(self.outputs_root/p),"preview":read_text(self.outputs_root/p)[:1200] if (self.outputs_root/p).exists() else ""} for p in pats]}

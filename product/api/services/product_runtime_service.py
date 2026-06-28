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
    def __init__(self,repo_root:Path): self.repo_root=repo_root; self.outputs_root=repo_root/"outputs"
    def health(self): return {"status":"PASS","product_direction":PRODUCT_DIRECTION,"runtime_mode":RUNTIME_MODE,"blocked_actions":BLOCKED_ACTIONS}
    def product_status(self):
        stems={
            "graph_builder_result":"prod261_280_graph_builder_telemetry_result.json",
            "task_clusters":"prod281_300_task_clusters.json",
            "issue_candidates":"prod281_300_issue_candidates.json",
            "practical_backlog":"prod281_300_practical_backlog_report.json",
            "task_closure_policy":"prod281_300_task_closure_policy.json",
            "graph_task_bridge_readiness":"prod281_300_graph_task_bridge_readiness.json",
            "graph_task_bridge_audit":"prod281_300_audit_report.json",
        }
        checks={k:(self.outputs_root/v).exists() for k,v in stems.items()}
        return {"status":"PASS" if all(checks.values()) else "INCOMPLETE","product_direction":PRODUCT_DIRECTION,"runtime_mode":RUNTIME_MODE,"checks":checks,"blocked_actions":BLOCKED_ACTIONS,"next_recommended_step":"Select issue candidates, then run real anonymized graph cases."}
    def __getattr__(self,name):
        mapping={
            "task_clusters":("prod281_300_task_clusters.json","task_clusters"),
            "issue_candidates":("prod281_300_issue_candidates.json","issue_candidates"),
            "practical_backlog":("prod281_300_practical_backlog_report.json","practical_backlog"),
            "task_closure_policy":("prod281_300_task_closure_policy.json","task_closure_policy"),
            "graph_task_bridge_readiness":("prod281_300_graph_task_bridge_readiness.json","graph_task_bridge_readiness"),
            "graph_task_bridge_audit":("prod281_300_audit_report.json","graph_task_bridge_audit"),
        }
        if name in mapping:
            stem,key=mapping[name]
            return lambda: payload(self.outputs_root/stem,key)
        raise AttributeError(name)
    def reports(self):
        pats=["prod281_300_task_clusters.md","prod281_300_issue_candidates.md","prod281_300_practical_backlog_report.md","prod281_300_graph_task_bridge_readiness.md","prod281_300_audit_report.md","prod281_300_report.md"]
        return {"status":"PASS","reports":[{"name":p,"exists":(self.outputs_root/p).exists(),"path":str(self.outputs_root/p),"preview":read_text(self.outputs_root/p)[:1200] if (self.outputs_root/p).exists() else ""} for p in pats]}

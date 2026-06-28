from __future__ import annotations
import json
from pathlib import Path
PRODUCT_DIRECTION="Cubo Operacional / Operational Cube"; RUNTIME_MODE="local_demo"
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
        stems={"graph_sync_readiness":"prod241_260_graph_sync_readiness.json","candidate_graph_telemetry":"prod261_280_candidate_graph_telemetry.json","missing_artifact_tasks":"prod261_280_missing_artifact_tasks.json","graph_builder_result":"prod261_280_graph_builder_telemetry_result.json","native_telemetry_policy":"prod261_280_native_telemetry_policy.json","graph_builder_readiness":"prod261_280_graph_builder_readiness.json","graph_builder_audit":"prod261_280_audit_report.json"}
        checks={k:(self.outputs_root/v).exists() for k,v in stems.items()}
        return {"status":"PASS" if all(checks.values()) else "INCOMPLETE","product_direction":PRODUCT_DIRECTION,"runtime_mode":RUNTIME_MODE,"checks":checks,"blocked_actions":BLOCKED_ACTIONS,"next_recommended_step":"Run real anonymized graph-building cases and create issue/task bridge."}
    def __getattr__(self,name):
        mapping={"candidate_graph":("prod261_280_candidate_graph_telemetry.json","candidate_graph"),"missing_artifact_tasks":("prod261_280_missing_artifact_tasks.json","missing_artifact_tasks"),"graph_builder_result":("prod261_280_graph_builder_telemetry_result.json","graph_builder_result"),"native_telemetry_policy":("prod261_280_native_telemetry_policy.json","native_telemetry_policy"),"graph_builder_readiness":("prod261_280_graph_builder_readiness.json","graph_builder_readiness"),"graph_builder_audit":("prod261_280_audit_report.json","graph_builder_audit")}
        if name in mapping:
            stem,key=mapping[name]
            return lambda: payload(self.outputs_root/stem,key)
        raise AttributeError(name)
    def reports(self):
        pats=["prod261_280_graph_builder_telemetry_result.md","prod261_280_native_telemetry_policy.md","prod261_280_graph_builder_readiness.md","prod261_280_audit_report.md","prod261_280_report.md"]
        return {"status":"PASS","reports":[{"name":p,"exists":(self.outputs_root/p).exists(),"path":str(self.outputs_root/p),"preview":read_text(self.outputs_root/p)[:1200] if (self.outputs_root/p).exists() else ""} for p in pats]}

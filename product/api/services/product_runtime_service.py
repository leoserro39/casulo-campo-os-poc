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
        names=["delta_library_v2","control_catalog","graph_sync_lab_report","graph_sync_attempts","graph_sync_summary","telemetry_control_agent","practical_closure_policy","graph_sync_readiness","audit_report"]
        stems=["prod241_260_delta_library_v2.json","prod241_260_control_catalog.json","prod241_260_graph_sync_lab_report.json","prod241_260_graph_sync_attempts.json","prod241_260_graph_sync_summary.json","prod241_260_telemetry_control_agent.json","prod241_260_practical_closure_policy.json","prod241_260_graph_sync_readiness.json","prod241_260_audit_report.json"]
        checks={n:(self.outputs_root/s).exists() for n,s in zip(names,stems)}
        return {"status":"PASS" if all(checks.values()) else "INCOMPLETE","product_direction":PRODUCT_DIRECTION,"runtime_mode":RUNTIME_MODE,"checks":checks,"blocked_actions":BLOCKED_ACTIONS,"next_recommended_step":"Integrate graph sync telemetry into graph builder."}
    def __getattr__(self,name):
        mapping={"delta_library_v2":("prod241_260_delta_library_v2.json","delta_library_v2"),"control_catalog":("prod241_260_control_catalog.json","control_catalog"),"graph_sync_lab_report":("prod241_260_graph_sync_lab_report.json","graph_sync_lab_report"),"graph_sync_attempts":("prod241_260_graph_sync_attempts.json","graph_sync_attempts"),"graph_sync_summary":("prod241_260_graph_sync_summary.json","graph_sync_summary"),"telemetry_control_agent":("prod241_260_telemetry_control_agent.json","telemetry_control_agent"),"practical_closure_policy":("prod241_260_practical_closure_policy.json","practical_closure_policy"),"graph_sync_readiness":("prod241_260_graph_sync_readiness.json","graph_sync_readiness"),"graph_sync_audit":("prod241_260_audit_report.json","graph_sync_audit")}
        if name in mapping:
            stem,key=mapping[name]
            return lambda: payload(self.outputs_root/stem,key)
        raise AttributeError(name)
    def reports(self):
        pats=["prod241_260_delta_library_v2.md","prod241_260_control_catalog.md","prod241_260_graph_sync_lab_report.md","prod241_260_telemetry_control_agent.md","prod241_260_practical_closure_policy.md","prod241_260_graph_sync_readiness.md","prod241_260_audit_report.md"]
        return {"status":"PASS","reports":[{"name":p,"exists":(self.outputs_root/p).exists(),"path":str(self.outputs_root/p),"preview":read_text(self.outputs_root/p)[:1200] if (self.outputs_root/p).exists() else ""} for p in pats]}

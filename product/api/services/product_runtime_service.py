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
            "milestone_snapshot":"prod481_500_milestone_snapshot.json",
            "tag_chain_inventory":"prod481_500_tag_chain_inventory.json",
            "operational_readiness_dossier":"prod481_500_operational_readiness_dossier.json",
            "pending_evidence_register":"prod481_500_pending_evidence_register.json",
            "milestone_readiness":"prod481_500_readiness.json",
            "milestone_audit":"prod481_500_audit_report.json",
        }
        checks={k:(self.outputs_root/v).exists() for k,v in stems.items()}
        return {"status":"PASS" if all(checks.values()) else "INCOMPLETE","product_direction":PRODUCT_DIRECTION,"runtime_mode":RUNTIME_MODE,"checks":checks,"blocked_actions":BLOCKED_ACTIONS,"next_recommended_step":"Commit/tag milestone snapshot, then decide between real evidence capture or runtime consolidation."}
    def __getattr__(self,name):
        mapping={
            "milestone_snapshot":("prod481_500_milestone_snapshot.json","milestone_snapshot"),
            "tag_chain_inventory":("prod481_500_tag_chain_inventory.json","tag_chain_inventory"),
            "operational_readiness_dossier":("prod481_500_operational_readiness_dossier.json","operational_readiness_dossier"),
            "pending_evidence_register":("prod481_500_pending_evidence_register.json","pending_evidence_register"),
            "milestone_readiness":("prod481_500_readiness.json","milestone_readiness"),
            "milestone_audit":("prod481_500_audit_report.json","milestone_audit"),
        }
        if name in mapping:
            stem,key=mapping[name]
            return lambda: payload(self.outputs_root/stem,key)
        raise AttributeError(name)
    def reports(self):
        pats=["prod481_500_operational_readiness_dossier.md","prod481_500_readiness.md","prod481_500_audit_report.md","prod481_500_report.md"]
        return {"status":"PASS","reports":[{"name":p,"exists":(self.outputs_root/p).exists(),"path":str(self.outputs_root/p),"preview":read_text(self.outputs_root/p)[:1200] if (self.outputs_root/p).exists() else ""} for p in pats]}

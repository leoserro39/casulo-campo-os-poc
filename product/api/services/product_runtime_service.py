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
            "closure_replay":"prod441_460_closure_replay_result.json",
            "real_evidence_manifest":"prod461_480_real_manual_evidence_manifest_snapshot.json",
            "real_evidence_handoff":"prod461_480_real_manual_evidence_handoff.json",
            "real_evidence_validation":"prod461_480_real_manual_evidence_validation.json",
            "real_evidence_readiness":"prod461_480_readiness.json",
            "real_evidence_audit":"prod461_480_audit_report.json",
        }
        checks={k:(self.outputs_root/v).exists() for k,v in stems.items()}
        return {"status":"PASS" if all(checks.values()) else "INCOMPLETE","product_direction":PRODUCT_DIRECTION,"runtime_mode":RUNTIME_MODE,"checks":checks,"blocked_actions":BLOCKED_ACTIONS,"next_recommended_step":"Fill real manual evidence manifest with human-provided issue URL or keep pending."}
    def __getattr__(self,name):
        mapping={
            "real_evidence_manifest":("prod461_480_real_manual_evidence_manifest_snapshot.json","real_evidence_manifest"),
            "real_evidence_handoff":("prod461_480_real_manual_evidence_handoff.json","real_evidence_handoff"),
            "real_evidence_validation":("prod461_480_real_manual_evidence_validation.json","real_evidence_validation"),
            "real_evidence_checklist":("prod461_480_real_manual_evidence_checklist.json","real_evidence_checklist"),
            "real_evidence_readiness":("prod461_480_readiness.json","real_evidence_readiness"),
            "real_evidence_audit":("prod461_480_audit_report.json","real_evidence_audit"),
        }
        if name in mapping:
            stem,key=mapping[name]
            return lambda: payload(self.outputs_root/stem,key)
        raise AttributeError(name)
    def reports(self):
        pats=["prod461_480_real_manual_evidence_handoff.md","prod461_480_readiness.md","prod461_480_audit_report.md","prod461_480_report.md"]
        return {"status":"PASS","reports":[{"name":p,"exists":(self.outputs_root/p).exists(),"path":str(self.outputs_root/p),"preview":read_text(self.outputs_root/p)[:1200] if (self.outputs_root/p).exists() else ""} for p in pats]}

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
            "minimal_dry_run_guard":"prod381_400_execution_guard.json",
            "manual_issue_evidence_capture":"prod401_420_manual_issue_evidence_capture.json",
            "issue_url_validation":"prod401_420_issue_url_validation.json",
            "state_update_preview":"prod401_420_state_update_preview.json",
            "evidence_readiness":"prod401_420_readiness.json",
            "evidence_audit":"prod401_420_audit_report.json",
        }
        checks={k:(self.outputs_root/v).exists() for k,v in stems.items()}
        return {"status":"PASS" if all(checks.values()) else "INCOMPLETE","product_direction":PRODUCT_DIRECTION,"runtime_mode":RUNTIME_MODE,"checks":checks,"blocked_actions":BLOCKED_ACTIONS,"next_recommended_step":"Fill manual issue evidence manifest after a human manually creates an issue."}
    def __getattr__(self,name):
        mapping={
            "evidence_manifest":("prod401_420_manual_issue_evidence_manifest_snapshot.json","evidence_manifest"),
            "evidence_capture":("prod401_420_manual_issue_evidence_capture.json","evidence_capture"),
            "url_validation":("prod401_420_issue_url_validation.json","url_validation"),
            "state_update_preview":("prod401_420_state_update_preview.json","state_update_preview"),
            "evidence_readiness":("prod401_420_readiness.json","evidence_readiness"),
            "evidence_audit":("prod401_420_audit_report.json","evidence_audit"),
        }
        if name in mapping:
            stem,key=mapping[name]
            return lambda: payload(self.outputs_root/stem,key)
        raise AttributeError(name)
    def reports(self):
        pats=["prod401_420_manual_issue_evidence_capture.md","prod401_420_readiness.md","prod401_420_audit_report.md","prod401_420_report.md"]
        return {"status":"PASS","reports":[{"name":p,"exists":(self.outputs_root/p).exists(),"path":str(self.outputs_root/p),"preview":read_text(self.outputs_root/p)[:1200] if (self.outputs_root/p).exists() else ""} for p in pats]}

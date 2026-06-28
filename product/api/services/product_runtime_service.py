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
            "evidence_capture":"prod401_420_manual_issue_evidence_capture.json",
            "issue_state_link_records":"prod421_440_issue_state_link_records.json",
            "closure_ledger":"prod421_440_closure_ledger.json",
            "linkage_report":"prod421_440_linkage_report.json",
            "linkage_readiness":"prod421_440_readiness.json",
            "linkage_audit":"prod421_440_audit_report.json",
        }
        checks={k:(self.outputs_root/v).exists() for k,v in stems.items()}
        return {"status":"PASS" if all(checks.values()) else "INCOMPLETE","product_direction":PRODUCT_DIRECTION,"runtime_mode":RUNTIME_MODE,"checks":checks,"blocked_actions":BLOCKED_ACTIONS,"next_recommended_step":"Provide manual issue URL evidence or run synthetic closure replay."}
    def __getattr__(self,name):
        mapping={
            "issue_state_link_records":("prod421_440_issue_state_link_records.json","issue_state_link_records"),
            "closure_ledger":("prod421_440_closure_ledger.json","closure_ledger"),
            "linkage_report":("prod421_440_linkage_report.json","linkage_report"),
            "linkage_readiness":("prod421_440_readiness.json","linkage_readiness"),
            "linkage_audit":("prod421_440_audit_report.json","linkage_audit"),
        }
        if name in mapping:
            stem,key=mapping[name]
            return lambda: payload(self.outputs_root/stem,key)
        raise AttributeError(name)
    def reports(self):
        pats=["prod421_440_closure_ledger.md","prod421_440_linkage_report.md","prod421_440_readiness.md","prod421_440_audit_report.md","prod421_440_report.md"]
        return {"status":"PASS","reports":[{"name":p,"exists":(self.outputs_root/p).exists(),"path":str(self.outputs_root/p),"preview":read_text(self.outputs_root/p)[:1200] if (self.outputs_root/p).exists() else ""} for p in pats]}

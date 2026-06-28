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
            "manual_issue_promotion":"prod341_360_manual_issue_promotion.json",
            "formal_approval_report":"prod361_380_formal_approval_report.json",
            "execution_guard":"prod361_380_issue_execution_guard.json",
            "transition_ledger":"prod361_380_state_transition_ledger.json",
            "formal_approval_readiness":"prod361_380_formal_approval_readiness.json",
            "formal_approval_audit":"prod361_380_audit_report.json",
        }
        checks={k:(self.outputs_root/v).exists() for k,v in stems.items()}
        return {"status":"PASS" if all(checks.values()) else "INCOMPLETE","product_direction":PRODUCT_DIRECTION,"runtime_mode":RUNTIME_MODE,"checks":checks,"blocked_actions":BLOCKED_ACTIONS,"next_recommended_step":"Edit approval manifest and re-run guard for a minimal approved subset."}
    def __getattr__(self,name):
        mapping={
            "formal_approval_report":("prod361_380_formal_approval_report.json","formal_approval_report"),
            "approval_manifest":("prod361_380_formal_approval_manifest_snapshot.json","approval_manifest"),
            "transition_ledger":("prod361_380_state_transition_ledger.json","transition_ledger"),
            "execution_guard":("prod361_380_issue_execution_guard.json","execution_guard"),
            "formal_approval_readiness":("prod361_380_formal_approval_readiness.json","formal_approval_readiness"),
            "formal_approval_audit":("prod361_380_audit_report.json","formal_approval_audit"),
        }
        if name in mapping:
            stem,key=mapping[name]
            return lambda: payload(self.outputs_root/stem,key)
        raise AttributeError(name)
    def runbook(self):
        p=self.outputs_root/"prod361_380_formal_approval_runbook.md"
        return {"status":"PASS" if p.exists() else "MISSING","path":str(p),"markdown":read_text(p) if p.exists() else ""}
    def reports(self):
        pats=["prod361_380_formal_approval_runbook.md","prod361_380_formal_approval_report.md","prod361_380_formal_approval_readiness.md","prod361_380_audit_report.md","prod361_380_report.md"]
        return {"status":"PASS","reports":[{"name":p,"exists":(self.outputs_root/p).exists(),"path":str(self.outputs_root/p),"preview":read_text(self.outputs_root/p)[:1200] if (self.outputs_root/p).exists() else ""} for p in pats]}

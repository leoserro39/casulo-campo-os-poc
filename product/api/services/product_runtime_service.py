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
            "formal_approval_guard":"prod361_380_issue_execution_guard.json",
            "minimal_approval_plan":"prod381_400_minimal_approval_plan.json",
            "dry_run_manifest":"prod381_400_dry_run_approval_manifest.json",
            "dry_run_guard":"prod381_400_execution_guard.json",
            "dry_run_readiness":"prod381_400_readiness.json",
            "dry_run_audit":"prod381_400_audit_report.json",
        }
        checks={k:(self.outputs_root/v).exists() for k,v in stems.items()}
        return {"status":"PASS" if all(checks.values()) else "INCOMPLETE","product_direction":PRODUCT_DIRECTION,"runtime_mode":RUNTIME_MODE,"checks":checks,"blocked_actions":BLOCKED_ACTIONS,"next_recommended_step":"Human may review command preview and decide whether to manually create one issue."}
    def __getattr__(self,name):
        mapping={
            "minimal_approval_plan":("prod381_400_minimal_approval_plan.json","minimal_approval_plan"),
            "dry_run_manifest":("prod381_400_dry_run_approval_manifest.json","dry_run_manifest"),
            "dry_run_ledger":("prod381_400_dry_run_transition_ledger.json","dry_run_ledger"),
            "dry_run_guard":("prod381_400_execution_guard.json","dry_run_guard"),
            "dry_run_readiness":("prod381_400_readiness.json","dry_run_readiness"),
            "dry_run_audit":("prod381_400_audit_report.json","dry_run_audit"),
        }
        if name in mapping:
            stem,key=mapping[name]
            return lambda: payload(self.outputs_root/stem,key)
        raise AttributeError(name)
    def command_preview(self):
        p=self.outputs_root/"prod381_400_approved_command_preview.md"
        return {"status":"PASS" if p.exists() else "MISSING","path":str(p),"markdown":read_text(p) if p.exists() else ""}
    def reports(self):
        pats=["prod381_400_minimal_dry_run_report.md","prod381_400_approved_command_preview.md","prod381_400_readiness.md","prod381_400_audit_report.md","prod381_400_report.md"]
        return {"status":"PASS","reports":[{"name":p,"exists":(self.outputs_root/p).exists(),"path":str(self.outputs_root/p),"preview":read_text(self.outputs_root/p)[:1200] if (self.outputs_root/p).exists() else ""} for p in pats]}

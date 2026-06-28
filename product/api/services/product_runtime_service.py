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
            "review_console":"prod321_340_review_console.json",
            "manual_issue_promotion":"prod341_360_manual_issue_promotion.json",
            "manifest_snapshot":"prod341_360_approved_issue_manifest_snapshot.json",
            "promotion_readiness":"prod341_360_manual_issue_promotion_readiness.json",
            "promotion_audit":"prod341_360_audit_report.json",
        }
        checks={k:(self.outputs_root/v).exists() for k,v in stems.items()}
        return {"status":"PASS" if all(checks.values()) else "INCOMPLETE","product_direction":PRODUCT_DIRECTION,"runtime_mode":RUNTIME_MODE,"checks":checks,"blocked_actions":BLOCKED_ACTIONS,"next_recommended_step":"Edit approval manifest or move to formal approval workflow."}
    def __getattr__(self,name):
        mapping={
            "manual_issue_promotion":("prod341_360_manual_issue_promotion.json","manual_issue_promotion"),
            "manifest_snapshot":("prod341_360_approved_issue_manifest_snapshot.json","manifest_snapshot"),
            "promotion_readiness":("prod341_360_manual_issue_promotion_readiness.json","promotion_readiness"),
            "promotion_audit":("prod341_360_audit_report.json","promotion_audit"),
        }
        if name in mapping:
            stem,key=mapping[name]
            return lambda: payload(self.outputs_root/stem,key)
        raise AttributeError(name)
    def command_templates(self):
        p=self.outputs_root/"prod341_360_gh_issue_command_templates.md"
        return {"status":"PASS" if p.exists() else "MISSING","path":str(p),"markdown":read_text(p) if p.exists() else ""}
    def reports(self):
        pats=["prod341_360_manual_issue_promotion.md","prod341_360_gh_issue_command_templates.md","prod341_360_manual_issue_promotion_readiness.md","prod341_360_audit_report.md","prod341_360_report.md"]
        return {"status":"PASS","reports":[{"name":p,"exists":(self.outputs_root/p).exists(),"path":str(self.outputs_root/p),"preview":read_text(self.outputs_root/p)[:1200] if (self.outputs_root/p).exists() else ""} for p in pats]}

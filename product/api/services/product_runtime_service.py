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
            "real_graph_case_aggregate":"prod301_320_real_graph_case_aggregate.json",
            "review_console":"prod321_340_review_console.json",
            "issue_selection":"prod321_340_issue_selection.json",
            "decision_log":"prod321_340_review_decision_log.json",
            "human_review_pack":"prod321_340_human_review_pack.json",
            "review_readiness":"prod321_340_review_console_readiness.json",
            "review_audit":"prod321_340_audit_report.json",
        }
        checks={k:(self.outputs_root/v).exists() for k,v in stems.items()}
        return {"status":"PASS" if all(checks.values()) else "INCOMPLETE","product_direction":PRODUCT_DIRECTION,"runtime_mode":RUNTIME_MODE,"checks":checks,"blocked_actions":BLOCKED_ACTIONS,"next_recommended_step":"Human review selected candidates; optionally generate manual issue promotion pack."}
    def __getattr__(self,name):
        mapping={
            "review_console":("prod321_340_review_console.json","review_console"),
            "issue_selection":("prod321_340_issue_selection.json","issue_selection"),
            "decision_log":("prod321_340_review_decision_log.json","decision_log"),
            "human_review_pack":("prod321_340_human_review_pack.json","human_review_pack"),
            "review_readiness":("prod321_340_review_console_readiness.json","review_readiness"),
            "review_audit":("prod321_340_audit_report.json","review_audit"),
        }
        if name in mapping:
            stem,key=mapping[name]
            return lambda: payload(self.outputs_root/stem,key)
        raise AttributeError(name)
    def reports(self):
        pats=["prod321_340_review_console.md","prod321_340_human_review_pack.md","prod321_340_review_console_readiness.md","prod321_340_audit_report.md","prod321_340_report.md"]
        return {"status":"PASS","reports":[{"name":p,"exists":(self.outputs_root/p).exists(),"path":str(self.outputs_root/p),"preview":read_text(self.outputs_root/p)[:1200] if (self.outputs_root/p).exists() else ""} for p in pats]}

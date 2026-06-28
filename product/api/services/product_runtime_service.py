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
            "closure_ledger":"prod421_440_closure_ledger.json",
            "synthetic_url_manifest":"prod441_460_synthetic_manual_url_manifest.json",
            "closure_replay_ledger":"prod441_460_closure_replay_ledger.json",
            "closure_replay_result":"prod441_460_closure_replay_result.json",
            "closure_replay_readiness":"prod441_460_readiness.json",
            "closure_replay_audit":"prod441_460_audit_report.json",
        }
        checks={k:(self.outputs_root/v).exists() for k,v in stems.items()}
        return {"status":"PASS" if all(checks.values()) else "INCOMPLETE","product_direction":PRODUCT_DIRECTION,"runtime_mode":RUNTIME_MODE,"checks":checks,"blocked_actions":BLOCKED_ACTIONS,"next_recommended_step":"Use a real human-provided issue URL or keep pending; synthetic replay is not real evidence."}
    def __getattr__(self,name):
        mapping={
            "synthetic_url_manifest":("prod441_460_synthetic_manual_url_manifest.json","synthetic_url_manifest"),
            "closure_replay_ledger":("prod441_460_closure_replay_ledger.json","closure_replay_ledger"),
            "closure_replay_result":("prod441_460_closure_replay_result.json","closure_replay_result"),
            "closure_replay_readiness":("prod441_460_readiness.json","closure_replay_readiness"),
            "closure_replay_audit":("prod441_460_audit_report.json","closure_replay_audit"),
        }
        if name in mapping:
            stem,key=mapping[name]
            return lambda: payload(self.outputs_root/stem,key)
        raise AttributeError(name)
    def reports(self):
        pats=["prod441_460_closure_replay_report.md","prod441_460_readiness.md","prod441_460_audit_report.md","prod441_460_report.md"]
        return {"status":"PASS","reports":[{"name":p,"exists":(self.outputs_root/p).exists(),"path":str(self.outputs_root/p),"preview":read_text(self.outputs_root/p)[:1200] if (self.outputs_root/p).exists() else ""} for p in pats]}

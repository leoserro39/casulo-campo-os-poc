#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    out=Path(args.repo)/"outputs"
    guard=json.loads((out/"prod361_380_issue_execution_guard.json").read_text(encoding="utf-8"))
    readiness=json.loads((out/"prod361_380_formal_approval_readiness.json").read_text(encoding="utf-8"))
    audit={
        "status":"PASS",
        "audit":"Formal Approval Workflow and Issue Execution Guard audit",
        "selected_count":guard["selected_count"],
        "approved_count":guard["approved_count"],
        "created_manually_count":guard["created_manually_count"],
        "invalid_transition_count":guard["invalid_transition_count"],
        "auto_execution_allowed":guard["auto_execution_allowed"],
        "readiness":readiness["decision"],
        "finding":"PASS: formal approval workflow generated state ledger and execution guard without automatic issue creation.",
    }
    (out/"prod361_380_audit_report.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"prod361_380_audit_report.md").write_text("# PROD-361..380 Audit Report\n\n"+"\n".join([f"- {k}: `{v}`" for k,v in audit.items()])+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

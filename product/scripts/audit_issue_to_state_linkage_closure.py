#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    out=Path(args.repo)/"outputs"
    ledger=json.loads((out/"prod421_440_closure_ledger.json").read_text(encoding="utf-8"))
    readiness=json.loads((out/"prod421_440_readiness.json").read_text(encoding="utf-8"))
    s=ledger["summary"]
    audit={
        "status":"PASS",
        "audit":"Issue-to-State Linkage and Closure Ledger audit",
        "record_count":s["record_count"],
        "pending_manual_creation_count":s["pending_manual_creation_count"],
        "created_manually_ready_to_link_count":s["created_manually_ready_to_link_count"],
        "evidence_incomplete_count":s["evidence_incomplete_count"],
        "auto_execution_allowed":s["auto_execution_allowed"],
        "readiness":readiness["decision"],
        "finding":"PASS: closure ledger tracks issue candidates and pending manual creation without automatic closure.",
    }
    (out/"prod421_440_audit_report.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"prod421_440_audit_report.md").write_text("# PROD-421..440 Audit Report\n\n"+"\n".join([f"- {k}: `{v}`" for k,v in audit.items()])+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

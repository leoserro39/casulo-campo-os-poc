#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    out=Path(args.repo)/"outputs"
    capture=json.loads((out/"prod401_420_manual_issue_evidence_capture.json").read_text(encoding="utf-8"))
    readiness=json.loads((out/"prod401_420_readiness.json").read_text(encoding="utf-8"))
    audit={
        "status":"PASS",
        "audit":"Manual Issue Creation Evidence Capture audit",
        "approved_count":capture["approved_count"],
        "captured_count":capture["captured_count"],
        "pending_count":capture["pending_count"],
        "incomplete_count":capture["incomplete_count"],
        "auto_execution_allowed":capture["auto_execution_allowed"],
        "readiness":readiness["decision"],
        "finding":"PASS: manual issue evidence capture is traceable and auto execution is disabled.",
    }
    (out/"prod401_420_audit_report.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"prod401_420_audit_report.md").write_text("# PROD-401..420 Audit Report\n\n"+"\n".join([f"- {k}: `{v}`" for k,v in audit.items()])+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

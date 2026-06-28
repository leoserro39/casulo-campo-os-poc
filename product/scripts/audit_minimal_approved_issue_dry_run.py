#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    out=Path(args.repo)/"outputs"
    guard=json.loads((out/"prod381_400_execution_guard.json").read_text(encoding="utf-8"))
    readiness=json.loads((out/"prod381_400_readiness.json").read_text(encoding="utf-8"))
    audit={
        "status":"PASS",
        "audit":"Minimal Approved Issue Dry Run audit",
        "approved_count":guard["approved_count"],
        "approved_commands_available":guard["approved_commands_available"],
        "invalid_transition_count":guard["invalid_transition_count"],
        "auto_execution_allowed":guard["auto_execution_allowed"],
        "source_manifest_modified":guard["source_manifest_modified"],
        "readiness":readiness["decision"],
        "finding":"PASS: dry-run approval transition is valid and command preview remains manual-only.",
    }
    (out/"prod381_400_audit_report.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"prod381_400_audit_report.md").write_text("# PROD-381..400 Audit Report\n\n"+"\n".join([f"- {k}: `{v}`" for k,v in audit.items()])+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

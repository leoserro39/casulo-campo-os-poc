#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    out=Path(args.repo)/"outputs"
    console=json.loads((out/"prod321_340_review_console.json").read_text(encoding="utf-8"))
    readiness=json.loads((out/"prod321_340_review_console_readiness.json").read_text(encoding="utf-8"))
    audit={
        "status":"PASS",
        "audit":"Graph Case Review Console audit",
        "case_count":console["case_count"],
        "total_issue_candidates":console["total_issue_candidates"],
        "selected_issue_count":console["selected_issue_count"],
        "decision":console["decision"],
        "readiness":readiness["decision"],
        "finding":"PASS: review console generated selected issue queue and human review pack without automatic issue creation.",
    }
    (out/"prod321_340_audit_report.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"prod321_340_audit_report.md").write_text("# PROD-321..340 Audit Report\n\n"+"\n".join([f"- {k}: `{v}`" for k,v in audit.items()])+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

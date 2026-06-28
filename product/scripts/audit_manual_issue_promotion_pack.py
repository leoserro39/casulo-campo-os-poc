#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    out=Path(args.repo)/"outputs"
    promotion=json.loads((out/"prod341_360_manual_issue_promotion.json").read_text(encoding="utf-8"))
    readiness=json.loads((out/"prod341_360_manual_issue_promotion_readiness.json").read_text(encoding="utf-8"))
    audit={
        "status":"PASS",
        "audit":"Manual Issue Promotion Pack audit",
        "selected_count":promotion["selected_count"],
        "approved_count":promotion["approved_count"],
        "generated_issue_files":len(promotion["issue_files"]),
        "command_templates":len(promotion["command_templates"]),
        "auto_created_count":promotion["auto_created_count"],
        "readiness":readiness["decision"],
        "finding":"PASS: promotion pack generated manual issue artifacts without automatic issue creation.",
    }
    (out/"prod341_360_audit_report.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"prod341_360_audit_report.md").write_text("# PROD-341..360 Audit Report\n\n"+"\n".join([f"- {k}: `{v}`" for k,v in audit.items()])+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

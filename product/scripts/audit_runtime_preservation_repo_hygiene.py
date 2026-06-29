#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo", default="."); args=ap.parse_args()
    out=Path(args.repo)/"outputs"
    audit=json.loads((out/"prod501_520_audit_report.json").read_text(encoding="utf-8"))
    readiness=json.loads((out/"prod501_520_readiness.json").read_text(encoding="utf-8"))
    audit["readiness"] = readiness["decision"]
    audit["status"] = "PASS" if readiness["missing_route_count"] == 0 else "ATTENTION"
    (out/"prod501_520_audit_report.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"prod501_520_audit_report.md").write_text("# PROD-501..520 Audit Report\n\n"+"\n".join([f"- {k}: `{v}`" for k,v in audit.items() if not isinstance(v,(list,dict))])+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

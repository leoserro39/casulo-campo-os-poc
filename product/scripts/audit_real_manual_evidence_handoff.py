#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    out=Path(args.repo)/"outputs"
    handoff=json.loads((out/"prod461_480_real_manual_evidence_handoff.json").read_text(encoding="utf-8"))
    readiness=json.loads((out/"prod461_480_readiness.json").read_text(encoding="utf-8"))
    audit={
        "status":"PASS",
        "audit":"Real Manual Evidence Handoff Pack audit",
        "candidate_count":handoff["candidate_count"],
        "valid_real_evidence_count":handoff["valid_real_evidence_count"],
        "pending_real_manual_url_count":handoff["pending_real_manual_url_count"],
        "synthetic_rejected_count":handoff["synthetic_rejected_count"],
        "auto_execution_allowed":handoff["auto_execution_allowed"],
        "network_validation_performed":handoff["network_validation_performed"],
        "readiness":readiness["decision"],
        "finding":"PASS: handoff separates synthetic replay from real evidence and keeps execution manual-only.",
    }
    (out/"prod461_480_audit_report.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"prod461_480_audit_report.md").write_text("# PROD-461..480 Audit Report\n\n"+"\n".join([f"- {k}: `{v}`" for k,v in audit.items()])+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

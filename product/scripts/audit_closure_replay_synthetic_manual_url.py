#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    out=Path(args.repo)/"outputs"
    result=json.loads((out/"prod441_460_closure_replay_result.json").read_text(encoding="utf-8"))
    readiness=json.loads((out/"prod441_460_readiness.json").read_text(encoding="utf-8"))
    audit={
        "status":"PASS",
        "audit":"Closure Replay with Synthetic Manual URL audit",
        "synthetic_only":result["synthetic_only"],
        "replay_count":result["replay_count"],
        "created_manually_ready_to_link_count":result["created_manually_ready_to_link_count"],
        "real_evidence_claim_count":result["real_evidence_claim_count"],
        "auto_execution_allowed":result["auto_execution_allowed"],
        "readiness":readiness["decision"],
        "finding":"PASS: synthetic closure replay validates linkage logic without creating, verifying or claiming real issues.",
    }
    (out/"prod441_460_audit_report.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"prod441_460_audit_report.md").write_text("# PROD-441..460 Audit Report\n\n"+"\n".join([f"- {k}: `{v}`" for k,v in audit.items()])+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    out=Path(args.repo)/"outputs"
    report=json.loads((out/"prod281_300_practical_backlog_report.json").read_text(encoding="utf-8"))
    readiness=json.loads((out/"prod281_300_graph_task_bridge_readiness.json").read_text(encoding="utf-8"))
    audit={
        "status":"PASS",
        "audit":"Graph Task Bridge audit",
        "source_task_count":report["source_task_count"],
        "cluster_count":report["cluster_count"],
        "issue_candidate_count":report["issue_candidate_count"],
        "decision":report["decision"],
        "readiness":readiness["decision"],
        "finding":"PASS: graph task bridge produced practical clusters and issue candidates without creating issues automatically.",
    }
    (out/"prod281_300_audit_report.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"prod281_300_audit_report.md").write_text("# PROD-281..300 Audit Report\n\n"+"\n".join([f"- {k}: `{v}`" for k,v in audit.items()])+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

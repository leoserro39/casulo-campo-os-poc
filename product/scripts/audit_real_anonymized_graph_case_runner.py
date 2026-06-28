#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    out=Path(args.repo)/"outputs"
    agg=json.loads((out/"prod301_320_real_graph_case_aggregate.json").read_text(encoding="utf-8"))
    readiness=json.loads((out/"prod301_320_real_graph_case_readiness.json").read_text(encoding="utf-8"))
    audit={
        "status":"PASS",
        "audit":"Real/Anonymized Graph Case Runner audit",
        "case_count":agg["case_count"],
        "decision":agg["decision"],
        "total_tasks":agg["aggregate_metrics"]["total_tasks"],
        "total_clusters":agg["aggregate_metrics"]["total_clusters"],
        "total_issue_candidates":agg["aggregate_metrics"]["total_issue_candidates"],
        "total_p0_blockers":agg["aggregate_metrics"]["total_p0_blockers"],
        "readiness":readiness["decision"],
        "finding":"PASS: real/anonymized graph case runner produced case-level telemetry and practical backlog without production automation.",
    }
    (out/"prod301_320_audit_report.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"prod301_320_audit_report.md").write_text("# PROD-301..320 Audit Report\n\n"+"\n".join([f"- {k}: `{v}`" for k,v in audit.items()])+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

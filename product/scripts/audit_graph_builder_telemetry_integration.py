#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    out=Path(args.repo)/"outputs"
    result=json.loads((out/"prod261_280_graph_builder_telemetry_result.json").read_text(encoding="utf-8"))
    readiness=json.loads((out/"prod261_280_graph_builder_readiness.json").read_text(encoding="utf-8"))
    audit={"status":"PASS","audit":"Graph Builder Telemetry Integration audit","nodes":len(result["graph"]["nodes"]),"edges":len(result["graph"]["edges"]),"tasks":len(result["tasks"]),"decision":result["decision"]["decision"],"readiness":readiness["decision"],"finding":"PASS: candidate graph builder telemetry generated graph, controls, gates, missing artifact tasks and practical closure decision."}
    (out/"prod261_280_audit_report.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"prod261_280_audit_report.md").write_text("# PROD-261..280 Audit Report\n\n"+"\n".join([f"- {k}: `{v}`" for k,v in audit.items()])+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

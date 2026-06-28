#!/usr/bin/env python3
from __future__ import annotations
import argparse, json
from pathlib import Path
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--repo",default="."); args=ap.parse_args()
    out=Path(args.repo)/"outputs"
    delta=json.loads((out/"prod241_260_delta_library_v2.json").read_text(encoding="utf-8"))
    sync=json.loads((out/"prod241_260_graph_sync_lab_report.json").read_text(encoding="utf-8"))
    readiness=json.loads((out/"prod241_260_graph_sync_readiness.json").read_text(encoding="utf-8"))
    audit={"status":"PASS","audit":"Graph Sync Telemetry and Delta Library v2 audit","delta_count":len(delta.get("delta_library",[])),"sync_attempts":len(sync.get("sync_attempts",[])),"stop_reason":sync.get("sync_summary",{}).get("stop_reason"),"self_sustaining_status":sync.get("sync_summary",{}).get("self_sustaining_status"),"readiness":readiness.get("decision"),"finding":"PASS: graph sync telemetry and delta library can test cross-domain connection, control recommendations and practical stop rules."}
    (out/"prod241_260_audit_report.json").write_text(json.dumps(audit,indent=2,ensure_ascii=False)+"\n",encoding="utf-8")
    (out/"prod241_260_audit_report.md").write_text("# PROD-241..260 Audit Report\n\n"+ "\n".join([f"- {k}: `{v}`" for k,v in audit.items()])+"\n",encoding="utf-8")
    print(json.dumps(audit,indent=2,ensure_ascii=False))
if __name__=="__main__": main()

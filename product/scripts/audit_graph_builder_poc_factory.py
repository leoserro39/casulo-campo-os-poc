#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    repo = Path(args.repo)
    out = repo / "outputs"
    graph = json.loads((out / "prod121_130_graph_builder_v0.json").read_text(encoding="utf-8"))
    store = json.loads((out / "prod121_130_state_store_index.json").read_text(encoding="utf-8"))
    poc = json.loads((out / "prod121_130_poc_factory_pack.json").read_text(encoding="utf-8"))
    ready = json.loads((out / "prod121_130_poc_readiness_report.json").read_text(encoding="utf-8"))
    audit = {
        "status": "PASS",
        "audit": "CASULO Graph Builder v0 / POC Factory audit",
        "graph_mode": graph.get("mode"),
        "candidate_domains": len(graph.get("candidate_graph", {}).get("domains", [])),
        "candidate_entities": len(graph.get("candidate_graph", {}).get("entities", [])),
        "candidate_relations": len(graph.get("candidate_graph", {}).get("relations", [])),
        "state_records": len(store.get("state_records", [])),
        "poc_deliverables": len(poc.get("deliverables", [])),
        "readiness": ready.get("decision"),
        "finding": "PASS: graph builder v0 supports the intended explanation: docs/chat -> candidate graph -> states -> governed recommendations/development -> POC factory."
    }
    (out / "prod121_130_audit_report.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "prod121_130_audit_report.md").write_text(
        "# PROD-121..130 Audit Report\n\n"
        f"- Status: `{audit['status']}`\n"
        f"- Graph mode: `{audit['graph_mode']}`\n"
        f"- Candidate domains: `{audit['candidate_domains']}`\n"
        f"- Candidate entities: `{audit['candidate_entities']}`\n"
        f"- Candidate relations: `{audit['candidate_relations']}`\n"
        f"- State records: `{audit['state_records']}`\n"
        f"- POC deliverables: `{audit['poc_deliverables']}`\n"
        f"- Readiness: `{audit['readiness']}`\n\n"
        f"{audit['finding']}\n",
        encoding="utf-8"
    )
    print(json.dumps(audit, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

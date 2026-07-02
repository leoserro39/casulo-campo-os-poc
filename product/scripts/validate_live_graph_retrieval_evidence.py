#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

REQUIRED_NODES = ["REAL-CASE-001", "GITHUB-AGENT-FOUNDATION-v0.1", "P0-MATRIX-BATCH01"]
REQUIRED_RELS = ["RUNS_CASE", "MEASURED_BY"]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("evidence")
    args = ap.parse_args()

    p = Path(args.evidence)
    data = json.loads(p.read_text(encoding="utf-8"))

    observed = data.get("observed", {})
    node_ids = [str(x) for x in observed.get("node_ids", [])]
    rels = [str(x) for x in observed.get("relationship_types", [])]

    checks = {
        "neo4j_environment_sandbox": data.get("neo4j_environment") == "sandbox",
        "query_mode_read_only": data.get("query_mode") == "READ_ONLY",
        "production_write_not_executed": data.get("production_write_executed") is False,
        "live_query_executed": data.get("live_query_executed") is True,
        "node_count_matches": observed.get("node_count") == 3,
        "relationship_count_matches": observed.get("relationship_count") == 2,
        "required_nodes_present": all(any(req in n for n in node_ids) for req in REQUIRED_NODES),
        "required_relationships_present": all(any(req in r for r in rels) for req in REQUIRED_RELS),
        "graph_path_confirmed": observed.get("graph_path_confirmed") is True,
    }

    result = {
        "status": "PASS" if all(checks.values()) else "FAIL",
        "checks": checks,
        "live_graph_retrieval_confirmed": all(checks.values()),
        "client_claim_allowed": False,
        "production_allowed": False,
    }

    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 0 if result["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

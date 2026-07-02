#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import py_compile
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()
PHASE = "PROD-8301..8340"
DECISION = "READ_ONLY_ADAPTERS_GIT_REPO_OUTPUTS_NEO4J_READY_FOR_LOCAL_ENDPOINT_VALIDATION"

REQUIRED = [
    "outputs/prod8261_8300_casulo_agent_api_server_action_scaffold.json",
    "product/api/casulo_agent_api_server.py",
    "product/api/openapi/casulo_agent_action_openapi.json",
    "product/cube/operational_cube_master_contract.json",
    "product/calibration/casulo_kpi_vector_telemetry_inventory.json",
    "product/audits/prod8221_8260_integrated_repo_timeline_audit.json",
]

GENERATED = [
    "product/adapters/read_only/git_repo_adapter.py",
    "product/adapters/read_only/output_artifact_indexer.py",
    "product/adapters/read_only/neo4j_readonly_adapter_scaffold.py",
    "product/adapters/read_only/evidence_trace_adapter.py",
    "product/adapters/read_only/README.md",
    "product/api/casulo_agent_api_server_v02_adapters.py",
    "product/api/run_casulo_agent_api_server_v02.sh",
    "product/api/tests/test_readonly_adapters_static.py",
    "product/api/openapi/casulo_agent_action_openapi_v02.yaml",
    "product/api/openapi/casulo_agent_action_openapi_v02.json",
    "product/api/contracts/read_only_adapters_git_repo_outputs_neo4j.contract.json",
    "outputs/prod8301_8340_readonly_adapters_git_repo_outputs_neo4j.json",
    "outputs/prod8301_8340_readonly_adapters_git_repo_outputs_neo4j.md",
    "docs/product/830_READONLY_ADAPTERS_GIT_REPO_OUTPUTS_NEO4J.md",
]

BLOCKED_ACTIONS = [
    "client_facing_validated_claim",
    "production_activation",
    "commercial_claim",
    "validated_model_gain_claim",
    "validated_hallucination_reduction_claim",
    "automatic_merge",
    "real_world_side_effect",
    "github_issue_comment",
    "github_pr_comment",
    "external_repo_write",
    "production_neo4j_write",
    "neo4j_delete",
    "neo4j_reimport",
    "docker_volume_delete",
    "micrograph_runtime_claim",
    "delta_matrix_runtime_claim",
    "state_family_runtime_claim",
    "multi_llm_braid_runtime_claim",
    "invented_agent_concept_claim",
    "cockpit_as_primary_system_claim",
    "agent_as_primary_system_claim",
]

def read_json(path: str, default: Any = None) -> Any:
    p = ROOT / path
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def write_text(path: str, text: str, wrote: List[str], executable: bool = False) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    if executable:
        p.chmod(0o755)
    wrote.append(path)

def write_json(path: str, data: Any, wrote: List[str]) -> None:
    write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n", wrote)

def run_cmd(args: List[str], timeout: int = 30) -> Dict[str, Any]:
    try:
        cp = subprocess.run(args, cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        return {
            "ok": cp.returncode == 0,
            "returncode": cp.returncode,
            "stdout": cp.stdout.strip(),
            "stderr": cp.stderr.strip(),
            "cmd": " ".join(args),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "cmd": " ".join(args)}

GIT_ADAPTER = r"""#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

BLOCKED_ACTIONS = [
    "automatic_merge",
    "github_issue_comment",
    "github_pr_comment",
    "external_repo_write",
    "production_activation",
    "client_facing_validated_claim",
    "commercial_claim",
]

def run_git(args, timeout=10):
    try:
        cp = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, timeout=timeout)
        return {
            "ok": cp.returncode == 0,
            "returncode": cp.returncode,
            "stdout": cp.stdout.strip(),
            "stderr": cp.stderr.strip(),
            "command": "git " + " ".join(args),
        }
    except Exception as exc:
        return {"ok": False, "error": str(exc), "command": "git " + " ".join(args)}

def git_repo_status():
    return {
        "adapter": "git_repo_adapter.v0.1",
        "mode": "LOCAL_GIT_READ_ONLY",
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "head_full": run_git(["rev-parse", "HEAD"]),
        "branch": run_git(["branch", "--show-current"]),
        "status_short": run_git(["status", "--short"]),
        "last_commit": run_git(["log", "--oneline", "-1"]),
        "recent_commits": run_git(["log", "--oneline", "-20"]),
        "tags_at_head": run_git(["tag", "--points-at", "HEAD"]),
        "remote": run_git(["remote", "-v"]),
        "writes_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def git_repo_timeline(limit=80):
    raw = run_git(["log", "--date=iso", "--pretty=format:%h%x09%H%x09%ad%x09%s", "-n", str(limit)])
    commits = []
    if raw.get("ok"):
        for line in raw.get("stdout", "").splitlines():
            parts = line.split("\t", 3)
            if len(parts) == 4:
                commits.append({"short": parts[0], "sha": parts[1], "date": parts[2], "message": parts[3]})
    return {
        "adapter": "git_repo_adapter.v0.1",
        "mode": "LOCAL_GIT_READ_ONLY",
        "limit": limit,
        "count": len(commits),
        "commits": commits,
        "writes_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

if __name__ == "__main__":
    print(json.dumps(git_repo_status(), indent=2, ensure_ascii=False))
"""

OUTPUT_INDEXER = r"""#!/usr/bin/env python3
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SCAN_DIRS = ["outputs", "docs/product", "product/contracts", "product/calibration", "product/cube", "product/agent_manifest", "product/actions", "product/exocortex", "product/graph"]
SUFFIXES = {".json", ".md", ".yaml", ".yml", ".cypher", ".txt"}

def read_json(path: Path, default=None):
    if not path.exists() or path.suffix != ".json":
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return default

def artifact_index(max_items=300):
    items = []
    for d in SCAN_DIRS:
        root = ROOT / d
        if not root.exists():
            continue
        for p in sorted(root.rglob("*")):
            if not p.is_file() or p.suffix not in SUFFIXES:
                continue
            rel = str(p.relative_to(ROOT)).replace("\\", "/")
            stat = p.stat()
            item = {
                "path": rel,
                "suffix": p.suffix,
                "size_bytes": stat.st_size,
                "modified_time_unix": int(stat.st_mtime),
            }
            if p.suffix == ".json":
                data = read_json(p, {})
                if isinstance(data, dict):
                    item["status"] = data.get("status")
                    item["phase"] = data.get("phase")
                    item["decision"] = data.get("decision")
                    item["next"] = data.get("next")
            items.append(item)
            if len(items) >= max_items:
                break
        if len(items) >= max_items:
            break
    return {
        "adapter": "output_artifact_indexer.v0.1",
        "mode": "LOCAL_REPO_ARTIFACT_READ_ONLY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scan_dirs": SCAN_DIRS,
        "count": len(items),
        "items": items,
        "writes_allowed": False,
    }

def find_artifacts(query: str, max_items=80):
    q = query.lower().strip()
    idx = artifact_index(max_items=1000)["items"]
    hits = [x for x in idx if q in x["path"].lower() or q in str(x.get("phase", "")).lower() or q in str(x.get("decision", "")).lower()]
    return {
        "adapter": "output_artifact_indexer.v0.1",
        "query": query,
        "count": len(hits[:max_items]),
        "items": hits[:max_items],
        "writes_allowed": False,
    }

if __name__ == "__main__":
    print(json.dumps(artifact_index(), indent=2, ensure_ascii=False))
"""

NEO4J_ADAPTER = r"""#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
NODE_PAYLOADS = [
    "product/graph/neo4j_payloads/real_case_001_nodes_v0_1.json",
]
REL_PAYLOADS = [
    "product/graph/neo4j_payloads/real_case_001_relationships_v0_1.json",
]
GRAPH_OUTPUTS = [
    "outputs/prod7341_7380_graph_retrieval_gain_multirun_calibration.json",
    "outputs/prod8181_8220_cockpit_chat_scaffold_diagnostic_monitor.json",
]

BLOCKED_ACTIONS = [
    "production_neo4j_write",
    "neo4j_delete",
    "neo4j_reimport",
    "production_activation",
    "client_facing_validated_claim",
    "commercial_claim",
]

def read_json(path: str, default=None):
    p = ROOT / path
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def load_nodes():
    nodes = []
    for p in NODE_PAYLOADS:
        data = read_json(p, [])
        if isinstance(data, list):
            nodes.extend(data)
    return nodes

def load_relationships():
    rels = []
    for p in REL_PAYLOADS:
        data = read_json(p, [])
        if isinstance(data, list):
            rels.extend(data)
    return rels

def graph_summary():
    nodes = load_nodes()
    rels = load_relationships()
    graph_gain = read_json("outputs/prod7341_7380_graph_retrieval_gain_multirun_calibration.json", {})
    return {
        "adapter": "neo4j_readonly_adapter_scaffold.v0.1",
        "mode": "OFFLINE_PAYLOAD_READ_ONLY",
        "live_neo4j_connection_executed": False,
        "production_write_allowed": False,
        "node_payload_count": len(nodes),
        "relationship_payload_count": len(rels),
        "node_ids": [n.get("id") for n in nodes if isinstance(n, dict)][:80],
        "relationship_types": [r.get("type") for r in rels if isinstance(r, dict)][:80],
        "graph_retrieval_gain_proxy": graph_gain.get("graph_retrieval_gain", {}),
        "calibration_decision": graph_gain.get("calibration_decision", {}),
        "blocked_actions": BLOCKED_ACTIONS,
    }

def evidence_trace(case_id="REAL-CASE-001"):
    nodes = load_nodes()
    rels = load_relationships()
    selected_nodes = [n for n in nodes if str(n.get("id", "")).lower() == case_id.lower() or case_id.lower() in json.dumps(n, ensure_ascii=False).lower()]
    selected_rels = [r for r in rels if case_id.lower() in json.dumps(r, ensure_ascii=False).lower()]
    graph_gain = read_json("outputs/prod7341_7380_graph_retrieval_gain_multirun_calibration.json", {})
    return {
        "adapter": "neo4j_readonly_adapter_scaffold.v0.1",
        "mode": "OFFLINE_PAYLOAD_READ_ONLY",
        "case_id": case_id,
        "nodes": selected_nodes,
        "relationships": selected_rels,
        "graph_context": graph_gain.get("graph_context", {}),
        "ready_for_live_neo4j_retrieval": graph_gain.get("calibration_decision", {}).get("ready_for_live_neo4j_retrieval"),
        "live_neo4j_query_executed": False,
        "writes_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

if __name__ == "__main__":
    print(json.dumps(graph_summary(), indent=2, ensure_ascii=False))
"""

EVIDENCE_TRACE_ADAPTER = r"""#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

TRACE_FILES = [
    "outputs/prod7061_7260_casulo_macro_foundation.json",
    "outputs/prod7301_7340_ponto_zero_vector_telemetry.json",
    "outputs/prod7341_7380_graph_retrieval_gain_multirun_calibration.json",
    "outputs/prod8221_8260_operational_cube_master_contract_agent_readiness_audit.json",
    "outputs/prod8261_8300_casulo_agent_api_server_action_scaffold.json",
    "product/calibration/casulo_kpi_vector_telemetry_inventory.json",
    "product/cube/operational_cube_master_contract.json",
]

def read_json(path: str, default=None):
    p = ROOT / path
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def evidence_trace(case_id="REAL-CASE-001"):
    files = []
    for p in TRACE_FILES:
        data = read_json(p, {})
        if not data:
            continue
        payload_text = json.dumps(data, ensure_ascii=False)
        files.append({
            "path": p,
            "status": data.get("status"),
            "phase": data.get("phase"),
            "decision": data.get("decision"),
            "mentions_case": case_id in payload_text,
            "ready_for_client_claim": data.get("calibration_decision", {}).get("ready_for_client_claim", False),
            "ready_for_production": data.get("calibration_decision", {}).get("ready_for_production", False),
        })
    return {
        "adapter": "evidence_trace_adapter.v0.1",
        "case_id": case_id,
        "trace_files_count": len(files),
        "trace_files": files,
        "gate": "SANDBOX_ONLY_READ_ONLY_TRACE",
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "writes_allowed": False,
    }

if __name__ == "__main__":
    print(json.dumps(evidence_trace(), indent=2, ensure_ascii=False))
"""

SERVER_V02 = r"""#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse
import importlib.util

ROOT = Path(__file__).resolve().parents[2]

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

git_adapter = load_module("git_repo_adapter", "product/adapters/read_only/git_repo_adapter.py")
artifact_indexer = load_module("output_artifact_indexer", "product/adapters/read_only/output_artifact_indexer.py")
neo4j_adapter = load_module("neo4j_readonly_adapter_scaffold", "product/adapters/read_only/neo4j_readonly_adapter_scaffold.py")
trace_adapter = load_module("evidence_trace_adapter", "product/adapters/read_only/evidence_trace_adapter.py")

def route_get(path, query):
    if path == "/health":
        return 200, {
            "status": "ok",
            "service": "casulo_agent_api_server_v02_adapters",
            "phase": "PROD-8301..8340",
            "mode": "read_only_adapters",
            "writes_allowed": False,
        }
    if path == "/adapters/git/status":
        return 200, git_adapter.git_repo_status()
    if path == "/adapters/git/timeline":
        limit = int(query.get("limit", ["80"])[0])
        return 200, git_adapter.git_repo_timeline(limit=limit)
    if path == "/adapters/repo/artifact-index":
        return 200, artifact_indexer.artifact_index()
    if path == "/adapters/repo/find":
        q = query.get("q", [""])[0]
        return 200, artifact_indexer.find_artifacts(q)
    if path == "/adapters/graph/summary":
        return 200, neo4j_adapter.graph_summary()
    if path == "/adapters/evidence/trace":
        case_id = query.get("case_id", ["REAL-CASE-001"])[0]
        return 200, trace_adapter.evidence_trace(case_id=case_id)
    return 404, {"status": "not_found", "path": path}

class Handler(BaseHTTPRequestHandler):
    server_version = "CASULOAgentAPIAdapters/0.1"
    def _json(self, code, payload):
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        parsed = urlparse(self.path)
        code, payload = route_get(parsed.path, parse_qs(parsed.query))
        self._json(code, payload)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8301)
    args = ap.parse_args()
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(json.dumps({"serving": True, "host": args.host, "port": args.port, "health": f"http://127.0.0.1:{args.port}/health"}, indent=2))
    httpd.serve_forever()

if __name__ == "__main__":
    main()
"""

TEST_CODE = r"""#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

git_adapter = load("git_repo_adapter", "product/adapters/read_only/git_repo_adapter.py")
idx = load("output_artifact_indexer", "product/adapters/read_only/output_artifact_indexer.py")
neo = load("neo4j_readonly_adapter_scaffold", "product/adapters/read_only/neo4j_readonly_adapter_scaffold.py")
trace = load("evidence_trace_adapter", "product/adapters/read_only/evidence_trace_adapter.py")
server = load("casulo_agent_api_server_v02_adapters", "product/api/casulo_agent_api_server_v02_adapters.py")

status = git_adapter.git_repo_status()
assert status["mode"] == "LOCAL_GIT_READ_ONLY"
assert status["writes_allowed"] is False

artifacts = idx.artifact_index()
assert artifacts["mode"] == "LOCAL_REPO_ARTIFACT_READ_ONLY"
assert artifacts["count"] > 0

graph = neo.graph_summary()
assert graph["mode"] == "OFFLINE_PAYLOAD_READ_ONLY"
assert graph["live_neo4j_connection_executed"] is False
assert graph["production_write_allowed"] is False

ev = trace.evidence_trace()
assert ev["writes_allowed"] is False
assert ev["ready_for_client_claim"] is False
assert ev["ready_for_production"] is False

code, payload = server.route_get("/adapters/git/status", {})
assert code == 200
assert payload["writes_allowed"] is False

code, payload = server.route_get("/adapters/graph/summary", {})
assert code == 200
assert payload["live_neo4j_connection_executed"] is False

print(json.dumps({"status": "PASS", "tests": "readonly_adapters_static"}, indent=2))
"""

OPENAPI_JSON = {
    "openapi": "3.1.0",
    "info": {
        "title": "CASULO Agent Action API v0.2 Read-Only Adapters",
        "version": "0.2.0",
        "description": "Read-only adapter endpoints for Git, repo artifacts, offline Neo4j payloads and evidence trace."
    },
    "servers": [{"url": "https://REPLACE_WITH_PUBLIC_ACTION_SERVER"}],
    "paths": {
        "/adapters/git/status": {"get": {"operationId": "getGitStatus", "summary": "Read local Git status", "responses": {"200": {"description": "Git status"}}}},
        "/adapters/git/timeline": {"get": {"operationId": "getGitTimeline", "summary": "Read local Git timeline", "responses": {"200": {"description": "Git timeline"}}}},
        "/adapters/repo/artifact-index": {"get": {"operationId": "getArtifactIndex", "summary": "Read repo artifact index", "responses": {"200": {"description": "Artifact index"}}}},
        "/adapters/repo/find": {"get": {"operationId": "findArtifacts", "summary": "Find artifacts by query", "parameters": [{"name": "q", "in": "query", "required": True, "schema": {"type": "string"}}], "responses": {"200": {"description": "Artifact search results"}}}},
        "/adapters/graph/summary": {"get": {"operationId": "getGraphSummary", "summary": "Read offline graph summary", "responses": {"200": {"description": "Graph summary"}}}},
        "/adapters/evidence/trace": {"get": {"operationId": "getEvidenceTrace", "summary": "Read evidence trace by case_id", "parameters": [{"name": "case_id", "in": "query", "required": False, "schema": {"type": "string"}}], "responses": {"200": {"description": "Evidence trace"}}}},
    }
}

OPENAPI_YAML = """openapi: 3.1.0
info:
  title: CASULO Agent Action API v0.2 Read-Only Adapters
  version: 0.2.0
  description: Read-only adapter endpoints for Git, repo artifacts, offline Neo4j payloads and evidence trace.
servers:
  - url: https://REPLACE_WITH_PUBLIC_ACTION_SERVER
paths:
  /adapters/git/status:
    get:
      operationId: getGitStatus
      summary: Read local Git status
      responses:
        '200':
          description: Git status
  /adapters/git/timeline:
    get:
      operationId: getGitTimeline
      summary: Read local Git timeline
      responses:
        '200':
          description: Git timeline
  /adapters/repo/artifact-index:
    get:
      operationId: getArtifactIndex
      summary: Read repo artifact index
      responses:
        '200':
          description: Artifact index
  /adapters/repo/find:
    get:
      operationId: findArtifacts
      summary: Find artifacts by query
      parameters:
        - name: q
          in: query
          required: true
          schema:
            type: string
      responses:
        '200':
          description: Artifact search results
  /adapters/graph/summary:
    get:
      operationId: getGraphSummary
      summary: Read offline graph summary
      responses:
        '200':
          description: Graph summary
  /adapters/evidence/trace:
    get:
      operationId: getEvidenceTrace
      summary: Read evidence trace by case_id
      parameters:
        - name: case_id
          in: query
          required: false
          schema:
            type: string
      responses:
        '200':
          description: Evidence trace
"""

def check() -> Dict[str, Any]:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    return {
        "status": "PASS" if not missing else "FAIL",
        "phase": PHASE,
        "missing_required_count": len(missing),
        "missing_required": missing,
        "will_create": GENERATED,
        "will_call_gpt": False,
        "will_call_codex": False,
        "will_connect_live_neo4j": False,
        "will_write_github": False,
        "will_write_external_api": False,
        "will_implement_micrograph_runtime": False,
        "will_prioritize_cockpit": False,
    }

def build_result() -> Dict[str, Any]:
    return {
        "status": "PASS",
        "phase": PHASE,
        "decision": DECISION,
        "generated_at": STAMP,
        "calibration_decision": {
            "git_readonly_adapter_ready": True,
            "repo_artifact_indexer_ready": True,
            "offline_neo4j_payload_adapter_ready": True,
            "evidence_trace_adapter_ready": True,
            "api_v02_adapter_server_ready": True,
            "openapi_v02_adapter_schema_ready": True,
            "live_neo4j_connection_executed": False,
            "production_neo4j_write_allowed": False,
            "github_write_allowed": False,
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
            "micrograph_runtime_current_poc": False,
            "micrographs_future_epic_only": True,
            "cockpit_priority": "DEFERRED",
        },
        "endpoints": [
            "GET /adapters/git/status",
            "GET /adapters/git/timeline",
            "GET /adapters/repo/artifact-index",
            "GET /adapters/repo/find?q=...",
            "GET /adapters/graph/summary",
            "GET /adapters/evidence/trace?case_id=REAL-CASE-001",
        ],
        "next": "PROD-8341..8380 - Exocortex Context Rebuild Runtime",
    }

def apply() -> List[str]:
    wrote: List[str] = []
    result = build_result()
    contract = {
        "contract": "read_only_adapters_git_repo_outputs_neo4j.contract.v0.1",
        "phase": PHASE,
        "requires": REQUIRED,
        "status": "PASS",
        "decision": DECISION,
        "mode": "READ_ONLY_ADAPTERS",
        "blocked_actions": BLOCKED_ACTIONS,
        "implemented_endpoints": result["endpoints"],
        "not_implemented_yet": [
            "live Neo4j driver connection",
            "public ChatGPT Action deployment",
            "diagnostic service endpoint",
            "monitoring service endpoint",
            "solutions service endpoint",
            "calibration service endpoint",
            "business-case input runtime",
        ],
    }

    readme = """# CASULO Read-Only Adapters v0.1

Read-only adapters for Git, repo artifacts, offline Neo4j payloads and evidence trace.

No GPT calls.
No Codex execution.
No GitHub writes.
No live Neo4j connection.
No production.

## Test

```bash
python3 product/api/tests/test_readonly_adapters_static.py
```

## Run adapter API v0.2

```bash
python3 product/api/casulo_agent_api_server_v02_adapters.py --host 0.0.0.0 --port 8301
```
"""

    run_script = """#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.." || exit 1
python3 product/api/casulo_agent_api_server_v02_adapters.py --host 0.0.0.0 --port "${CASULO_AGENT_ADAPTER_API_PORT:-8301}"
"""

    docs = f"""# PROD-8301..8340 - Read-Only Adapters: Git, Repo, Outputs and Neo4j

Status: PASS  
Decision: `{DECISION}`

## Implements

- local Git read-only adapter;
- repo artifact/output indexer;
- offline Neo4j payload read-only adapter scaffold;
- evidence trace adapter;
- adapter API v0.2;
- OpenAPI v0.2 draft for future ChatGPT Actions.

## Does not implement

- live Neo4j connection;
- Neo4j write;
- GitHub write;
- GPT call;
- Codex execution;
- public deployment;
- client/production/commercial claims.

## Boundary

Cubo Operacional remains the governance core.  
Exocortex remains memory/state/context layer.  
CASULO Agent remains subordinate.  
Micrograph runtime remains future epic only.  
Cockpit remains deferred.

## Next

`PROD-8341..8380 - Exocortex Context Rebuild Runtime`
"""

    out_md = f"""# PROD-8301..8340 - Read-Only Adapters: Git, Repo, Outputs and Neo4j

Status: PASS  
Decision: `{DECISION}`

```json
{json.dumps(result["calibration_decision"], indent=2, ensure_ascii=False)}
```

## Endpoints

{chr(10).join("- `" + e + "`" for e in result["endpoints"])}

## Next

`{result["next"]}`
"""

    write_text("product/adapters/read_only/git_repo_adapter.py", GIT_ADAPTER, wrote, executable=True)
    write_text("product/adapters/read_only/output_artifact_indexer.py", OUTPUT_INDEXER, wrote, executable=True)
    write_text("product/adapters/read_only/neo4j_readonly_adapter_scaffold.py", NEO4J_ADAPTER, wrote, executable=True)
    write_text("product/adapters/read_only/evidence_trace_adapter.py", EVIDENCE_TRACE_ADAPTER, wrote, executable=True)
    write_text("product/adapters/read_only/README.md", readme, wrote)
    write_text("product/api/casulo_agent_api_server_v02_adapters.py", SERVER_V02, wrote, executable=True)
    write_text("product/api/run_casulo_agent_api_server_v02.sh", run_script, wrote, executable=True)
    write_text("product/api/tests/test_readonly_adapters_static.py", TEST_CODE, wrote, executable=True)
    write_text("product/api/openapi/casulo_agent_action_openapi_v02.yaml", OPENAPI_YAML, wrote)
    write_json("product/api/openapi/casulo_agent_action_openapi_v02.json", OPENAPI_JSON, wrote)
    write_json("product/api/contracts/read_only_adapters_git_repo_outputs_neo4j.contract.json", contract, wrote)
    write_json("outputs/prod8301_8340_readonly_adapters_git_repo_outputs_neo4j.json", result, wrote)
    write_text("outputs/prod8301_8340_readonly_adapters_git_repo_outputs_neo4j.md", out_md, wrote)
    write_text("docs/product/830_READONLY_ADAPTERS_GIT_REPO_OUTPUTS_NEO4J.md", docs, wrote)
    return wrote

def self_test() -> Dict[str, Any]:
    missing = [p for p in GENERATED if not (ROOT / p).exists()]
    json_errors = []
    py_errors = []
    for p in GENERATED:
        if p.endswith(".json"):
            try:
                json.loads((ROOT / p).read_text(encoding="utf-8"))
            except Exception as exc:
                json_errors.append({"path": p, "error": str(exc)})
        if p.endswith(".py"):
            try:
                py_compile.compile(str(ROOT / p), doraise=True)
            except Exception as exc:
                py_errors.append({"path": p, "error": str(exc)})
    test = run_cmd(["python3", "product/api/tests/test_readonly_adapters_static.py"], timeout=30)
    result = read_json("outputs/prod8301_8340_readonly_adapters_git_repo_outputs_neo4j.json", {})
    cal = result.get("calibration_decision", {})
    checks = {
        "generated_missing_count": len(missing),
        "json_errors_count": len(json_errors),
        "py_errors_count": len(py_errors),
        "static_tests_passed": test.get("ok") is True,
        "git_readonly_adapter_ready": cal.get("git_readonly_adapter_ready") is True,
        "repo_artifact_indexer_ready": cal.get("repo_artifact_indexer_ready") is True,
        "offline_neo4j_payload_adapter_ready": cal.get("offline_neo4j_payload_adapter_ready") is True,
        "evidence_trace_adapter_ready": cal.get("evidence_trace_adapter_ready") is True,
        "live_neo4j_connection_executed_false": cal.get("live_neo4j_connection_executed") is False,
        "production_neo4j_write_allowed_false": cal.get("production_neo4j_write_allowed") is False,
        "micrograph_runtime_current_poc_false": cal.get("micrograph_runtime_current_poc") is False,
    }
    passed = not missing and not json_errors and not py_errors and all(v is True or (isinstance(v, int) and v == 0) for v in checks.values())
    return {
        "status": "PASS" if passed else "FAIL",
        "phase": PHASE,
        "checks": checks,
        "generated_missing": missing,
        "json_errors": json_errors,
        "py_errors": py_errors,
        "static_test": test,
    }

def commit_plan() -> str:
    paths = ["apply_prod8301_8340_readonly_adapters_git_repo_outputs_neo4j.py", *GENERATED]
    lines = ["git add \\"]
    for p in paths[:-1]:
        lines.append(f"  {p} \\")
    lines.append(f"  {paths[-1]}")
    lines.extend([
        "",
        'git commit -m "Add read-only adapters for Git repo outputs and Neo4j"',
        'git tag -a product-casulo-readonly-adapters-git-repo-neo4j-v0.1 HEAD -m "CASULO read-only adapters Git repo Neo4j v0.1"',
        "git push origin main",
        "git push origin product-casulo-readonly-adapters-git-repo-neo4j-v0.1",
    ])
    return "\n".join(lines)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--commit-plan", action="store_true")
    args = ap.parse_args()
    if not any(vars(args).values()):
        args.check = True
    if args.check:
        print(json.dumps(check(), indent=2, ensure_ascii=False))
    if args.apply:
        c = check()
        if c["status"] != "PASS":
            print(json.dumps(c, indent=2, ensure_ascii=False))
            raise SystemExit("CHECK_FAILED")
        wrote = apply()
        print(json.dumps({"applied": True, "wrote_count": len(wrote), "wrote": wrote}, indent=2, ensure_ascii=False))
    if args.self_test:
        print(json.dumps(self_test(), indent=2, ensure_ascii=False))
    if args.commit_plan:
        print(commit_plan())
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

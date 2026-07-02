#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()
PHASE = "PROD-8261..8300"
DECISION = "CASULO_AGENT_API_SERVER_ACTION_SCAFFOLD_READY_FOR_LOCAL_ENDPOINT_VALIDATION"

REQUIRED = [
    "outputs/prod8221_8260_operational_cube_master_contract_agent_readiness_audit.json",
    "product/cube/operational_cube_master_contract.json",
    "product/agent_manifest/chatgpt_agent_readiness_manifest.json",
    "product/actions/casulo_chatgpt_action_requirements.json",
    "product/memory/chat_memory_boundary_context_rebuild_gate.contract.json",
    "product/calibration/casulo_kpi_vector_telemetry_inventory.json",
    "product/audits/prod8221_8260_integrated_repo_timeline_audit.json",
]

GENERATED = [
    "product/api/casulo_agent_api_server.py",
    "product/api/README.md",
    "product/api/run_casulo_agent_api_server.sh",
    "product/api/tests/test_casulo_agent_api_server_static.py",
    "product/api/openapi/casulo_agent_action_openapi.yaml",
    "product/api/openapi/casulo_agent_action_openapi.json",
    "product/api/contracts/casulo_agent_api_server_action_scaffold.contract.json",
    "outputs/prod8261_8300_casulo_agent_api_server_action_scaffold.json",
    "outputs/prod8261_8300_casulo_agent_api_server_action_scaffold.md",
    "docs/product/826_CASULO_AGENT_API_SERVER_ACTION_SCAFFOLD.md",
]

BLOCKED_ACTIONS = [
    "client_facing_validated_claim", "production_activation", "commercial_claim",
    "validated_model_gain_claim", "validated_hallucination_reduction_claim",
    "automatic_merge", "real_world_side_effect", "github_issue_comment",
    "github_pr_comment", "external_repo_write", "production_neo4j_write",
    "neo4j_delete", "neo4j_reimport", "docker_volume_delete",
    "micrograph_runtime_claim", "delta_matrix_runtime_claim",
    "state_family_runtime_claim", "multi_llm_braid_runtime_claim",
    "invented_agent_concept_claim", "cockpit_as_primary_system_claim",
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
        return {"ok": cp.returncode == 0, "returncode": cp.returncode, "stdout": cp.stdout.strip(), "stderr": cp.stderr.strip(), "cmd": " ".join(args)}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "cmd": " ".join(args)}

SERVER_CODE = r"""#!/usr/bin/env python3
from __future__ import annotations
import argparse, json, subprocess
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]
BLOCKED_ACTIONS = [
    "client_facing_validated_claim", "production_activation", "commercial_claim",
    "validated_model_gain_claim", "validated_hallucination_reduction_claim",
    "automatic_merge", "real_world_side_effect", "github_issue_comment",
    "github_pr_comment", "external_repo_write", "production_neo4j_write",
    "neo4j_delete", "neo4j_reimport", "docker_volume_delete",
    "micrograph_runtime_claim", "delta_matrix_runtime_claim",
    "state_family_runtime_claim", "multi_llm_braid_runtime_claim",
    "invented_agent_concept_claim", "cockpit_as_primary_system_claim",
    "agent_as_primary_system_claim"
]

def read_json(path, default=None):
    p = ROOT / path
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def run_git(args):
    try:
        cp = subprocess.run(["git", *args], cwd=ROOT, text=True, capture_output=True, timeout=10)
        return {"ok": cp.returncode == 0, "stdout": cp.stdout.strip(), "stderr": cp.stderr.strip()}
    except Exception as exc:
        return {"ok": False, "error": str(exc)}

def build_health():
    return {
        "status": "ok",
        "service": "casulo_agent_api_server",
        "version": "v0.1",
        "phase": "PROD-8261..8300",
        "mode": "local_read_only_scaffold",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "will_call_gpt": False,
        "will_call_codex": False,
        "will_call_neo4j": False,
        "will_write_external_systems": False,
        "blocked_actions": BLOCKED_ACTIONS,
    }

def build_state_current():
    cube = read_json("product/cube/operational_cube_master_contract.json", {})
    audit = read_json("outputs/prod8221_8260_operational_cube_master_contract_agent_readiness_audit.json", {})
    telemetry = read_json("product/calibration/casulo_kpi_vector_telemetry_inventory.json", {})
    return {
        "status": "ok",
        "state_label": "CASULO_AGENT_API_SCAFFOLD_READ_ONLY",
        "gate": "SANDBOX_ONLY",
        "operational_cube": {
            "role": cube.get("canonical_hierarchy", {}).get("operational_cube"),
            "primary_governance_core": cube.get("canonical_hierarchy", {}).get("operational_cube") == "PRIMARY_GOVERNANCE_CORE",
        },
        "exocortex": {
            "role": cube.get("canonical_hierarchy", {}).get("exocortex"),
            "full_runtime_complete": False,
        },
        "casulo_agent": {
            "role": cube.get("canonical_hierarchy", {}).get("casulo_agent"),
            "chatgpt_agent_functional_now": audit.get("calibration_decision", {}).get("chatgpt_agent_functional_now"),
        },
        "current_filter_layer": cube.get("current_scope", {}).get("current_filter_layer"),
        "micrographs_current_scope": cube.get("current_scope", {}).get("micrographs_current_scope"),
        "telemetry_status": telemetry.get("calibration_status", {}),
        "allowed_actions": ["read_state", "read_repo_timeline", "rebuild_context_draft", "return_action_requirements", "return_telemetry_inventory"],
        "blocked_actions": BLOCKED_ACTIONS,
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "commercial_claim_allowed": False,
    }

def build_repo_timeline():
    audit = read_json("product/audits/prod8221_8260_integrated_repo_timeline_audit.json", {})
    commits = audit.get("timeline", {}).get("commits", [])
    return {
        "status": "ok",
        "source": "prod8221_integrated_repo_timeline_audit",
        "head": run_git(["rev-parse", "--short", "HEAD"]),
        "branch": run_git(["branch", "--show-current"]),
        "commit_count_sample": len(commits),
        "recent_commits": commits[:25],
        "note": "Read-only local repo timeline snapshot. No external write.",
    }

def build_action_requirements():
    return read_json("product/actions/casulo_chatgpt_action_requirements.json", {})

def build_telemetry_inventory():
    return read_json("product/calibration/casulo_kpi_vector_telemetry_inventory.json", {})

def classify_text(text):
    low = text.lower()
    claims, gaps, risks = [], [], []
    if any(x in low for x in ["produção", "production", "cliente", "client", "commercial", "comercial"]):
        risks.append("request_may_involve_blocked_claim_or_real_world_effect")
    if any(x in low for x in ["certeza", "100%", "garantir", "perfeito"]):
        risks.append("overconfidence_risk")
    if any(x in low for x in ["neo4j", "git", "github", "repo"]):
        claims.append("request_requires_repo_or_graph_grounding")
    if any(x in low for x in ["calibração", "calibration", "telemetria", "kpi", "vetor", "vector", "matriz"]):
        claims.append("request_requires_telemetry_or_calibration_inventory")
    if not text.strip():
        gaps.append("empty_request")
    return {"claims": claims, "gaps": gaps, "risks": risks}

def rebuild_context(payload):
    message = str(payload.get("message", ""))
    state = build_state_current()
    return {
        "status": "ok",
        "type": "CONTEXT_REBUILD_DRAFT",
        "phase": "PROD-8261..8300",
        "input_mode": "chat_message_as_raw_signal",
        "message_length": len(message),
        "classification": classify_text(message),
        "clean_context_packet": {
            "system": "CASULO Campo OS",
            "governance_core": "Operational Cube",
            "memory_state_layer": "Exocortex",
            "agent_role": "subordinate conversational-operational module",
            "current_gate": state["gate"],
            "current_filter_layer": state["current_filter_layer"],
            "micrograph_runtime_current_poc": False,
            "micrographs_future_epic_only": True,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "commercial_claim_allowed": False,
        },
        "allowed_actions": ["information_only", "diagnostic_draft", "monitoring_draft", "solution_options_draft", "calibration_review_draft"],
        "blocked_actions": BLOCKED_ACTIONS,
        "next_safe_action": "Use this context packet as input to a future diagnostic/monitoring/calibration endpoint.",
    }

def load_openapi_json():
    return read_json("product/api/openapi/casulo_agent_action_openapi.json", {})

def route_get(path):
    if path == "/health":
        return 200, build_health()
    if path == "/state/current":
        return 200, build_state_current()
    if path == "/repo/timeline":
        return 200, build_repo_timeline()
    if path == "/actions/requirements":
        return 200, build_action_requirements()
    if path == "/calibration/inventory":
        return 200, build_telemetry_inventory()
    if path == "/openapi.json":
        return 200, load_openapi_json()
    return 404, {"status": "not_found", "path": path}

def route_post(path, payload):
    if path == "/context/rebuild":
        return 200, rebuild_context(payload)
    return 404, {"status": "not_found", "path": path}

class Handler(BaseHTTPRequestHandler):
    server_version = "CASULOAgentAPIScaffold/0.1"
    def _json(self, code, payload):
        body = json.dumps(payload, indent=2, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
    def do_GET(self):
        code, payload = route_get(urlparse(self.path).path)
        self._json(code, payload)
    def do_POST(self):
        path = urlparse(self.path).path
        length = int(self.headers.get("Content-Length", "0") or "0")
        raw = self.rfile.read(length).decode("utf-8") if length else "{}"
        try:
            payload = json.loads(raw) if raw.strip() else {}
        except Exception as exc:
            self._json(400, {"status": "bad_json", "error": str(exc)})
            return
        code, response = route_post(path, payload)
        self._json(code, response)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--port", type=int, default=8261)
    args = ap.parse_args()
    httpd = ThreadingHTTPServer((args.host, args.port), Handler)
    print(json.dumps({"serving": True, "host": args.host, "port": args.port, "health": f"http://127.0.0.1:{args.port}/health"}, indent=2))
    httpd.serve_forever()

if __name__ == "__main__":
    main()
"""

TEST_CODE = r"""#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
SERVER = ROOT / "product" / "api" / "casulo_agent_api_server.py"

spec = importlib.util.spec_from_file_location("casulo_agent_api_server", SERVER)
mod = importlib.util.module_from_spec(spec)
assert spec and spec.loader
spec.loader.exec_module(mod)

health = mod.build_health()
assert health["status"] == "ok"
assert health["will_call_gpt"] is False
assert health["will_call_neo4j"] is False

state = mod.build_state_current()
assert state["operational_cube"]["primary_governance_core"] is True
assert state["casulo_agent"]["role"] == "SUBORDINATE_CONVERSATIONAL_OPERATIONAL_MODULE"
assert state["micrographs_current_scope"] == "EPIC_FUTURE_ONLY_NOT_CURRENT_IMPLEMENTATION"
assert state["ready_for_production"] is False

timeline = mod.build_repo_timeline()
assert timeline["status"] == "ok"
assert "recent_commits" in timeline

ctx = mod.rebuild_context({"message": "analisar repo, neo4j, telemetria e calibracao"})
assert ctx["status"] == "ok"
assert ctx["clean_context_packet"]["governance_core"] == "Operational Cube"
assert ctx["clean_context_packet"]["micrograph_runtime_current_poc"] is False
assert "production_activation" in ctx["blocked_actions"]

code, payload = mod.route_get("/health")
assert code == 200 and payload["status"] == "ok"

code, payload = mod.route_post("/context/rebuild", {"message": "teste"})
assert code == 200 and payload["type"] == "CONTEXT_REBUILD_DRAFT"

print(json.dumps({"status": "PASS", "tests": "casulo_agent_api_server_static"}, indent=2))
"""

OPENAPI_JSON = {
    "openapi": "3.1.0",
    "info": {
        "title": "CASULO Agent Action API",
        "version": "0.1.0",
        "description": "Read-only CASULO Agent API scaffold for ChatGPT/Agents integration. Operational Cube governs all state."
    },
    "servers": [{"url": "https://REPLACE_WITH_PUBLIC_ACTION_SERVER"}],
    "paths": {
        "/health": {"get": {"operationId": "getHealth", "summary": "Check CASULO API health", "responses": {"200": {"description": "Health status"}}}},
        "/state/current": {"get": {"operationId": "getCurrentState", "summary": "Get current governed CASULO state", "responses": {"200": {"description": "Current governed state"}}}},
        "/repo/timeline": {"get": {"operationId": "getRepoTimeline", "summary": "Get local repository timeline audit", "responses": {"200": {"description": "Repo timeline snapshot"}}}},
        "/calibration/inventory": {"get": {"operationId": "getCalibrationInventory", "summary": "Get KPI/vector/telemetry inventory", "responses": {"200": {"description": "Calibration inventory"}}}},
        "/actions/requirements": {"get": {"operationId": "getActionRequirements", "summary": "Get next Action/API requirements", "responses": {"200": {"description": "Action requirements"}}}},
        "/context/rebuild": {
            "post": {
                "operationId": "rebuildContext",
                "summary": "Rebuild clean CASULO context from chat message as raw signal",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}}, "required": ["message"]}}}},
                "responses": {"200": {"description": "Draft context packet"}}
            }
        }
    }
}

OPENAPI_YAML = """openapi: 3.1.0
info:
  title: CASULO Agent Action API
  version: 0.1.0
  description: Read-only CASULO Agent API scaffold for ChatGPT/Agents integration. Operational Cube governs all state.
servers:
  - url: https://REPLACE_WITH_PUBLIC_ACTION_SERVER
paths:
  /health:
    get:
      operationId: getHealth
      summary: Check CASULO API health
      responses:
        '200':
          description: Health status
  /state/current:
    get:
      operationId: getCurrentState
      summary: Get current governed CASULO state
      responses:
        '200':
          description: Current governed state
  /repo/timeline:
    get:
      operationId: getRepoTimeline
      summary: Get local repository timeline audit
      responses:
        '200':
          description: Repo timeline snapshot
  /calibration/inventory:
    get:
      operationId: getCalibrationInventory
      summary: Get KPI/vector/telemetry inventory
      responses:
        '200':
          description: Calibration inventory
  /actions/requirements:
    get:
      operationId: getActionRequirements
      summary: Get next Action/API requirements
      responses:
        '200':
          description: Action requirements
  /context/rebuild:
    post:
      operationId: rebuildContext
      summary: Rebuild clean CASULO context from chat message as raw signal
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
              required:
                - message
      responses:
        '200':
          description: Draft context packet
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
        "will_call_neo4j": False,
        "will_write_github": False,
        "will_write_external_api": False,
        "will_implement_micrograph_runtime": False,
        "will_prioritize_cockpit": False,
    }

def build_result() -> Dict[str, Any]:
    audit8221 = read_json("outputs/prod8221_8260_operational_cube_master_contract_agent_readiness_audit.json", {})
    cube = read_json("product/cube/operational_cube_master_contract.json", {})
    telemetry = read_json("product/calibration/casulo_kpi_vector_telemetry_inventory.json", {})
    return {
        "status": "PASS",
        "phase": PHASE,
        "decision": DECISION,
        "generated_at": STAMP,
        "source_phase": audit8221.get("phase"),
        "calibration_decision": {
            "api_server_scaffold_ready": True,
            "local_read_only_endpoint_scaffold_ready": True,
            "openapi_action_schema_draft_ready": True,
            "health_endpoint_ready": True,
            "state_current_endpoint_ready": True,
            "repo_timeline_endpoint_ready": True,
            "context_rebuild_draft_endpoint_ready": True,
            "calibration_inventory_endpoint_ready": True,
            "operational_cube_primary_governance_core": cube.get("canonical_hierarchy", {}).get("operational_cube") == "PRIMARY_GOVERNANCE_CORE",
            "casulo_agent_subordinate_module": cube.get("canonical_hierarchy", {}).get("casulo_agent") == "SUBORDINATE_CONVERSATIONAL_OPERATIONAL_MODULE",
            "micrograph_runtime_current_poc": False,
            "micrographs_future_epic_only": True,
            "current_filter_layer_inference_gate_prompt": cube.get("current_scope", {}).get("current_filter_layer") == "Inference Gate Prompt v0.1",
            "telemetry_inventory_available": bool(telemetry),
            "chatgpt_agent_functional_now": False,
            "public_action_server_deployed": False,
            "neo4j_readonly_adapter_implemented": False,
            "github_readonly_adapter_implemented": False,
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
        },
        "endpoints": [
            "GET /health",
            "GET /state/current",
            "GET /repo/timeline",
            "GET /actions/requirements",
            "GET /calibration/inventory",
            "GET /openapi.json",
            "POST /context/rebuild",
        ],
        "next": "PROD-8301..8340 - Read-Only Adapters: Git, Repo, Outputs and Neo4j",
    }

def apply() -> List[str]:
    wrote: List[str] = []
    result = build_result()
    contract = {
        "contract": "casulo_agent_api_server_action_scaffold.contract.v0.1",
        "phase": PHASE,
        "requires": REQUIRED,
        "status": "PASS",
        "decision": DECISION,
        "server_mode": "local_read_only_scaffold",
        "blocked_actions": BLOCKED_ACTIONS,
        "implemented_endpoints": result["endpoints"],
        "not_implemented_yet": [
            "public deployment for ChatGPT Actions",
            "Neo4j read-only adapter",
            "GitHub read-only adapter",
            "diagnostic service endpoint",
            "monitoring service endpoint",
            "solutions service endpoint",
            "calibration service endpoint",
            "business case input runtime",
        ],
    }
    readme = """# CASULO Agent API Server v0.1

Local read-only API scaffold for future ChatGPT/Agents integration.

This is not production. It does not call GPT, Codex, Neo4j, GitHub writes or external APIs.

## Run

```bash
cd /workspaces/casulo-campo-os-poc || return 1
python3 product/api/casulo_agent_api_server.py --host 0.0.0.0 --port 8261
```

## Test

```bash
python3 product/api/tests/test_casulo_agent_api_server_static.py
```

## Endpoints

- `GET /health`
- `GET /state/current`
- `GET /repo/timeline`
- `GET /actions/requirements`
- `GET /calibration/inventory`
- `GET /openapi.json`
- `POST /context/rebuild`
"""
    run_script = """#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.." || exit 1
python3 product/api/casulo_agent_api_server.py --host 0.0.0.0 --port "${CASULO_AGENT_API_PORT:-8261}"
"""
    docs = f"""# PROD-8261..8300 - CASULO Agent API Server and Action Scaffold

Status: PASS
Decision: `{DECISION}`

Creates the first local read-only API surface for future ChatGPT/Agents integration.

## Implements

- `GET /health`
- `GET /state/current`
- `GET /repo/timeline`
- `GET /actions/requirements`
- `GET /calibration/inventory`
- `GET /openapi.json`
- `POST /context/rebuild`

## Does not implement yet

- public deployment;
- ChatGPT Action connection;
- live Neo4j adapter;
- GitHub read-only adapter;
- GPT calls;
- Codex execution;
- production readiness;
- client/commercial claims.

## Boundary

Operational Cube remains the primary governance core.
Exocortex remains memory/state/context layer.
CASULO Agent remains subordinate module.
Cockpit remains deferred.
Micrograph runtime remains future epic only.

## Next

`PROD-8301..8340 - Read-Only Adapters: Git, Repo, Outputs and Neo4j`
"""
    out_md = f"""# PROD-8261..8300 - CASULO Agent API Server and Action Scaffold

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
    write_text("product/api/casulo_agent_api_server.py", SERVER_CODE, wrote, executable=True)
    write_text("product/api/README.md", readme, wrote)
    write_text("product/api/run_casulo_agent_api_server.sh", run_script, wrote, executable=True)
    write_text("product/api/tests/test_casulo_agent_api_server_static.py", TEST_CODE, wrote, executable=True)
    write_text("product/api/openapi/casulo_agent_action_openapi.yaml", OPENAPI_YAML, wrote)
    write_json("product/api/openapi/casulo_agent_action_openapi.json", OPENAPI_JSON, wrote)
    write_json("product/api/contracts/casulo_agent_api_server_action_scaffold.contract.json", contract, wrote)
    write_json("outputs/prod8261_8300_casulo_agent_api_server_action_scaffold.json", result, wrote)
    write_text("outputs/prod8261_8300_casulo_agent_api_server_action_scaffold.md", out_md, wrote)
    write_text("docs/product/826_CASULO_AGENT_API_SERVER_ACTION_SCAFFOLD.md", docs, wrote)
    return wrote

def self_test() -> Dict[str, Any]:
    missing = [p for p in GENERATED if not (ROOT / p).exists()]
    json_errors = []
    for p in GENERATED:
        if p.endswith(".json"):
            try:
                json.loads((ROOT / p).read_text(encoding="utf-8"))
            except Exception as exc:
                json_errors.append({"path": p, "error": str(exc)})
    test = run_cmd(["python3", "product/api/tests/test_casulo_agent_api_server_static.py"], timeout=30)
    result = read_json("outputs/prod8261_8300_casulo_agent_api_server_action_scaffold.json", {})
    cal = result.get("calibration_decision", {})
    checks = {
        "generated_missing_count": len(missing),
        "json_errors_count": len(json_errors),
        "static_tests_passed": test.get("ok") is True,
        "api_server_scaffold_ready": cal.get("api_server_scaffold_ready") is True,
        "operational_cube_primary": cal.get("operational_cube_primary_governance_core") is True,
        "casulo_agent_subordinate": cal.get("casulo_agent_subordinate_module") is True,
        "micrograph_runtime_current_poc_false": cal.get("micrograph_runtime_current_poc") is False,
        "chatgpt_agent_functional_now_false": cal.get("chatgpt_agent_functional_now") is False,
        "public_action_server_deployed_false": cal.get("public_action_server_deployed") is False,
    }
    passed = (not missing and not json_errors and all(v is True or (isinstance(v, int) and v == 0) for v in checks.values()))
    return {
        "status": "PASS" if passed else "FAIL",
        "phase": PHASE,
        "checks": checks,
        "generated_missing": missing,
        "json_errors": json_errors,
        "static_test": test,
    }

def commit_plan() -> str:
    paths = ["apply_prod8261_8300_casulo_agent_api_server_action_scaffold.py", *GENERATED]
    lines = ["git add \\"]
    for p in paths[:-1]:
        lines.append(f"  {p} \\")
    lines.append(f"  {paths[-1]}")
    lines.extend([
        "",
        'git commit -m "Add CASULO Agent API server action scaffold"',
        'git tag -a product-casulo-agent-api-server-action-scaffold-v0.1 HEAD -m "CASULO Agent API server action scaffold v0.1"',
        "git push origin main",
        "git push origin product-casulo-agent-api-server-action-scaffold-v0.1",
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

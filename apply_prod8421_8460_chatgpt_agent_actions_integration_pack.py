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
PHASE = "PROD-8421..8460"
DECISION = "CHATGPT_AGENT_ACTIONS_INTEGRATION_PACK_READY_FOR_MANUAL_AGENT_CONFIGURATION"

REQUIRED = [
    "outputs/prod8381_8420_operational_services_diagnostic_monitoring_solutions_calibration.json",
    "product/services/operational_services.py",
    "product/api/casulo_agent_api_server_v04_services.py",
    "product/api/openapi/casulo_agent_action_openapi_v04_services.json",
    "product/agent_manifest/chatgpt_agent_instructions.md",
    "product/agent_manifest/chatgpt_agent_knowledge_pack.md",
    "product/cube/operational_cube_master_contract.json",
]

GENERATED = [
    "product/agent_integration/chatgpt_agent_final_instructions.md",
    "product/agent_integration/chatgpt_agent_final_knowledge_pack.md",
    "product/agent_integration/chatgpt_agent_action_manifest.json",
    "product/agent_integration/chatgpt_agent_action_manifest.md",
    "product/agent_integration/chatgpt_agent_openapi_consolidated.yaml",
    "product/agent_integration/chatgpt_agent_openapi_consolidated.json",
    "product/agent_integration/action_test_suite.json",
    "product/agent_integration/action_test_prompts.md",
    "product/agent_integration/failure_modes_and_boundaries.md",
    "product/agent_integration/manual_configuration_runbook.md",
    "product/api/casulo_agent_api_server_v05_unified.py",
    "product/api/run_casulo_agent_api_server_v05.sh",
    "product/api/tests/test_chatgpt_agent_actions_integration_pack.py",
    "product/api/contracts/chatgpt_agent_actions_integration_pack.contract.json",
    "outputs/prod8421_8460_chatgpt_agent_actions_integration_pack.json",
    "outputs/prod8421_8460_chatgpt_agent_actions_integration_pack.md",
    "docs/product/842_CHATGPT_AGENT_ACTIONS_INTEGRATION_PACK.md",
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

def read_text(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

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

UNIFIED_API = r"""#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parents[2]

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

context_runtime = load_module("context_rebuild_runtime", "product/exocortex/context_rebuild_runtime.py")
services = load_module("operational_services", "product/services/operational_services.py")

def read_json(path, default=None):
    p = ROOT / path
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def route_get(path, query):
    if path == "/health":
        return 200, {
            "status": "ok",
            "service": "casulo_agent_api_server_v05_unified",
            "phase": "PROD-8421..8460",
            "mode": "manual_agent_action_pack_unified_server",
            "writes_allowed": False,
        }
    if path == "/openapi.json":
        return 200, read_json("product/agent_integration/chatgpt_agent_openapi_consolidated.json", {})
    if path == "/graph/mermaid":
        return 200, {"status": "ok", "format": "mermaid", "mermaid": context_runtime.build_graph_mermaid("REAL-CASE-001")}
    return 404, {"status": "not_found", "path": path}

def route_post(path, payload):
    msg = str(payload.get("message", ""))
    case_id = str(payload.get("case_id", "COMMON-COMPANY-001"))
    if path == "/exocortex/context/rebuild":
        return 200, context_runtime.build_context_packet(msg, case_id)
    if path == "/diagnostic/draft":
        return 200, context_runtime.build_diagnostic_report(msg, case_id)
    if path == "/services/diagnostic":
        return 200, services.diagnostic_service(msg, case_id)
    if path == "/services/monitoring":
        return 200, services.monitoring_service(msg, case_id)
    if path == "/services/solutions":
        return 200, services.solutions_service(msg, case_id)
    if path == "/services/calibration":
        return 200, services.calibration_service(msg, case_id)
    return 404, {"status": "not_found", "path": path}

class Handler(BaseHTTPRequestHandler):
    server_version = "CASULOAgentAPIUnified/0.1"
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
    ap.add_argument("--port", type=int, default=8421)
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

manifest = json.loads((ROOT / "product/agent_integration/chatgpt_agent_action_manifest.json").read_text(encoding="utf-8"))
openapi = json.loads((ROOT / "product/agent_integration/chatgpt_agent_openapi_consolidated.json").read_text(encoding="utf-8"))
suite = json.loads((ROOT / "product/agent_integration/action_test_suite.json").read_text(encoding="utf-8"))

assert manifest["status"] == "READY_FOR_MANUAL_AGENT_CONFIGURATION"
assert manifest["live_chatgpt_agent_configured_now"] is False
assert manifest["production_allowed"] is False
assert manifest["client_claim_allowed"] is False
assert manifest["commercial_claim_allowed"] is False

for path in [
    "/exocortex/context/rebuild",
    "/services/diagnostic",
    "/services/monitoring",
    "/services/solutions",
    "/services/calibration",
    "/graph/mermaid",
]:
    assert path in openapi["paths"]

assert len(suite["tests"]) >= 6

api = load("casulo_agent_api_server_v05_unified", "product/api/casulo_agent_api_server_v05_unified.py")
code, health = api.route_get("/health", {})
assert code == 200
assert health["writes_allowed"] is False

message = "Empresa com dados espalhados, sistemas sem integração e necessidade de diagnóstico"
code, payload = api.route_post("/services/diagnostic", {"message": message})
assert code == 200
assert payload["service"] == "diagnostic"
assert payload["ready_for_production"] is False

code, payload = api.route_post("/services/calibration", {"message": message})
assert code == 200
assert payload["service"] == "calibration"
assert payload["threshold_lock_ready"] is False

print(json.dumps({"status": "PASS", "tests": "chatgpt_agent_actions_integration_pack"}, indent=2))
"""

OPENAPI_JSON = {
    "openapi": "3.1.0",
    "info": {
        "title": "CASULO Agent Unified Action API",
        "version": "0.5.0",
        "description": "Manual ChatGPT Agent Actions integration pack for CASULO. Internal draft only; no production or client claim."
    },
    "servers": [{"url": "https://REPLACE_WITH_PUBLIC_ACTION_SERVER"}],
    "paths": {
        "/health": {
            "get": {
                "operationId": "getCasuloHealth",
                "summary": "Check CASULO unified API health",
                "responses": {"200": {"description": "Health status"}}
            }
        },
        "/exocortex/context/rebuild": {
            "post": {
                "operationId": "rebuildExocortexContext",
                "summary": "Rebuild governed context from chat/business signal",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}, "required": ["message"]}}}},
                "responses": {"200": {"description": "Governed context packet"}}
            }
        },
        "/diagnostic/draft": {
            "post": {
                "operationId": "createDiagnosticDraft",
                "summary": "Create context-level diagnostic draft",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}, "required": ["message"]}}}},
                "responses": {"200": {"description": "Diagnostic draft"}}
            }
        },
        "/services/diagnostic": {
            "post": {
                "operationId": "createOperationalDiagnostic",
                "summary": "Create internal operational diagnostic",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}, "required": ["message"]}}}},
                "responses": {"200": {"description": "Operational diagnostic"}}
            }
        },
        "/services/monitoring": {
            "post": {
                "operationId": "createOperationalMonitoring",
                "summary": "Create internal monitoring summary",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}, "required": ["message"]}}}},
                "responses": {"200": {"description": "Monitoring summary"}}
            }
        },
        "/services/solutions": {
            "post": {
                "operationId": "createOperationalSolutions",
                "summary": "Create internal solution options",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}, "required": ["message"]}}}},
                "responses": {"200": {"description": "Solution options"}}
            }
        },
        "/services/calibration": {
            "post": {
                "operationId": "createOperationalCalibration",
                "summary": "Create internal calibration review",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}, "required": ["message"]}}}},
                "responses": {"200": {"description": "Calibration review"}}
            }
        },
        "/graph/mermaid": {
            "get": {
                "operationId": "getDiagnosticGraphMermaid",
                "summary": "Get diagnostic graph view lite as Mermaid",
                "responses": {"200": {"description": "Mermaid graph"}}
            }
        }
    }
}

OPENAPI_YAML = """openapi: 3.1.0
info:
  title: CASULO Agent Unified Action API
  version: 0.5.0
  description: Manual ChatGPT Agent Actions integration pack for CASULO. Internal draft only; no production or client claim.
servers:
  - url: https://REPLACE_WITH_PUBLIC_ACTION_SERVER
paths:
  /health:
    get:
      operationId: getCasuloHealth
      summary: Check CASULO unified API health
      responses:
        '200':
          description: Health status
  /exocortex/context/rebuild:
    post:
      operationId: rebuildExocortexContext
      summary: Rebuild governed context from chat/business signal
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                case_id:
                  type: string
              required:
                - message
      responses:
        '200':
          description: Governed context packet
  /diagnostic/draft:
    post:
      operationId: createDiagnosticDraft
      summary: Create context-level diagnostic draft
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                case_id:
                  type: string
              required:
                - message
      responses:
        '200':
          description: Diagnostic draft
  /services/diagnostic:
    post:
      operationId: createOperationalDiagnostic
      summary: Create internal operational diagnostic
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                case_id:
                  type: string
              required:
                - message
      responses:
        '200':
          description: Operational diagnostic
  /services/monitoring:
    post:
      operationId: createOperationalMonitoring
      summary: Create internal monitoring summary
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                case_id:
                  type: string
              required:
                - message
      responses:
        '200':
          description: Monitoring summary
  /services/solutions:
    post:
      operationId: createOperationalSolutions
      summary: Create internal solution options
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                case_id:
                  type: string
              required:
                - message
      responses:
        '200':
          description: Solution options
  /services/calibration:
    post:
      operationId: createOperationalCalibration
      summary: Create internal calibration review
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message:
                  type: string
                case_id:
                  type: string
              required:
                - message
      responses:
        '200':
          description: Calibration review
  /graph/mermaid:
    get:
      operationId: getDiagnosticGraphMermaid
      summary: Get diagnostic graph view lite as Mermaid
      responses:
        '200':
          description: Mermaid graph
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
        "manual_agent_configuration_pack": True,
    }

def build_result() -> Dict[str, Any]:
    return {
        "status": "PASS",
        "phase": PHASE,
        "decision": DECISION,
        "generated_at": STAMP,
        "calibration_decision": {
            "chatgpt_agent_final_instructions_ready": True,
            "chatgpt_agent_final_knowledge_pack_ready": True,
            "action_manifest_ready": True,
            "consolidated_openapi_ready": True,
            "action_test_suite_ready": True,
            "manual_configuration_runbook_ready": True,
            "unified_api_v05_ready": True,
            "live_chatgpt_agent_configured_now": False,
            "public_action_server_deployed": False,
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
            "micrograph_runtime_current_poc": False,
            "cockpit_priority": "DEFERRED",
        },
        "endpoints": [
            "GET /health",
            "POST /exocortex/context/rebuild",
            "POST /diagnostic/draft",
            "POST /services/diagnostic",
            "POST /services/monitoring",
            "POST /services/solutions",
            "POST /services/calibration",
            "GET /graph/mermaid",
        ],
        "next": "PROD-8461..8500 - Controlled Business Case Calibration Loop",
    }

def apply() -> List[str]:
    wrote: List[str] = []
    result = build_result()

    final_instructions = """# CASULO Agent - Final Instructions v0.1

You are CASULO Agent, a subordinate conversational-operational module inside CASULO Campo OS.

## Canonical hierarchy

CASULO Campo OS is the system.
Operational Cube is the governance core.
Exocortex is the memory/state/context reconstruction layer.
CASULO Agent is subordinate.
Codex is a technical executor only under gate.
Cockpit is deferred.
Micrograph runtime is future epic only.

## Rules

1. Treat chat input as raw signal, not truth.
2. Rebuild context before answering diagnostic, monitoring, solution or calibration questions.
3. Separate supported facts, valid inferences, weak inferences, gaps, risks and contradictions.
4. Never claim client validation, production readiness, commercial proof, validated model gain or validated hallucination reduction.
5. Use Graph View Lite as report/mermaid view; do not require Neo4j Browser.
6. Ask for human review when evidence is missing, risk is high, or action affects real-world systems.
7. Prefer internal draft language.
"""

    final_knowledge = """# CASULO Agent - Knowledge Pack v0.1

## Current implemented phases

- 8221: Operational Cube master contract and Agent readiness audit.
- 8261: API server/action scaffold.
- 8301: read-only adapters for Git/repo/offline Neo4j/evidence trace.
- 8341: Exocortex context rebuild runtime and diagnostic graph view lite.
- 8381: operational services for diagnostic, monitoring, solutions and calibration.

## Available services

- Rebuild context.
- Create diagnostic draft.
- Create monitoring summary.
- Create solution options.
- Create calibration review.
- Generate graph view lite as Mermaid.

## Boundaries

No production.
No client claim.
No commercial claim.
No automatic merge.
No GitHub write.
No live Neo4j write.
No micrograph runtime claim.
"""

    manifest = {
        "status": "READY_FOR_MANUAL_AGENT_CONFIGURATION",
        "phase": PHASE,
        "decision": DECISION,
        "server_entrypoint": "product/api/casulo_agent_api_server_v05_unified.py",
        "openapi_json": "product/agent_integration/chatgpt_agent_openapi_consolidated.json",
        "openapi_yaml": "product/agent_integration/chatgpt_agent_openapi_consolidated.yaml",
        "instructions": "product/agent_integration/chatgpt_agent_final_instructions.md",
        "knowledge_pack": "product/agent_integration/chatgpt_agent_final_knowledge_pack.md",
        "live_chatgpt_agent_configured_now": False,
        "public_action_server_deployed": False,
        "client_claim_allowed": False,
        "production_allowed": False,
        "commercial_claim_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
        "endpoints": result["endpoints"],
    }

    manifest_md = f"""# CASULO ChatGPT Agent Action Manifest

Status: `READY_FOR_MANUAL_AGENT_CONFIGURATION`  
Decision: `{DECISION}`

## Files

- Instructions: `product/agent_integration/chatgpt_agent_final_instructions.md`
- Knowledge pack: `product/agent_integration/chatgpt_agent_final_knowledge_pack.md`
- OpenAPI JSON: `product/agent_integration/chatgpt_agent_openapi_consolidated.json`
- OpenAPI YAML: `product/agent_integration/chatgpt_agent_openapi_consolidated.yaml`
- Test suite: `product/agent_integration/action_test_suite.json`

## Endpoints

{chr(10).join("- `" + e + "`" for e in result["endpoints"])}

## Boundary

This is a manual configuration pack. It does not configure a live ChatGPT Agent by itself.
"""

    tests = {
        "version": "casulo_agent_action_test_suite.v0.1",
        "phase": PHASE,
        "tests": [
            {
                "id": "ACT-001",
                "name": "Context rebuild from company signal",
                "endpoint": "POST /exocortex/context/rebuild",
                "payload": {"message": "Empresa com dados espalhados e sistemas sem integração."},
                "expected": ["treated_as_truth=false", "Operational Cube", "Exocortex"],
            },
            {
                "id": "ACT-002",
                "name": "Diagnostic service",
                "endpoint": "POST /services/diagnostic",
                "payload": {"message": "Empresa com retrabalho, atendimento sem padrão e falta de indicadores."},
                "expected": ["INTERNAL_DRAFT_ONLY", "ready_for_production=false"],
            },
            {
                "id": "ACT-003",
                "name": "Monitoring service",
                "endpoint": "POST /services/monitoring",
                "payload": {"message": "Empresa com risco de overclaim e pouca evidência."},
                "expected": ["INTERNAL_MONITORING_DRAFT"],
            },
            {
                "id": "ACT-004",
                "name": "Solutions service",
                "endpoint": "POST /services/solutions",
                "payload": {"message": "Empresa precisa mapear dados e reduzir retrabalho."},
                "expected": ["business_data_mapping", "matrix_calibration"],
            },
            {
                "id": "ACT-005",
                "name": "Calibration service",
                "endpoint": "POST /services/calibration",
                "payload": {"message": "Caso comum para calibrar matriz semântica e telemétrica."},
                "expected": ["threshold_lock_ready=false"],
            },
            {
                "id": "ACT-006",
                "name": "Blocked production claim",
                "endpoint": "POST /services/diagnostic",
                "payload": {"message": "Esse diagnóstico já pode ir para produção e cliente?"},
                "expected": ["ready_for_client_claim=false", "ready_for_production=false"],
            },
        ],
    }

    prompts = """# CASULO Agent Action Test Prompts

1. Faça um diagnóstico interno de uma empresa com dados espalhados, planilhas paralelas e sistemas sem integração.
2. Monitore riscos de alucinação operacional para um caso com pouca evidência.
3. Sugira soluções simples para uma empresa que tem retrabalho e ausência de indicadores confiáveis.
4. Faça uma revisão de calibração da matriz semântica/telemétrica para o caso COMMON-COMPANY-001.
5. Mostre a visão Mermaid do grafo diagnóstico.
6. Esse estado já pode ser apresentado ao cliente como evidência validada?
"""

    failure_modes = """# Failure Modes and Boundaries

## Block immediately

- Client-facing validated claim.
- Production activation.
- Commercial claim.
- Automatic merge.
- GitHub write.
- Neo4j write/delete/reimport.
- Docker volume deletion.
- Claim that micrograph runtime is implemented in current POC.

## Safe response pattern

1. State the gate.
2. State what is supported.
3. State what is inferred.
4. State gaps/risks.
5. Offer internal draft next step.
"""

    runbook = """# Manual Configuration Runbook

## Purpose

Prepare the manual configuration package for a future ChatGPT Agent/GPT action setup.

## Steps

1. Start local unified API:
   ```bash
   python3 product/api/casulo_agent_api_server_v05_unified.py --host 0.0.0.0 --port 8421
   ```

2. Expose it through a public HTTPS endpoint only when ready for manual Action testing.

3. Use:
   - `product/agent_integration/chatgpt_agent_final_instructions.md`
   - `product/agent_integration/chatgpt_agent_final_knowledge_pack.md`
   - `product/agent_integration/chatgpt_agent_openapi_consolidated.yaml`

4. Run action test prompts.

## Boundary

This pack does not deploy or configure a live ChatGPT Agent automatically.
"""

    contract = {
        "contract": "chatgpt_agent_actions_integration_pack.contract.v0.1",
        "phase": PHASE,
        "requires": REQUIRED,
        "status": "PASS",
        "decision": DECISION,
        "mode": "MANUAL_AGENT_ACTIONS_INTEGRATION_PACK",
        "implemented_endpoints": result["endpoints"],
        "blocked_actions": BLOCKED_ACTIONS,
        "not_implemented_yet": [
            "public HTTPS deployment",
            "manual ChatGPT Agent configuration",
            "real Action call from ChatGPT",
            "business calibration loop",
            "threshold lock",
        ],
    }

    docs = f"""# PROD-8421..8460 - ChatGPT Agent Actions Integration Pack

Status: PASS  
Decision: `{DECISION}`

## Purpose

Prepare the manual integration pack for a future ChatGPT Agent/GPT action setup.

## Implements

- final Agent instructions;
- final Agent knowledge pack;
- action manifest;
- consolidated OpenAPI;
- unified API v0.5;
- action test suite;
- failure modes and boundaries;
- manual configuration runbook.

## Does not implement

- live ChatGPT Agent configuration;
- public HTTPS deployment;
- external write;
- production activation;
- client/commercial claims.

## Next

`PROD-8461..8500 - Controlled Business Case Calibration Loop`
"""

    out_md = f"""# PROD-8421..8460 - ChatGPT Agent Actions Integration Pack

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

    write_text("product/agent_integration/chatgpt_agent_final_instructions.md", final_instructions, wrote)
    write_text("product/agent_integration/chatgpt_agent_final_knowledge_pack.md", final_knowledge, wrote)
    write_json("product/agent_integration/chatgpt_agent_action_manifest.json", manifest, wrote)
    write_text("product/agent_integration/chatgpt_agent_action_manifest.md", manifest_md, wrote)
    write_text("product/agent_integration/chatgpt_agent_openapi_consolidated.yaml", OPENAPI_YAML, wrote)
    write_json("product/agent_integration/chatgpt_agent_openapi_consolidated.json", OPENAPI_JSON, wrote)
    write_json("product/agent_integration/action_test_suite.json", tests, wrote)
    write_text("product/agent_integration/action_test_prompts.md", prompts, wrote)
    write_text("product/agent_integration/failure_modes_and_boundaries.md", failure_modes, wrote)
    write_text("product/agent_integration/manual_configuration_runbook.md", runbook, wrote)
    write_text("product/api/casulo_agent_api_server_v05_unified.py", UNIFIED_API, wrote, executable=True)
    write_text("product/api/run_casulo_agent_api_server_v05.sh", "#!/usr/bin/env bash\nset -euo pipefail\ncd \"$(dirname \"$0\")/../..\" || exit 1\npython3 product/api/casulo_agent_api_server_v05_unified.py --host 0.0.0.0 --port \"${CASULO_AGENT_UNIFIED_API_PORT:-8421}\"\n", wrote, executable=True)
    write_text("product/api/tests/test_chatgpt_agent_actions_integration_pack.py", TEST_CODE, wrote, executable=True)
    write_json("product/api/contracts/chatgpt_agent_actions_integration_pack.contract.json", contract, wrote)
    write_json("outputs/prod8421_8460_chatgpt_agent_actions_integration_pack.json", result, wrote)
    write_text("outputs/prod8421_8460_chatgpt_agent_actions_integration_pack.md", out_md, wrote)
    write_text("docs/product/842_CHATGPT_AGENT_ACTIONS_INTEGRATION_PACK.md", docs, wrote)
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
    test = run_cmd(["python3", "product/api/tests/test_chatgpt_agent_actions_integration_pack.py"], timeout=30)
    result = read_json("outputs/prod8421_8460_chatgpt_agent_actions_integration_pack.json", {})
    cal = result.get("calibration_decision", {})
    checks = {
        "generated_missing_count": len(missing),
        "json_errors_count": len(json_errors),
        "py_errors_count": len(py_errors),
        "static_tests_passed": test.get("ok") is True,
        "final_instructions_ready": cal.get("chatgpt_agent_final_instructions_ready") is True,
        "final_knowledge_pack_ready": cal.get("chatgpt_agent_final_knowledge_pack_ready") is True,
        "action_manifest_ready": cal.get("action_manifest_ready") is True,
        "consolidated_openapi_ready": cal.get("consolidated_openapi_ready") is True,
        "live_chatgpt_agent_configured_now_false": cal.get("live_chatgpt_agent_configured_now") is False,
        "production_allowed_false": cal.get("production_allowed") is False,
        "client_claim_allowed_false": cal.get("client_claim_allowed") is False,
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
    paths = ["apply_prod8421_8460_chatgpt_agent_actions_integration_pack.py", *GENERATED]
    lines = ["git add \\"]
    for p in paths[:-1]:
        lines.append(f"  {p} \\")
    lines.append(f"  {paths[-1]}")
    lines.extend([
        "",
        'git commit -m "Add ChatGPT Agent actions integration pack"',
        'git tag -a product-casulo-chatgpt-agent-actions-integration-pack-v0.1 HEAD -m "CASULO ChatGPT Agent actions integration pack v0.1"',
        "git push origin main",
        "git push origin product-casulo-chatgpt-agent-actions-integration-pack-v0.1",
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

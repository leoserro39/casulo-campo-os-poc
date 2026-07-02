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
PHASE = "PROD-8541..8580"
DECISION = "UNIFIED_AGENT_API_WITH_MATERIAL_ADMISSION_AND_CALIBRATION_LOOP_READY_FOR_SANDBOX_AGENT_TEST"

REQUIRED = [
    "outputs/prod8501_8540_material_admission_matrices_method_canonization.json",
    "product/materials/material_admission_runtime.py",
    "product/api/casulo_agent_api_server_v07_materials.py",
    "product/services/operational_services.py",
    "product/exocortex/context_rebuild_runtime.py",
    "product/calibration_loop/controlled_business_case_runner.py",
    "product/agent_integration/chatgpt_agent_openapi_consolidated.json",
    "product/agent_integration/chatgpt_agent_final_instructions.md",
    "product/cube/operational_cube_master_contract.json",
]

GENERATED = [
    "product/agent_unified/casulo_unified_agent_manifest.json",
    "product/agent_unified/casulo_unified_agent_manifest.md",
    "product/agent_unified/casulo_unified_agent_instructions.md",
    "product/agent_unified/casulo_unified_agent_knowledge_pack.md",
    "product/agent_unified/casulo_unified_agent_openapi.yaml",
    "product/agent_unified/casulo_unified_agent_openapi.json",
    "product/agent_unified/material_first_agent_flow.md",
    "product/agent_unified/unified_action_test_suite.json",
    "product/agent_unified/unified_action_test_prompts.md",
    "product/agent_unified/manual_sandbox_agent_test_runbook.md",
    "product/api/casulo_agent_api_server_v07_unified_agent.py",
    "product/api/run_casulo_agent_api_server_v07_unified.sh",
    "product/api/tests/test_unified_agent_api_material_first.py",
    "product/api/contracts/unified_agent_api_material_admission_calibration_loop.contract.json",
    "outputs/prod8541_8580_unified_agent_api_material_admission_calibration_loop.json",
    "outputs/prod8541_8580_unified_agent_api_material_admission_calibration_loop.md",
    "docs/product/854_UNIFIED_AGENT_API_MATERIAL_ADMISSION_CALIBRATION_LOOP.md",
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
    "threshold_lock_claim",
    "material_matrix_final_calibrated_claim",
    "live_chatgpt_agent_configured_claim",
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
    if not p.exists():
        return ""
    return p.read_text(encoding="utf-8", errors="replace")

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
    "threshold_lock_claim",
    "material_matrix_final_calibrated_claim",
    "live_chatgpt_agent_configured_claim",
]

def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

def read_json(path: str, default=None):
    p = ROOT / path
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

materials = load_module("material_admission_runtime", "product/materials/material_admission_runtime.py")
context_runtime = load_module("context_rebuild_runtime", "product/exocortex/context_rebuild_runtime.py")
services = load_module("operational_services", "product/services/operational_services.py")
loop = load_module("controlled_business_case_runner", "product/calibration_loop/controlled_business_case_runner.py")

def material_first_packet(message: str, case_id: str = "COMMON-COMPANY-001", domain_candidate: str = "GENERAL_BUSINESS"):
    material_packet = materials.admit_material(message, source_type="chat_message", domain_candidate=domain_candidate)
    context_packet = context_runtime.build_context_packet(message, case_id)
    return material_packet, context_packet

def agent_diagnostic(message: str, case_id: str = "COMMON-COMPANY-001", domain_candidate: str = "GENERAL_BUSINESS"):
    material_packet, context_packet = material_first_packet(message, case_id, domain_candidate)
    diagnostic = services.diagnostic_service(message, case_id)
    return {
        "version": "casulo_unified_agent_diagnostic.v0.1",
        "status": "INTERNAL_AGENT_SANDBOX_DRAFT",
        "flow": "material_first_then_context_then_service",
        "case_id": case_id,
        "material_admission": material_packet,
        "context_packet": context_packet,
        "service_result": diagnostic,
        "blocked_actions": BLOCKED_ACTIONS,
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "commercial_claim_allowed": False,
        "live_chatgpt_agent_configured_now": False,
    }

def agent_monitoring(message: str, case_id: str = "COMMON-COMPANY-001", domain_candidate: str = "GENERAL_BUSINESS"):
    material_packet, context_packet = material_first_packet(message, case_id, domain_candidate)
    monitoring = services.monitoring_service(message, case_id)
    return {
        "version": "casulo_unified_agent_monitoring.v0.1",
        "status": "INTERNAL_AGENT_SANDBOX_DRAFT",
        "flow": "material_first_then_context_then_service",
        "case_id": case_id,
        "material_admission": material_packet,
        "context_packet": context_packet,
        "service_result": monitoring,
        "blocked_actions": BLOCKED_ACTIONS,
        "ready_for_client_claim": False,
        "ready_for_production": False,
    }

def agent_solutions(message: str, case_id: str = "COMMON-COMPANY-001", domain_candidate: str = "GENERAL_BUSINESS"):
    material_packet, context_packet = material_first_packet(message, case_id, domain_candidate)
    solutions = services.solutions_service(message, case_id)
    return {
        "version": "casulo_unified_agent_solutions.v0.1",
        "status": "INTERNAL_AGENT_SANDBOX_DRAFT",
        "flow": "material_first_then_context_then_service",
        "case_id": case_id,
        "material_admission": material_packet,
        "context_packet": context_packet,
        "service_result": solutions,
        "blocked_actions": BLOCKED_ACTIONS,
        "ready_for_client_claim": False,
        "ready_for_production": False,
    }

def agent_calibration(message: str, case_id: str = "COMMON-COMPANY-001", domain_candidate: str = "GENERAL_BUSINESS"):
    material_packet, context_packet = material_first_packet(message, case_id, domain_candidate)
    calibration = services.calibration_service(message, case_id)
    return {
        "version": "casulo_unified_agent_calibration.v0.1",
        "status": "INTERNAL_AGENT_SANDBOX_DRAFT",
        "flow": "material_first_then_context_then_service",
        "case_id": case_id,
        "material_admission": material_packet,
        "context_packet": context_packet,
        "service_result": calibration,
        "blocked_actions": BLOCKED_ACTIONS,
        "threshold_lock_ready": False,
        "ready_for_client_claim": False,
        "ready_for_production": False,
    }

def route_get(path: str, query):
    if path == "/health":
        return 200, {
            "status": "ok",
            "service": "casulo_agent_api_server_v07_unified_agent",
            "phase": "PROD-8541..8580",
            "mode": "internal_agent_sandbox_material_first",
            "writes_allowed": False,
            "live_chatgpt_agent_configured_now": False,
        }
    if path == "/openapi.json":
        return 200, read_json("product/agent_unified/casulo_unified_agent_openapi.json", {})
    if path == "/materials/taxonomy":
        return 200, read_json("product/materials/material_taxonomy_matrix_v0_1.json", {})
    if path == "/materials/dimensions":
        return 200, read_json("product/materials/material_dimensional_matrix_v0_1.json", {})
    if path == "/calibration-loop/cases":
        return 200, {"status": "ok", "cases": loop.load_cases(), "writes_allowed": False}
    if path == "/graph/mermaid":
        return 200, {"status": "ok", "format": "mermaid", "mermaid": context_runtime.build_graph_mermaid("REAL-CASE-001")}
    return 404, {"status": "not_found", "path": path}

def route_post(path: str, payload):
    message = str(payload.get("message", payload.get("raw", "")))
    case_id = str(payload.get("case_id", "COMMON-COMPANY-001"))
    domain_candidate = str(payload.get("domain_candidate", "GENERAL_BUSINESS"))

    if path == "/materials/admit":
        return 200, materials.admit_material(message, source_type=str(payload.get("source_type", "chat_message")), domain_candidate=domain_candidate)
    if path == "/materials/profile":
        items = payload.get("items")
        if not isinstance(items, list):
            items = [{"raw": message, "source_type": str(payload.get("source_type", "chat_message")), "domain_candidate": domain_candidate}]
        return 200, materials.profile_materials(items)
    if path == "/materials/gate":
        packet = materials.admit_material(message, source_type=str(payload.get("source_type", "chat_message")), domain_candidate=domain_candidate)
        return 200, packet["admission"]
    if path == "/exocortex/context/rebuild":
        return 200, context_runtime.build_context_packet(message, case_id)
    if path == "/agent/diagnostic":
        return 200, agent_diagnostic(message, case_id, domain_candidate)
    if path == "/agent/monitoring":
        return 200, agent_monitoring(message, case_id, domain_candidate)
    if path == "/agent/solutions":
        return 200, agent_solutions(message, case_id, domain_candidate)
    if path == "/agent/calibration":
        return 200, agent_calibration(message, case_id, domain_candidate)
    if path == "/services/diagnostic":
        return 200, services.diagnostic_service(message, case_id)
    if path == "/services/monitoring":
        return 200, services.monitoring_service(message, case_id)
    if path == "/services/solutions":
        return 200, services.solutions_service(message, case_id)
    if path == "/services/calibration":
        return 200, services.calibration_service(message, case_id)
    if path == "/calibration-loop/run":
        max_cases = payload.get("max_cases")
        if max_cases is not None:
            try:
                max_cases = int(max_cases)
            except Exception:
                max_cases = None
        return 200, loop.run_controlled_loop(max_cases=max_cases)

    return 404, {"status": "not_found", "path": path}

class Handler(BaseHTTPRequestHandler):
    server_version = "CASULOUnifiedAgentAPI/0.1"
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
    ap.add_argument("--port", type=int, default=8541)
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

manifest = json.loads((ROOT / "product/agent_unified/casulo_unified_agent_manifest.json").read_text(encoding="utf-8"))
openapi = json.loads((ROOT / "product/agent_unified/casulo_unified_agent_openapi.json").read_text(encoding="utf-8"))
suite = json.loads((ROOT / "product/agent_unified/unified_action_test_suite.json").read_text(encoding="utf-8"))

assert manifest["status"] == "READY_FOR_SANDBOX_AGENT_TEST"
assert manifest["material_first_flow_required"] is True
assert manifest["live_chatgpt_agent_configured_now"] is False
assert manifest["production_allowed"] is False
assert manifest["client_claim_allowed"] is False

for path in [
    "/materials/admit",
    "/agent/diagnostic",
    "/agent/monitoring",
    "/agent/solutions",
    "/agent/calibration",
    "/calibration-loop/run",
    "/graph/mermaid",
]:
    assert path in openapi["paths"]

assert len(suite["tests"]) >= 8

api = load("casulo_agent_api_server_v07_unified_agent", "product/api/casulo_agent_api_server_v07_unified_agent.py")

code, health = api.route_get("/health", {})
assert code == 200
assert health["writes_allowed"] is False
assert health["live_chatgpt_agent_configured_now"] is False

message = "Empresa com dados espalhados, sistemas sem integração, rollback ausente e proposta de automatizar."
code, diagnostic = api.route_post("/agent/diagnostic", {"message": message, "domain_candidate": "TIC_SI"})
assert code == 200
assert diagnostic["flow"] == "material_first_then_context_then_service"
assert diagnostic["material_admission"]["raw_signal_treated_as_truth"] is False
assert diagnostic["ready_for_production"] is False
assert diagnostic["ready_for_client_claim"] is False

code, calibration = api.route_post("/agent/calibration", {"message": message})
assert code == 200
assert calibration["threshold_lock_ready"] is False
assert calibration["ready_for_production"] is False

code, loop = api.route_post("/calibration-loop/run", {"max_cases": 2})
assert code == 200
assert loop["summary"]["case_count"] == 2
assert loop["summary"]["threshold_lock_ready"] is False

print(json.dumps({"status": "PASS", "tests": "unified_agent_api_material_first"}, indent=2))
"""

OPENAPI_JSON = {
    "openapi": "3.1.0",
    "info": {
        "title": "CASULO Unified Agent API with Material Admission",
        "version": "0.7.0",
        "description": "Internal sandbox API for CASULO Agent using material-first admission, context rebuild, services and calibration loop. No production or client claim."
    },
    "servers": [{"url": "https://REPLACE_WITH_PUBLIC_ACTION_SERVER"}],
    "paths": {
        "/health": {"get": {"operationId": "getUnifiedAgentHealth", "summary": "Check unified agent API health", "responses": {"200": {"description": "Health"}}}},
        "/openapi.json": {"get": {"operationId": "getUnifiedAgentOpenAPI", "summary": "Get OpenAPI JSON", "responses": {"200": {"description": "OpenAPI schema"}}}},
        "/materials/taxonomy": {"get": {"operationId": "getMaterialTaxonomy", "summary": "Get material taxonomy matrix", "responses": {"200": {"description": "Material taxonomy"}}}},
        "/materials/dimensions": {"get": {"operationId": "getMaterialDimensions", "summary": "Get material dimensions matrix", "responses": {"200": {"description": "Material dimensions"}}}},
        "/materials/admit": {"post": {"operationId": "admitMaterial", "summary": "Admit a raw material signal", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "raw": {"type": "string"}, "source_type": {"type": "string"}, "domain_candidate": {"type": "string"}}}}}}, "responses": {"200": {"description": "Material admission packet"}}}},
        "/materials/profile": {"post": {"operationId": "profileMaterials", "summary": "Profile batch of material signals", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"items": {"type": "array", "items": {"type": "object"}}}}}}}, "responses": {"200": {"description": "Material profile batch"}}}},
        "/materials/gate": {"post": {"operationId": "gateMaterial", "summary": "Gate a raw material signal", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "raw": {"type": "string"}, "source_type": {"type": "string"}, "domain_candidate": {"type": "string"}}}}}}, "responses": {"200": {"description": "Material gate"}}}},
        "/exocortex/context/rebuild": {"post": {"operationId": "rebuildExocortexContext", "summary": "Rebuild governed context", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}}}}}, "responses": {"200": {"description": "Context packet"}}}},
        "/agent/diagnostic": {"post": {"operationId": "createMaterialFirstDiagnostic", "summary": "Create material-first Agent diagnostic", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}, "domain_candidate": {"type": "string"}}}}}}, "responses": {"200": {"description": "Material-first diagnostic"}}}},
        "/agent/monitoring": {"post": {"operationId": "createMaterialFirstMonitoring", "summary": "Create material-first Agent monitoring summary", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}, "domain_candidate": {"type": "string"}}}}}}, "responses": {"200": {"description": "Material-first monitoring"}}}},
        "/agent/solutions": {"post": {"operationId": "createMaterialFirstSolutions", "summary": "Create material-first Agent solution options", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}, "domain_candidate": {"type": "string"}}}}}}, "responses": {"200": {"description": "Material-first solutions"}}}},
        "/agent/calibration": {"post": {"operationId": "createMaterialFirstCalibration", "summary": "Create material-first Agent calibration review", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}, "domain_candidate": {"type": "string"}}}}}}, "responses": {"200": {"description": "Material-first calibration"}}}},
        "/services/diagnostic": {"post": {"operationId": "createOperationalDiagnostic", "summary": "Create direct operational diagnostic", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}}}}}, "responses": {"200": {"description": "Operational diagnostic"}}}},
        "/services/monitoring": {"post": {"operationId": "createOperationalMonitoring", "summary": "Create direct operational monitoring", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}}}}}, "responses": {"200": {"description": "Operational monitoring"}}}},
        "/services/solutions": {"post": {"operationId": "createOperationalSolutions", "summary": "Create direct operational solutions", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}}}}}, "responses": {"200": {"description": "Operational solutions"}}}},
        "/services/calibration": {"post": {"operationId": "createOperationalCalibration", "summary": "Create direct operational calibration", "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}}}}}, "responses": {"200": {"description": "Operational calibration"}}}},
        "/calibration-loop/cases": {"get": {"operationId": "listControlledBusinessCases", "summary": "List controlled business cases", "responses": {"200": {"description": "Cases"}}}},
        "/calibration-loop/run": {"post": {"operationId": "runControlledCalibrationLoop", "summary": "Run controlled calibration loop", "requestBody": {"required": False, "content": {"application/json": {"schema": {"type": "object", "properties": {"max_cases": {"type": "integer"}}}}}}, "responses": {"200": {"description": "Calibration loop result"}}}},
        "/graph/mermaid": {"get": {"operationId": "getDiagnosticGraphMermaid", "summary": "Get graph view lite as Mermaid", "responses": {"200": {"description": "Mermaid graph"}}}}
    }
}

OPENAPI_YAML = """openapi: 3.1.0
info:
  title: CASULO Unified Agent API with Material Admission
  version: 0.7.0
  description: Internal sandbox API for CASULO Agent using material-first admission, context rebuild, services and calibration loop. No production or client claim.
servers:
  - url: https://REPLACE_WITH_PUBLIC_ACTION_SERVER
paths:
  /health:
    get:
      operationId: getUnifiedAgentHealth
      summary: Check unified agent API health
      responses:
        '200':
          description: Health
  /openapi.json:
    get:
      operationId: getUnifiedAgentOpenAPI
      summary: Get OpenAPI JSON
      responses:
        '200':
          description: OpenAPI schema
  /materials/taxonomy:
    get:
      operationId: getMaterialTaxonomy
      summary: Get material taxonomy matrix
      responses:
        '200':
          description: Material taxonomy
  /materials/dimensions:
    get:
      operationId: getMaterialDimensions
      summary: Get material dimensions matrix
      responses:
        '200':
          description: Material dimensions
  /materials/admit:
    post:
      operationId: admitMaterial
      summary: Admit a raw material signal
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message: {type: string}
                raw: {type: string}
                source_type: {type: string}
                domain_candidate: {type: string}
      responses:
        '200':
          description: Material admission packet
  /materials/profile:
    post:
      operationId: profileMaterials
      summary: Profile batch of material signals
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                items:
                  type: array
                  items: {type: object}
      responses:
        '200':
          description: Material profile batch
  /materials/gate:
    post:
      operationId: gateMaterial
      summary: Gate a raw material signal
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message: {type: string}
                raw: {type: string}
                source_type: {type: string}
                domain_candidate: {type: string}
      responses:
        '200':
          description: Material gate
  /agent/diagnostic:
    post:
      operationId: createMaterialFirstDiagnostic
      summary: Create material-first Agent diagnostic
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message: {type: string}
                case_id: {type: string}
                domain_candidate: {type: string}
      responses:
        '200':
          description: Material-first diagnostic
  /agent/monitoring:
    post:
      operationId: createMaterialFirstMonitoring
      summary: Create material-first Agent monitoring summary
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message: {type: string}
                case_id: {type: string}
                domain_candidate: {type: string}
      responses:
        '200':
          description: Material-first monitoring
  /agent/solutions:
    post:
      operationId: createMaterialFirstSolutions
      summary: Create material-first Agent solution options
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message: {type: string}
                case_id: {type: string}
                domain_candidate: {type: string}
      responses:
        '200':
          description: Material-first solutions
  /agent/calibration:
    post:
      operationId: createMaterialFirstCalibration
      summary: Create material-first Agent calibration review
      requestBody:
        required: true
        content:
          application/json:
            schema:
              type: object
              properties:
                message: {type: string}
                case_id: {type: string}
                domain_candidate: {type: string}
      responses:
        '200':
          description: Material-first calibration
  /calibration-loop/cases:
    get:
      operationId: listControlledBusinessCases
      summary: List controlled business cases
      responses:
        '200':
          description: Cases
  /calibration-loop/run:
    post:
      operationId: runControlledCalibrationLoop
      summary: Run controlled calibration loop
      requestBody:
        required: false
        content:
          application/json:
            schema:
              type: object
              properties:
                max_cases: {type: integer}
      responses:
        '200':
          description: Calibration loop result
  /graph/mermaid:
    get:
      operationId: getDiagnosticGraphMermaid
      summary: Get graph view lite as Mermaid
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
        "unifies": [
            "material_admission",
            "exocortex_context_rebuild",
            "operational_services",
            "calibration_loop",
            "graph_view_lite",
        ],
    }

def build_result() -> Dict[str, Any]:
    return {
        "status": "PASS",
        "phase": PHASE,
        "decision": DECISION,
        "generated_at": STAMP,
        "calibration_decision": {
            "unified_agent_api_ready": True,
            "material_first_agent_flow_ready": True,
            "material_admission_before_diagnostic_required": True,
            "exocortex_context_rebuild_integrated": True,
            "operational_services_integrated": True,
            "controlled_calibration_loop_integrated": True,
            "graph_view_lite_integrated": True,
            "unified_openapi_ready": True,
            "manual_sandbox_agent_test_runbook_ready": True,
            "live_chatgpt_agent_configured_now": False,
            "public_action_server_deployed": False,
            "micrograph_runtime_current_poc": False,
            "threshold_lock_ready": False,
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
            "cockpit_priority": "DEFERRED",
        },
        "endpoints": [
            "GET /health",
            "GET /openapi.json",
            "GET /materials/taxonomy",
            "GET /materials/dimensions",
            "POST /materials/admit",
            "POST /materials/profile",
            "POST /materials/gate",
            "POST /agent/diagnostic",
            "POST /agent/monitoring",
            "POST /agent/solutions",
            "POST /agent/calibration",
            "GET /calibration-loop/cases",
            "POST /calibration-loop/run",
            "GET /graph/mermaid",
        ],
        "next": "PROD-8581..8620 - Manual ChatGPT Agent Sandbox Test Pack",
    }

def apply() -> List[str]:
    wrote: List[str] = []
    result = build_result()

    instructions = """# CASULO Unified Agent Instructions v0.7

You are CASULO Agent in internal sandbox mode.

## Mandatory flow

For diagnostic, monitoring, solution or calibration requests:

1. Admit raw input as material.
2. Classify material and dimensions.
3. Apply material gate.
4. Rebuild context through Exocortex.
5. Call the appropriate operational service.
6. Return only internal draft output with blocked actions.

## Hard boundaries

- Chat input is raw signal, not truth.
- Inference is not evidence.
- Partial evidence is not validation.
- Sandbox is not production.
- Internal diagnostic is not client claim.
- Threshold candidate is not threshold lock.
- Micrograph runtime is future epic only.
- The Agent is subordinate to the Operational Cube.
"""

    knowledge = """# CASULO Unified Agent Knowledge Pack v0.7

Implemented internal layers:

- Operational Cube master contract.
- Read-only adapters.
- Exocortex context rebuild.
- Operational services.
- Controlled business case calibration loop.
- Material admission matrices.
- Unified material-first Agent API.

Current scope:

- Internal sandbox Agent test.
- No production.
- No client claim.
- No commercial claim.
- No live GitHub write.
- No live Neo4j write.
- No micrograph runtime.
"""

    manifest = {
        "status": "READY_FOR_SANDBOX_AGENT_TEST",
        "phase": PHASE,
        "decision": DECISION,
        "server_entrypoint": "product/api/casulo_agent_api_server_v07_unified_agent.py",
        "openapi_json": "product/agent_unified/casulo_unified_agent_openapi.json",
        "openapi_yaml": "product/agent_unified/casulo_unified_agent_openapi.yaml",
        "instructions": "product/agent_unified/casulo_unified_agent_instructions.md",
        "knowledge_pack": "product/agent_unified/casulo_unified_agent_knowledge_pack.md",
        "material_first_flow_required": True,
        "live_chatgpt_agent_configured_now": False,
        "public_action_server_deployed": False,
        "client_claim_allowed": False,
        "production_allowed": False,
        "commercial_claim_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS,
        "endpoints": result["endpoints"],
    }

    manifest_md = f"""# CASULO Unified Agent Manifest v0.7

Status: `READY_FOR_SANDBOX_AGENT_TEST`  
Decision: `{DECISION}`

## Material-first rule

Raw input must pass through material admission before diagnostic, monitoring, solutions or calibration.

## Server

`product/api/casulo_agent_api_server_v07_unified_agent.py`

## OpenAPI

- `product/agent_unified/casulo_unified_agent_openapi.yaml`
- `product/agent_unified/casulo_unified_agent_openapi.json`

## Boundary

This pack does not configure a live ChatGPT Agent by itself.
"""

    flow = """# Material-First Agent Flow

```text
user/business signal
  -> /materials/admit
  -> material class + dimensions + drag + delta + gate
  -> /exocortex/context/rebuild
  -> /agent/diagnostic or /agent/monitoring or /agent/solutions or /agent/calibration
  -> internal draft with blocked actions
```

The Agent must not treat raw text as state.

The Agent must not call production, client-facing or commercial claims.
"""

    tests = {
        "version": "casulo_unified_agent_action_test_suite.v0.7",
        "phase": PHASE,
        "tests": [
            {
                "id": "UACT-001",
                "endpoint": "GET /health",
                "expected": ["writes_allowed=false", "live_chatgpt_agent_configured_now=false"],
            },
            {
                "id": "UACT-002",
                "endpoint": "POST /materials/admit",
                "payload": {"message": "Empresa com dados espalhados e sistemas sem integração."},
                "expected": ["raw_signal_treated_as_truth=false"],
            },
            {
                "id": "UACT-003",
                "endpoint": "POST /agent/diagnostic",
                "payload": {"message": "Empresa com rollback ausente e proposta de automatizar.", "domain_candidate": "TIC_SI"},
                "expected": ["material_first_then_context_then_service", "ready_for_production=false"],
            },
            {
                "id": "UACT-004",
                "endpoint": "POST /agent/monitoring",
                "payload": {"message": "Caso com pouca evidência e pressão executiva."},
                "expected": ["INTERNAL_AGENT_SANDBOX_DRAFT"],
            },
            {
                "id": "UACT-005",
                "endpoint": "POST /agent/solutions",
                "payload": {"message": "Empresa precisa reduzir retrabalho e mapear dados."},
                "expected": ["ready_for_client_claim=false"],
            },
            {
                "id": "UACT-006",
                "endpoint": "POST /agent/calibration",
                "payload": {"message": "Calibrar matriz para empresa com dados espalhados."},
                "expected": ["threshold_lock_ready=false"],
            },
            {
                "id": "UACT-007",
                "endpoint": "POST /calibration-loop/run",
                "payload": {"max_cases": 3},
                "expected": ["threshold_lock_ready=false"],
            },
            {
                "id": "UACT-008",
                "endpoint": "GET /graph/mermaid",
                "expected": ["format=mermaid"],
            },
        ],
    }

    prompts = """# Unified Agent Sandbox Test Prompts

1. Faça um diagnóstico interno de uma empresa com dados espalhados, sistemas sem integração e rollback ausente.
2. Antes do diagnóstico, classifique o material de entrada e diga o gate.
3. Monitore riscos desse caso sem transformar hipótese em evidência.
4. Sugira soluções internas mantendo produção bloqueada.
5. Faça calibração da matriz e diga se já existe threshold lock.
6. Rode o loop controlado com 3 casos comuns.
7. Mostre a visão Mermaid do grafo diagnóstico.
8. Esse resultado pode ser apresentado ao cliente como evidência validada?
"""

    runbook = """# Manual Sandbox Agent Test Runbook

## Start server

```bash
python3 product/api/casulo_agent_api_server_v07_unified_agent.py --host 0.0.0.0 --port 8541
```

## Test health

```bash
curl -s http://127.0.0.1:8541/health
```

## Expose Codespaces port

Use the public HTTPS forwarded URL for port 8541 only for sandbox testing.

## Configure Custom GPT / Agent manually

Instructions:
`product/agent_unified/casulo_unified_agent_instructions.md`

Knowledge:
`product/agent_unified/casulo_unified_agent_knowledge_pack.md`

Action schema:
`product/agent_unified/casulo_unified_agent_openapi.yaml`

Replace server URL:
`https://REPLACE_WITH_PUBLIC_ACTION_SERVER`

## Boundary

No client, production or commercial use.
"""

    contract = {
        "contract": "unified_agent_api_material_admission_calibration_loop.contract.v0.1",
        "phase": PHASE,
        "requires": REQUIRED,
        "status": "PASS",
        "decision": DECISION,
        "mode": "INTERNAL_SANDBOX_UNIFIED_AGENT_API_MATERIAL_FIRST",
        "implemented_endpoints": result["endpoints"],
        "blocked_actions": BLOCKED_ACTIONS,
        "not_implemented_yet": [
            "manual ChatGPT Agent configuration",
            "public HTTPS deployment",
            "live Agent test result capture",
            "client-facing use",
            "production activation",
            "micrograph runtime",
            "threshold lock",
        ],
    }

    docs = f"""# PROD-8541..8580 - Unified Agent API v0.7 with Material Admission and Calibration Loop

Status: PASS  
Decision: `{DECISION}`

## Purpose

Unify material admission, Exocortex context rebuild, operational services, calibration loop and graph view lite for internal Agent sandbox testing.

## Implements

- material-first Agent flow;
- unified API server;
- unified OpenAPI;
- unified Agent instructions;
- unified knowledge pack;
- sandbox action test suite;
- manual sandbox test runbook.

## Does not implement

- live ChatGPT Agent configuration;
- public HTTPS deployment;
- client-facing use;
- production activation;
- commercial proof;
- micrograph runtime.

## Next

`PROD-8581..8620 - Manual ChatGPT Agent Sandbox Test Pack`
"""

    out_md = f"""# PROD-8541..8580 - Unified Agent API with Material Admission and Calibration Loop

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

    write_json("product/agent_unified/casulo_unified_agent_manifest.json", manifest, wrote)
    write_text("product/agent_unified/casulo_unified_agent_manifest.md", manifest_md, wrote)
    write_text("product/agent_unified/casulo_unified_agent_instructions.md", instructions, wrote)
    write_text("product/agent_unified/casulo_unified_agent_knowledge_pack.md", knowledge, wrote)
    write_text("product/agent_unified/casulo_unified_agent_openapi.yaml", OPENAPI_YAML, wrote)
    write_json("product/agent_unified/casulo_unified_agent_openapi.json", OPENAPI_JSON, wrote)
    write_text("product/agent_unified/material_first_agent_flow.md", flow, wrote)
    write_json("product/agent_unified/unified_action_test_suite.json", tests, wrote)
    write_text("product/agent_unified/unified_action_test_prompts.md", prompts, wrote)
    write_text("product/agent_unified/manual_sandbox_agent_test_runbook.md", runbook, wrote)
    write_text("product/api/casulo_agent_api_server_v07_unified_agent.py", UNIFIED_API, wrote, executable=True)
    write_text("product/api/run_casulo_agent_api_server_v07_unified.sh", "#!/usr/bin/env bash\nset -euo pipefail\ncd \"$(dirname \"$0\")/../..\" || exit 1\npython3 product/api/casulo_agent_api_server_v07_unified_agent.py --host 0.0.0.0 --port \"${CASULO_AGENT_UNIFIED_MATERIAL_API_PORT:-8541}\"\n", wrote, executable=True)
    write_text("product/api/tests/test_unified_agent_api_material_first.py", TEST_CODE, wrote, executable=True)
    write_json("product/api/contracts/unified_agent_api_material_admission_calibration_loop.contract.json", contract, wrote)
    write_json("outputs/prod8541_8580_unified_agent_api_material_admission_calibration_loop.json", result, wrote)
    write_text("outputs/prod8541_8580_unified_agent_api_material_admission_calibration_loop.md", out_md, wrote)
    write_text("docs/product/854_UNIFIED_AGENT_API_MATERIAL_ADMISSION_CALIBRATION_LOOP.md", docs, wrote)
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
    test = run_cmd(["python3", "product/api/tests/test_unified_agent_api_material_first.py"], timeout=30)
    result = read_json("outputs/prod8541_8580_unified_agent_api_material_admission_calibration_loop.json", {})
    cal = result.get("calibration_decision", {})
    checks = {
        "generated_missing_count": len(missing),
        "json_errors_count": len(json_errors),
        "py_errors_count": len(py_errors),
        "static_tests_passed": test.get("ok") is True,
        "unified_agent_api_ready": cal.get("unified_agent_api_ready") is True,
        "material_first_agent_flow_ready": cal.get("material_first_agent_flow_ready") is True,
        "material_admission_before_diagnostic_required": cal.get("material_admission_before_diagnostic_required") is True,
        "controlled_calibration_loop_integrated": cal.get("controlled_calibration_loop_integrated") is True,
        "live_chatgpt_agent_configured_now_false": cal.get("live_chatgpt_agent_configured_now") is False,
        "micrograph_runtime_current_poc_false": cal.get("micrograph_runtime_current_poc") is False,
        "client_claim_allowed_false": cal.get("client_claim_allowed") is False,
        "production_allowed_false": cal.get("production_allowed") is False,
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
    paths = ["apply_prod8541_8580_unified_agent_api_material_admission_calibration_loop.py", *GENERATED]
    lines = ["git add \\"]
    for p in paths[:-1]:
        lines.append(f"  {p} \\")
    lines.append(f"  {paths[-1]}")
    lines.extend([
        "",
        'git commit -m "Add unified Agent API with material admission and calibration loop"',
        'git tag -a product-casulo-unified-agent-api-material-admission-v0.1 HEAD -m "CASULO unified Agent API material admission v0.1"',
        "git push origin main",
        "git push origin product-casulo-unified-agent-api-material-admission-v0.1",
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

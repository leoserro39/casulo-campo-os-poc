#!/usr/bin/env python3
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

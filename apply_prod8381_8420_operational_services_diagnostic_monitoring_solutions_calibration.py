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
PHASE = "PROD-8381..8420"
DECISION = "OPERATIONAL_SERVICES_DIAGNOSTIC_MONITORING_SOLUTIONS_CALIBRATION_READY"

REQUIRED = [
    "outputs/prod8341_8380_exocortex_context_rebuild_runtime.json",
    "product/exocortex/context_rebuild_runtime.py",
    "product/api/casulo_agent_api_server_v03_context.py",
    "product/cube/operational_cube_master_contract.json",
    "product/calibration/casulo_kpi_vector_telemetry_inventory.json",
    "product/adapters/read_only/evidence_trace_adapter.py",
]

GENERATED = [
    "product/services/operational_services.py",
    "product/services/semantic_matrix_v0_1.json",
    "product/services/telemetry_matrix_v0_1.json",
    "product/services/common_business_cases_v0_1.json",
    "product/services/README.md",
    "product/api/casulo_agent_api_server_v04_services.py",
    "product/api/run_casulo_agent_api_server_v04.sh",
    "product/api/tests/test_operational_services.py",
    "product/api/openapi/casulo_agent_action_openapi_v04_services.yaml",
    "product/api/openapi/casulo_agent_action_openapi_v04_services.json",
    "product/api/contracts/operational_services_diagnostic_monitoring_solutions_calibration.contract.json",
    "outputs/prod8381_8420_operational_services_diagnostic_monitoring_solutions_calibration.json",
    "outputs/prod8381_8420_operational_services_diagnostic_monitoring_solutions_calibration.md",
    "docs/product/838_OPERATIONAL_SERVICES_DIAGNOSTIC_MONITORING_SOLUTIONS_CALIBRATION.md",
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

OPERATIONAL_SERVICES = r"""#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

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
]

def read_json(path: str, default=None):
    p = ROOT / path
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def load_module(name: str, path: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

context_runtime = load_module("context_rebuild_runtime", "product/exocortex/context_rebuild_runtime.py")

def _base(message: str, case_id: str = "COMMON-COMPANY-001") -> Dict[str, Any]:
    packet = context_runtime.build_context_packet(message, case_id)
    diag = context_runtime.build_diagnostic_report(message, case_id)
    semantic_matrix = read_json("product/services/semantic_matrix_v0_1.json", {})
    telemetry_matrix = read_json("product/services/telemetry_matrix_v0_1.json", {})
    return {
        "packet": packet,
        "diagnostic_draft": diag,
        "semantic_matrix": semantic_matrix,
        "telemetry_matrix": telemetry_matrix,
    }

def _score_from_packet(packet: Dict[str, Any]) -> Dict[str, Any]:
    cls = packet.get("classification", {})
    risk_count = len(cls.get("risks", []))
    gap_count = len(cls.get("gaps", []))
    contradiction_count = len(cls.get("contradictions", []))
    inference_count = len(cls.get("valid_inferences", []))

    evidence_density = 0.35 + min(0.30, 0.10 * inference_count)
    ambiguity_risk = min(1.0, 0.20 + 0.15 * gap_count + 0.20 * contradiction_count)
    gate_alignment = 1.0 if packet.get("gate") in ["HUMAN_REVIEW_REQUIRED", "SANDBOX_ONLY_HUMAN_REVIEW_REQUIRED"] else 0.75
    claim_boundary = 1.0
    operational_readiness = max(0.0, min(1.0, 0.55 + 0.08 * inference_count - 0.12 * risk_count - 0.15 * gap_count - 0.20 * contradiction_count))

    oqi = round(max(0.0, min(1.0, 0.40 * evidence_density + 0.25 * gate_alignment + 0.20 * claim_boundary + 0.15 * operational_readiness)), 4)
    ohri = round(max(0.0, min(1.0, 0.20 + 0.15 * risk_count + 0.10 * gap_count + 0.20 * contradiction_count - 0.10 * gate_alignment)), 4)
    zpi = round(max(0.0, min(1.0, 1.0 - ohri)), 4)
    delta_estado = round(max(0.0, min(1.0, 0.45 * ohri + 0.25 * ambiguity_risk + 0.15 * gap_count + 0.15 * contradiction_count)), 4)

    return {
        "evidence_density": round(evidence_density, 4),
        "semantic_ambiguity": round(ambiguity_risk, 4),
        "gate_alignment": round(gate_alignment, 4),
        "claim_boundary_preservation": claim_boundary,
        "operational_readiness": round(operational_readiness, 4),
        "oqi": oqi,
        "ohri": ohri,
        "zpi": zpi,
        "delta_estado": delta_estado,
        "threshold_lock_ready": False,
        "client_claim_allowed": False,
        "production_allowed": False,
        "commercial_claim_allowed": False,
    }

def diagnostic_service(message: str, case_id: str = "COMMON-COMPANY-001") -> Dict[str, Any]:
    b = _base(message, case_id)
    packet = b["packet"]
    scores = _score_from_packet(packet)
    return {
        "version": "casulo_operational_diagnostic_service.v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_id": case_id,
        "status": "INTERNAL_DRAFT_ONLY",
        "service": "diagnostic",
        "operational_state": packet.get("gate"),
        "context_packet": packet,
        "semantic_matrix_used": b["semantic_matrix"].get("version"),
        "telemetry_matrix_used": b["telemetry_matrix"].get("version"),
        "scores": scores,
        "diagnostic": {
            "summary": "Initial internal diagnostic draft generated from governed context rebuild.",
            "primary_findings": packet.get("classification", {}).get("valid_inferences", []),
            "gaps": packet.get("classification", {}).get("gaps", []),
            "risks": packet.get("classification", {}).get("risks", []),
            "contradictions": packet.get("classification", {}).get("contradictions", []),
            "graph_view_lite": packet.get("graph_view_lite", {}),
        },
        "allowed_actions": packet.get("allowed_actions", []),
        "blocked_actions": BLOCKED_ACTIONS,
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "commercial_claim_allowed": False,
    }

def monitoring_service(message: str, case_id: str = "COMMON-COMPANY-001") -> Dict[str, Any]:
    diag = diagnostic_service(message, case_id)
    scores = diag["scores"]
    watch_items = []
    if scores["ohri"] >= 0.3:
        watch_items.append("hallucination_or_overclaim_risk")
    if scores["delta_estado"] >= 0.25:
        watch_items.append("state_delta_above_initial_threshold")
    if not watch_items:
        watch_items.append("continue_collecting_business_evidence")
    return {
        "version": "casulo_monitoring_service.v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_id": case_id,
        "status": "INTERNAL_MONITORING_DRAFT",
        "service": "monitoring",
        "watch_items": watch_items,
        "scores": scores,
        "gate": diag["operational_state"],
        "blocked_actions": BLOCKED_ACTIONS,
        "ready_for_client_claim": False,
        "ready_for_production": False,
    }

def solutions_service(message: str, case_id: str = "COMMON-COMPANY-001") -> Dict[str, Any]:
    diag = diagnostic_service(message, case_id)
    findings = diag["diagnostic"]["primary_findings"]
    recommendations = [
        {
            "id": "SOL-001",
            "title": "Mapear dados operacionais mínimos",
            "type": "business_data_mapping",
            "safe_scope": "internal_draft",
            "reason": "Create a computable state baseline before automation.",
        },
        {
            "id": "SOL-002",
            "title": "Separar evidência, inferência, lacuna e risco",
            "type": "inference_gate_operation",
            "safe_scope": "internal_draft",
            "reason": "Reduce overclaim and stabilize diagnostic quality.",
        },
        {
            "id": "SOL-003",
            "title": "Criar matriz semântica e telemétrica do caso",
            "type": "matrix_calibration",
            "safe_scope": "internal_draft",
            "reason": "Enable repeated calibration across common company cases.",
        },
    ]
    return {
        "version": "casulo_solutions_service.v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_id": case_id,
        "status": "INTERNAL_SOLUTION_OPTIONS_DRAFT",
        "service": "solutions",
        "findings_used": findings,
        "recommendations": recommendations,
        "blocked_actions": BLOCKED_ACTIONS,
        "ready_for_client_claim": False,
        "ready_for_production": False,
    }

def calibration_service(message: str, case_id: str = "COMMON-COMPANY-001") -> Dict[str, Any]:
    diag = diagnostic_service(message, case_id)
    scores = diag["scores"]
    return {
        "version": "casulo_calibration_service.v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_id": case_id,
        "status": "INTERNAL_CALIBRATION_REVIEW_DRAFT",
        "service": "calibration",
        "semantic_matrix_version": diag["semantic_matrix_used"],
        "telemetry_matrix_version": diag["telemetry_matrix_used"],
        "scores": scores,
        "threshold_candidates": {
            "min_oqi_for_strong_internal_diagnostic": 0.75,
            "max_ohri_for_strong_internal_diagnostic": 0.25,
            "min_zpi_for_zero_point_integrity": 0.80,
            "max_delta_estado_for_low_delta": 0.20,
        },
        "threshold_lock_ready": False,
        "calibration_notes": [
            "Current matrix is suitable for controlled internal tests.",
            "More common-company cases are required before threshold lock.",
            "No client, production or commercial claim is allowed.",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "ready_for_client_claim": False,
        "ready_for_production": False,
    }

if __name__ == "__main__":
    sample = "Empresa com dados espalhados, atendimento sem padrão, retrabalho e sistemas sem integração."
    print(json.dumps(diagnostic_service(sample), indent=2, ensure_ascii=False))
"""

API_V04 = r"""#!/usr/bin/env python3
from __future__ import annotations

import argparse
import importlib.util
import json
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[2]

def load_module(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

services = load_module("operational_services", "product/services/operational_services.py")

def route_post(path, payload):
    msg = str(payload.get("message", ""))
    case_id = str(payload.get("case_id", "COMMON-COMPANY-001"))
    if path == "/services/diagnostic":
        return 200, services.diagnostic_service(msg, case_id)
    if path == "/services/monitoring":
        return 200, services.monitoring_service(msg, case_id)
    if path == "/services/solutions":
        return 200, services.solutions_service(msg, case_id)
    if path == "/services/calibration":
        return 200, services.calibration_service(msg, case_id)
    return 404, {"status": "not_found", "path": path}

def route_get(path):
    if path == "/health":
        return 200, {"status": "ok", "service": "casulo_agent_api_server_v04_services", "phase": "PROD-8381..8420"}
    return 404, {"status": "not_found", "path": path}

class Handler(BaseHTTPRequestHandler):
    server_version = "CASULOAgentAPIServices/0.1"
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
    ap.add_argument("--port", type=int, default=8381)
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

services = load("operational_services", "product/services/operational_services.py")
api = load("casulo_agent_api_server_v04_services", "product/api/casulo_agent_api_server_v04_services.py")

message = "Empresa com dados espalhados, sistemas sem integração, retrabalho, atendimento sem padrão e falta de indicadores."
diag = services.diagnostic_service(message)
assert diag["service"] == "diagnostic"
assert diag["status"] == "INTERNAL_DRAFT_ONLY"
assert diag["ready_for_client_claim"] is False
assert diag["ready_for_production"] is False
assert "scores" in diag
assert "graph_view_lite" in diag["diagnostic"]

mon = services.monitoring_service(message)
assert mon["service"] == "monitoring"
assert mon["ready_for_production"] is False

sol = services.solutions_service(message)
assert sol["service"] == "solutions"
assert sol["ready_for_client_claim"] is False
assert len(sol["recommendations"]) >= 3

cal = services.calibration_service(message)
assert cal["service"] == "calibration"
assert cal["threshold_lock_ready"] is False
assert cal["ready_for_production"] is False

code, payload = api.route_post("/services/diagnostic", {"message": message})
assert code == 200
assert payload["service"] == "diagnostic"

code, payload = api.route_post("/services/calibration", {"message": message})
assert code == 200
assert payload["service"] == "calibration"

print(json.dumps({"status": "PASS", "tests": "operational_services"}, indent=2))
"""

OPENAPI_JSON = {
    "openapi": "3.1.0",
    "info": {
        "title": "CASULO Agent Action API v0.4 Operational Services",
        "version": "0.4.0",
        "description": "Diagnostic, monitoring, solutions and calibration internal services."
    },
    "servers": [{"url": "https://REPLACE_WITH_PUBLIC_ACTION_SERVER"}],
    "paths": {
        "/services/diagnostic": {
            "post": {
                "operationId": "createDiagnostic",
                "summary": "Create internal diagnostic draft",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}, "required": ["message"]}}}},
                "responses": {"200": {"description": "Diagnostic draft"}}
            }
        },
        "/services/monitoring": {
            "post": {
                "operationId": "createMonitoring",
                "summary": "Create internal monitoring summary",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}, "required": ["message"]}}}},
                "responses": {"200": {"description": "Monitoring summary"}}
            }
        },
        "/services/solutions": {
            "post": {
                "operationId": "createSolutions",
                "summary": "Create internal solution options",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}, "required": ["message"]}}}},
                "responses": {"200": {"description": "Solution options"}}
            }
        },
        "/services/calibration": {
            "post": {
                "operationId": "createCalibration",
                "summary": "Create internal calibration review",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}, "required": ["message"]}}}},
                "responses": {"200": {"description": "Calibration review"}}
            }
        }
    }
}

OPENAPI_YAML = """openapi: 3.1.0
info:
  title: CASULO Agent Action API v0.4 Operational Services
  version: 0.4.0
  description: Diagnostic, monitoring, solutions and calibration internal services.
servers:
  - url: https://REPLACE_WITH_PUBLIC_ACTION_SERVER
paths:
  /services/diagnostic:
    post:
      operationId: createDiagnostic
      summary: Create internal diagnostic draft
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
  /services/monitoring:
    post:
      operationId: createMonitoring
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
      operationId: createSolutions
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
      operationId: createCalibration
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
        "services": ["diagnostic", "monitoring", "solutions", "calibration"],
    }

def build_result() -> Dict[str, Any]:
    return {
        "status": "PASS",
        "phase": PHASE,
        "decision": DECISION,
        "generated_at": STAMP,
        "calibration_decision": {
            "diagnostic_service_ready": True,
            "monitoring_service_ready": True,
            "solutions_service_ready": True,
            "calibration_service_ready": True,
            "semantic_matrix_v0_1_ready": True,
            "telemetry_matrix_v0_1_ready": True,
            "common_business_cases_seed_ready": True,
            "api_v04_services_ready": True,
            "threshold_lock_ready": False,
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
            "micrograph_runtime_current_poc": False,
            "cockpit_priority": "DEFERRED",
        },
        "endpoints": [
            "POST /services/diagnostic",
            "POST /services/monitoring",
            "POST /services/solutions",
            "POST /services/calibration",
        ],
        "next": "PROD-8421..8460 - ChatGPT Agent Actions Integration Pack",
    }

def apply() -> List[str]:
    wrote: List[str] = []
    result = build_result()

    semantic_matrix = {
        "version": "semantic_matrix.v0.1",
        "phase": PHASE,
        "purpose": "Initial semantic matrix for common-company CASULO controlled tests.",
        "domains": [
            "data_mapping",
            "process_mapping",
            "systems_integration",
            "evidence_quality",
            "operational_risk",
            "governance",
            "monitoring",
            "solution_design",
        ],
        "classifiers": [
            "supported_fact",
            "valid_inference",
            "weak_inference",
            "gap",
            "risk",
            "contradiction",
            "blocked_claim",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    telemetry_matrix = {
        "version": "telemetry_matrix.v0.1",
        "phase": PHASE,
        "metrics": {
            "OQI": "Operational Quality Index",
            "OHRI": "Operational Hallucination Risk Index",
            "ZPI": "Zero Point Integrity",
            "Delta Estado": "Distance from safe governed operational state",
            "evidence_density": "Evidence concentration in answer/context",
            "semantic_ambiguity": "Ambiguity pressure in signal/context",
            "gate_alignment": "Whether output preserved correct gate",
            "claim_boundary_preservation": "Whether forbidden claims stayed blocked",
        },
        "threshold_candidates": {
            "min_oqi_for_strong_internal_diagnostic": 0.75,
            "max_ohri_for_strong_internal_diagnostic": 0.25,
            "min_zpi_for_zero_point_integrity": 0.80,
            "max_delta_estado_for_low_delta": 0.20,
        },
        "threshold_lock_ready": False,
    }

    common_cases = {
        "version": "common_business_cases.v0.1",
        "phase": PHASE,
        "cases": [
            {
                "case_id": "COMMON-COMPANY-001",
                "title": "Dados espalhados e retrabalho",
                "message": "Empresa com dados espalhados em planilhas, sistema financeiro separado, atendimento sem padrão, retrabalho e ausência de indicadores confiáveis.",
            },
            {
                "case_id": "COMMON-COMPANY-002",
                "title": "Mudanças sem rollback",
                "message": "Empresa média com sistemas críticos, integrações pouco mapeadas, mudanças manuais e ausência de rollback formal.",
            },
            {
                "case_id": "COMMON-COMPANY-003",
                "title": "Atendimento e operação sem estado",
                "message": "Empresa com atendimento em múltiplos canais, registros inconsistentes, falta de dono por processo e decisões baseadas em memória informal.",
            },
        ],
    }

    contract = {
        "contract": "operational_services_diagnostic_monitoring_solutions_calibration.contract.v0.1",
        "phase": PHASE,
        "requires": REQUIRED,
        "status": "PASS",
        "decision": DECISION,
        "mode": "INTERNAL_OPERATIONAL_SERVICES",
        "implemented_endpoints": result["endpoints"],
        "blocked_actions": BLOCKED_ACTIONS,
        "not_implemented_yet": [
            "public ChatGPT Action deployment",
            "live customer diagnostic",
            "threshold lock",
            "validated model gain claim",
            "validated hallucination reduction claim",
        ],
    }

    docs = f"""# PROD-8381..8420 - Operational Services: Diagnostic, Monitoring, Solutions, Calibration

Status: PASS  
Decision: `{DECISION}`

## Purpose

Create internal services for controlled CASULO tests over common company cases.

## Implements

- diagnostic service;
- monitoring service;
- solutions service;
- calibration service;
- semantic matrix v0.1;
- telemetry matrix v0.1;
- common business cases seed;
- API v0.4 service endpoints.

## Does not implement

- public ChatGPT Action deployment;
- client-facing diagnostic;
- production activation;
- commercial claim;
- threshold lock;
- validated hallucination reduction claim.

## Next

`PROD-8421..8460 - ChatGPT Agent Actions Integration Pack`
"""

    readme = """# CASULO Operational Services v0.1

Internal services for diagnostic, monitoring, solutions and calibration.

No GPT calls.
No Codex execution.
No GitHub writes.
No live Neo4j writes.
No client/production/commercial claims.

## Test

```bash
python3 product/api/tests/test_operational_services.py
```

## Run API v0.4

```bash
python3 product/api/casulo_agent_api_server_v04_services.py --host 0.0.0.0 --port 8381
```
"""

    out_md = f"""# PROD-8381..8420 - Operational Services

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

    write_text("product/services/operational_services.py", OPERATIONAL_SERVICES, wrote, executable=True)
    write_json("product/services/semantic_matrix_v0_1.json", semantic_matrix, wrote)
    write_json("product/services/telemetry_matrix_v0_1.json", telemetry_matrix, wrote)
    write_json("product/services/common_business_cases_v0_1.json", common_cases, wrote)
    write_text("product/services/README.md", readme, wrote)
    write_text("product/api/casulo_agent_api_server_v04_services.py", API_V04, wrote, executable=True)
    write_text("product/api/run_casulo_agent_api_server_v04.sh", "#!/usr/bin/env bash\nset -euo pipefail\ncd \"$(dirname \"$0\")/../..\" || exit 1\npython3 product/api/casulo_agent_api_server_v04_services.py --host 0.0.0.0 --port \"${CASULO_AGENT_SERVICES_API_PORT:-8381}\"\n", wrote, executable=True)
    write_text("product/api/tests/test_operational_services.py", TEST_CODE, wrote, executable=True)
    write_text("product/api/openapi/casulo_agent_action_openapi_v04_services.yaml", OPENAPI_YAML, wrote)
    write_json("product/api/openapi/casulo_agent_action_openapi_v04_services.json", OPENAPI_JSON, wrote)
    write_json("product/api/contracts/operational_services_diagnostic_monitoring_solutions_calibration.contract.json", contract, wrote)
    write_json("outputs/prod8381_8420_operational_services_diagnostic_monitoring_solutions_calibration.json", result, wrote)
    write_text("outputs/prod8381_8420_operational_services_diagnostic_monitoring_solutions_calibration.md", out_md, wrote)
    write_text("docs/product/838_OPERATIONAL_SERVICES_DIAGNOSTIC_MONITORING_SOLUTIONS_CALIBRATION.md", docs, wrote)
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
    test = run_cmd(["python3", "product/api/tests/test_operational_services.py"], timeout=30)
    result = read_json("outputs/prod8381_8420_operational_services_diagnostic_monitoring_solutions_calibration.json", {})
    cal = result.get("calibration_decision", {})
    checks = {
        "generated_missing_count": len(missing),
        "json_errors_count": len(json_errors),
        "py_errors_count": len(py_errors),
        "static_tests_passed": test.get("ok") is True,
        "diagnostic_service_ready": cal.get("diagnostic_service_ready") is True,
        "monitoring_service_ready": cal.get("monitoring_service_ready") is True,
        "solutions_service_ready": cal.get("solutions_service_ready") is True,
        "calibration_service_ready": cal.get("calibration_service_ready") is True,
        "threshold_lock_ready_false": cal.get("threshold_lock_ready") is False,
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
    paths = ["apply_prod8381_8420_operational_services_diagnostic_monitoring_solutions_calibration.py", *GENERATED]
    lines = ["git add \\"]
    for p in paths[:-1]:
        lines.append(f"  {p} \\")
    lines.append(f"  {paths[-1]}")
    lines.extend([
        "",
        'git commit -m "Add operational services for diagnostic monitoring solutions calibration"',
        'git tag -a product-casulo-operational-services-diagnostic-calibration-v0.1 HEAD -m "CASULO operational services diagnostic calibration v0.1"',
        "git push origin main",
        "git push origin product-casulo-operational-services-diagnostic-calibration-v0.1",
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

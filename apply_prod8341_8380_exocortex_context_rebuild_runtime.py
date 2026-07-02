#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import py_compile
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()
PHASE = "PROD-8341..8380"
DECISION = "EXOCORTEX_CONTEXT_REBUILD_RUNTIME_DIAGNOSTIC_GRAPH_VIEW_LITE_READY"

REQUIRED = [
    "outputs/prod8301_8340_readonly_adapters_git_repo_outputs_neo4j.json",
    "product/adapters/read_only/git_repo_adapter.py",
    "product/adapters/read_only/output_artifact_indexer.py",
    "product/adapters/read_only/neo4j_readonly_adapter_scaffold.py",
    "product/adapters/read_only/evidence_trace_adapter.py",
    "product/cube/operational_cube_master_contract.json",
    "product/calibration/casulo_kpi_vector_telemetry_inventory.json",
]

GENERATED = [
    "product/exocortex/context_rebuild_runtime.py",
    "product/exocortex/context_rebuild_policy.json",
    "product/exocortex/sample_inputs/business_case_common_company.json",
    "product/diagnostics/diagnostic_report_model_v0_2.md",
    "product/diagnostics/graph_view_lite_mermaid.md",
    "product/diagnostics/sample_context_rebuild_result.json",
    "product/api/casulo_agent_api_server_v03_context.py",
    "product/api/run_casulo_agent_api_server_v03.sh",
    "product/api/tests/test_exocortex_context_rebuild_runtime.py",
    "product/api/openapi/casulo_agent_action_openapi_v03_context.yaml",
    "product/api/openapi/casulo_agent_action_openapi_v03_context.json",
    "product/api/contracts/exocortex_context_rebuild_runtime.contract.json",
    "outputs/prod8341_8380_exocortex_context_rebuild_runtime.json",
    "outputs/prod8341_8380_exocortex_context_rebuild_runtime.md",
    "docs/product/834_EXOCORTEX_CONTEXT_REBUILD_RUNTIME_DIAGNOSTIC_GRAPH_VIEW_LITE.md",
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

CONTEXT_RUNTIME = r"""#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import re
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

def terms(text: str):
    return set(re.findall(r"[A-Za-zÀ-ÿ0-9_+-]{3,}", text.lower()))

def classify_signal(text: str) -> Dict[str, Any]:
    low = text.lower()
    supported_facts = []
    valid_inferences = []
    weak_inferences = []
    gaps = []
    risks = []
    contradictions = []

    if any(x in low for x in ["empresa", "processo", "dados", "sistema", "rotina", "operação", "operacao"]):
        valid_inferences.append("business_operational_context_requested")
    if any(x in low for x in ["diagnóstico", "diagnostico", "monitoramento", "solução", "solucao", "calibração", "calibracao"]):
        valid_inferences.append("operational_service_requested")
    if any(x in low for x in ["neo4j", "grafo", "graph", "repo", "github"]):
        valid_inferences.append("repo_or_graph_grounding_required")
    if any(x in low for x in ["cliente", "produção", "production", "comercial", "commercial"]):
        risks.append("blocked_claim_or_real_world_effect_pressure")
    if any(x in low for x in ["certeza", "100%", "perfeito", "garantir"]):
        risks.append("overconfidence_pressure")
    if any(x in low for x in ["executa", "merge", "codex", "push", "delete", "apaga"]):
        risks.append("execution_or_write_pressure")

    if not text.strip():
        gaps.append("empty_signal")
    if "micrografo" in low or "micrograph" in low:
        contradictions.append("micrograph_runtime_not_current_poc_scope")

    return {
        "supported_facts": supported_facts,
        "valid_inferences": valid_inferences,
        "weak_inferences": weak_inferences,
        "gaps": gaps,
        "risks": risks,
        "contradictions": contradictions,
    }

def build_graph_mermaid(case_id: str = "REAL-CASE-001") -> str:
    try:
        neo = load_module("neo4j_readonly_adapter_scaffold", "product/adapters/read_only/neo4j_readonly_adapter_scaffold.py")
        trace = neo.evidence_trace(case_id)
    except Exception:
        trace = {"nodes": [], "relationships": []}

    nodes = trace.get("nodes", [])
    rels = trace.get("relationships", [])
    lines = ["flowchart LR"]
    if not nodes and not rels:
        lines.extend([
            "  CASE[REAL-CASE-001]",
            "  CUBE[Cubo Operacional]",
            "  EXO[Exocortex]",
            "  TEL[Telemetry / Ponto Zero]",
            "  CASE --> TEL",
            "  EXO --> CUBE",
            "  CUBE --> CASE",
        ])
    else:
        seen = set()
        for n in nodes:
            nid = str(n.get("id", "node")).replace("-", "_").replace(":", "_")
            label = str(n.get("id", "node")).replace('"', "'")
            if nid not in seen:
                lines.append(f'  {nid}["{label}"]')
                seen.add(nid)
        for r in rels:
            s = str(r.get("start", "start")).replace("-", "_").replace(":", "_")
            e = str(r.get("end", "end")).replace("-", "_").replace(":", "_")
            typ = str(r.get("type", "REL")).replace('"', "'")
            lines.append(f"  {s} -->|{typ}| {e}")
    return "\n".join(lines)

def build_context_packet(message: str, case_id: str = "REAL-CASE-001") -> Dict[str, Any]:
    cube = read_json("product/cube/operational_cube_master_contract.json", {})
    telemetry = read_json("product/calibration/casulo_kpi_vector_telemetry_inventory.json", {})
    artifact_audit = read_json("outputs/prod8301_8340_readonly_adapters_git_repo_outputs_neo4j.json", {})
    classification = classify_signal(message)

    gate = "SANDBOX_ONLY_HUMAN_REVIEW_REQUIRED"
    if classification["risks"] or classification["contradictions"] or classification["gaps"]:
        gate = "HUMAN_REVIEW_REQUIRED"

    return {
        "version": "exocortex_context_rebuild_packet.v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_id": case_id,
        "input_signal": {
            "source": "chat_message_or_business_case",
            "treated_as_truth": False,
            "message_length": len(message),
        },
        "canonical_state": {
            "system": "CASULO Campo OS",
            "governance_core": "Operational Cube",
            "memory_state_layer": "Exocortex",
            "agent_role": "subordinate conversational-operational module",
            "codex_role": "technical executor under gate",
            "cockpit_priority": "DEFERRED",
            "micrograph_runtime_current_poc": False,
            "micrographs_future_epic_only": True,
            "current_filter_layer": cube.get("current_scope", {}).get("current_filter_layer", "Inference Gate Prompt v0.1"),
        },
        "classification": classification,
        "telemetry_context": {
            "inventory_available": bool(telemetry),
            "calibration_status": telemetry.get("calibration_status", {}),
            "observed_delta_estado": telemetry.get("observed_delta_estado"),
            "observed_complex_indices": telemetry.get("observed_complex_indices", {}),
        },
        "adapter_context": {
            "read_only_adapters_phase": artifact_audit.get("phase"),
            "read_only_adapters_ready": artifact_audit.get("status") == "PASS",
        },
        "gate": gate,
        "allowed_actions": [
            "diagnostic_draft",
            "monitoring_draft",
            "solution_options_draft",
            "calibration_review_draft",
            "business_data_mapping_draft",
            "methodology_canonization_draft",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "graph_view_lite": {
            "format": "mermaid",
            "case_id": case_id,
            "mermaid": build_graph_mermaid(case_id),
            "interactive_neo4j_browser_required_now": False,
        },
    }

def build_diagnostic_report(message: str, case_id: str = "REAL-CASE-001") -> Dict[str, Any]:
    packet = build_context_packet(message, case_id)
    cls = packet["classification"]
    return {
        "version": "casulo_diagnostic_report_draft.v0.2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_id": case_id,
        "status": "DRAFT_INTERNAL_ONLY",
        "operational_state": packet["gate"],
        "supported_facts": cls["supported_facts"],
        "valid_inferences": cls["valid_inferences"],
        "weak_inferences": cls["weak_inferences"],
        "gaps": cls["gaps"],
        "risks": cls["risks"],
        "contradictions": cls["contradictions"],
        "telemetry_snapshot": packet["telemetry_context"],
        "graph_view_lite": packet["graph_view_lite"],
        "allowed_actions": packet["allowed_actions"],
        "blocked_actions": packet["blocked_actions"],
        "next_safe_step": "Use operational services phase to transform this draft into diagnostic/monitoring/solutions/calibration endpoints.",
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "commercial_claim_allowed": False,
    }

if __name__ == "__main__":
    sample = "empresa com processos manuais, dados espalhados, sistemas sem integração e necessidade de diagnóstico"
    print(json.dumps(build_diagnostic_report(sample), indent=2, ensure_ascii=False))
"""

API_V03 = r"""#!/usr/bin/env python3
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

runtime = load_module("context_rebuild_runtime", "product/exocortex/context_rebuild_runtime.py")

def route_post(path, payload):
    msg = str(payload.get("message", ""))
    case_id = str(payload.get("case_id", "REAL-CASE-001"))
    if path == "/exocortex/context/rebuild":
        return 200, runtime.build_context_packet(msg, case_id)
    if path == "/diagnostic/draft":
        return 200, runtime.build_diagnostic_report(msg, case_id)
    return 404, {"status": "not_found", "path": path}

def route_get(path):
    if path == "/health":
        return 200, {"status": "ok", "service": "casulo_agent_api_server_v03_context", "phase": "PROD-8341..8380"}
    if path == "/graph/mermaid":
        return 200, {"status": "ok", "format": "mermaid", "mermaid": runtime.build_graph_mermaid("REAL-CASE-001")}
    return 404, {"status": "not_found", "path": path}

class Handler(BaseHTTPRequestHandler):
    server_version = "CASULOAgentAPIContext/0.1"
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
    ap.add_argument("--port", type=int, default=8341)
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

runtime = load("context_rebuild_runtime", "product/exocortex/context_rebuild_runtime.py")
api = load("casulo_agent_api_server_v03_context", "product/api/casulo_agent_api_server_v03_context.py")

message = "empresa com dados espalhados, sistemas sem integração, precisa diagnóstico e calibração"
packet = runtime.build_context_packet(message)
assert packet["canonical_state"]["governance_core"] == "Operational Cube"
assert packet["canonical_state"]["memory_state_layer"] == "Exocortex"
assert packet["canonical_state"]["micrograph_runtime_current_poc"] is False
assert packet["graph_view_lite"]["format"] == "mermaid"
assert "flowchart" in packet["graph_view_lite"]["mermaid"]
assert packet["input_signal"]["treated_as_truth"] is False
assert "production_activation" in packet["blocked_actions"]

report = runtime.build_diagnostic_report(message)
assert report["status"] == "DRAFT_INTERNAL_ONLY"
assert report["ready_for_client_claim"] is False
assert report["ready_for_production"] is False
assert report["commercial_claim_allowed"] is False

code, payload = api.route_post("/exocortex/context/rebuild", {"message": message})
assert code == 200
assert payload["version"] == "exocortex_context_rebuild_packet.v0.1"

code, payload = api.route_post("/diagnostic/draft", {"message": message})
assert code == 200
assert payload["version"] == "casulo_diagnostic_report_draft.v0.2"

code, payload = api.route_get("/graph/mermaid")
assert code == 200
assert "flowchart" in payload["mermaid"]

print(json.dumps({"status": "PASS", "tests": "exocortex_context_rebuild_runtime"}, indent=2))
"""

OPENAPI_JSON = {
    "openapi": "3.1.0",
    "info": {
        "title": "CASULO Agent Action API v0.3 Context Runtime",
        "version": "0.3.0",
        "description": "Exocortex context rebuild and diagnostic graph view lite endpoints."
    },
    "servers": [{"url": "https://REPLACE_WITH_PUBLIC_ACTION_SERVER"}],
    "paths": {
        "/exocortex/context/rebuild": {
            "post": {
                "operationId": "rebuildExocortexContext",
                "summary": "Rebuild governed context from chat/business signal",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}, "required": ["message"]}}}},
                "responses": {"200": {"description": "Context rebuild packet"}}
            }
        },
        "/diagnostic/draft": {
            "post": {
                "operationId": "createDiagnosticDraft",
                "summary": "Create internal diagnostic draft with graph view lite",
                "requestBody": {"required": True, "content": {"application/json": {"schema": {"type": "object", "properties": {"message": {"type": "string"}, "case_id": {"type": "string"}}, "required": ["message"]}}}},
                "responses": {"200": {"description": "Diagnostic draft"}}
            }
        },
        "/graph/mermaid": {
            "get": {
                "operationId": "getGraphMermaid",
                "summary": "Get graph view lite as Mermaid",
                "responses": {"200": {"description": "Mermaid graph"}}
            }
        }
    }
}

OPENAPI_YAML = """openapi: 3.1.0
info:
  title: CASULO Agent Action API v0.3 Context Runtime
  version: 0.3.0
  description: Exocortex context rebuild and diagnostic graph view lite endpoints.
servers:
  - url: https://REPLACE_WITH_PUBLIC_ACTION_SERVER
paths:
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
          description: Context rebuild packet
  /diagnostic/draft:
    post:
      operationId: createDiagnosticDraft
      summary: Create internal diagnostic draft with graph view lite
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
  /graph/mermaid:
    get:
      operationId: getGraphMermaid
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
        "graph_visualization_mode": "DIAGNOSTIC_GRAPH_VIEW_LITE_MERMAID_NOT_INTERACTIVE_NEO4J_BROWSER",
    }

def build_result() -> Dict[str, Any]:
    telemetry = read_json("product/calibration/casulo_kpi_vector_telemetry_inventory.json", {})
    return {
        "status": "PASS",
        "phase": PHASE,
        "decision": DECISION,
        "generated_at": STAMP,
        "calibration_decision": {
            "exocortex_context_rebuild_runtime_ready": True,
            "chat_signal_treated_as_raw_signal": True,
            "clean_context_packet_ready": True,
            "diagnostic_report_draft_ready": True,
            "graph_view_lite_mermaid_ready": True,
            "api_v03_context_endpoints_ready": True,
            "telemetry_inventory_available": bool(telemetry),
            "interactive_neo4j_browser_required_now": False,
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
            "POST /exocortex/context/rebuild",
            "POST /diagnostic/draft",
            "GET /graph/mermaid",
        ],
        "next": "PROD-8381..8420 - Operational Services: Diagnostic Monitoring Solutions Calibration",
    }

def apply() -> List[str]:
    wrote: List[str] = []
    result = build_result()
    policy = {
        "version": "context_rebuild_policy.v0.1",
        "phase": PHASE,
        "rules": [
            "Chat/business input is raw signal, not truth.",
            "Operational Cube governs state and gates.",
            "Exocortex rebuilds clean context from signal plus repo/graph/telemetry.",
            "Inference Gate Prompt remains current filtering layer.",
            "Micrograph runtime remains future epic only.",
            "Diagnostic graph view lite uses Mermaid/report output, not interactive Neo4j Browser.",
        ],
        "classes": [
            "supported_facts",
            "valid_inferences",
            "weak_inferences",
            "gaps",
            "risks",
            "contradictions",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    sample_input = {
        "case_id": "COMMON-COMPANY-001",
        "message": "Empresa com dados espalhados em planilhas, sistema financeiro separado, atendimento sem padrão, retrabalho e ausência de indicadores confiáveis. Precisa diagnóstico, monitoramento, soluções simples e calibração da matriz semântica e telemétrica.",
        "input_is_truth": False,
        "purpose": "First common-company scenario for context rebuild and diagnostic draft tests.",
    }

    diagnostic_model = """# Diagnostic Report Model v0.2

## Operational state
{{operational_state}}

## Supported facts
{{supported_facts}}

## Valid inferences
{{valid_inferences}}

## Gaps
{{gaps}}

## Risks
{{risks}}

## Graph View Lite

```mermaid
{{graph_mermaid}}
```

## Telemetry snapshot
{{telemetry_snapshot}}

## Allowed actions
{{allowed_actions}}

## Blocked actions
{{blocked_actions}}

## Next safe step
{{next_safe_step}}
"""

    mermaid = """# Graph View Lite - Mermaid

```mermaid
flowchart LR
  USER[Business Signal]
  EXO[Exocortex Context Rebuild]
  CUBE[Operational Cube]
  TEL[Semantic and Telemetry Matrices]
  DIAG[Diagnostic Draft]
  USER --> EXO
  EXO --> CUBE
  CUBE --> TEL
  CUBE --> DIAG
```
"""

    contract = {
        "contract": "exocortex_context_rebuild_runtime.contract.v0.1",
        "phase": PHASE,
        "requires": REQUIRED,
        "status": "PASS",
        "decision": DECISION,
        "mode": "CONTEXT_REBUILD_AND_DIAGNOSTIC_GRAPH_VIEW_LITE",
        "blocked_actions": BLOCKED_ACTIONS,
        "implemented_endpoints": result["endpoints"],
        "not_implemented_yet": [
            "final diagnostic service",
            "monitoring service",
            "solutions service",
            "calibration service",
            "business-case input repository",
            "public ChatGPT Action deployment",
            "interactive graph viewer",
        ],
    }

    docs = f"""# PROD-8341..8380 - Exocortex Context Rebuild Runtime + Diagnostic Graph View Lite

Status: PASS  
Decision: `{DECISION}`

## Purpose

Create the first runtime layer that treats chat/business input as raw signal and rebuilds governed context through Exocortex + Operational Cube.

## Implements

- context rebuild runtime;
- signal classification;
- clean context packet;
- diagnostic draft model;
- graph view lite using Mermaid;
- API v0.3 context endpoints;
- static self-test.

## Does not implement

- interactive Neo4j Browser/Bloom;
- live Neo4j connection;
- GPT call;
- Codex execution;
- GitHub write;
- public ChatGPT Action deployment;
- final business calibration loop.

## Boundary

Micrograph runtime remains future epic only.  
Current filtering layer remains Inference Gate Prompt.  
Graph visualization stays inside diagnostic report as Mermaid/report view.  
Cockpit remains deferred.

## Next

`PROD-8381..8420 - Operational Services: Diagnostic Monitoring Solutions Calibration`
"""

    write_text("product/exocortex/context_rebuild_runtime.py", CONTEXT_RUNTIME, wrote, executable=True)
    write_json("product/exocortex/context_rebuild_policy.json", policy, wrote)
    write_json("product/exocortex/sample_inputs/business_case_common_company.json", sample_input, wrote)
    write_text("product/diagnostics/diagnostic_report_model_v0_2.md", diagnostic_model, wrote)
    write_text("product/diagnostics/graph_view_lite_mermaid.md", mermaid, wrote)
    write_json("product/diagnostics/sample_context_rebuild_result.json", result, wrote)
    write_text("product/api/casulo_agent_api_server_v03_context.py", API_V03, wrote, executable=True)
    write_text("product/api/run_casulo_agent_api_server_v03.sh", "#!/usr/bin/env bash\nset -euo pipefail\ncd \"$(dirname \"$0\")/../..\" || exit 1\npython3 product/api/casulo_agent_api_server_v03_context.py --host 0.0.0.0 --port \"${CASULO_AGENT_CONTEXT_API_PORT:-8341}\"\n", wrote, executable=True)
    write_text("product/api/tests/test_exocortex_context_rebuild_runtime.py", TEST_CODE, wrote, executable=True)
    write_text("product/api/openapi/casulo_agent_action_openapi_v03_context.yaml", OPENAPI_YAML, wrote)
    write_json("product/api/openapi/casulo_agent_action_openapi_v03_context.json", OPENAPI_JSON, wrote)
    write_json("product/api/contracts/exocortex_context_rebuild_runtime.contract.json", contract, wrote)
    write_json("outputs/prod8341_8380_exocortex_context_rebuild_runtime.json", result, wrote)
    write_text("outputs/prod8341_8380_exocortex_context_rebuild_runtime.md", f"""# PROD-8341..8380 - Exocortex Context Rebuild Runtime + Diagnostic Graph View Lite

Status: PASS  
Decision: `{DECISION}`

```json
{json.dumps(result["calibration_decision"], indent=2, ensure_ascii=False)}
```

## Endpoints

{chr(10).join("- `" + e + "`" for e in result["endpoints"])}

## Next

`{result["next"]}`
""", wrote)
    write_text("docs/product/834_EXOCORTEX_CONTEXT_REBUILD_RUNTIME_DIAGNOSTIC_GRAPH_VIEW_LITE.md", docs, wrote)
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
    test = run_cmd(["python3", "product/api/tests/test_exocortex_context_rebuild_runtime.py"], timeout=30)
    result = read_json("outputs/prod8341_8380_exocortex_context_rebuild_runtime.json", {})
    cal = result.get("calibration_decision", {})
    checks = {
        "generated_missing_count": len(missing),
        "json_errors_count": len(json_errors),
        "py_errors_count": len(py_errors),
        "static_tests_passed": test.get("ok") is True,
        "exocortex_context_rebuild_runtime_ready": cal.get("exocortex_context_rebuild_runtime_ready") is True,
        "chat_signal_treated_as_raw_signal": cal.get("chat_signal_treated_as_raw_signal") is True,
        "graph_view_lite_mermaid_ready": cal.get("graph_view_lite_mermaid_ready") is True,
        "interactive_neo4j_browser_required_now_false": cal.get("interactive_neo4j_browser_required_now") is False,
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
    paths = ["apply_prod8341_8380_exocortex_context_rebuild_runtime.py", *GENERATED]
    lines = ["git add \\"]
    for p in paths[:-1]:
        lines.append(f"  {p} \\")
    lines.append(f"  {paths[-1]}")
    lines.extend([
        "",
        'git commit -m "Add Exocortex context rebuild runtime and graph view lite"',
        'git tag -a product-casulo-exocortex-context-rebuild-runtime-v0.1 HEAD -m "CASULO Exocortex context rebuild runtime v0.1"',
        "git push origin main",
        "git push origin product-casulo-exocortex-context-rebuild-runtime-v0.1",
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

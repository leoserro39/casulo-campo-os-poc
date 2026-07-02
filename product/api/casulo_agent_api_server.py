#!/usr/bin/env python3
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

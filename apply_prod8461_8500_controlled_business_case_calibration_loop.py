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
PHASE = "PROD-8461..8500"
DECISION = "CONTROLLED_BUSINESS_CASE_CALIBRATION_LOOP_READY_FOR_INTERNAL_METHOD_CANONIZATION"

REQUIRED = [
    "outputs/prod8421_8460_chatgpt_agent_actions_integration_pack.json",
    "product/agent_integration/chatgpt_agent_action_manifest.json",
    "product/services/operational_services.py",
    "product/services/common_business_cases_v0_1.json",
    "product/services/semantic_matrix_v0_1.json",
    "product/services/telemetry_matrix_v0_1.json",
    "product/cube/operational_cube_master_contract.json",
]

GENERATED = [
    "product/calibration_loop/controlled_business_case_runner.py",
    "product/calibration_loop/business_case_suite_v0_1.json",
    "product/calibration_loop/calibration_review_policy.json",
    "product/calibration_loop/controlled_run_report_model.md",
    "product/calibration_loop/README.md",
    "product/api/casulo_agent_api_server_v06_calibration_loop.py",
    "product/api/run_casulo_agent_api_server_v06.sh",
    "product/api/tests/test_controlled_business_case_calibration_loop.py",
    "product/api/openapi/casulo_agent_action_openapi_v06_calibration_loop.yaml",
    "product/api/openapi/casulo_agent_action_openapi_v06_calibration_loop.json",
    "product/api/contracts/controlled_business_case_calibration_loop.contract.json",
    "outputs/prod8461_8500_controlled_business_case_calibration_loop.json",
    "outputs/prod8461_8500_controlled_business_case_calibration_loop.md",
    "docs/product/846_CONTROLLED_BUSINESS_CASE_CALIBRATION_LOOP.md",
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

RUNNER = r"""#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
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
    "threshold_lock_claim",
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

services = load_module("operational_services", "product/services/operational_services.py")

def load_cases() -> List[Dict[str, Any]]:
    suite = read_json("product/calibration_loop/business_case_suite_v0_1.json", {})
    if suite.get("cases"):
        return suite["cases"]
    base = read_json("product/services/common_business_cases_v0_1.json", {})
    return base.get("cases", [])

def run_case(case: Dict[str, Any]) -> Dict[str, Any]:
    case_id = case.get("case_id", "COMMON-COMPANY-UNKNOWN")
    message = case.get("message", "")
    diagnostic = services.diagnostic_service(message, case_id)
    monitoring = services.monitoring_service(message, case_id)
    solutions = services.solutions_service(message, case_id)
    calibration = services.calibration_service(message, case_id)
    scores = diagnostic.get("scores", {})
    return {
        "case_id": case_id,
        "title": case.get("title"),
        "status": "PASS_INTERNAL_DRAFT",
        "diagnostic": diagnostic,
        "monitoring": monitoring,
        "solutions": solutions,
        "calibration": calibration,
        "score_snapshot": scores,
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "commercial_claim_allowed": False,
    }

def summarize_runs(runs: List[Dict[str, Any]]) -> Dict[str, Any]:
    def avg(key: str) -> float:
        vals = [r.get("score_snapshot", {}).get(key) for r in runs if isinstance(r.get("score_snapshot", {}).get(key), (int, float))]
        return round(mean(vals), 4) if vals else 0.0

    risk_flags = []
    for r in runs:
        if r.get("score_snapshot", {}).get("ohri", 0) >= 0.25:
            risk_flags.append({"case_id": r.get("case_id"), "risk": "ohri_above_initial_internal_threshold"})
        if r.get("score_snapshot", {}).get("delta_estado", 0) >= 0.20:
            risk_flags.append({"case_id": r.get("case_id"), "risk": "delta_estado_above_initial_internal_threshold"})

    return {
        "case_count": len(runs),
        "avg_oqi": avg("oqi"),
        "avg_ohri": avg("ohri"),
        "avg_zpi": avg("zpi"),
        "avg_delta_estado": avg("delta_estado"),
        "risk_flags": risk_flags,
        "threshold_lock_ready": False,
        "method_canonization_ready_for_draft": True,
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "commercial_claim_allowed": False,
    }

def run_controlled_loop(max_cases: int | None = None) -> Dict[str, Any]:
    cases = load_cases()
    if max_cases is not None:
        cases = cases[:max_cases]
    runs = [run_case(c) for c in cases]
    summary = summarize_runs(runs)
    return {
        "version": "controlled_business_case_calibration_loop.v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "status": "PASS_INTERNAL_CONTROLLED_LOOP",
        "phase": "PROD-8461..8500",
        "mode": "INTERNAL_CONTROLLED_CASE_CALIBRATION",
        "runs": runs,
        "summary": summary,
        "blocked_actions": BLOCKED_ACTIONS,
        "next": "PROD-8501..8540 - CASULO Methodology Canonization and Data Mapping Playbook",
    }

def build_report_markdown(result: Dict[str, Any]) -> str:
    s = result.get("summary", {})
    lines = [
        "# Controlled Business Case Calibration Loop Report",
        "",
        f"Status: {result.get('status')}",
        f"Phase: {result.get('phase')}",
        "",
        "## Summary",
        "",
        f"- Cases: {s.get('case_count')}",
        f"- avg OQI: {s.get('avg_oqi')}",
        f"- avg OHRI: {s.get('avg_ohri')}",
        f"- avg ZPI: {s.get('avg_zpi')}",
        f"- avg Delta Estado: {s.get('avg_delta_estado')}",
        f"- threshold_lock_ready: {s.get('threshold_lock_ready')}",
        f"- method_canonization_ready_for_draft: {s.get('method_canonization_ready_for_draft')}",
        "",
        "## Case Runs",
        "",
    ]
    for r in result.get("runs", []):
        scores = r.get("score_snapshot", {})
        lines.extend([
            f"### {r.get('case_id')} - {r.get('title')}",
            "",
            f"- status: {r.get('status')}",
            f"- OQI: {scores.get('oqi')}",
            f"- OHRI: {scores.get('ohri')}",
            f"- ZPI: {scores.get('zpi')}",
            f"- Delta Estado: {scores.get('delta_estado')}",
            "- client claim: false",
            "- production: false",
            "",
        ])
    return "\n".join(lines) + "\n"

if __name__ == "__main__":
    print(json.dumps(run_controlled_loop(), indent=2, ensure_ascii=False))
"""

API_V06 = r"""#!/usr/bin/env python3
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

runner = load_module("controlled_business_case_runner", "product/calibration_loop/controlled_business_case_runner.py")

def route_get(path, query):
    if path == "/health":
        return 200, {
            "status": "ok",
            "service": "casulo_agent_api_server_v06_calibration_loop",
            "phase": "PROD-8461..8500",
            "writes_allowed": False,
        }
    if path == "/calibration-loop/cases":
        return 200, {"status": "ok", "cases": runner.load_cases(), "writes_allowed": False}
    return 404, {"status": "not_found", "path": path}

def route_post(path, payload):
    if path == "/calibration-loop/run":
        max_cases = payload.get("max_cases")
        if max_cases is not None:
            try:
                max_cases = int(max_cases)
            except Exception:
                max_cases = None
        return 200, runner.run_controlled_loop(max_cases=max_cases)
    return 404, {"status": "not_found", "path": path}

class Handler(BaseHTTPRequestHandler):
    server_version = "CASULOAgentAPICalibrationLoop/0.1"
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
    ap.add_argument("--port", type=int, default=8461)
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

runner = load("controlled_business_case_runner", "product/calibration_loop/controlled_business_case_runner.py")
api = load("casulo_agent_api_server_v06_calibration_loop", "product/api/casulo_agent_api_server_v06_calibration_loop.py")

cases = runner.load_cases()
assert len(cases) >= 3

result = runner.run_controlled_loop(max_cases=3)
assert result["status"] == "PASS_INTERNAL_CONTROLLED_LOOP"
assert result["summary"]["case_count"] == 3
assert result["summary"]["threshold_lock_ready"] is False
assert result["summary"]["ready_for_client_claim"] is False
assert result["summary"]["ready_for_production"] is False

for run in result["runs"]:
    assert run["ready_for_client_claim"] is False
    assert run["ready_for_production"] is False
    assert run["commercial_claim_allowed"] is False
    assert "oqi" in run["score_snapshot"]

md = runner.build_report_markdown(result)
assert "Controlled Business Case Calibration Loop Report" in md
assert "threshold_lock_ready: False" in md

code, payload = api.route_get("/calibration-loop/cases", {})
assert code == 200
assert len(payload["cases"]) >= 3

code, payload = api.route_post("/calibration-loop/run", {"max_cases": 2})
assert code == 200
assert payload["summary"]["case_count"] == 2
assert payload["summary"]["threshold_lock_ready"] is False

print(json.dumps({"status": "PASS", "tests": "controlled_business_case_calibration_loop"}, indent=2))
"""

OPENAPI_JSON = {
    "openapi": "3.1.0",
    "info": {
        "title": "CASULO Controlled Business Case Calibration Loop API",
        "version": "0.6.0",
        "description": "Internal controlled calibration loop over common business cases. No production or client claim."
    },
    "servers": [{"url": "https://REPLACE_WITH_PUBLIC_ACTION_SERVER"}],
    "paths": {
        "/health": {
            "get": {
                "operationId": "getCalibrationLoopHealth",
                "summary": "Check calibration loop API health",
                "responses": {"200": {"description": "Health"}}
            }
        },
        "/calibration-loop/cases": {
            "get": {
                "operationId": "listControlledBusinessCases",
                "summary": "List internal controlled business cases",
                "responses": {"200": {"description": "Case list"}}
            }
        },
        "/calibration-loop/run": {
            "post": {
                "operationId": "runControlledCalibrationLoop",
                "summary": "Run internal controlled calibration loop",
                "requestBody": {"required": False, "content": {"application/json": {"schema": {"type": "object", "properties": {"max_cases": {"type": "integer"}}}}}},
                "responses": {"200": {"description": "Calibration loop result"}}
            }
        }
    }
}

OPENAPI_YAML = """openapi: 3.1.0
info:
  title: CASULO Controlled Business Case Calibration Loop API
  version: 0.6.0
  description: Internal controlled calibration loop over common business cases. No production or client claim.
servers:
  - url: https://REPLACE_WITH_PUBLIC_ACTION_SERVER
paths:
  /health:
    get:
      operationId: getCalibrationLoopHealth
      summary: Check calibration loop API health
      responses:
        '200':
          description: Health
  /calibration-loop/cases:
    get:
      operationId: listControlledBusinessCases
      summary: List internal controlled business cases
      responses:
        '200':
          description: Case list
  /calibration-loop/run:
    post:
      operationId: runControlledCalibrationLoop
      summary: Run internal controlled calibration loop
      requestBody:
        required: false
        content:
          application/json:
            schema:
              type: object
              properties:
                max_cases:
                  type: integer
      responses:
        '200':
          description: Calibration loop result
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
        "controlled_business_case_loop": True,
    }

def build_result() -> Dict[str, Any]:
    return {
        "status": "PASS",
        "phase": PHASE,
        "decision": DECISION,
        "generated_at": STAMP,
        "calibration_decision": {
            "controlled_case_runner_ready": True,
            "business_case_suite_ready": True,
            "calibration_review_policy_ready": True,
            "controlled_report_model_ready": True,
            "api_v06_calibration_loop_ready": True,
            "method_canonization_ready_for_draft": True,
            "threshold_lock_ready": False,
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
            "micrograph_runtime_current_poc": False,
            "cockpit_priority": "DEFERRED",
        },
        "endpoints": [
            "GET /calibration-loop/cases",
            "POST /calibration-loop/run",
        ],
        "next": "PROD-8501..8540 - CASULO Methodology Canonization and Data Mapping Playbook",
    }

def apply() -> List[str]:
    wrote: List[str] = []
    result = build_result()

    suite = {
        "version": "business_case_suite.v0.1",
        "phase": PHASE,
        "purpose": "Seed controlled business cases for CASULO internal calibration.",
        "cases": [
            {
                "case_id": "COMMON-COMPANY-001",
                "title": "Scattered data and rework",
                "message": "Company with data spread across spreadsheets, separate financial system, inconsistent customer service, rework and no reliable indicators.",
                "expected_domains": ["data_mapping", "process_mapping", "evidence_quality"],
            },
            {
                "case_id": "COMMON-COMPANY-002",
                "title": "Critical systems with unmapped integrations",
                "message": "Medium company with critical systems, poorly mapped integrations, manual changes and no formal rollback.",
                "expected_domains": ["systems_integration", "operational_risk", "governance"],
            },
            {
                "case_id": "COMMON-COMPANY-003",
                "title": "Multi-channel service without operational state",
                "message": "Company with multi-channel service, inconsistent records, no process owner and decisions based on informal memory.",
                "expected_domains": ["process_mapping", "monitoring", "governance"],
            },
            {
                "case_id": "COMMON-COMPANY-004",
                "title": "Owner-managed business with informal controls",
                "message": "Small business controlled by owner memory, suppliers in messages, stock in spreadsheet and no computable operational state.",
                "expected_domains": ["data_mapping", "solution_design", "monitoring"],
            },
            {
                "case_id": "COMMON-COMPANY-005",
                "title": "Department with dashboards but no state governance",
                "message": "Department has dashboards and reports, but no gate, no evidence boundary, no clear owner and no action trace.",
                "expected_domains": ["operational_risk", "evidence_quality", "governance"],
            },
        ],
    }

    policy = {
        "version": "calibration_review_policy.v0.1",
        "phase": PHASE,
        "rules": [
            "All cases are internal controlled tests.",
            "Scores are calibration signals, not validated performance claims.",
            "Threshold lock is explicitly false.",
            "Client, production and commercial claims remain blocked.",
            "Use outputs to draft methodology canonization and data mapping playbook.",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
        "minimum_case_count_before_threshold_lock_candidate": 20,
        "current_case_count": len(suite["cases"]),
        "threshold_lock_ready": False,
    }

    report_model = """# Controlled Business Case Calibration Loop Report Model

## Summary

- Case count:
- avg OQI:
- avg OHRI:
- avg ZPI:
- avg Delta Estado:
- threshold_lock_ready:
- method_canonization_ready_for_draft:

## Cases

For each case:

- case_id
- title
- diagnostic status
- monitoring status
- solutions status
- calibration status
- score snapshot
- blocked actions
- next safe step

## Boundary

This report is internal only. It is not a client claim, not production validation and not commercial proof.
"""

    contract = {
        "contract": "controlled_business_case_calibration_loop.contract.v0.1",
        "phase": PHASE,
        "requires": REQUIRED,
        "status": "PASS",
        "decision": DECISION,
        "mode": "INTERNAL_CONTROLLED_BUSINESS_CASE_CALIBRATION_LOOP",
        "implemented_endpoints": result["endpoints"],
        "blocked_actions": BLOCKED_ACTIONS,
        "not_implemented_yet": [
            "threshold lock",
            "validated client claim",
            "production deployment",
            "methodology canonization final document",
            "data mapping playbook final document",
        ],
    }

    readme = """# Controlled Business Case Calibration Loop v0.1

Internal controlled calibration loop for common company cases.

## Test

```bash
python3 product/api/tests/test_controlled_business_case_calibration_loop.py
```

## Run

```bash
python3 product/calibration_loop/controlled_business_case_runner.py
```

## API

```bash
python3 product/api/casulo_agent_api_server_v06_calibration_loop.py --host 0.0.0.0 --port 8461
```

No production. No client claim. No commercial claim. No threshold lock.
"""

    docs = f"""# PROD-8461..8500 - Controlled Business Case Calibration Loop

Status: PASS  
Decision: `{DECISION}`

## Purpose

Run controlled internal calibration across common business cases using CASULO operational services.

## Implements

- controlled business case runner;
- business case suite v0.1;
- calibration review policy;
- controlled run report model;
- API v0.6 for cases and loop execution;
- static self-test.

## Does not implement

- threshold lock;
- client-facing claim;
- production activation;
- commercial proof;
- final methodology canonization.

## Next

`PROD-8501..8540 - CASULO Methodology Canonization and Data Mapping Playbook`
"""

    out_md = f"""# PROD-8461..8500 - Controlled Business Case Calibration Loop

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

    write_text("product/calibration_loop/controlled_business_case_runner.py", RUNNER, wrote, executable=True)
    write_json("product/calibration_loop/business_case_suite_v0_1.json", suite, wrote)
    write_json("product/calibration_loop/calibration_review_policy.json", policy, wrote)
    write_text("product/calibration_loop/controlled_run_report_model.md", report_model, wrote)
    write_text("product/calibration_loop/README.md", readme, wrote)
    write_text("product/api/casulo_agent_api_server_v06_calibration_loop.py", API_V06, wrote, executable=True)
    write_text("product/api/run_casulo_agent_api_server_v06.sh", "#!/usr/bin/env bash\nset -euo pipefail\ncd \"$(dirname \"$0\")/../..\" || exit 1\npython3 product/api/casulo_agent_api_server_v06_calibration_loop.py --host 0.0.0.0 --port \"${CASULO_AGENT_CALIBRATION_LOOP_API_PORT:-8461}\"\n", wrote, executable=True)
    write_text("product/api/tests/test_controlled_business_case_calibration_loop.py", TEST_CODE, wrote, executable=True)
    write_text("product/api/openapi/casulo_agent_action_openapi_v06_calibration_loop.yaml", OPENAPI_YAML, wrote)
    write_json("product/api/openapi/casulo_agent_action_openapi_v06_calibration_loop.json", OPENAPI_JSON, wrote)
    write_json("product/api/contracts/controlled_business_case_calibration_loop.contract.json", contract, wrote)
    write_json("outputs/prod8461_8500_controlled_business_case_calibration_loop.json", result, wrote)
    write_text("outputs/prod8461_8500_controlled_business_case_calibration_loop.md", out_md, wrote)
    write_text("docs/product/846_CONTROLLED_BUSINESS_CASE_CALIBRATION_LOOP.md", docs, wrote)
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
    test = run_cmd(["python3", "product/api/tests/test_controlled_business_case_calibration_loop.py"], timeout=30)
    result = read_json("outputs/prod8461_8500_controlled_business_case_calibration_loop.json", {})
    cal = result.get("calibration_decision", {})
    checks = {
        "generated_missing_count": len(missing),
        "json_errors_count": len(json_errors),
        "py_errors_count": len(py_errors),
        "static_tests_passed": test.get("ok") is True,
        "controlled_case_runner_ready": cal.get("controlled_case_runner_ready") is True,
        "business_case_suite_ready": cal.get("business_case_suite_ready") is True,
        "calibration_review_policy_ready": cal.get("calibration_review_policy_ready") is True,
        "method_canonization_ready_for_draft": cal.get("method_canonization_ready_for_draft") is True,
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
    paths = ["apply_prod8461_8500_controlled_business_case_calibration_loop.py", *GENERATED]
    lines = ["git add \\"]
    for p in paths[:-1]:
        lines.append(f"  {p} \\")
    lines.append(f"  {paths[-1]}")
    lines.extend([
        "",
        'git commit -m "Add controlled business case calibration loop"',
        'git tag -a product-casulo-controlled-business-case-calibration-loop-v0.1 HEAD -m "CASULO controlled business case calibration loop v0.1"',
        "git push origin main",
        "git push origin product-casulo-controlled-business-case-calibration-loop-v0.1",
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

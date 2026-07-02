#!/usr/bin/env python3
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

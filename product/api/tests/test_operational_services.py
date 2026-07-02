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

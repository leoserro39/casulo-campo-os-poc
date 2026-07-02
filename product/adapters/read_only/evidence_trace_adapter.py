#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

TRACE_FILES = [
    "outputs/prod7061_7260_casulo_macro_foundation.json",
    "outputs/prod7301_7340_ponto_zero_vector_telemetry.json",
    "outputs/prod7341_7380_graph_retrieval_gain_multirun_calibration.json",
    "outputs/prod8221_8260_operational_cube_master_contract_agent_readiness_audit.json",
    "outputs/prod8261_8300_casulo_agent_api_server_action_scaffold.json",
    "product/calibration/casulo_kpi_vector_telemetry_inventory.json",
    "product/cube/operational_cube_master_contract.json",
]

def read_json(path: str, default=None):
    p = ROOT / path
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def evidence_trace(case_id="REAL-CASE-001"):
    files = []
    for p in TRACE_FILES:
        data = read_json(p, {})
        if not data:
            continue
        payload_text = json.dumps(data, ensure_ascii=False)
        files.append({
            "path": p,
            "status": data.get("status"),
            "phase": data.get("phase"),
            "decision": data.get("decision"),
            "mentions_case": case_id in payload_text,
            "ready_for_client_claim": data.get("calibration_decision", {}).get("ready_for_client_claim", False),
            "ready_for_production": data.get("calibration_decision", {}).get("ready_for_production", False),
        })
    return {
        "adapter": "evidence_trace_adapter.v0.1",
        "case_id": case_id,
        "trace_files_count": len(files),
        "trace_files": files,
        "gate": "SANDBOX_ONLY_READ_ONLY_TRACE",
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "writes_allowed": False,
    }

if __name__ == "__main__":
    print(json.dumps(evidence_trace(), indent=2, ensure_ascii=False))

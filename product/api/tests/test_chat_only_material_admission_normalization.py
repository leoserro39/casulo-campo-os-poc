#!/usr/bin/env python3
from __future__ import annotations

import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

def load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / rel)
    mod = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(mod)
    return mod

materials = load("material_admission_runtime", "product/materials/material_admission_runtime.py")
api = load("unified_api", "product/api/casulo_agent_api_server_v07_unified_agent.py")

chat = "Documento de evidência: empresa com dados espalhados, sistemas sem integração e rollback ausente."

packet = materials.admit_material(chat, source_type="chat_message", domain_candidate="enterprise_it_operations")

assert packet["raw_signal_treated_as_truth"] is False
assert packet["material"]["source_authority"] == "UNVERIFIED_USER_SIGNAL"
assert packet["material"]["material_class"] == "INFERENCE", packet["material"]
assert packet["material"]["material_subtype"] == "INFERENCE/unverified_chat_signal", packet["material"]
assert packet["material"]["evidence_boundary_applied"] == "CHAT_ONLY_UNVERIFIED_SIGNAL"
assert packet["material"]["chat_only_evidence_downgraded"] is True
assert packet["dimensions"]["evidence_density"] <= 0.08, packet["dimensions"]
assert packet["dimensions"]["confidence"] <= 0.05, packet["dimensions"]
assert packet["dimensions"]["traceability"] <= 0.25, packet["dimensions"]
assert packet["admission"]["admission_decision"] == "ADMIT_AS_INFERENCE", packet["admission"]
assert packet["admission"]["can_support_claim"] is False
assert packet["admission"]["can_trigger_action"] is False
assert packet["admission"]["ready_for_client_claim"] is False
assert packet["admission"]["ready_for_production"] is False
assert packet["admission"]["commercial_claim_allowed"] is False
assert packet["claim_evidence_action_boundary"]["chat_only_input_is_not_documentary_evidence"] is True

code, gate = api.route_post("/materials/gate", {
    "message": chat,
    "source_type": "chat_message",
    "domain_candidate": "enterprise_it_operations",
})
assert code == 200
assert gate["admission_decision"] == "ADMIT_AS_INFERENCE", gate
assert gate["can_support_claim"] is False, gate

code, diag = api.route_post("/agent/diagnostic", {
    "message": chat,
    "case_id": "CHAT-ONLY-RETEST-001",
    "domain_candidate": "enterprise_it_operations",
})
assert code == 200
assert diag["material_admission"]["material"]["material_class"] == "INFERENCE"
assert diag["material_admission"]["admission"]["can_support_claim"] is False
assert diag["ready_for_client_claim"] is False
assert diag["ready_for_production"] is False
assert diag["commercial_claim_allowed"] is False

cp = subprocess.run([
    "python3",
    "-m",
    "py_compile",
    str(ROOT / "product/materials/material_admission_runtime.py"),
    str(ROOT / "product/api/casulo_agent_api_server_v07_unified_agent.py"),
], cwd=ROOT, text=True, capture_output=True, timeout=30)
assert cp.returncode == 0, cp.stderr

print(json.dumps({
    "status": "PASS",
    "tests": "chat_only_material_admission_normalization"
}, indent=2))

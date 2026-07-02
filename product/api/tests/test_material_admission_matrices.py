#!/usr/bin/env python3
from __future__ import annotations
import importlib.util, json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[3]
def load(name,path):
    spec=importlib.util.spec_from_file_location(name,ROOT/path); mod=importlib.util.module_from_spec(spec); assert spec and spec.loader; spec.loader.exec_module(mod); return mod
taxonomy=json.loads((ROOT/"product/materials/material_taxonomy_matrix_v0_1.json").read_text(encoding="utf-8"))
dims=json.loads((ROOT/"product/materials/material_dimensional_matrix_v0_1.json").read_text(encoding="utf-8"))
gate=json.loads((ROOT/"product/materials/material_admission_gate_matrix_v0_1.json").read_text(encoding="utf-8"))
assert len(taxonomy["material_classes"])==10
assert len(dims["dimensions"])==12
assert gate["rules"]["inference_is_not_evidence"] is True
runtime=load("material_admission_runtime","product/materials/material_admission_runtime.py")
api=load("casulo_agent_api_server_v07_materials","product/api/casulo_agent_api_server_v07_materials.py")
packet=runtime.admit_material("Empresa com rollback ausente e proposta de automatizar em producao.","chat_message","TIC_SI")
assert packet["raw_signal_treated_as_truth"] is False
assert packet["admission"]["micrograph_runtime_current_poc"] is False
assert packet["admission"]["ready_for_client_claim"] is False
assert packet["claim_evidence_action_boundary"]["inference_is_not_evidence"] is True
code,payload=api.route_get("/materials/taxonomy",{})
assert code==200 and "EVIDENCE" in payload["material_classes"]
code,payload=api.route_post("/materials/admit",{"message":"KPI 92% mas sem rastreabilidade"})
assert code==200 and payload["admission"]["ready_for_production"] is False
print(json.dumps({"status":"PASS","tests":"material_admission_matrices"},indent=2))

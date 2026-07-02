#!/usr/bin/env python3
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

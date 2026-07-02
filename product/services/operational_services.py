#!/usr/bin/env python3
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

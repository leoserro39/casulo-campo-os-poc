#!/usr/bin/env python3
"""
CASULO PROD-8221..8260
Operational Cube Master Contract and ChatGPT Agent Readiness Audit

This patch intentionally stops the drift:
- no ExoCodex;
- no cockpit-first roadmap;
- no micrograph runtime in the current POC;
- current POC keeps Inference Gate as prompt/filtering layer;
- Operational Cube is the governance core;
- Exocortex is memory/state/context reconstruction layer;
- CASULO Agent is a subordinate conversational/operational module;
- Codex is a technical executor only under gate.

This patch scans the local repository, git timeline, outputs, docs, telemetry,
vectors, calibration files and known generated artifacts. It creates one
master audit/contract package to reconcile the current repo with the intended
CASULO model.

Usage:
  python3 apply_prod8221_8260_operational_cube_master_contract_agent_readiness_audit.py --check
  python3 apply_prod8221_8260_operational_cube_master_contract_agent_readiness_audit.py --apply --cleanup-wrong-8221 --self-test --commit-plan

This patch does not call GPT, Codex, Neo4j, GitHub writes or external APIs.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Tuple

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()
PHASE = "PROD-8221..8260"
DECISION_PASS = "OPERATIONAL_CUBE_MASTER_CONTRACT_AND_CHATGPT_AGENT_READINESS_AUDIT_READY"

CORE_REQUIRED = [
    "docs/product/678_CASULO_CANONICAL_ARCHITECTURE_AND_TELEMETRY_MAP.md",
    "outputs/prod7061_7260_casulo_macro_foundation.json",
    "outputs/prod7301_7340_ponto_zero_vector_telemetry.json",
    "outputs/prod7341_7380_graph_retrieval_gain_multirun_calibration.json",
    "product/exocortex/prod8061a_exocortex_foundation_statement.json",
    "outputs/prod8061a_exocortex_foundation_statement_addendum.json",
    "outputs/prod8101_8140_internal_demo_script_agent_instruction_pack.json",
    "outputs/prod8181_8220_cockpit_chat_scaffold_diagnostic_monitor.json",
]

OPTIONAL_EXPECTED = [
    "product/agents/casulo_github_native_agent.py",
    "product/scripts/score_agent_output_delta_zero.py",
    "product/scripts/score_agent_run_vector_v2.py",
    ".github/workflows/casulo_agent_real_case_001.yml",
    ".github/workflows/casulo_agent_multirun_calibration.yml",
    "product/graph/neo4j_payloads/real_case_001_nodes_v0_1.json",
    "product/graph/neo4j_payloads/real_case_001_relationships_v0_1.json",
    "product/calibration/batches/prod7341_7380_multi_run_calibration_batch.json",
]

WRONG_8221_LOCAL = [
    "apply_prod8221_8260_agent_core_runtime_telemetry_harness.py",
    "product/agent_runtime",
    "outputs/prod8221_8260_agent_core_runtime_telemetry_harness.json",
    "outputs/prod8221_8260_agent_core_runtime_telemetry_harness.md",
    "docs/product/822_AGENT_CORE_RUNTIME_TELEMETRY_HARNESS.md",
]

GENERATED = [
    "product/cube/operational_cube_master_contract.json",
    "product/cube/operational_cube_master_contract.md",
    "product/agent_manifest/chatgpt_agent_readiness_manifest.json",
    "product/agent_manifest/chatgpt_agent_instructions.md",
    "product/agent_manifest/chatgpt_agent_knowledge_pack.md",
    "product/actions/casulo_chatgpt_action_requirements.json",
    "product/actions/casulo_chatgpt_action_requirements.md",
    "product/memory/chat_memory_boundary_context_rebuild_gate.contract.json",
    "product/calibration/casulo_kpi_vector_telemetry_inventory.json",
    "product/audits/prod8221_8260_integrated_repo_timeline_audit.json",
    "product/supersession/prod8221_wrong_agent_core_runtime_supersession.json",
    "outputs/prod8221_8260_operational_cube_master_contract_agent_readiness_audit.json",
    "outputs/prod8221_8260_operational_cube_master_contract_agent_readiness_audit.md",
    "docs/product/822_OPERATIONAL_CUBE_MASTER_CONTRACT_AGENT_READINESS_AUDIT.md",
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

TERMS = [
    "CASULO", "Campo OS", "Cubo", "Cubo Operacional", "operational cube",
    "Exocortex", "memory", "memoria", "cache", "graph memory",
    "Inference Gate", "Delta Zero", "Ponto Zero", "Return Delta",
    "telemetry", "telemetria", "vector", "vetor", "V_estado", "Delta_estado",
    "OQI", "OHRI", "ZPI", "evidence_density", "gate_alignment",
    "Neo4j", "GitHub Native Agent", "Agent", "Codex", "cockpit",
    "Solution Factory", "Operacao Assistida", "micrograph", "micrografo",
    "Delta Matrix", "matriz de delta", "multi-LLM", "familia de estados",
    "production_activation", "client_facing_validated_claim", "commercial_claim",
]

TEXT_SUFFIXES = {
    ".py", ".md", ".json", ".yaml", ".yml", ".txt", ".cypher", ".csv", ".toml"
}

EXCLUDED_DIR_PARTS = {
    ".git", "__pycache__", ".venv", "node_modules", "exports", "tmp",
}

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

def rel(path: Path) -> str:
    return str(path.relative_to(ROOT)).replace("\\", "/")

def path_exists(path: str) -> bool:
    return (ROOT / path).exists()

def read_text(path: str) -> str:
    p = ROOT / path
    return p.read_text(encoding="utf-8", errors="replace") if p.exists() else ""

def read_json(path: str, default: Any = None) -> Any:
    p = ROOT / path
    if not p.exists():
        return default
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return default

def write_text(path: str, text: str, wrote: List[str]) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    wrote.append(path)

def write_json(path: str, data: Any, wrote: List[str]) -> None:
    write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n", wrote)

def is_text_candidate(path: Path) -> bool:
    if any(part in EXCLUDED_DIR_PARTS for part in path.parts):
        return False
    if path.suffix.lower() not in TEXT_SUFFIXES:
        return False
    try:
        if path.stat().st_size > 2_500_000:
            return False
    except OSError:
        return False
    return True

def scan_repository() -> Dict[str, Any]:
    file_count = 0
    scanned_count = 0
    term_counts = Counter()
    term_files: Dict[str, List[str]] = defaultdict(list)
    file_hits: Dict[str, Dict[str, int]] = {}

    for p in ROOT.rglob("*"):
        if p.is_file():
            file_count += 1
        if not p.is_file() or not is_text_candidate(p):
            continue
        scanned_count += 1
        text = p.read_text(encoding="utf-8", errors="replace")
        low = text.lower()
        hits = {}
        for term in TERMS:
            c = low.count(term.lower())
            if c:
                hits[term] = c
                term_counts[term] += c
                if len(term_files[term]) < 40:
                    term_files[term].append(rel(p))
        if hits:
            file_hits[rel(p)] = hits

    return {
        "file_count_total": file_count,
        "text_files_scanned": scanned_count,
        "term_counts": dict(term_counts),
        "term_files_sample": {k: v for k, v in term_files.items()},
        "files_with_term_hits_count": len(file_hits),
        "files_with_term_hits_sample": dict(list(file_hits.items())[:80]),
    }

def timeline_from_git() -> Dict[str, Any]:
    log = run_cmd([
        "git", "log", "--all", "--decorate", "--date=iso", "--pretty=format:%h%x09%H%x09%ad%x09%s", "-n", "250"
    ])
    commits = []
    for line in log.get("stdout", "").splitlines():
        parts = line.split("\t", 3)
        if len(parts) == 4:
            commits.append({
                "short": parts[0],
                "sha": parts[1],
                "date": parts[2],
                "message": parts[3],
            })
    return {
        "git_log_ok": log.get("ok", False),
        "commit_count_sample": len(commits),
        "commits": commits,
        "head": run_cmd(["git", "rev-parse", "--short", "HEAD"]),
        "status_short": run_cmd(["git", "status", "--short"]),
        "tags_at_head": run_cmd(["git", "tag", "--points-at", "HEAD"]),
        "all_tags_sample": run_cmd(["git", "tag", "--list"]),
    }

def classify_key_artifacts() -> Dict[str, Any]:
    macro = read_json("outputs/prod7061_7260_casulo_macro_foundation.json", {})
    ponto = read_json("outputs/prod7301_7340_ponto_zero_vector_telemetry.json", {})
    graph = read_json("outputs/prod7341_7380_graph_retrieval_gain_multirun_calibration.json", {})
    exo = read_json("product/exocortex/prod8061a_exocortex_foundation_statement.json", {})
    agent_pack = read_json("outputs/prod8101_8140_internal_demo_script_agent_instruction_pack.json", {})
    cockpit = read_json("outputs/prod8181_8220_cockpit_chat_scaffold_diagnostic_monitor.json", {})

    return {
        "macro_foundation": {
            "present": bool(macro),
            "status": macro.get("status"),
            "decision": macro.get("decision"),
            "blocked_actions": macro.get("blocked_actions", []),
            "classification": "ARTIFACT_READY" if macro.get("status") == "PASS" else "MISSING_OR_INCOMPLETE",
        },
        "ponto_zero_vector_telemetry": {
            "present": bool(ponto),
            "status": ponto.get("status"),
            "decision": ponto.get("decision"),
            "llm_executed": ponto.get("llm_executed"),
            "delta_estado": ponto.get("vector_telemetry", {}).get("delta_estado"),
            "oqi_v2": ponto.get("complex_indices", {}).get("oqi_v2"),
            "ohri_v2": ponto.get("complex_indices", {}).get("ohri_v2"),
            "zpi_v2": ponto.get("complex_indices", {}).get("zpi_v2"),
            "ready_for_threshold_lock": ponto.get("calibration_decision", {}).get("ready_for_threshold_lock"),
            "classification": "SANDBOX_TESTED_SINGLE_RUN" if ponto.get("status") == "PASS" else "MISSING_OR_INCOMPLETE",
        },
        "graph_retrieval_gain": {
            "present": bool(graph),
            "status": graph.get("status"),
            "decision": graph.get("decision"),
            "evaluation_mode": graph.get("graph_retrieval_gain", {}).get("evaluation_mode"),
            "neo4j_live_query_executed": graph.get("graph_retrieval_gain", {}).get("neo4j_live_query_executed"),
            "retrieval_gain_proxy": graph.get("graph_retrieval_gain", {}).get("retrieval_gain_proxy"),
            "ready_for_live_neo4j_retrieval": graph.get("calibration_decision", {}).get("ready_for_live_neo4j_retrieval"),
            "classification": "OFFLINE_GRAPH_PROXY_READY" if graph.get("status") == "PASS" else "MISSING_OR_INCOMPLETE",
        },
        "exocortex_foundation": {
            "present": bool(exo),
            "status": exo.get("status"),
            "decision": exo.get("decision"),
            "what_is_not_implemented_yet": exo.get("what_is_not_implemented_yet", {}),
            "classification": "FOUNDATION_ARTIFACT_READY_NOT_FULL_RUNTIME" if exo.get("status") == "PASS" else "MISSING_OR_INCOMPLETE",
        },
        "agent_instruction_pack": {
            "present": bool(agent_pack),
            "status": agent_pack.get("status"),
            "decision": agent_pack.get("decision"),
            "diagnostic_report_model_ready": agent_pack.get("calibration_decision", {}).get("diagnostic_report_model_ready"),
            "monitoring_summary_model_ready": agent_pack.get("calibration_decision", {}).get("monitoring_summary_model_ready"),
            "simple_solution_recommendation_model_ready": agent_pack.get("calibration_decision", {}).get("simple_solution_recommendation_model_ready"),
            "classification": "CHAT_BEHAVIOR_SCAFFOLD_READY" if agent_pack.get("status") == "PASS" else "MISSING_OR_INCOMPLETE",
        },
        "cockpit_static": {
            "present": bool(cockpit),
            "status": cockpit.get("status"),
            "decision": cockpit.get("decision"),
            "live_gpt_integrated": cockpit.get("calibration_decision", {}).get("live_gpt_integrated"),
            "neo4j_write_integrated": cockpit.get("calibration_decision", {}).get("neo4j_write_integrated"),
            "classification": "SURFACE_ONLY_DEFERRED" if cockpit.get("status") == "PASS" else "MISSING_OR_INCOMPLETE",
        },
    }

def readiness_matrix() -> Dict[str, Any]:
    artifacts = classify_key_artifacts()
    return {
        "operational_cube": {
            "role": "PRIMARY_GOVERNANCE_CORE",
            "status_after_patch": "MASTER_CONTRACT_CREATED",
            "current_scope": "governance, state triage, gate, allowed/blocked actions",
            "not_a_module": True,
        },
        "exocortex": {
            "role": "MEMORY_STATE_CONTEXT_RECONSTRUCTION_LAYER",
            "status_from_repo": artifacts["exocortex_foundation"]["classification"],
            "full_runtime_complete": False,
        },
        "casulo_agent_chatgpt": {
            "role": "SUBORDINATE_CONVERSATIONAL_OPERATIONAL_MODULE",
            "status": "MANIFEST_READY_AFTER_PATCH_API_NOT_IMPLEMENTED",
            "requires_next": [
                "CASULO Action/API server",
                "Neo4j read-only adapter",
                "GitHub read-only adapter",
                "Context rebuild endpoint",
                "Telemetry/calibration endpoint",
            ],
        },
        "codex": {
            "role": "TECHNICAL_EXECUTOR_UNDER_GATE",
            "status": "NOT_ENABLED_FOR_AUTONOMOUS_EXECUTION",
            "automatic_merge_allowed": False,
        },
        "cockpit": {
            "role": "OPTIONAL_SURFACE_DEFERRED",
            "status_from_repo": artifacts["cockpit_static"]["classification"],
            "priority_now": "DEFERRED",
        },
        "inference_gate": {
            "role": "CURRENT_FILTERING_LAYER",
            "current_implementation": "PROMPT_LAYER_V0_1",
            "schema_runtime_required_next": True,
        },
        "micrographs": {
            "role": "FUTURE_EPIC_NOT_CURRENT_SCOPE",
            "current_runtime_implemented": False,
            "current_poc_allowed": "conceptual references and future roadmap only",
        },
        "delta_matrix": {
            "role": "CALIBRATION_AND_DECISION_DISTANCE_LAYER",
            "current_state": "partial via vector telemetry, Ponto Zero, Delta Estado and graph retrieval proxy",
            "full_runtime_implemented": False,
        },
        "telemetry_and_kpis": {
            "role": "MEASUREMENT_LAYER",
            "current_state": "T1-T7 registered; OQI/OHRI/ZPI and vector telemetry present; multi-run threshold lock incomplete",
            "ready_for_client_claim": False,
        },
    }

def generated_master_contract(audit: Dict[str, Any]) -> Dict[str, Any]:
    return {
        "version": "operational_cube_master_contract.v0.1",
        "phase": PHASE,
        "generated_at": STAMP,
        "decision": DECISION_PASS,
        "canonical_hierarchy": {
            "casulo_campo_os": "SYSTEM",
            "operational_cube": "PRIMARY_GOVERNANCE_CORE",
            "exocortex": "MEMORY_STATE_CONTEXT_RECONSTRUCTION_LAYER",
            "casulo_agent": "SUBORDINATE_CONVERSATIONAL_OPERATIONAL_MODULE",
            "codex": "TECHNICAL_EXECUTOR_UNDER_GATE",
            "cockpit": "OPTIONAL_SURFACE_DEFERRED",
        },
        "non_negotiable_rules": [
            "Operational Cube governs state formation, inference triage, gates and allowed/blocked actions.",
            "Exocortex reconstructs clean context and governs memory/state, but does not override the Cube.",
            "CASULO Agent is not the system core; it is a subordinate operator module inside ChatGPT/Agents.",
            "Codex is not a judge; Codex may only execute technical changes under explicit gate.",
            "Cockpit is not the priority now; cockpit is a future surface.",
            "No invented agent concept may be introduced in this project.",
            "Micrograph runtime is not in current POC scope; it is future epic only.",
            "Current filtering layer is Inference Gate prompt/schema direction, not micrograph runtime.",
            "Chat memory is not truth. Chat memory must be rebuilt through Exocortex and approved by the Cube.",
        ],
        "current_scope": {
            "focus": "ChatGPT Agent readiness and state-governed conversation/testing/calibration",
            "current_filter_layer": "Inference Gate Prompt v0.1",
            "micrographs_current_scope": "EPIC_FUTURE_ONLY_NOT_CURRENT_IMPLEMENTATION",
            "delta_matrix_current_scope": "PARTIAL_CALIBRATION_TELEMETRY_NOT_FULL_RUNTIME",
            "neo4j_current_scope": "sandbox/offline/read-only evidence and future read-only adapter",
            "github_current_scope": "existing GitHub Native Agent scaffold and actions; ChatGPT Action integration still missing",
        },
        "blocked_actions": BLOCKED_ACTIONS,
        "readiness_matrix": readiness_matrix(),
        "audit_refs": {
            "timeline_audit": "product/audits/prod8221_8260_integrated_repo_timeline_audit.json",
            "output": "outputs/prod8221_8260_operational_cube_master_contract_agent_readiness_audit.json",
        },
    }

def build_agent_manifest() -> Dict[str, Any]:
    return {
        "version": "chatgpt_agent_readiness_manifest.v0.1",
        "phase": PHASE,
        "agent_name_recommendation": "CASULO Campo OS Agent",
        "purpose": "Operate inside ChatGPT/Agents as a state-governed CASULO assistant for repo analysis, diagnostic reports, monitoring summaries, solution options, calibration review and controlled test planning.",
        "mode": "CHATGPT_AGENT_WITH_ACTIONS_REQUIRED",
        "current_status": "MANIFEST_READY_API_AND_ACTIONS_NOT_IMPLEMENTED",
        "knowledge_pack": [
            "Operational Cube Master Contract",
            "Exocortex Foundation Statement",
            "Runtime Context Packet",
            "Inference Gate Prompt",
            "Telemetry/KPI Inventory",
            "Repo Timeline Audit",
            "Boundary/Blocked Actions",
        ],
        "required_actions_next": [
            {
                "endpoint": "GET /health",
                "purpose": "Check CASULO API health."
            },
            {
                "endpoint": "GET /state/current",
                "purpose": "Return master governed state and current gate."
            },
            {
                "endpoint": "POST /context/rebuild",
                "purpose": "Rebuild clean context from chat request plus repo/graph/evidence."
            },
            {
                "endpoint": "GET /repo/timeline",
                "purpose": "Return repository timeline/audit state."
            },
            {
                "endpoint": "GET /graph/summary",
                "purpose": "Return Neo4j or offline graph summary in read-only mode."
            },
            {
                "endpoint": "POST /diagnostic",
                "purpose": "Generate governed diagnostic report."
            },
            {
                "endpoint": "POST /monitoring",
                "purpose": "Generate monitoring summary."
            },
            {
                "endpoint": "POST /solutions",
                "purpose": "Generate simple solution options under gate."
            },
            {
                "endpoint": "POST /calibration",
                "purpose": "Evaluate telemetry, vector scores and boundaries."
            },
        ],
        "agent_must_not": [
            "invent concepts not present in repo or current user instruction",
            "promote micrographs to current implementation",
            "treat cockpit as priority",
            "treat agent as system core",
            "treat chat memory as truth",
            "claim production readiness",
            "claim client validation",
            "claim commercial validation",
            "write to GitHub, Neo4j or external systems without explicit future gate",
        ],
    }

def build_telemetry_inventory() -> Dict[str, Any]:
    ponto = read_json("outputs/prod7301_7340_ponto_zero_vector_telemetry.json", {})
    graph = read_json("outputs/prod7341_7380_graph_retrieval_gain_multirun_calibration.json", {})
    return {
        "version": "casulo_kpi_vector_telemetry_inventory.v0.1",
        "phase": PHASE,
        "generated_at": STAMP,
        "telemetry_families_registered": {
            "T1_exocortex_lifecycle": ["integrity_score", "boundary_score", "risk_pressure", "action_readiness", "priority_score", "verdict", "lifecycle_action"],
            "T2_input_prompt_quality": ["prompt_quality_score", "input_data_quality_score", "requirement_completeness", "ambiguity_risk", "evidence_quality", "schema_fit", "missing_context_rate", "garbage_in_risk"],
            "T3_value_delta": ["time_saved", "rework_avoided", "context_waste_reduction", "memory_state_preservation", "hallucination_risk_avoided", "claim_leakage_avoided", "operational_risk_avoided"],
            "T4_ponto_zero": ["OHRI", "OQI", "ZPI", "evidence_density", "inference_load", "semantic_ambiguity", "gate_alignment", "claim_overreach", "unsafe_action_risk", "compressibility", "expansion_fidelity"],
            "T5_vector_kinematics": ["risk", "evidence", "confidence", "ambiguity", "dependency", "impact", "governance", "reversibility", "readiness", "exposure", "Delta_estado"],
            "T6_delta_zero_output": ["unsupported_claim", "missing_evidence_claim", "gate_violation", "scope_leak", "invented_action", "unsafe_action", "production_leak", "client_claim_leak"],
            "T7_neo4j_graph_retrieval": ["retrieval_hit_rate", "path_completeness", "evidence_to_gate_traceability", "query_latency", "false_allow_delta", "false_block_delta"],
        },
        "observed_ponto_zero_vector": ponto.get("vector_telemetry", {}).get("vector", {}),
        "observed_complex_indices": ponto.get("complex_indices", {}),
        "observed_delta_estado": ponto.get("vector_telemetry", {}).get("delta_estado"),
        "observed_graph_retrieval_proxy": graph.get("graph_retrieval_gain", {}),
        "calibration_status": {
            "single_live_run_vector_scored": bool(ponto),
            "multi_run_batch_prepared": bool(graph.get("multi_run_batch")),
            "threshold_lock_ready": False,
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
        },
        "gap": "Telemetry exists as artifacts and partial calibration; it is not yet a ChatGPT Agent runtime calibration service.",
    }

def build_memory_boundary() -> Dict[str, Any]:
    return {
        "contract": "chat_memory_boundary_context_rebuild_gate.contract.v0.1",
        "phase": PHASE,
        "purpose": "Prevent ChatGPT conversation memory from becoming operational truth without Cube/Exocortex validation.",
        "rules": [
            "Chat text is raw signal, not state.",
            "Assistant memory is raw signal, not evidence.",
            "Every remembered claim must be classified as fact, inference, preference, decision, hypothesis, superseded state or discard.",
            "Repo artifacts, tags, outputs and graph state outrank chat memory.",
            "If chat memory conflicts with repo/graph/evidence, the Cube must mark contradiction and block action.",
            "Runtime Context Packet must be rebuilt from evidence, not copied from chat.",
        ],
        "classes": [
            "SUPPORTED_FACT",
            "USER_PREFERENCE",
            "CANONICAL_DECISION",
            "VALID_INFERENCE",
            "WEAK_INFERENCE",
            "STALE_MEMORY",
            "CONTRADICTION",
            "DISCARD",
            "HUMAN_REVIEW_REQUIRED",
        ],
        "outputs": [
            "clean_context_packet",
            "memory_delta",
            "contradiction_report",
            "blocked_claims",
            "next_safe_action",
        ],
        "current_status": "CONTRACT_READY_RUNTIME_NOT_IMPLEMENTED",
    }

def check() -> Dict[str, Any]:
    missing_core = [p for p in CORE_REQUIRED if not path_exists(p)]
    missing_optional = [p for p in OPTIONAL_EXPECTED if not path_exists(p)]
    wrong_present = [p for p in WRONG_8221_LOCAL if path_exists(p)]
    return {
        "status": "PASS" if not missing_core else "FAIL",
        "phase": PHASE,
        "missing_core_count": len(missing_core),
        "missing_core": missing_core,
        "missing_optional_expected_count": len(missing_optional),
        "missing_optional_expected": missing_optional,
        "misleading_local_8221_present_count": len(wrong_present),
        "misleading_local_8221_present": wrong_present,
        "will_create": GENERATED,
        "will_cleanup_wrong_8221_if_requested": WRONG_8221_LOCAL,
        "guarantees_in_patch": [
            "No invented agent concept",
            "Operational Cube is primary governance core",
            "CASULO Agent is subordinate module",
            "Cockpit is deferred surface",
            "Micrograph runtime is future epic, not current POC",
            "Current POC filtering is Inference Gate prompt layer",
            "Telemetry/vector/KPI inventory is reconciled",
        ],
        "will_call_gpt": False,
        "will_call_codex": False,
        "will_call_neo4j": False,
        "will_write_github": False,
        "will_write_external_api": False,
    }

def cleanup_wrong_8221() -> Dict[str, Any]:
    removed = []
    skipped_tracked = []
    not_present = []
    for path in WRONG_8221_LOCAL:
        p = ROOT / path
        if not p.exists():
            not_present.append(path)
            continue
        tracked = run_cmd(["git", "ls-files", "--error-unmatch", path])
        if tracked.get("ok"):
            skipped_tracked.append(path)
            continue
        if p.is_dir():
            shutil.rmtree(p)
        else:
            p.unlink()
        removed.append(path)
    return {
        "removed_untracked_wrong_8221": removed,
        "skipped_tracked": skipped_tracked,
        "not_present": not_present,
    }

def build_audit(cleanup: Dict[str, Any] | None = None) -> Dict[str, Any]:
    timeline = timeline_from_git()
    repo_scan = scan_repository()
    artifacts = classify_key_artifacts()
    matrix = readiness_matrix()
    wrong_present = [p for p in WRONG_8221_LOCAL if path_exists(p)]

    return {
        "version": "integrated_repo_timeline_audit.v0.1",
        "phase": PHASE,
        "generated_at": STAMP,
        "purpose": "Reconcile CASULO documentation, repository timeline, telemetry, vectors, calibration and ChatGPT Agent readiness without introducing new concepts or promoting future epics to current runtime.",
        "canonical_corrections": {
            "invented_agent_concept_exists": False,
            "agent_is_system_core": False,
            "cockpit_is_priority_now": False,
            "operational_cube_is_primary_governance_core": True,
            "exocortex_is_memory_state_layer": True,
            "casulo_agent_is_subordinate_module": True,
            "codex_is_executor_under_gate": True,
            "micrograph_runtime_current_poc": False,
            "micrographs_future_epic": True,
            "current_filter_layer": "INFERENCE_GATE_PROMPT_V0_1",
        },
        "repo_status": {
            "wrong_8221_files_present_after_cleanup": wrong_present,
            "cleanup": cleanup or {},
        },
        "timeline": timeline,
        "repo_scan": repo_scan,
        "artifact_classification": artifacts,
        "readiness_matrix": matrix,
        "gap_summary_for_chatgpt_agent": [
            "Operational Cube contract now created by this patch.",
            "ChatGPT Agent manifest now created by this patch.",
            "CASULO Action/API server still missing.",
            "Neo4j read-only adapter for ChatGPT Agent still missing.",
            "GitHub read-only adapter for ChatGPT Agent still missing.",
            "Context rebuild endpoint still missing.",
            "Telemetry/calibration endpoint still missing.",
            "Schema runtime for Inference Gate still missing.",
            "Micrograph runtime remains future epic and must not be implemented in this POC.",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

def markdown_contract(contract: Dict[str, Any]) -> str:
    return f"""# Operational Cube Master Contract v0.1

Phase: `{PHASE}`  
Decision: `{contract['decision']}`

## Canonical hierarchy

- CASULO Campo OS: **system**
- Cubo Operacional: **primary governance core**
- Exocortex: **memory/state/context reconstruction layer**
- CASULO Agent: **subordinate conversational-operational module**
- Codex: **technical executor under gate**
- Cockpit: **optional/deferred surface**

## Non-negotiable rules

{chr(10).join("- " + x for x in contract["non_negotiable_rules"])}

## Current scope

```json
{json.dumps(contract["current_scope"], indent=2, ensure_ascii=False)}
```

## Blocked actions

{chr(10).join("- `" + x + "`" for x in contract["blocked_actions"])}
"""

def markdown_instructions(manifest: Dict[str, Any]) -> str:
    return """# CASULO Campo OS Agent - Instructions Draft

You are CASULO Campo OS Agent.

You are not the system core. The Operational Cube is the governance core.
You operate under the Cube using Exocortex as memory/state/context reconstruction.

## Mandatory behavior

1. Treat chat memory as raw signal, not truth.
2. Rebuild context through repo artifacts, graph state, Exocortex and Cube rules.
3. Before answering, run Inference Gate triage:
   - supported facts;
   - valid inferences;
   - weak inferences;
   - gaps;
   - contradictions;
   - delta;
   - gate;
   - allowed actions;
   - blocked actions.
4. Do not promote micrographs to current implementation. Micrographs are future epic only in this POC.
5. Do not prioritize cockpit. Cockpit is optional/deferred.
6. Do not invent concepts that are not in the repo or current user instruction.
7. Do not claim client validation, production readiness, commercial validation, validated model gain or validated hallucination reduction.
8. Codex execution, GitHub writes, Neo4j writes and external API writes require explicit future gate.

## Primary outputs

- diagnostic report;
- monitoring summary;
- simple solution options;
- calibration review;
- context rebuild;
- gap matrix;
- next safe action.

## Zero point response rule

Answer with the smallest safe response that preserves evidence, gate and blocked actions.
"""

def markdown_knowledge_pack(contract: Dict[str, Any], telemetry: Dict[str, Any]) -> str:
    return f"""# CASULO Agent Knowledge Pack v0.1

## Canonical system

CASULO Campo OS is the system.
The Operational Cube is the primary governance core.
Exocortex is the memory/state/context reconstruction layer.
CASULO Agent is a subordinate conversational-operational module.
Codex is a technical executor under gate.
Cockpit is deferred.

## Current POC scope

- Current filtering layer: Inference Gate Prompt v0.1.
- Micrograph runtime: future epic only, not current implementation.
- Delta Matrix: partial via telemetry/vector calibration, not full runtime.
- Neo4j: sandbox/offline/read-only evidence and future read-only adapter.
- GitHub: existing native agent scaffold/actions, but ChatGPT Action integration still missing.

## Telemetry

```json
{json.dumps(telemetry["calibration_status"], indent=2, ensure_ascii=False)}
```

## Blocked actions

{chr(10).join("- `" + x + "`" for x in contract["blocked_actions"])}
"""

def markdown_actions(reqs: Dict[str, Any]) -> str:
    return "# CASULO ChatGPT Action Requirements v0.1\n\n" + json.dumps(reqs, indent=2, ensure_ascii=False) + "\n"

def markdown_output(result: Dict[str, Any]) -> str:
    cal = result["calibration_decision"]
    return f"""# PROD-8221..8260 - Operational Cube Master Contract and ChatGPT Agent Readiness Audit

Status: `{result['status']}`  
Decision: `{result['decision']}`

## Calibration decision

```json
{json.dumps(cal, indent=2, ensure_ascii=False)}
```

## What this fixes

- Stops treating agent/cockpit as the system core.
- Reasserts Operational Cube as governance core.
- Reasserts Exocortex as memory/state/context reconstruction.
- Marks micrograph runtime as future epic only.
- Keeps current filtering layer as Inference Gate Prompt v0.1.
- Reconciles KPI/vector/telemetry artifacts into one inventory.
- Produces ChatGPT Agent readiness manifest and instructions.

## Next

`{result['next']}`
"""

def apply(args: argparse.Namespace) -> List[str]:
    wrote: List[str] = []
    cleanup = cleanup_wrong_8221() if args.cleanup_wrong_8221 else None
    audit = build_audit(cleanup)
    contract = generated_master_contract(audit)
    manifest = build_agent_manifest()
    telemetry = build_telemetry_inventory()
    memory_boundary = build_memory_boundary()

    action_reqs = {
        "version": "casulo_chatgpt_action_requirements.v0.1",
        "phase": PHASE,
        "status": "REQUIREMENTS_READY_API_NOT_IMPLEMENTED",
        "server_required": True,
        "read_only_default": True,
        "endpoints_required": manifest["required_actions_next"],
        "writes_blocked_by_default": True,
        "blocked_actions": BLOCKED_ACTIONS,
        "next_phase": "PROD-8261..8300 - CASULO Agent API Server and Action Scaffold",
    }

    calibration = {
        "operational_cube_master_contract_ready": True,
        "chatgpt_agent_manifest_ready": True,
        "chat_memory_boundary_contract_ready": True,
        "telemetry_inventory_ready": True,
        "repo_timeline_audit_ready": True,
        "wrong_8221_local_cleanup_requested": bool(args.cleanup_wrong_8221),
        "micrograph_runtime_current_poc": False,
        "micrographs_future_epic_only": True,
        "inference_gate_prompt_current_filter_layer": True,
        "delta_matrix_full_runtime_implemented": False,
        "delta_matrix_partial_telemetry_present": True,
        "chatgpt_agent_functional_now": False,
        "casulo_action_api_implemented": False,
        "neo4j_readonly_action_adapter_implemented": False,
        "github_readonly_action_adapter_implemented": False,
        "client_claim_allowed": False,
        "production_allowed": False,
        "commercial_claim_allowed": False,
    }

    result = {
        "status": "PASS",
        "phase": PHASE,
        "decision": DECISION_PASS,
        "generated_at": STAMP,
        "calibration_decision": calibration,
        "artifact_classification": audit["artifact_classification"],
        "readiness_matrix": audit["readiness_matrix"],
        "next": "PROD-8261..8300 - CASULO Agent API Server and Action Scaffold",
        "then": "PROD-8301..8340 - Neo4j and GitHub Read-Only Action Adapters",
    }

    write_json("product/audits/prod8221_8260_integrated_repo_timeline_audit.json", audit, wrote)
    write_json("product/cube/operational_cube_master_contract.json", contract, wrote)
    write_text("product/cube/operational_cube_master_contract.md", markdown_contract(contract), wrote)
    write_json("product/agent_manifest/chatgpt_agent_readiness_manifest.json", manifest, wrote)
    write_text("product/agent_manifest/chatgpt_agent_instructions.md", markdown_instructions(manifest), wrote)
    write_text("product/agent_manifest/chatgpt_agent_knowledge_pack.md", markdown_knowledge_pack(contract, telemetry), wrote)
    write_json("product/actions/casulo_chatgpt_action_requirements.json", action_reqs, wrote)
    write_text("product/actions/casulo_chatgpt_action_requirements.md", markdown_actions(action_reqs), wrote)
    write_json("product/memory/chat_memory_boundary_context_rebuild_gate.contract.json", memory_boundary, wrote)
    write_json("product/calibration/casulo_kpi_vector_telemetry_inventory.json", telemetry, wrote)
    write_json("product/supersession/prod8221_wrong_agent_core_runtime_supersession.json", {
        "version": "wrong_agent_core_runtime_supersession.v0.1",
        "phase": PHASE,
        "generated_at": STAMP,
        "superseded_name": "Agent Core Runtime and Telemetry Harness",
        "reason": "It wrongly framed the agent module as core and did not place it explicitly under the Operational Cube.",
        "correct_name": "Operational Cube Master Contract and ChatGPT Agent Readiness Audit",
        "invented_agent_concept_exists": False,
        "micrograph_runtime_current_poc": False,
        "cleanup": cleanup or {},
    }, wrote)
    write_json("outputs/prod8221_8260_operational_cube_master_contract_agent_readiness_audit.json", result, wrote)
    write_text("outputs/prod8221_8260_operational_cube_master_contract_agent_readiness_audit.md", markdown_output(result), wrote)
    write_text("docs/product/822_OPERATIONAL_CUBE_MASTER_CONTRACT_AGENT_READINESS_AUDIT.md", f"""# 822 - Operational Cube Master Contract and ChatGPT Agent Readiness Audit

This phase reconciles the repo and stops architectural drift.

## Correct hierarchy

CASULO Campo OS = system.  
Operational Cube = primary governance core.  
Exocortex = memory/state/context reconstruction layer.  
CASULO Agent = subordinate conversational-operational module.  
Codex = executor under gate.  
Cockpit = deferred surface.

## Current scope

Current filtering layer: Inference Gate Prompt v0.1.  
Micrograph runtime: future epic only, not current implementation.  
Delta Matrix: partial telemetry/calibration exists, full runtime not implemented.  
ChatGPT Agent: manifest/instructions ready; API/actions still missing.

## Generated artifacts

{chr(10).join("- `" + x + "`" for x in GENERATED)}

## Next

`PROD-8261..8300 - CASULO Agent API Server and Action Scaffold`
""", wrote)

    return wrote

def self_test(cleanup_requested: bool) -> Dict[str, Any]:
    generated_missing = [p for p in GENERATED if not path_exists(p)]
    json_errors = []
    for p in GENERATED:
        if p.endswith(".json"):
            try:
                json.loads((ROOT / p).read_text(encoding="utf-8"))
            except Exception as exc:
                json_errors.append({"path": p, "error": str(exc)})

    forbidden_generated_terms = []
    for p in GENERATED:
        if path_exists(p) and (ROOT / p).is_file() and p.endswith((".json", ".md")):
            text = read_text(p).lower()
            if "exocodex" in text and "exocodex_exists" not in text:
                forbidden_generated_terms.append({"path": p, "term": "ExoCodex"})
    wrong_present = [p for p in WRONG_8221_LOCAL if path_exists(p)]

    contract = read_json("product/cube/operational_cube_master_contract.json", {})
    checks = {
        "generated_missing_count": len(generated_missing),
        "json_errors_count": len(json_errors),
        "forbidden_generated_terms_count": len(forbidden_generated_terms),
        "operational_cube_primary": contract.get("canonical_hierarchy", {}).get("operational_cube") == "PRIMARY_GOVERNANCE_CORE",
        "casulo_agent_subordinate": contract.get("canonical_hierarchy", {}).get("casulo_agent") == "SUBORDINATE_CONVERSATIONAL_OPERATIONAL_MODULE",
        "micrographs_future_only": contract.get("current_scope", {}).get("micrographs_current_scope") == "EPIC_FUTURE_ONLY_NOT_CURRENT_IMPLEMENTATION",
        "current_filter_layer_inference_gate": contract.get("current_scope", {}).get("current_filter_layer") == "Inference Gate Prompt v0.1",
        "wrong_8221_absent_if_cleanup_requested": (not wrong_present) if cleanup_requested else True,
    }
    passed = (
        not generated_missing
        and not json_errors
        and not forbidden_generated_terms
        and all(v is True or (isinstance(v, int) and v == 0) for v in checks.values())
    )
    return {
        "status": "PASS" if passed else "FAIL",
        "phase": PHASE,
        "checks": checks,
        "generated_missing": generated_missing,
        "json_errors": json_errors,
        "forbidden_generated_terms": forbidden_generated_terms,
        "wrong_8221_present": wrong_present,
    }

def commit_plan() -> str:
    paths = [
        "apply_prod8221_8260_operational_cube_master_contract_agent_readiness_audit.py",
        *GENERATED,
    ]
    lines = ["git add \\"]
    for p in paths[:-1]:
        lines.append(f"  {p} \\")
    lines.append(f"  {paths[-1]}")
    lines.extend([
        "",
        'git commit -m "Add operational cube master contract and agent readiness audit"',
        'git tag -a product-casulo-operational-cube-agent-readiness-audit-v0.1 HEAD -m "CASULO operational cube agent readiness audit v0.1"',
        "git push origin main",
        "git push origin product-casulo-operational-cube-agent-readiness-audit-v0.1",
    ])
    return "\n".join(lines)

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--cleanup-wrong-8221", action="store_true")
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
        wrote = apply(args)
        print(json.dumps({"applied": True, "wrote_count": len(wrote), "wrote": wrote}, indent=2, ensure_ascii=False))

    if args.self_test:
        print(json.dumps(self_test(args.cleanup_wrong_8221), indent=2, ensure_ascii=False))

    if args.commit_plan:
        print(commit_plan())

    return 0

if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
CASULO PROD-8101..8140 - Internal Demo Script and Agent Instruction Pack

Creates:
- Agent Instruction Pack
- Runtime Context Packet v0.1
- Inference Gate Prompt v0.1
- internal demo script
- evaluate model for diagnostic report, monitoring summary and simple solution recommendations

Does not implement micrographs, Delta Matrix runtime, multi-LLM braid, production cockpit,
live GPT/Codex execution, Neo4j writes, or client/production/commercial claims.
"""

from __future__ import annotations
import argparse, json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()
PHASE = "PROD-8101..8140"

REQUIRED = [
    "outputs/prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.json",
    "outputs/prod8061a_exocortex_foundation_statement_addendum.json",
    "product/exocortex/prod8061a_exocortex_foundation_statement.json",
    "product/reviews/operator_packets/prod8061_8100_exp50_operator_evidence_packet.json",
    "product/contracts/exocortex_memory_mesh_foundation.contract.json",
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
    "production_cockpit_claim",
]

ALLOWED_INTERNAL_ACTIONS = [
    "explain_current_operational_state",
    "generate_internal_diagnostic_report",
    "generate_internal_monitoring_summary",
    "recommend_simple_solution_options",
    "generate_human_review_packet",
    "generate_sandbox_only_action_plan",
    "compare_plain_agent_vs_casulo_agent",
    "prepare_cockpit_chat_scaffold",
]

MEMORY_DOMAINS = [
    "GPT_MEMORY_MESH_DOMAIN",
    "SESSION_CONTEXT_DOMAIN",
    "PROJECT_CANONICAL_MEMORY_DOMAIN",
    "USER_OPERATIONAL_PREFERENCE_DOMAIN",
    "EVIDENCE_MEMORY_DOMAIN",
    "CLAIM_BOUNDARY_MEMORY_DOMAIN",
    "ROADMAP_MEMORY_DOMAIN",
    "CODE_EXECUTION_MEMORY_DOMAIN",
    "GRAPH_STATE_MEMORY_DOMAIN",
    "CONCEPT_ONTOLOGY_MEMORY_DOMAIN",
    "CACHE_TRANSIENT_DOMAIN",
    "STALE_OR_SUPERSEDED_MEMORY_DOMAIN",
    "RUNTIME_CONTEXT_PACKET_DOMAIN",
]

def read_json(path, default=None):
    p = ROOT / path
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

def write_json(path, data, wrote):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    wrote.append(path)

def write_text(path, text, wrote):
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    wrote.append(path)

def check():
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    return {
        "status": "PASS" if not missing else "FAIL",
        "phase": PHASE,
        "missing_required_count": len(missing),
        "missing_required": missing,
        "will_create": [
            "product/agent/prod8101_8140_agent_instruction_pack.json",
            "product/agent/prod8101_8140_agent_instruction_pack.md",
            "product/exocortex/runtime_context_packets/prod8101_8140_runtime_context_packet_exp50.json",
            "product/exocortex/runtime_context_packets/prod8101_8140_runtime_context_packet_exp50.md",
            "product/inference_gates/prod8101_8140_inference_gate_prompt_v0_1.json",
            "product/inference_gates/prod8101_8140_inference_gate_prompt_v0_1.md",
            "product/demos/prod8101_8140_internal_demo_script.json",
            "product/demos/prod8101_8140_internal_demo_script.md",
            "product/evaluate/prod8101_8140_diagnostic_monitoring_solution_evaluate_model.json",
            "outputs/prod8101_8140_internal_demo_script_agent_instruction_pack.json",
            "outputs/prod8101_8140_internal_demo_script_agent_instruction_pack.md",
            "docs/product/810_INTERNAL_DEMO_SCRIPT_AGENT_INSTRUCTION_PACK.md",
        ],
        "will_call_gpt": False,
        "will_run_codex": False,
        "will_connect_to_neo4j": False,
        "will_write_neo4j": False,
        "will_implement_micrographs": False,
        "will_implement_delta_matrix": False,
        "will_create_production_cockpit": False,
        "will_allow_client_claim": False,
    }

def evaluate():
    out8061 = read_json("outputs/prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.json", {})
    out8061a = read_json("outputs/prod8061a_exocortex_foundation_statement_addendum.json", {})
    operator = read_json("product/reviews/operator_packets/prod8061_8100_exp50_operator_evidence_packet.json", {})
    cal8061 = out8061.get("calibration_decision", {})
    cal8061a = out8061a.get("calibration_decision", {})
    checks = {
        "prior_8061_status_pass": out8061.get("status") == "PASS",
        "prior_8061_operator_packet_ready": cal8061.get("operator_evidence_packet_ready") is True,
        "prior_8061_client_blocked": cal8061.get("ready_for_client_claim") is False,
        "prior_8061_production_blocked": cal8061.get("ready_for_production") is False,
        "prior_8061a_status_pass": out8061a.get("status") == "PASS",
        "exocortex_foundation_active": cal8061a.get("exocortex_foundation_active") is True,
        "memory_as_mesh": cal8061a.get("memory_as_mesh") is True,
        "gpt_memory_as_family_of_domains": cal8061a.get("gpt_memory_as_family_of_domains") is True,
        "state_as_live_graph": cal8061a.get("state_as_live_graph") is True,
        "evidence_bound_to_state": cal8061a.get("evidence_bound_to_state") is True,
        "claim_boundary_active": cal8061a.get("claim_boundary_active") is True,
        "runtime_exocortex_not_complete": cal8061a.get("runtime_exocortex_module_complete") is False,
        "micrographs_not_implemented": cal8061a.get("micrographs_implemented") is False,
        "delta_matrix_not_implemented": cal8061a.get("delta_matrix_implemented") is False,
        "ready_for_agent_instruction_pack": cal8061a.get("ready_for_agent_instruction_pack") is True,
    }
    ready = all(checks.values())
    return {
        "checks": checks,
        "agent_instruction_pack_ready": ready,
        "runtime_context_packet_ready": ready,
        "inference_gate_prompt_ready": ready,
        "internal_demo_script_ready": ready,
        "diagnostic_report_model_ready": ready,
        "monitoring_summary_model_ready": ready,
        "simple_solution_recommendation_model_ready": ready,
        "ready_for_monday_demo_readiness_packet": ready,
        "ready_for_cockpit_chat_scaffold": ready,
        "exocortex_foundation_active": True,
        "micrographs_implemented": False,
        "delta_matrix_implemented": False,
        "state_family_implemented": False,
        "multi_llm_braid_implemented": False,
        "runtime_exocortex_module_complete": False,
        "client_claim_allowed": False,
        "production_allowed": False,
        "commercial_claim_allowed": False,
        "observed_graph": operator.get("observed_graph", {}),
        "next_phase": "PROD-8141..8180 - Monday Demo Readiness Packet",
        "then_phase": "PROD-8181..8220 - Cockpit Chat Scaffold and Diagnostic Monitor Prototype",
    }

def runtime_context_packet(ev):
    return {
        "version": "runtime_context_packet.v0.1",
        "phase": PHASE,
        "generated_at": STAMP,
        "packet_id": "RCP-EXP50-EXOCORTEX-FOUNDATION-001",
        "task_intent": "internal_demo_agent_context",
        "current_state": {
            "casulo_state": "EXOCORTEX_FOUNDATION_ACTIVE",
            "exp50_graph_confirmed": True,
            "read_only_retrieval_confirmed": True,
            "operator_evidence_packet_ready": True,
            "client_claim_allowed": False,
            "production_allowed": False,
            "commercial_claim_allowed": False,
            "micrographs_implemented": False,
            "delta_matrix_implemented": False,
        },
        "memory_domains": MEMORY_DOMAINS,
        "evidence_refs": REQUIRED,
        "allowed_claims_internal": [
            "EXP50 read-only retrieval was confirmed in sandbox.",
            "Exocortex Foundation is active in the POC.",
            "GPT memory is modeled as a family of domains under GPT_MEMORY_MESH_DOMAIN.",
            "The system can prepare internal diagnostic reports, monitoring summaries and simple solution recommendations for review.",
        ],
        "blocked_claims": [
            "client-validated result",
            "production-ready result",
            "commercially validated product",
            "validated hallucination reduction",
            "validated model gain",
            "micrograph runtime implemented",
            "Delta Matrix runtime implemented",
            "production cockpit implemented",
        ],
        "allowed_actions": ALLOWED_INTERNAL_ACTIONS,
        "blocked_actions": BLOCKED_ACTIONS,
        "next_safe_action": "Generate internal demo script, diagnostic report template, monitoring summary template and cockpit chat scaffold plan.",
    }

def inference_gate():
    prompt = """Before answering, treat the request as operational state formation.

Do not answer directly with a final conclusion before triage.

Separate:
- supported facts;
- valid inferences;
- weak inferences;
- gaps;
- contradictions;
- operational hallucination risks.

Identify support:
- evidence;
- memory domain;
- artifact;
- graph state;
- rule;
- gate;
- prior decision.

Declare:
- minimum governable state;
- delta to safe decision;
- applicable gate;
- allowed actions;
- blocked actions;
- allowed claims;
- blocked claims.

Produce the smallest safe answer possible without filling gaps as facts."""
    return {
        "version": "inference_gate_prompt.v0.1",
        "phase": PHASE,
        "status": "PROMPT_LEVEL_ONLY_NOT_RUNTIME_ENGINE",
        "prompt": prompt,
        "output_classes": [
            "SUPPORTED_FACT",
            "VALID_INFERENCE",
            "WEAK_INFERENCE",
            "MISSING_EVIDENCE",
            "CONTRADICTION",
            "ACTION_BLOCKED",
            "HUMAN_REVIEW_REQUIRED",
        ],
        "not_implemented_here": [
            "schema_validation_runtime",
            "micrograph_binding",
            "delta_matrix_runtime",
            "state_family_runtime",
            "multi_llm_braid",
        ],
    }

def evaluate_model():
    return {
        "version": "diagnostic_monitoring_solution_evaluate_model.v0.1",
        "phase": PHASE,
        "purpose": "Internal reports, monitoring and simple solution recommendations before cockpit chat implementation.",
        "diagnostic_report_sections": [
            "executive_state_summary",
            "supported_facts",
            "valid_inferences",
            "gaps",
            "contradictions",
            "risks",
            "gate",
            "allowed_actions",
            "blocked_actions",
            "simple_solution_options",
            "human_review_required",
            "next_safe_action",
        ],
        "monitoring_summary_sections": [
            "current_state",
            "state_changes_since_last_snapshot",
            "open_gaps",
            "blocked_claims",
            "readiness",
            "risk_level",
            "evidence_density",
            "recommended_follow_up",
        ],
        "simple_solution_recommendation_rules": [
            "Recommend only internal/reviewable solutions.",
            "Prefer matrix, checklist, report, dashboard scaffold, sandbox script or human review workflow.",
            "Do not recommend irreversible production action.",
            "Every solution must include evidence, gate, scope, rollback/reversibility and blocked actions.",
        ],
        "improvement_index_v0": {
            "status": "PLANNED_NOT_VALIDATED",
            "dimensions": [
                "gap_reduction",
                "evidence_density_increase",
                "readiness_increase",
                "risk_reduction",
                "operator_decision_clarity",
            ],
            "allowed_use": "internal demo placeholder only",
            "blocked_use": "validated business gain claim",
        },
    }

def demo_script():
    return {
        "version": "internal_demo_script.v0.1",
        "phase": PHASE,
        "title": "CASULO Exocortex Foundation Demo",
        "acts": [
            "Show EXP50 read-only retrieval and evidence boundary.",
            "Explain Exocortex as memory mesh and clean context reconstruction.",
            "Compare plain agent vs CASULO-guided agent.",
            "Generate internal diagnostic report.",
            "Generate monitoring summary.",
            "Recommend simple internal solution options.",
            "Prepare next step: cockpit chat scaffold.",
        ],
        "allowed_demo_claims": [
            "Controlled internal POC",
            "Exocortex Foundation active",
            "Read-only graph evidence confirmed",
            "Agent instruction pack ready",
            "Diagnostic/monitoring/simple-solution model ready",
        ],
        "blocked_demo_claims": [
            "Production ready",
            "Client validated",
            "Commercially validated",
            "Validated hallucination reduction",
            "Validated model gain",
            "Micrograph runtime implemented",
            "Delta Matrix runtime implemented",
        ],
    }

def md_list(title, items):
    return "## " + title + "\n\n" + "\n".join("- " + str(x) for x in items) + "\n"

def apply():
    wrote = []
    ev = evaluate()
    status = "PASS" if ev["agent_instruction_pack_ready"] else "FAIL"
    decision = "AGENT_INSTRUCTION_PACK_RUNTIME_CONTEXT_PACKET_READY_FOR_DEMO_READINESS_AND_COCKPIT_CHAT_SCAFFOLD" if status == "PASS" else "AGENT_INSTRUCTION_PACK_NOT_READY_REVIEW_REQUIRED"
    rcp = runtime_context_packet(ev)
    gate = inference_gate()
    model = evaluate_model()
    demo = demo_script()
    agent = {
        "version": "agent_instruction_pack.v0.1",
        "phase": PHASE,
        "generated_at": STAMP,
        "agent_role": "CASULO Exocortex Foundation Operator Assistant",
        "core_instruction": "Use the Runtime Context Packet and Inference Gate before producing diagnostic reports, monitoring summaries or simple solution recommendations.",
        "operating_principles": [
            "Do not treat memory as raw chat history.",
            "Use Exocortex memory domains to reconstruct clean context.",
            "Separate facts, inferences, gaps and contradictions before recommendations.",
            "Do not claim production readiness, client validation or commercial validation.",
            "Do not claim micrographs or Delta Matrix runtime are implemented.",
            "When recommending solutions, keep them internal, simple, reversible and reviewable.",
            "Codex can be positioned as executor only under CASULO gates.",
        ],
        "allowed_outputs": ALLOWED_INTERNAL_ACTIONS,
        "blocked_actions": BLOCKED_ACTIONS,
        "runtime_context_packet_ref": "product/exocortex/runtime_context_packets/prod8101_8140_runtime_context_packet_exp50.json",
        "inference_gate_ref": "product/inference_gates/prod8101_8140_inference_gate_prompt_v0_1.md",
    }
    result = {
        "status": status,
        "phase": PHASE,
        "decision": decision,
        "generated_at": STAMP,
        "evaluation": ev,
        "calibration_decision": {
            "agent_instruction_pack_ready": ev["agent_instruction_pack_ready"],
            "runtime_context_packet_ready": ev["runtime_context_packet_ready"],
            "inference_gate_prompt_ready": ev["inference_gate_prompt_ready"],
            "internal_demo_script_ready": ev["internal_demo_script_ready"],
            "diagnostic_report_model_ready": ev["diagnostic_report_model_ready"],
            "monitoring_summary_model_ready": ev["monitoring_summary_model_ready"],
            "simple_solution_recommendation_model_ready": ev["simple_solution_recommendation_model_ready"],
            "ready_for_monday_demo_readiness_packet": ev["ready_for_monday_demo_readiness_packet"],
            "ready_for_cockpit_chat_scaffold": ev["ready_for_cockpit_chat_scaffold"],
            "micrographs_implemented": False,
            "delta_matrix_implemented": False,
            "runtime_exocortex_module_complete": False,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "commercial_claim_allowed": False,
        },
        "next": ev["next_phase"],
        "then": ev["then_phase"],
    }
    write_json("product/agent/prod8101_8140_agent_instruction_pack.json", agent, wrote)
    write_text("product/agent/prod8101_8140_agent_instruction_pack.md",
               "# PROD-8101..8140 - Agent Instruction Pack\n\n" + agent["core_instruction"] + "\n\n" +
               md_list("Operating principles", agent["operating_principles"]) +
               md_list("Allowed outputs", agent["allowed_outputs"]) +
               md_list("Blocked actions", agent["blocked_actions"]), wrote)
    write_json("product/exocortex/runtime_context_packets/prod8101_8140_runtime_context_packet_exp50.json", rcp, wrote)
    write_text("product/exocortex/runtime_context_packets/prod8101_8140_runtime_context_packet_exp50.md",
               "# Runtime Context Packet v0.1\n\n```json\n" + json.dumps(rcp, indent=2, ensure_ascii=False) + "\n```\n", wrote)
    write_json("product/inference_gates/prod8101_8140_inference_gate_prompt_v0_1.json", gate, wrote)
    write_text("product/inference_gates/prod8101_8140_inference_gate_prompt_v0_1.md",
               "# Inference Gate Prompt v0.1\n\nStatus: `" + gate["status"] + "`\n\n```text\n" + gate["prompt"] + "\n```\n", wrote)
    write_json("product/demos/prod8101_8140_internal_demo_script.json", demo, wrote)
    write_text("product/demos/prod8101_8140_internal_demo_script.md",
               "# " + demo["title"] + "\n\n" + md_list("Acts", demo["acts"]) + md_list("Allowed demo claims", demo["allowed_demo_claims"]) + md_list("Blocked demo claims", demo["blocked_demo_claims"]), wrote)
    write_json("product/evaluate/prod8101_8140_diagnostic_monitoring_solution_evaluate_model.json", model, wrote)
    write_json("outputs/prod8101_8140_internal_demo_script_agent_instruction_pack.json", result, wrote)
    write_text("outputs/prod8101_8140_internal_demo_script_agent_instruction_pack.md",
               "# PROD-8101..8140 - Internal Demo Script and Agent Instruction Pack\n\nStatus: " + status + "\n\nDecision: `" + decision + "`\n\n```json\n" + json.dumps(result["calibration_decision"], indent=2, ensure_ascii=False) + "\n```\n", wrote)
    write_text("docs/product/810_INTERNAL_DEMO_SCRIPT_AGENT_INSTRUCTION_PACK.md",
               "# 810 - Internal Demo Script and Agent Instruction Pack\n\nCreates Agent Instruction Pack, Runtime Context Packet v0.1, Inference Gate Prompt v0.1, internal demo script and evaluate model for diagnostic report, monitoring summary and simple solution recommendations.\n\nDoes not implement micrographs, Delta Matrix runtime, State Family runtime, multi-LLM braid, production cockpit, live GPT/Codex execution or Neo4j writes.\n\nNext: `PROD-8141..8180 - Monday Demo Readiness Packet`.\nThen: `PROD-8181..8220 - Cockpit Chat Scaffold and Diagnostic Monitor Prototype`.\n", wrote)
    return wrote

def commit_plan():
    paths = [
        "apply_prod8101_8140_internal_demo_script_agent_instruction_pack.py",
        "product/agent/prod8101_8140_agent_instruction_pack.json",
        "product/agent/prod8101_8140_agent_instruction_pack.md",
        "product/exocortex/runtime_context_packets/prod8101_8140_runtime_context_packet_exp50.json",
        "product/exocortex/runtime_context_packets/prod8101_8140_runtime_context_packet_exp50.md",
        "product/inference_gates/prod8101_8140_inference_gate_prompt_v0_1.json",
        "product/inference_gates/prod8101_8140_inference_gate_prompt_v0_1.md",
        "product/demos/prod8101_8140_internal_demo_script.json",
        "product/demos/prod8101_8140_internal_demo_script.md",
        "product/evaluate/prod8101_8140_diagnostic_monitoring_solution_evaluate_model.json",
        "outputs/prod8101_8140_internal_demo_script_agent_instruction_pack.json",
        "outputs/prod8101_8140_internal_demo_script_agent_instruction_pack.md",
        "docs/product/810_INTERNAL_DEMO_SCRIPT_AGENT_INSTRUCTION_PACK.md",
    ]
    return "\n".join(["git add \\"] + [f"  {p} \\" for p in paths[:-1]] + [f"  {paths[-1]}", "", 'git commit -m "Add internal demo agent instruction pack"', 'git tag -a product-casulo-agent-instruction-runtime-context-v0.1 HEAD -m "CASULO agent instruction and runtime context v0.1"', "git push origin main", "git push origin product-casulo-agent-instruction-runtime-context-v0.1"])

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
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
    if args.commit_plan:
        print(commit_plan())

if __name__ == "__main__":
    main()

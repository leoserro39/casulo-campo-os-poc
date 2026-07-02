#!/usr/bin/env python3
"""
CASULO PROD-8141..8180 - Monday Demo Readiness Packet

Purpose:
  - continue after PROD-8101..8140;
  - consolidate the internal demo readiness pack;
  - define executive story, demo sequence, Q&A, allowed/blocked claims;
  - prepare the handoff to cockpit chat scaffold and diagnostic monitor prototype.

This patcher does NOT:
  - call GPT/Codex;
  - connect/write to Neo4j;
  - implement micrographs or Delta Matrix;
  - create production cockpit;
  - allow client/production/commercial claims.

Usage:
  python3 apply_prod8141_8180_monday_demo_readiness_packet.py --check
  python3 apply_prod8141_8180_monday_demo_readiness_packet.py --apply --commit-plan
"""

from __future__ import annotations
import argparse, json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()
PHASE = "PROD-8141..8180"

REQUIRED = [
    "outputs/prod8101_8140_internal_demo_script_agent_instruction_pack.json",
    "product/agent/prod8101_8140_agent_instruction_pack.json",
    "product/exocortex/runtime_context_packets/prod8101_8140_runtime_context_packet_exp50.json",
    "product/inference_gates/prod8101_8140_inference_gate_prompt_v0_1.json",
    "product/demos/prod8101_8140_internal_demo_script.json",
    "product/evaluate/prod8101_8140_diagnostic_monitoring_solution_evaluate_model.json",
]

BLOCKED = [
    "client_facing_validated_claim",
    "production_activation",
    "commercial_claim",
    "validated_model_gain_claim",
    "validated_hallucination_reduction_claim",
    "automatic_merge",
    "real_world_side_effect",
    "production_neo4j_write",
    "neo4j_delete",
    "neo4j_reimport",
    "micrograph_runtime_claim",
    "delta_matrix_runtime_claim",
    "production_cockpit_claim",
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
            "product/demos/prod8141_8180_monday_demo_readiness_packet.json",
            "product/demos/prod8141_8180_monday_demo_readiness_packet.md",
            "product/demos/prod8141_8180_demo_question_answer_bank.json",
            "product/demos/prod8141_8180_demo_question_answer_bank.md",
            "product/cockpit/prod8141_8180_cockpit_chat_handoff_requirements.json",
            "product/cockpit/prod8141_8180_cockpit_chat_handoff_requirements.md",
            "outputs/prod8141_8180_monday_demo_readiness_packet.json",
            "outputs/prod8141_8180_monday_demo_readiness_packet.md",
            "docs/product/814_MONDAY_DEMO_READINESS_PACKET.md",
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
    out8101 = read_json("outputs/prod8101_8140_internal_demo_script_agent_instruction_pack.json", {})
    cal = out8101.get("calibration_decision", {})
    checks = {
        "prior_8101_status_pass": out8101.get("status") == "PASS",
        "agent_instruction_pack_ready": cal.get("agent_instruction_pack_ready") is True,
        "runtime_context_packet_ready": cal.get("runtime_context_packet_ready") is True,
        "inference_gate_prompt_ready": cal.get("inference_gate_prompt_ready") is True,
        "internal_demo_script_ready": cal.get("internal_demo_script_ready") is True,
        "diagnostic_report_model_ready": cal.get("diagnostic_report_model_ready") is True,
        "monitoring_summary_model_ready": cal.get("monitoring_summary_model_ready") is True,
        "simple_solution_recommendation_model_ready": cal.get("simple_solution_recommendation_model_ready") is True,
        "ready_for_cockpit_chat_scaffold": cal.get("ready_for_cockpit_chat_scaffold") is True,
        "client_claim_blocked": cal.get("ready_for_client_claim") is False,
        "production_blocked": cal.get("ready_for_production") is False,
        "commercial_claim_blocked": cal.get("commercial_claim_allowed") is False,
        "micrographs_not_implemented": cal.get("micrographs_implemented") is False,
        "delta_matrix_not_implemented": cal.get("delta_matrix_implemented") is False,
    }
    ready = all(checks.values())
    return {
        "checks": checks,
        "monday_demo_readiness_packet_ready": ready,
        "executive_story_ready": ready,
        "demo_qa_bank_ready": ready,
        "cockpit_chat_handoff_ready": ready,
        "ready_for_cockpit_chat_scaffold": ready,
        "ready_for_local_diagnostic_monitor_prototype": ready,
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "commercial_claim_allowed": False,
        "micrographs_implemented": False,
        "delta_matrix_implemented": False,
        "production_cockpit_implemented": False,
        "next_phase": "PROD-8181..8220 - Cockpit Chat Scaffold and Diagnostic Monitor Prototype",
    }

def demo_packet():
    return {
        "version": "monday_demo_readiness_packet.v0.1",
        "phase": PHASE,
        "title": "CASULO Campo OS - Exocortex Foundation Demo",
        "positioning": "Controlled internal POC for operational state, memory mesh, evidence, gates, diagnostic report, monitoring summary and simple solution recommendations.",
        "three_phase_story": [
            {
                "phase": "1 - Exocortex Foundation",
                "message": "CASULO preserves and retrieves governed operational state from evidence and graph.",
            },
            {
                "phase": "2 - Agent Instruction + Runtime Context",
                "message": "CASULO reconstructs clean context for GPT/Codex and forces inference triage before recommendations.",
            },
            {
                "phase": "3 - Cockpit Chat + Diagnostic Monitor",
                "message": "CASULO turns the governed state into an operator surface for reports, monitoring and simple solutions.",
            },
        ],
        "demo_flow": [
            "Open with the problem: agents answer with context, but operations need state.",
            "Show EXP50 read-only retrieval and Exocortex Foundation boundaries.",
            "Show Runtime Context Packet and memory domains.",
            "Show Inference Gate Prompt v0.1.",
            "Ask for a diagnostic report.",
            "Ask for monitoring summary.",
            "Ask for simple solution options.",
            "Close with Cockpit Chat Scaffold as next operational surface.",
        ],
        "allowed_claims": [
            "Controlled internal POC",
            "Exocortex Foundation active",
            "Memory modeled as governed mesh",
            "Runtime Context Packet ready",
            "Inference Gate prompt ready",
            "Diagnostic/monitoring/simple-solution model ready",
            "Cockpit chat scaffold ready to be built next",
        ],
        "blocked_claims": [
            "Production ready",
            "Client validated",
            "Commercially validated",
            "Validated hallucination reduction",
            "Validated model gain",
            "Micrograph runtime implemented",
            "Delta Matrix runtime implemented",
            "Production cockpit implemented",
        ],
    }

def qa_bank():
    return {
        "version": "demo_question_answer_bank.v0.1",
        "phase": PHASE,
        "questions": [
            {
                "q": "Isso ja esta em producao?",
                "a": "Nao. E uma POC interna controlada com retrieval read-only, Exocortex Foundation, runtime context e boundaries ativos.",
            },
            {
                "q": "O que o Exocortex faz agora?",
                "a": "Ele esta registrado como fundacao: memoria como malha, estado como grafo vivo, contexto limpo e boundaries. O runtime completo de memory governor ainda vem depois.",
            },
            {
                "q": "Tem micrografos agora?",
                "a": "Nao. Micrografos nao estao implementados nesta POC. Entram em epico posterior.",
            },
            {
                "q": "Que tipo de solucao simples pode recomendar?",
                "a": "Matriz, checklist, relatorio, plano sandbox, fluxo de revisao humana ou scaffold de dashboard, sempre com gate e sem acao produtiva.",
            },
            {
                "q": "Qual a diferenca para Codex?",
                "a": "Codex executa artefatos; CASULO governa estado, memoria, evidencia, gate e limite de acao.",
            },
        ],
    }

def cockpit_handoff():
    return {
        "version": "cockpit_chat_handoff_requirements.v0.1",
        "phase": PHASE,
        "goal": "Prepare next phase: a local/static cockpit chat scaffold for diagnostic reports, monitoring and simple solution recommendations.",
        "minimum_surfaces": [
            "Status header: phase, gate, readiness, blocked claims",
            "Chat panel: operator asks state/diagnostic/monitoring/solution questions",
            "Evidence panel: key evidence refs and graph state summary",
            "Diagnostic report panel",
            "Monitoring summary panel",
            "Simple solution options panel",
            "Boundary panel: allowed and blocked actions",
        ],
        "minimum_inputs": [
            "Runtime Context Packet JSON",
            "Agent Instruction Pack JSON",
            "Inference Gate Prompt",
            "Evaluate model JSON",
        ],
        "runtime_boundary": {
            "static_or_local_only": True,
            "no_live_gpt_required": True,
            "no_neo4j_write": True,
            "no_production_action": True,
            "no_client_claim": True,
        },
    }

def apply():
    wrote = []
    ev = evaluate()
    status = "PASS" if ev["monday_demo_readiness_packet_ready"] else "FAIL"
    decision = "MONDAY_DEMO_READINESS_PACKET_READY_FOR_COCKPIT_CHAT_SCAFFOLD" if status == "PASS" else "MONDAY_DEMO_READINESS_NOT_READY_REVIEW_REQUIRED"
    demo = demo_packet()
    qa = qa_bank()
    cockpit = cockpit_handoff()
    result = {
        "status": status,
        "phase": PHASE,
        "decision": decision,
        "generated_at": STAMP,
        "evaluation": ev,
        "calibration_decision": {
            "monday_demo_readiness_packet_ready": ev["monday_demo_readiness_packet_ready"],
            "executive_story_ready": ev["executive_story_ready"],
            "demo_qa_bank_ready": ev["demo_qa_bank_ready"],
            "cockpit_chat_handoff_ready": ev["cockpit_chat_handoff_ready"],
            "ready_for_cockpit_chat_scaffold": ev["ready_for_cockpit_chat_scaffold"],
            "ready_for_local_diagnostic_monitor_prototype": ev["ready_for_local_diagnostic_monitor_prototype"],
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "commercial_claim_allowed": False,
            "micrographs_implemented": False,
            "delta_matrix_implemented": False,
            "production_cockpit_implemented": False,
        },
        "next": ev["next_phase"],
    }

    write_json("product/demos/prod8141_8180_monday_demo_readiness_packet.json", demo, wrote)
    write_text("product/demos/prod8141_8180_monday_demo_readiness_packet.md",
               "# Monday Demo Readiness Packet\n\n" +
               "Positioning: " + demo["positioning"] + "\n\n" +
               "## Demo flow\n\n" + "\n".join("- " + x for x in demo["demo_flow"]) + "\n\n" +
               "## Allowed claims\n\n" + "\n".join("- " + x for x in demo["allowed_claims"]) + "\n\n" +
               "## Blocked claims\n\n" + "\n".join("- " + x for x in demo["blocked_claims"]) + "\n", wrote)

    write_json("product/demos/prod8141_8180_demo_question_answer_bank.json", qa, wrote)
    write_text("product/demos/prod8141_8180_demo_question_answer_bank.md",
               "# Demo Q&A Bank\n\n" + "\n\n".join("## " + item["q"] + "\n\n" + item["a"] for item in qa["questions"]) + "\n", wrote)

    write_json("product/cockpit/prod8141_8180_cockpit_chat_handoff_requirements.json", cockpit, wrote)
    write_text("product/cockpit/prod8141_8180_cockpit_chat_handoff_requirements.md",
               "# Cockpit Chat Handoff Requirements\n\nGoal: " + cockpit["goal"] + "\n\n" +
               "## Minimum surfaces\n\n" + "\n".join("- " + x for x in cockpit["minimum_surfaces"]) + "\n\n" +
               "## Runtime boundary\n\n```json\n" + json.dumps(cockpit["runtime_boundary"], indent=2, ensure_ascii=False) + "\n```\n", wrote)

    write_json("outputs/prod8141_8180_monday_demo_readiness_packet.json", result, wrote)
    write_text("outputs/prod8141_8180_monday_demo_readiness_packet.md",
               "# PROD-8141..8180 - Monday Demo Readiness Packet\n\nStatus: " + status + "\n\nDecision: `" + decision + "`\n\n```json\n" + json.dumps(result["calibration_decision"], indent=2, ensure_ascii=False) + "\n```\n", wrote)

    write_text("docs/product/814_MONDAY_DEMO_READINESS_PACKET.md",
               "# 814 - Monday Demo Readiness Packet\n\nCreates executive demo story, Q&A bank and cockpit chat handoff requirements.\n\nDoes not implement micrographs, Delta Matrix, production cockpit or production/client/commercial claims.\n\nNext: `PROD-8181..8220 - Cockpit Chat Scaffold and Diagnostic Monitor Prototype`.\n", wrote)
    return wrote

def commit_plan():
    paths = [
        "apply_prod8141_8180_monday_demo_readiness_packet.py",
        "product/demos/prod8141_8180_monday_demo_readiness_packet.json",
        "product/demos/prod8141_8180_monday_demo_readiness_packet.md",
        "product/demos/prod8141_8180_demo_question_answer_bank.json",
        "product/demos/prod8141_8180_demo_question_answer_bank.md",
        "product/cockpit/prod8141_8180_cockpit_chat_handoff_requirements.json",
        "product/cockpit/prod8141_8180_cockpit_chat_handoff_requirements.md",
        "outputs/prod8141_8180_monday_demo_readiness_packet.json",
        "outputs/prod8141_8180_monday_demo_readiness_packet.md",
        "docs/product/814_MONDAY_DEMO_READINESS_PACKET.md",
    ]
    return "\n".join(["git add \\"] + [f"  {p} \\" for p in paths[:-1]] + [f"  {paths[-1]}", "", 'git commit -m "Add Monday demo readiness packet"', 'git tag -a product-casulo-monday-demo-readiness-v0.1 HEAD -m "CASULO Monday demo readiness v0.1"', "git push origin main", "git push origin product-casulo-monday-demo-readiness-v0.1"])

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

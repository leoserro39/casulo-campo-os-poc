#!/usr/bin/env python3
"""
CASULO PROD-8181..8220 - Cockpit Chat Scaffold and Diagnostic Monitor Prototype

Purpose:
  - continue after PROD-8141..8180;
  - create a local/static cockpit chat scaffold;
  - create a diagnostic monitor prototype powered by the existing Runtime Context Packet,
    Agent Instruction Pack, Inference Gate Prompt and Evaluate Model;
  - provide a simple browser UI with canned operator prompts and deterministic local responses;
  - prepare the next phase: local static runtime / browser validation.

This patcher does NOT:
  - call GPT;
  - run Codex;
  - connect/write to Neo4j;
  - implement micrographs;
  - implement Delta Matrix;
  - implement production cockpit;
  - allow client/production/commercial claims.

Usage:
  python3 apply_prod8181_8220_cockpit_chat_scaffold_diagnostic_monitor.py --check
  python3 apply_prod8181_8220_cockpit_chat_scaffold_diagnostic_monitor.py --apply --commit-plan
"""

from __future__ import annotations
import argparse, json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()
PHASE = "PROD-8181..8220"

REQUIRED = [
    "outputs/prod8141_8180_monday_demo_readiness_packet.json",
    "product/cockpit/prod8141_8180_cockpit_chat_handoff_requirements.json",
    "product/agent/prod8101_8140_agent_instruction_pack.json",
    "product/exocortex/runtime_context_packets/prod8101_8140_runtime_context_packet_exp50.json",
    "product/inference_gates/prod8101_8140_inference_gate_prompt_v0_1.json",
    "product/evaluate/prod8101_8140_diagnostic_monitoring_solution_evaluate_model.json",
]

BLOCKED_ACTIONS = [
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
    "docker_volume_delete",
    "micrograph_runtime_claim",
    "delta_matrix_runtime_claim",
    "state_family_runtime_claim",
    "multi_llm_braid_runtime_claim",
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
            "product/cockpit/prod8181_8220_cockpit_chat_scaffold.json",
            "product/cockpit/prod8181_8220_cockpit_chat_scaffold.md",
            "product/cockpit/static/prod8181_8220/index.html",
            "product/cockpit/static/prod8181_8220/app.js",
            "product/cockpit/static/prod8181_8220/styles.css",
            "product/cockpit/static/prod8181_8220/README.md",
            "product/cockpit/static/prod8181_8220/sample_runtime_context_packet.json",
            "product/cockpit/static/prod8181_8220/sample_evaluate_model.json",
            "outputs/prod8181_8220_cockpit_chat_scaffold_diagnostic_monitor.json",
            "outputs/prod8181_8220_cockpit_chat_scaffold_diagnostic_monitor.md",
            "docs/product/818_COCKPIT_CHAT_SCAFFOLD_DIAGNOSTIC_MONITOR.md",
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
    out8141 = read_json("outputs/prod8141_8180_monday_demo_readiness_packet.json", {})
    cal8141 = out8141.get("calibration_decision", {})
    rcp = read_json("product/exocortex/runtime_context_packets/prod8101_8140_runtime_context_packet_exp50.json", {})
    eval_model = read_json("product/evaluate/prod8101_8140_diagnostic_monitoring_solution_evaluate_model.json", {})
    checks = {
        "prior_8141_status_pass": out8141.get("status") == "PASS",
        "monday_demo_readiness_packet_ready": cal8141.get("monday_demo_readiness_packet_ready") is True,
        "cockpit_chat_handoff_ready": cal8141.get("cockpit_chat_handoff_ready") is True,
        "ready_for_cockpit_chat_scaffold": cal8141.get("ready_for_cockpit_chat_scaffold") is True,
        "ready_for_local_diagnostic_monitor_prototype": cal8141.get("ready_for_local_diagnostic_monitor_prototype") is True,
        "client_claim_blocked": cal8141.get("ready_for_client_claim") is False,
        "production_blocked": cal8141.get("ready_for_production") is False,
        "commercial_claim_blocked": cal8141.get("commercial_claim_allowed") is False,
        "micrographs_not_implemented": cal8141.get("micrographs_implemented") is False,
        "delta_matrix_not_implemented": cal8141.get("delta_matrix_implemented") is False,
        "runtime_context_packet_present": rcp.get("version") == "runtime_context_packet.v0.1",
        "evaluate_model_present": eval_model.get("version") == "diagnostic_monitoring_solution_evaluate_model.v0.1",
    }
    ready = all(checks.values())
    return {
        "checks": checks,
        "cockpit_chat_scaffold_ready": ready,
        "diagnostic_monitor_prototype_ready": ready,
        "static_ui_ready": ready,
        "sample_data_ready": ready,
        "local_browser_validation_ready": ready,
        "ready_for_local_static_runtime_validation": ready,
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "commercial_claim_allowed": False,
        "micrographs_implemented": False,
        "delta_matrix_implemented": False,
        "production_cockpit_implemented": False,
        "live_gpt_integrated": False,
        "neo4j_write_integrated": False,
        "next_phase": "PROD-8221..8260 - Local Static Cockpit Runtime Validation",
    }

def build_scaffold():
    return {
        "version": "cockpit_chat_scaffold.v0.1",
        "phase": PHASE,
        "purpose": "Local/static operator cockpit for CASULO Exocortex Foundation demo.",
        "surfaces": [
            {
                "name": "Status Header",
                "purpose": "Show phase, gate, readiness and blocked claims.",
            },
            {
                "name": "Cockpit Chat",
                "purpose": "Operator asks for state, diagnostic report, monitoring summary or simple solution options.",
            },
            {
                "name": "Evidence Panel",
                "purpose": "Show runtime context packet evidence refs and graph summary.",
            },
            {
                "name": "Diagnostic Report Panel",
                "purpose": "Show supported facts, gaps, risks, gate, allowed and blocked actions.",
            },
            {
                "name": "Monitoring Panel",
                "purpose": "Show current state, readiness, blocked claims, risk and follow-up.",
            },
            {
                "name": "Simple Solution Panel",
                "purpose": "Show internal/reviewable solution options only.",
            },
            {
                "name": "Boundary Panel",
                "purpose": "Keep client, production and commercial claims blocked.",
            },
        ],
        "runtime_mode": {
            "static_local_only": True,
            "deterministic_canned_responses": True,
            "live_gpt": False,
            "codex_execution": False,
            "neo4j_write": False,
            "production": False,
        },
    }

def html():
    return """<!doctype html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>CASULO Cockpit Chat - Exocortex Foundation</title>
  <link rel="stylesheet" href="./styles.css" />
</head>
<body>
  <header class="topbar">
    <div>
      <p class="eyebrow">CASULO Campo OS</p>
      <h1>Cockpit Chat — Exocortex Foundation</h1>
      <p class="subtitle">Protótipo local/static para diagnóstico, monitoramento e soluções simples internas.</p>
    </div>
    <div class="status-pill">SANDBOX / INTERNAL ONLY</div>
  </header>

  <main class="layout">
    <section class="card span-2">
      <h2>Estado atual</h2>
      <div id="stateGrid" class="grid"></div>
    </section>

    <section class="card">
      <h2>Boundary</h2>
      <ul id="blockedClaims"></ul>
    </section>

    <section class="card chat-card">
      <h2>Cockpit Chat</h2>
      <div class="quick-actions">
        <button data-prompt="estado">Estado</button>
        <button data-prompt="diagnostico">Diagnóstico</button>
        <button data-prompt="monitoramento">Monitoramento</button>
        <button data-prompt="solucoes">Soluções simples</button>
      </div>
      <textarea id="operatorInput" placeholder="Pergunte sobre estado, diagnóstico, monitoramento ou solução simples..."></textarea>
      <button id="askBtn">Gerar resposta controlada</button>
      <div id="chatOutput" class="chat-output"></div>
    </section>

    <section class="card">
      <h2>Evidências</h2>
      <ul id="evidenceRefs"></ul>
    </section>

    <section class="card span-2">
      <h2>Relatório de diagnóstico</h2>
      <div id="diagnosticPanel"></div>
    </section>

    <section class="card">
      <h2>Monitoramento</h2>
      <div id="monitorPanel"></div>
    </section>

    <section class="card">
      <h2>Soluções simples</h2>
      <div id="solutionPanel"></div>
    </section>
  </main>

  <footer>
    Não usa GPT ao vivo. Não escreve no Neo4j. Não ativa produção. Não libera claim comercial/cliente.
  </footer>

  <script src="./app.js"></script>
</body>
</html>
"""

def css():
    return """:root {
  --bg: #0f172a;
  --panel: #111827;
  --panel-2: #1f2937;
  --text: #e5e7eb;
  --muted: #9ca3af;
  --line: #374151;
  --accent: #38bdf8;
  --ok: #22c55e;
  --warn: #f59e0b;
  --bad: #ef4444;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
  background: radial-gradient(circle at top left, #1e293b 0, var(--bg) 42%);
  color: var(--text);
}
.topbar {
  padding: 28px;
  display: flex;
  justify-content: space-between;
  gap: 20px;
  border-bottom: 1px solid var(--line);
}
.eyebrow { color: var(--accent); text-transform: uppercase; letter-spacing: .14em; font-size: 12px; margin: 0 0 6px; }
h1 { margin: 0; font-size: 28px; }
h2 { margin: 0 0 14px; font-size: 18px; }
.subtitle { color: var(--muted); margin: 8px 0 0; }
.status-pill {
  align-self: start;
  border: 1px solid var(--accent);
  color: var(--accent);
  padding: 10px 14px;
  border-radius: 999px;
  font-weight: 700;
  white-space: nowrap;
}
.layout {
  padding: 24px;
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 16px;
}
.card {
  background: rgba(17, 24, 39, .88);
  border: 1px solid var(--line);
  border-radius: 18px;
  padding: 18px;
  box-shadow: 0 14px 40px rgba(0,0,0,.24);
}
.span-2 { grid-column: span 2; }
.grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 10px;
}
.metric {
  background: var(--panel-2);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 12px;
}
.metric .label { color: var(--muted); font-size: 12px; }
.metric .value { font-size: 16px; margin-top: 6px; font-weight: 800; }
ul { margin: 0; padding-left: 18px; color: var(--muted); }
li { margin-bottom: 8px; }
textarea {
  width: 100%;
  min-height: 90px;
  background: #020617;
  color: var(--text);
  border: 1px solid var(--line);
  border-radius: 12px;
  padding: 12px;
  margin: 12px 0;
}
button {
  background: var(--accent);
  color: #082f49;
  border: 0;
  border-radius: 12px;
  padding: 10px 12px;
  font-weight: 800;
  cursor: pointer;
}
.quick-actions { display: flex; flex-wrap: wrap; gap: 8px; }
.chat-output, #diagnosticPanel, #monitorPanel, #solutionPanel {
  background: #020617;
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 14px;
  min-height: 90px;
  color: var(--muted);
  white-space: pre-wrap;
}
footer { color: var(--muted); padding: 0 24px 24px; }
@media (max-width: 900px) {
  .layout { grid-template-columns: 1fr; }
  .span-2 { grid-column: span 1; }
  .topbar { flex-direction: column; }
  .grid { grid-template-columns: 1fr; }
}
"""

def js():
    return """const runtimeContext = {
  current_state: {
    casulo_state: "EXOCORTEX_FOUNDATION_ACTIVE",
    exp50_graph_confirmed: true,
    read_only_retrieval_confirmed: true,
    operator_evidence_packet_ready: true,
    client_claim_allowed: false,
    production_allowed: false,
    commercial_claim_allowed: false,
    micrographs_implemented: false,
    delta_matrix_implemented: false
  },
  blocked_claims: [
    "client-validated result",
    "production-ready result",
    "commercially validated product",
    "validated hallucination reduction",
    "validated model gain",
    "micrograph runtime implemented",
    "Delta Matrix runtime implemented",
    "production cockpit implemented"
  ],
  evidence_refs: [
    "outputs/prod8021_8060_exp50_read_only_retrieval_result_ingestion_confirmation_gate.json",
    "outputs/prod8061_8100_exp50_operator_evidence_packet_scope_boundary_review.json",
    "outputs/prod8061a_exocortex_foundation_statement_addendum.json",
    "outputs/prod8101_8140_internal_demo_script_agent_instruction_pack.json",
    "outputs/prod8141_8180_monday_demo_readiness_packet.json"
  ]
};

const responses = {
  estado: `Estado controlado: Exocortex Foundation ativo. O sistema confirmou EXP50 read-only retrieval em sandbox, preserva boundaries e prepara contexto limpo para o agent. Cliente, produção e comercial seguem bloqueados.`,
  diagnostico: `Relatório diagnóstico interno:
- Fatos: EXP50 confirmado, Exocortex Foundation ativo, Runtime Context Packet pronto.
- Lacunas: runtime completo do Memory Governor ainda não implementado; micrografos e Delta Matrix não implementados.
- Gate: SANDBOX_ONLY / HUMAN_REVIEW_REQUIRED.
- Próxima ação segura: usar o cockpit scaffold para revisão interna e demonstração controlada.`,
  monitoramento: `Monitoramento:
- Readiness interno: pronto para demo/cockpit scaffold.
- Risco: médio controlado, pois há boundaries explícitos.
- Claims bloqueados: cliente, produção, comercial, ganho validado, redução de alucinação validada.
- Follow-up: validar cockpit local e depois planejar runtime controlado.`,
  solucoes: `Soluções simples internas:
1. Matriz de diagnóstico por domínio.
2. Checklist de revisão humana.
3. Relatório de gaps e riscos.
4. Painel de monitoramento local.
5. Plano sandbox reversível.
Nenhuma solução autoriza produção ou claim externo.`
};

function renderState() {
  const grid = document.getElementById("stateGrid");
  grid.innerHTML = "";
  Object.entries(runtimeContext.current_state).forEach(([k, v]) => {
    const div = document.createElement("div");
    div.className = "metric";
    div.innerHTML = `<div class="label">${k}</div><div class="value">${String(v).toUpperCase()}</div>`;
    grid.appendChild(div);
  });

  const blocked = document.getElementById("blockedClaims");
  blocked.innerHTML = runtimeContext.blocked_claims.map(x => `<li>${x}</li>`).join("");

  const evidence = document.getElementById("evidenceRefs");
  evidence.innerHTML = runtimeContext.evidence_refs.map(x => `<li>${x}</li>`).join("");

  document.getElementById("diagnosticPanel").textContent = responses.diagnostico;
  document.getElementById("monitorPanel").textContent = responses.monitoramento;
  document.getElementById("solutionPanel").textContent = responses.solucoes;
}

function answer(kind) {
  const text = document.getElementById("operatorInput").value.toLowerCase();
  let key = kind || "estado";
  if (!kind) {
    if (text.includes("diagn")) key = "diagnostico";
    else if (text.includes("monitor")) key = "monitoramento";
    else if (text.includes("solu")) key = "solucoes";
  }
  document.getElementById("chatOutput").textContent = responses[key] || responses.estado;
}

document.addEventListener("DOMContentLoaded", () => {
  renderState();
  document.getElementById("askBtn").addEventListener("click", () => answer());
  document.querySelectorAll("[data-prompt]").forEach(btn => {
    btn.addEventListener("click", () => {
      const key = btn.getAttribute("data-prompt");
      document.getElementById("operatorInput").value = key;
      answer(key);
    });
  });
});
"""

def apply():
    wrote = []
    ev = evaluate()
    status = "PASS" if ev["cockpit_chat_scaffold_ready"] else "FAIL"
    decision = "COCKPIT_CHAT_SCAFFOLD_DIAGNOSTIC_MONITOR_READY_FOR_LOCAL_STATIC_RUNTIME_VALIDATION" if status == "PASS" else "COCKPIT_CHAT_SCAFFOLD_NOT_READY_REVIEW_REQUIRED"
    scaffold = build_scaffold()
    result = {
        "status": status,
        "phase": PHASE,
        "decision": decision,
        "generated_at": STAMP,
        "evaluation": ev,
        "calibration_decision": {
            "cockpit_chat_scaffold_ready": ev["cockpit_chat_scaffold_ready"],
            "diagnostic_monitor_prototype_ready": ev["diagnostic_monitor_prototype_ready"],
            "static_ui_ready": ev["static_ui_ready"],
            "sample_data_ready": ev["sample_data_ready"],
            "local_browser_validation_ready": ev["local_browser_validation_ready"],
            "ready_for_local_static_runtime_validation": ev["ready_for_local_static_runtime_validation"],
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "commercial_claim_allowed": False,
            "micrographs_implemented": False,
            "delta_matrix_implemented": False,
            "production_cockpit_implemented": False,
            "live_gpt_integrated": False,
            "neo4j_write_integrated": False,
        },
        "next": ev["next_phase"],
    }

    write_json("product/cockpit/prod8181_8220_cockpit_chat_scaffold.json", scaffold, wrote)
    write_text("product/cockpit/prod8181_8220_cockpit_chat_scaffold.md",
               "# Cockpit Chat Scaffold\n\nLocal/static cockpit for Exocortex Foundation demo.\n\n" +
               "## Surfaces\n\n" + "\n".join("- " + s["name"] + ": " + s["purpose"] for s in scaffold["surfaces"]) +
               "\n\n## Runtime mode\n\n```json\n" + json.dumps(scaffold["runtime_mode"], indent=2, ensure_ascii=False) + "\n```\n", wrote)

    write_text("product/cockpit/static/prod8181_8220/index.html", html(), wrote)
    write_text("product/cockpit/static/prod8181_8220/app.js", js(), wrote)
    write_text("product/cockpit/static/prod8181_8220/styles.css", css(), wrote)
    write_text("product/cockpit/static/prod8181_8220/README.md",
               "# CASULO Cockpit Chat Scaffold\n\nRun locally:\n\n```bash\ncd product/cockpit/static/prod8181_8220\npython3 -m http.server 4181\n```\n\nOpen the forwarded port/page in Codespaces.\n\nThis is static/local only. No live GPT, no Neo4j write, no production.\n", wrote)

    rcp = read_json("product/exocortex/runtime_context_packets/prod8101_8140_runtime_context_packet_exp50.json", {})
    eval_model = read_json("product/evaluate/prod8101_8140_diagnostic_monitoring_solution_evaluate_model.json", {})
    write_json("product/cockpit/static/prod8181_8220/sample_runtime_context_packet.json", rcp, wrote)
    write_json("product/cockpit/static/prod8181_8220/sample_evaluate_model.json", eval_model, wrote)

    write_json("outputs/prod8181_8220_cockpit_chat_scaffold_diagnostic_monitor.json", result, wrote)
    write_text("outputs/prod8181_8220_cockpit_chat_scaffold_diagnostic_monitor.md",
               "# PROD-8181..8220 - Cockpit Chat Scaffold and Diagnostic Monitor Prototype\n\nStatus: " + status + "\n\nDecision: `" + decision + "`\n\n```json\n" + json.dumps(result["calibration_decision"], indent=2, ensure_ascii=False) + "\n```\n", wrote)

    write_text("docs/product/818_COCKPIT_CHAT_SCAFFOLD_DIAGNOSTIC_MONITOR.md",
               "# 818 - Cockpit Chat Scaffold and Diagnostic Monitor Prototype\n\nCreates a local/static cockpit chat scaffold with diagnostic, monitoring and simple solution panels.\n\nDoes not call GPT, run Codex, write Neo4j, implement micrographs, implement Delta Matrix or authorize production/client/commercial claims.\n\nRun:\n\n```bash\ncd product/cockpit/static/prod8181_8220\npython3 -m http.server 4181\n```\n", wrote)
    return wrote

def commit_plan():
    paths = [
        "apply_prod8181_8220_cockpit_chat_scaffold_diagnostic_monitor.py",
        "product/cockpit/prod8181_8220_cockpit_chat_scaffold.json",
        "product/cockpit/prod8181_8220_cockpit_chat_scaffold.md",
        "product/cockpit/static/prod8181_8220/index.html",
        "product/cockpit/static/prod8181_8220/app.js",
        "product/cockpit/static/prod8181_8220/styles.css",
        "product/cockpit/static/prod8181_8220/README.md",
        "product/cockpit/static/prod8181_8220/sample_runtime_context_packet.json",
        "product/cockpit/static/prod8181_8220/sample_evaluate_model.json",
        "outputs/prod8181_8220_cockpit_chat_scaffold_diagnostic_monitor.json",
        "outputs/prod8181_8220_cockpit_chat_scaffold_diagnostic_monitor.md",
        "docs/product/818_COCKPIT_CHAT_SCAFFOLD_DIAGNOSTIC_MONITOR.md",
    ]
    return "\n".join(["git add \\"] + [f"  {p} \\" for p in paths[:-1]] + [f"  {paths[-1]}", "", 'git commit -m "Add cockpit chat scaffold diagnostic monitor"', 'git tag -a product-casulo-cockpit-chat-scaffold-v0.1 HEAD -m "CASULO cockpit chat scaffold v0.1"', "git push origin main", "git push origin product-casulo-cockpit-chat-scaffold-v0.1"])

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

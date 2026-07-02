const runtimeContext = {
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

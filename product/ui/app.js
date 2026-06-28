const api = {
  health: "/api/health",
  status: "/api/product/status",
  verticals: "/api/verticals",
  vfState: "/api/verticals/vesselflow/state-request",
  vfManifest: "/api/vesselflow/import-manifest",
  reports: "/api/reports",
};

const state = {};

async function fetchJson(url) {
  const res = await fetch(url);
  if (!res.ok) throw new Error(`${url}: ${res.status}`);
  return await res.json();
}

function pretty(obj) {
  return JSON.stringify(obj, null, 2);
}

function setText(id, text) {
  const el = document.getElementById(id);
  if (el) el.textContent = text;
}

function list(id, items) {
  const el = document.getElementById(id);
  if (!el) return;
  el.innerHTML = "";
  (items || []).forEach(item => {
    const li = document.createElement("li");
    li.textContent = item;
    el.appendChild(li);
  });
}

function card(title, body) {
  const article = document.createElement("article");
  article.className = "card";
  const h3 = document.createElement("h3");
  h3.textContent = title;
  const pre = document.createElement("pre");
  pre.textContent = body;
  article.appendChild(h3);
  article.appendChild(pre);
  return article;
}

function renderVerticals(data) {
  const root = document.getElementById("verticalCards");
  root.innerHTML = "";
  data.verticals.forEach(v => {
    const article = document.createElement("article");
    article.className = "card";
    article.innerHTML = `
      <h3>${v.vertical_name}</h3>
      <p><strong>ID:</strong> ${v.vertical_id}</p>
      <p><strong>Complexidade:</strong> ${v.complexity}</p>
      <p><strong>Domínios:</strong> ${v.domains_count}</p>
      <p><strong>Entidades:</strong> ${v.entities_count}</p>
      <p><strong>Gates:</strong> ${v.gates_count}</p>
    `;
    root.appendChild(article);
  });
}

function renderCubeFaces(vfState) {
  const root = document.getElementById("cubeFaces");
  root.innerHTML = "";
  const faces = vfState.state_request.cube.faces || {};
  Object.entries(faces).forEach(([name, meaning]) => {
    const div = document.createElement("div");
    div.className = "cube-face";
    div.innerHTML = `<strong>${name}</strong><span>${meaning}</span>`;
    root.appendChild(div);
  });
}

function renderReports(data) {
  const root = document.getElementById("reportCards");
  root.innerHTML = "";
  data.reports.forEach(r => {
    root.appendChild(card(r.name, r.exists ? r.preview : "Nao encontrado"));
  });
}

async function load() {
  try {
    state.health = await fetchJson(api.health);
    state.status = await fetchJson(api.status);
    state.verticals = await fetchJson(api.verticals);
    state.vfState = await fetchJson(api.vfState);
    state.vfManifest = await fetchJson(api.vfManifest);
    state.reports = await fetchJson(api.reports);

    setText("runtimeStatus", `API ${state.health.status}`);
    setText("productStatus", pretty(state.status));
    list("blockedActions", state.status.blocked_actions);
    setText("nextStep", state.status.next_recommended_step);

    renderVerticals(state.verticals);

    const vf = state.verticals.verticals.find(v => v.vertical_id === "vesselflow");
    setText("vesselflowSummary", pretty(vf));
    list("vesselflowGates", state.vfState.state_request.gates);
    renderCubeFaces(state.vfState);

    setText("stateRequest", pretty(state.vfState.state_request));
    setText("importManifest", pretty(state.vfManifest.manifest));
    renderReports(state.reports);
  } catch (err) {
    setText("runtimeStatus", "ERRO");
    setText("productStatus", String(err));
  }
}

document.querySelectorAll(".nav").forEach(button => {
  button.addEventListener("click", () => {
    document.querySelectorAll(".nav").forEach(b => b.classList.remove("active"));
    document.querySelectorAll(".screen").forEach(s => s.classList.remove("active"));
    button.classList.add("active");
    document.getElementById(`screen-${button.dataset.screen}`).classList.add("active");
  });
});

load();

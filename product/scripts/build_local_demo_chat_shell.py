#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2301..2340"
REQ_TAG = "product-demo-scenario-pack-v0.1"

PACK = ROOT / "product/chat/demo_scenario_pack_v0_1.json"
DOC = ROOT / "docs/product/559_LOCAL_DEMO_CHAT_SHELL.md"
CONTRACT = ROOT / "product/contracts/local_demo_chat_shell.contract.json"
SCHEMA = ROOT / "product/schemas/local_demo_chat_shell.schema.json"
HTML = ROOT / "product/demo_chat/index.html"
RUNBOOK = ROOT / "product/demo_chat/RUNBOOK.md"
OUT_JSON = ROOT / "outputs/prod2301_2340_local_demo_chat_shell.json"
OUT_MD = ROOT / "outputs/prod2301_2340_local_demo_chat_shell.md"

BLOCKED = [
    "gpt_call",
    "external_api_call",
    "codex_execution",
    "automatic_merge",
    "production_activation",
    "client_facing_claim"
]

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def tags():
    raw = subprocess.check_output(["git", "tag", "--list"], cwd=ROOT, text=True)
    return set(x.strip() for x in raw.splitlines() if x.strip())

def main():
    errors = []
    pack = read_json(PACK) if PACK.exists() else {}
    scenarios = pack.get("scenarios", [])

    doc = """# PROD-2301..2340 - Local Demo Chat Shell

Static local demo shell for CASULO.

It shows prompt, task type, risk, gate, likely generic answer, CASULO answer and next allowed action.

Boundary: no GPT call, no external API, no Codex, no production and no client-facing claim.
"""

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "static_local_demo_shell",
        "gpt_call_allowed": False,
        "external_api_call_allowed": False,
        "codex_execution_allowed": False,
        "automatic_merge_allowed": False,
        "production_activation_allowed": False,
        "client_facing_claim_allowed": False,
        "recommended_next_phase": "PROD-2341..2380 - Demo Runbook and Evidence Capture",
        "blocked_actions": BLOCKED
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Local Demo Chat Shell",
        "type": "object"
    }

    runbook = """# Local Demo Chat Shell Runbook

Start server from repository root:

python3 -m http.server 4173

Open:

http://127.0.0.1:4173/product/demo_chat/index.html

Boundary: static local demo only. No GPT call, no external API, no Codex, no production.
"""

    html = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CASULO Demo Chat</title>
<style>
body{margin:0;font-family:Arial,Helvetica,sans-serif;background:#0b1020;color:#e8eefc}
header{padding:22px 28px;border-bottom:1px solid #26365e;background:#101833}
h1{margin:0;font-size:24px}.sub{color:#aab6d8;margin-top:6px}
main{display:grid;grid-template-columns:340px 1fr;gap:18px;padding:18px}
.panel{background:#121a35;border:1px solid #26365e;border-radius:14px;padding:16px}
button{width:100%;text-align:left;margin:6px 0;padding:10px;border:1px solid #314673;border-radius:10px;background:#172347;color:#e8eefc;cursor:pointer}
button:hover{background:#20315f}
.badge{display:inline-block;padding:4px 8px;border-radius:999px;background:#263a72;margin-right:6px;font-size:12px}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.box{background:#0e1530;border:1px solid #26365e;border-radius:12px;padding:14px;margin-top:14px}
.muted{color:#aab6d8}.small{font-size:13px;line-height:1.45}pre{white-space:pre-wrap;font-family:inherit}
</style>
</head>
<body>
<header>
<h1>CASULO Demo Chat</h1>
<div class="sub">Resposta genérica provável vs resposta CASULO state-grounded.</div>
</header>
<main>
<section class="panel"><h2>Cenários</h2><div id="list"></div></section>
<section class="panel"><div id="detail">Carregando...</div></section>
</main>
<script>
async function loadPack(){
  const res = await fetch("../chat/demo_scenario_pack_v0_1.json");
  return await res.json();
}
function show(s){
  document.getElementById("detail").innerHTML =
    '<span class="badge">'+s.task_type+'</span>' +
    '<span class="badge">'+s.risk+'</span>' +
    '<span class="badge">'+s.gate+'</span>' +
    '<h2>'+s.title+'</h2>' +
    '<p class="muted">'+s.demo_point+'</p>' +
    '<div class="box"><b>Pedido</b><pre>'+s.prompt+'</pre></div>' +
    '<div class="grid">' +
    '<div class="box"><h3>Resposta genérica provável</h3><p class="small">'+s.generic_response+'</p><h4>Risco</h4><p class="small">'+s.generic_response_risk+'</p></div>' +
    '<div class="box"><h3>Resposta CASULO</h3><p class="small">'+s.casulo_response+'</p><h4>Próxima ação permitida</h4><p class="small">'+s.next_allowed_action+'</p></div>' +
    '</div>';
}
loadPack().then(pack=>{
  const list=document.getElementById("list");
  pack.scenarios.forEach((s,i)=>{
    const b=document.createElement("button");
    b.innerHTML='<b>'+s.id+'</b> - '+s.title+'<br><span class="muted">'+s.task_type+'</span>';
    b.onclick=()=>show(s);
    list.appendChild(b);
    if(i===0) show(s);
  });
}).catch(err=>{
  document.getElementById("detail").innerText="Erro ao carregar cenário: "+err;
});
</script>
</body>
</html>
"""

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write(RUNBOOK, runbook)
    write(HTML, html)

    html_text = HTML.read_text(encoding="utf-8")
    checks = {
        "pack_exists": PACK.exists(),
        "scenario_count": len(scenarios),
        "required_tag_present": REQ_TAG in tags(),
        "html_exists": HTML.exists(),
        "runbook_exists": RUNBOOK.exists(),
        "html_loads_pack": "demo_scenario_pack_v0_1.json" in html_text,
        "html_has_generic": "Resposta genérica provável" in html_text,
        "html_has_casulo": "Resposta CASULO" in html_text,
        "html_has_next_action": "Próxima ação permitida" in html_text,
        "gpt_blocked": contract["gpt_call_allowed"] is False,
        "external_api_blocked": contract["external_api_call_allowed"] is False,
        "codex_blocked": contract["codex_execution_allowed"] is False,
        "production_blocked": contract["production_activation_allowed"] is False,
        "client_claim_blocked": contract["client_facing_claim_allowed"] is False
    }

    if checks["scenario_count"] < 8:
        errors.append("scenario_count below 8")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "LOCAL_DEMO_CHAT_SHELL_READY" if status == "PASS" else "LOCAL_DEMO_CHAT_SHELL_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "local_demo_chat_shell": {
            "html": "product/demo_chat/index.html",
            "runbook": "product/demo_chat/RUNBOOK.md",
            "scenario_count": len(scenarios),
            "local_url": "http://127.0.0.1:4173/product/demo_chat/index.html",
            "recommended_next_phase": contract["recommended_next_phase"],
            "calibration_status": "NOT_CALIBRATED_STATIC_DEMO_SHELL_ONLY"
        },
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2301..2340 Local Demo Chat Shell",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        "- HTML: `product/demo_chat/index.html`",
        "- URL: `http://127.0.0.1:4173/product/demo_chat/index.html`",
        f"- Scenarios: `{len(scenarios)}`",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("url:", result["local_demo_chat_shell"]["local_url"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

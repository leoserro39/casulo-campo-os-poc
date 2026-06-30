#!/usr/bin/env python3
import json, subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2261..2300"
REQ_TAG = "product-demo-chat-comparative-response-engine-v0.1"

ENGINE_OUT = ROOT / "outputs/prod2221_2260_demo_chat_comparative_engine.json"
DOC = ROOT / "docs/product/558_DEMO_SCENARIO_PACK.md"
CONTRACT = ROOT / "product/contracts/demo_scenario_pack.contract.json"
SCHEMA = ROOT / "product/schemas/demo_scenario_pack.schema.json"
PACK = ROOT / "product/chat/demo_scenario_pack_v0_1.json"
OUT_JSON = ROOT / "outputs/prod2261_2300_demo_scenario_pack.json"
OUT_MD = ROOT / "outputs/prod2261_2300_demo_scenario_pack.md"

BLOCKED = ["gpt_call","codex_execution","automatic_merge","production_activation","client_facing_claim","runtime_chat_ui_implementation"]

def jload(p):
    return json.loads(p.read_text(encoding="utf-8"))

def jwrite(p, data):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write(p, text):
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text.rstrip() + "\n", encoding="utf-8")

def tags():
    raw = subprocess.check_output(["git","tag","--list"], cwd=ROOT, text=True)
    return set(x.strip() for x in raw.splitlines() if x.strip())

def main():
    errors = []
    engine = jload(ENGINE_OUT) if ENGINE_OUT.exists() else {}
    comps = engine.get("engine", {}).get("comparisons", [])

    scenario_order = [
        ("D01", "Pergunta simples / produção", "production_activation_request", "Mostra que CASULO responde estado, gate e bloqueio sem florear."),
        ("D02", "Claim cliente", "client_claim_request", "Mostra limite entre evidência interna e fala externa."),
        ("D03", "Merge/Codex", "codex_or_merge_request", "Mostra bloqueio de execução automática sem revisão."),
        ("D04", "Parser/planilha", "parser_generation_request", "Mostra alucinação operacional: código que compila mas inventa estrutura."),
        ("D05", "Produto/MVP", "product_generation_request", "Mostra diferença entre feature dump e spec validável."),
        ("D06", "Pesquisa/stack", "research_request", "Mostra exigência de fonte, data e incerteza."),
        ("D07", "Diagnóstico", "diagnostic_request", "Mostra separação entre sintoma, hipótese e evidência."),
        ("D08", "Arquitetura/solução", "solution_design_request", "Mostra blueprint com escopo, premissas, risco e validação.")
    ]

    by_type = {c["task_type"]: c for c in comps}
    scenarios = []
    for sid, title, task_type, demo_point in scenario_order:
        c = by_type.get(task_type)
        if not c:
            errors.append("missing comparison for " + task_type)
            continue
        scenarios.append({
            "id": sid,
            "title": title,
            "task_type": task_type,
            "demo_point": demo_point,
            "prompt": c["prompt"],
            "risk": c["risk"],
            "gate": c["gate"],
            "generic_response": c["generic_response"],
            "generic_response_risk": c["generic_response_risk"],
            "casulo_response": c["casulo_response"],
            "next_allowed_action": c["next_allowed_action"]
        })

    pack = {
        "version": "demo_scenario_pack.v0.1",
        "purpose": "Feed the local demo chat shell with curated scenarios.",
        "demo_story": [
            "Comece com produção/cliente para mostrar segurança.",
            "Depois mostre merge/Codex para mostrar gate humano.",
            "Use parser como caso técnico mais forte.",
            "Feche com produto, pesquisa, diagnóstico e arquitetura para mostrar valor comercial."
        ],
        "scenarios": scenarios,
        "recommended_next_phase": "PROD-2301..2340 - Local Demo Chat Shell"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "scenario_pack_only",
        "runtime_chat_ui_allowed": False,
        "gpt_call_allowed": False,
        "production_activation_allowed": False,
        "client_facing_claim_allowed": False,
        "recommended_next_phase": "PROD-2301..2340 - Local Demo Chat Shell",
        "blocked_actions": BLOCKED
    }

    schema = {"$schema":"https://json-schema.org/draft/2020-12/schema","title":"CASULO Demo Scenario Pack","type":"object"}
    doc = "# PROD-2261..2300 - Demo Scenario Pack\n\nOrganizes curated demo scenarios for the CASULO local chat shell.\n\nBoundary: no GPT call, no runtime UI, no production and no client-facing claim.\n"

    write(DOC, doc)
    jwrite(CONTRACT, contract)
    jwrite(SCHEMA, schema)
    jwrite(PACK, pack)

    checks = {
        "engine_output_exists": ENGINE_OUT.exists(),
        "prior_engine_pass": engine.get("status") == "PASS",
        "required_tag_present": REQ_TAG in tags(),
        "scenario_count": len(scenarios),
        "has_production": "production_activation_request" in by_type,
        "has_client": "client_claim_request" in by_type,
        "has_merge": "codex_or_merge_request" in by_type,
        "has_parser": "parser_generation_request" in by_type,
        "has_product": "product_generation_request" in by_type,
        "has_research": "research_request" in by_type,
        "has_diagnostic": "diagnostic_request" in by_type,
        "has_solution": "solution_design_request" in by_type,
        "runtime_ui_blocked": contract["runtime_chat_ui_allowed"] is False,
        "gpt_blocked": contract["gpt_call_allowed"] is False,
        "production_blocked": contract["production_activation_allowed"] is False,
        "client_claim_blocked": contract["client_facing_claim_allowed"] is False
    }

    if checks["scenario_count"] < 8:
        errors.append("scenario_count below 8")
    for k,v in checks.items():
        if isinstance(v,bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "DEMO_SCENARIO_PACK_READY" if status == "PASS" else "DEMO_SCENARIO_PACK_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scenario_pack": pack,
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    jwrite(OUT_JSON, result)

    lines = [
        "# PROD-2261..2300 Demo Scenario Pack",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Scenarios: `{len(scenarios)}`",
        f"- Next: `{pack['recommended_next_phase']}`",
        "",
        "## Scenarios"
    ]
    for s in scenarios:
        lines.append(f"- `{s['id']}` {s['title']} -> `{s['task_type']}` | `{s['risk']}` | `{s['gate']}`")
    lines += ["", "## Errors"]
    lines += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(lines))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("scenario_count:", len(scenarios))
    print("errors:", errors)
    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

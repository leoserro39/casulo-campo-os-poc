#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2221..2260"
REQ_TAG = "product-demo-chat-semantic-classifier-v0.1"

CLASSIFIER = ROOT / "product/chat/demo_chat_semantic_classifier_v0_1.json"
DOC = ROOT / "docs/product/557_DEMO_CHAT_COMPARATIVE_ENGINE.md"
CONTRACT = ROOT / "product/contracts/demo_chat_comparative_engine.contract.json"
SCHEMA = ROOT / "product/schemas/demo_chat_comparative_engine.schema.json"
ENGINE = ROOT / "product/chat/demo_chat_comparative_engine_v0_1.json"
OUT_JSON = ROOT / "outputs/prod2221_2260_demo_chat_comparative_engine.json"
OUT_MD = ROOT / "outputs/prod2221_2260_demo_chat_comparative_engine.md"

BLOCKED = [
    "gpt_call",
    "codex_execution",
    "automatic_merge",
    "production_activation",
    "client_facing_claim",
    "runtime_chat_ui_implementation"
]

SCENARIOS = [
    "Esse estado ja libera producao?",
    "Podemos apresentar isso ao cliente como evidencia validada?",
    "Transforme esse delta em codigo e faca merge automatico.",
    "Crie um parser para essa planilha e ja implemente.",
    "Crie um produto de IA para pequenos negocios.",
    "Pesquise o mercado e recomende a melhor stack.",
    "Diagnostique por que esse fluxo falhou.",
    "Desenhe uma arquitetura para essa solucao."
]

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")

def tags():
    raw = subprocess.check_output(["git", "tag", "--list"], cwd=ROOT, text=True)
    return set(x.strip() for x in raw.splitlines() if x.strip())

def classify(prompt, tasks):
    p = prompt.lower()
    best = None
    for t in tasks:
        score = sum(1 for s in t.get("signals", []) if s.lower() in p)
        candidate = (score, t.get("priority", 0), t)
        if best is None or candidate[:2] > best[:2]:
            best = candidate
    if best and best[0] > 0:
        return best[2]
    return next(t for t in tasks if t["name"] == "simple_state_question")

def generic_response(task):
    return (
        "Resposta genérica provável: seguiria com uma recomendação plausível, "
        "mas poderia omitir gate, evidência, contrato, validação ou ação bloqueada."
    )

def casulo_response(task):
    return (
        f"Classificação: {task['name']}. "
        f"Risco: {task['risk']}. Gate: {task['gate']}. "
        f"Modo de saída: {task['mode']}. "
        f"Resposta: {task['casulo']} "
        f"Próxima ação permitida: produzir o artefato intermediário antes da execução final."
    )

def main():
    errors = []

    classifier = read_json(CLASSIFIER) if CLASSIFIER.exists() else {}
    tasks = classifier.get("task_types", [])

    doc = """# PROD-2221..2260 - Demo Chat Comparative Engine

Creates the deterministic comparison layer for the demo chat.

It compares generic plausible output against CASULO state-grounded output.

Boundary: no GPT call, no Codex, no runtime UI, no merge, no production and no client-facing claim.
"""
    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "deterministic_comparison_not_runtime_ui",
        "gpt_call_allowed": False,
        "codex_execution_allowed": False,
        "automatic_merge_allowed": False,
        "production_activation_allowed": False,
        "client_facing_claim_allowed": False,
        "runtime_chat_ui_allowed": False,
        "recommended_next_phase": "PROD-2261..2300 - Demo Scenario Pack",
        "later_phase": "PROD-2301..2340 - Local Demo Chat Shell",
        "blocked_actions": BLOCKED
    }
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Demo Chat Comparative Engine",
        "type": "object",
        "required": ["status", "phase", "decision", "engine", "checks", "blocked_actions"]
    }
    engine = {
        "version": "demo_chat_comparative_engine.v0.1",
        "input": "user_prompt",
        "output": [
            "task_type",
            "risk",
            "gate",
            "generic_response",
            "generic_response_risk",
            "casulo_response",
            "problems_avoided",
            "next_allowed_action"
        ]
    }

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(ENGINE, engine)

    comparisons = []
    for prompt in SCENARIOS:
        task = classify(prompt, tasks)
        comparisons.append({
            "prompt": prompt,
            "task_type": task["name"],
            "risk": task["risk"],
            "gate": task["gate"],
            "mode": task["mode"],
            "required_evidence": task["evidence"],
            "generic_response": generic_response(task),
            "generic_response_risk": task["generic_risk"],
            "casulo_response": casulo_response(task),
            "problems_avoided": [
                "missing_gate",
                "missing_evidence",
                "unsafe_action",
                "generic_output",
                "rework"
            ],
            "next_allowed_action": f"Produce {task['mode']} before final execution."
        })

    types = {c["task_type"] for c in comparisons}

    checks = {
        "classifier_exists": CLASSIFIER.exists(),
        "required_tag_present": REQ_TAG in tags(),
        "task_count": len(tasks),
        "comparison_count": len(comparisons),
        "has_production": "production_activation_request" in types,
        "has_client": "client_claim_request" in types,
        "has_merge": "codex_or_merge_request" in types,
        "has_parser": "parser_generation_request" in types,
        "has_product": "product_generation_request" in types,
        "has_research": "research_request" in types,
        "has_diagnostic": "diagnostic_request" in types,
        "has_solution": "solution_design_request" in types,
        "all_have_generic": all(c["generic_response"] for c in comparisons),
        "all_have_casulo": all(c["casulo_response"] for c in comparisons),
        "all_have_gate": all(c["gate"] for c in comparisons),
        "gpt_blocked": contract["gpt_call_allowed"] is False,
        "codex_blocked": contract["codex_execution_allowed"] is False,
        "merge_blocked": contract["automatic_merge_allowed"] is False,
        "production_blocked": contract["production_activation_allowed"] is False,
        "client_claim_blocked": contract["client_facing_claim_allowed"] is False,
        "runtime_ui_blocked": contract["runtime_chat_ui_allowed"] is False
    }

    if checks["task_count"] < 10:
        errors.append("task_count below 10")
    if checks["comparison_count"] < 8:
        errors.append("comparison_count below 8")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": "DEMO_CHAT_COMPARATIVE_ENGINE_READY" if status == "PASS" else "DEMO_CHAT_COMPARATIVE_ENGINE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "engine": {
            "version": engine["version"],
            "comparison_count": len(comparisons),
            "comparisons": comparisons,
            "recommended_next_phase": contract["recommended_next_phase"],
            "later_phase": contract["later_phase"],
            "calibration_status": "NOT_CALIBRATED_DEMO_COMPARISON_ONLY"
        },
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    lines = [
        "# PROD-2221..2260 Demo Chat Comparative Engine",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Comparisons: `{len(comparisons)}`",
        f"- Next: `{contract['recommended_next_phase']}`",
        "",
        "## Comparisons"
    ]
    for c in comparisons:
        lines.append(f"- `{c['task_type']}` | risk `{c['risk']}` | gate `{c['gate']}` | prompt: {c['prompt']}")
    lines += ["", "## Errors"]
    lines += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(lines))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("comparison_count:", len(comparisons))
    print("errors:", errors)
    for c in comparisons:
        print(c["task_type"], "|", c["risk"], "|", c["gate"])

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

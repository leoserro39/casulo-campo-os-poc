#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2181..2220"
DECISION = "DEMO_CHAT_SEMANTIC_CLASSIFIER_READY"
TAG_REQUIRED = "product-capability-state-ontology-living-company-state-anchor-v0.1"

DOC = ROOT / "docs/product/556_DEMO_CHAT_SEMANTIC_CLASSIFIER.md"
CONTRACT = ROOT / "product/contracts/demo_chat_semantic_classifier.contract.json"
SCHEMA = ROOT / "product/schemas/demo_chat_semantic_classifier.schema.json"
CLASSIFIER = ROOT / "product/chat/demo_chat_semantic_classifier_v0_1.json"
PRIOR = ROOT / "outputs/prod2141_2180_capability_state_ontology_living_company_state_anchor.json"
OUT_JSON = ROOT / "outputs/prod2181_2220_demo_chat_semantic_classifier.json"
OUT_MD = ROOT / "outputs/prod2181_2220_demo_chat_semantic_classifier.md"

BLOCKED = [
    "client_facing_claim",
    "validated_commercial_claim",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "gpt_call",
    "codex_execution",
    "runtime_chat_ui_implementation",
    "final_calibration"
]

TASKS = [
    {
        "name": "production_activation_request",
        "priority": 100,
        "risk": "critical",
        "signals": ["producao", "produção", "liberar", "libera", "ativar", "go live", "deploy"],
        "gate": "PRODUCTION_REVIEW_REQUIRED",
        "mode": "PRODUCTION_REVIEW_PACKET",
        "evidence": ["production_gate", "tests", "rollback", "approval"],
        "generic_risk": "Pode liberar produção sem gate, rollback ou aprovação.",
        "casulo": "Bloqueia produção e exige gate, evidência, rollback e revisão."
    },
    {
        "name": "client_claim_request",
        "priority": 95,
        "risk": "critical",
        "signals": ["cliente", "apresentar", "claim", "evidencia validada", "evidência validada", "conformidade"],
        "gate": "CLIENT_CLAIM_REVIEW_REQUIRED",
        "mode": "CLIENT_CLAIM_REVIEW_PACKET",
        "evidence": ["evidence_status", "review_status", "approval"],
        "generic_risk": "Pode transformar evidência fraca em claim externo.",
        "casulo": "Bloqueia claim cliente até evidência e aprovação."
    },
    {
        "name": "codex_or_merge_request",
        "priority": 90,
        "risk": "critical",
        "signals": ["codex", "merge", "commit", "push", "pull request", "automatico", "automático"],
        "gate": "HUMAN_REVIEW_REQUIRED",
        "mode": "HUMAN_REVIEW_PACKET",
        "evidence": ["repo_state", "checks", "approval", "rollback"],
        "generic_risk": "Pode sugerir execução, commit ou merge prematuro.",
        "casulo": "Bloqueia Codex/merge e gera pacote de revisão."
    },
    {
        "name": "parser_generation_request",
        "priority": 85,
        "risk": "critical",
        "signals": ["parser", "planilha", "excel", "xlsx", "abas", "colunas", "schema"],
        "gate": "SCHEMA_REQUIRED",
        "mode": "PARSER_CONTRACT_PACKET",
        "evidence": ["workbook_inventory", "schema", "fixture", "golden_output", "validator"],
        "generic_risk": "Pode gerar código que compila, mas inventa abas, colunas e regras.",
        "casulo": "Bloqueia parser final e exige inventário, schema, fixture, golden output e validador."
    },
    {
        "name": "implementation_request",
        "priority": 80,
        "risk": "critical",
        "signals": ["implemente", "codigo", "código", "patch", "script", "desenvolver"],
        "gate": "IMPLEMENTATION_REVIEW_REQUIRED",
        "mode": "IMPLEMENTATION_PACKET",
        "evidence": ["repo_state", "contract", "tests", "validator"],
        "generic_risk": "Pode gerar código sem contrato, teste ou estado real do repo.",
        "casulo": "Exige repo state, contrato, testes, validação e rollback antes de implementar."
    },
    {
        "name": "product_generation_request",
        "priority": 70,
        "risk": "high",
        "signals": ["produto", "mvp", "pacote", "oferta", "funcionalidades"],
        "gate": "PRODUCT_REVIEW_REQUIRED",
        "mode": "PRODUCT_SPEC_PACKET",
        "evidence": ["target_user", "pain", "scope", "validation_plan"],
        "generic_risk": "Pode gerar lista bonita de features sem validação ou escopo.",
        "casulo": "Gera especificação limitada, hipótese de valor, escopo e plano de validação."
    },
    {
        "name": "solution_design_request",
        "priority": 65,
        "risk": "high",
        "signals": ["arquitetura", "modelo", "fluxo", "sistema", "solucao", "solução"],
        "gate": "SOLUTION_REVIEW_REQUIRED",
        "mode": "SOLUTION_BLUEPRINT",
        "evidence": ["problem", "constraints", "target_state", "acceptance_criteria"],
        "generic_risk": "Pode desenhar arquitetura sem restrição real.",
        "casulo": "Gera blueprint com escopo, premissas, riscos, validação e próximo passo."
    },
    {
        "name": "research_request",
        "priority": 60,
        "risk": "high",
        "signals": ["pesquise", "pesquisa", "mercado", "referencias", "referências", "artigos", "stack"],
        "gate": "SOURCE_REVIEW_REQUIRED",
        "mode": "RESEARCH_PACKET",
        "evidence": ["sources", "dates", "citations", "uncertainty"],
        "generic_risk": "Pode responder de memória, sem fonte ou com informação vencida.",
        "casulo": "Exige fonte, data, incerteza, lacunas e próximo teste."
    },
    {
        "name": "diagnostic_request",
        "priority": 50,
        "risk": "high",
        "signals": ["diagnostico", "diagnóstico", "diagnostique", "problema", "erro", "falhou", "falha", "causa"],
        "gate": "DIAGNOSTIC_REVIEW_REQUIRED",
        "mode": "DIAGNOSTIC_PACKET",
        "evidence": ["symptom", "artifact", "state_snapshot", "validator"],
        "generic_risk": "Pode inventar causa raiz sem evidência.",
        "casulo": "Separa sintoma, hipótese, evidência, risco e validação."
    },
    {
        "name": "simple_state_question",
        "priority": 10,
        "risk": "medium",
        "signals": ["pode", "status", "pronto", "estado", "o que fazer agora"],
        "gate": "STATE_REVIEW_REQUIRED",
        "mode": "STATE_ANSWER",
        "evidence": ["state_snapshot", "gate", "blocked_actions"],
        "generic_risk": "Pode responder sim/não sem gate.",
        "casulo": "Responde curto: estado, gate, risco e próxima ação permitida."
    }
]

SCENARIOS = [
    ("DEMO-PROD", "Esse estado ja libera producao?", "production_activation_request"),
    ("DEMO-CLIENT", "Podemos apresentar isso ao cliente como evidencia validada?", "client_claim_request"),
    ("DEMO-MERGE", "Transforme esse delta em codigo e faca merge automatico.", "codex_or_merge_request"),
    ("DEMO-PARSER", "Crie um parser para essa planilha e ja implemente.", "parser_generation_request"),
    ("DEMO-PRODUCT", "Crie um produto de IA para pequenos negocios.", "product_generation_request"),
    ("DEMO-RESEARCH", "Pesquise o mercado e recomende a melhor stack.", "research_request"),
    ("DEMO-DIAG", "Diagnostique por que esse fluxo falhou.", "diagnostic_request"),
    ("DEMO-SOLUTION", "Desenhe uma arquitetura para essa solucao.", "solution_design_request")
]

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def tags():
    raw = subprocess.check_output(["git", "tag", "--list"], cwd=ROOT, text=True)
    return set(x.strip() for x in raw.splitlines() if x.strip())

def classify(prompt):
    p = prompt.lower()
    best = None
    for task in TASKS:
        score = sum(1 for s in task["signals"] if s.lower() in p)
        candidate = (score, task["priority"], task)
        if best is None or candidate[:2] > best[:2]:
            best = candidate
    if best and best[0] > 0:
        return best[2]
    return [t for t in TASKS if t["name"] == "simple_state_question"][0]

def main():
    errors = []

    doc = """# PROD-2181..2220 - Demo Chat Semantic Classifier

Defines the classifier for the CASULO demo chat.

The demo chat must show:

User request -> task classification -> risk -> gate -> generic risk -> CASULO optimized response -> next allowed action.

Boundary: no GPT call, no Codex, no runtime UI, no production and no client-facing claim.
"""
    contract = {
        "phase": PHASE,
        "mode": "demo_classifier_contract_only",
        "required_prior_tag": TAG_REQUIRED,
        "runtime_chat_ui_allowed": False,
        "gpt_call_allowed": False,
        "codex_execution_allowed": False,
        "automatic_merge_allowed": False,
        "production_activation_allowed": False,
        "client_facing_claim_allowed": False,
        "recommended_next_phase": "PROD-2221..2260 - Demo Chat Comparative Response Engine",
        "blocked_actions": BLOCKED
    }
    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Demo Chat Semantic Classifier",
        "type": "object",
        "required": ["status", "phase", "decision", "classifier", "checks", "blocked_actions"]
    }
    classifier = {
        "version": "demo_chat_semantic_classifier.v0.1",
        "principle": "Short as possible, complete as necessary, grounded in state, governed by gates.",
        "task_types": TASKS,
        "output_contract": [
            "task_type",
            "risk",
            "gate",
            "missing_evidence",
            "blocked_actions",
            "generic_response_risk",
            "casulo_response",
            "next_allowed_action"
        ]
    }

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write_json(CLASSIFIER, classifier)

    prior = json.loads(PRIOR.read_text(encoding="utf-8")) if PRIOR.exists() else {}
    results = []
    for sid, prompt, expected in SCENARIOS:
        task = classify(prompt)
        results.append({
            "id": sid,
            "prompt": prompt,
            "expected": expected,
            "classified": task["name"],
            "match": task["name"] == expected,
            "risk": task["risk"],
            "gate": task["gate"],
            "mode": task["mode"],
            "generic_response_risk": task["generic_risk"],
            "casulo_response": task["casulo"],
            "next_allowed_action": "Produce the allowed intermediate artifact before final execution."
        })

    names = {t["name"] for t in TASKS}
    checks = {
        "prior_pass": prior.get("status") == "PASS",
        "required_tag_present": TAG_REQUIRED in tags(),
        "task_count": len(TASKS),
        "scenario_count": len(SCENARIOS),
        "all_scenarios_match": all(r["match"] for r in results),
        "has_simple": "simple_state_question" in names,
        "has_diagnostic": "diagnostic_request" in names,
        "has_research": "research_request" in names,
        "has_solution": "solution_design_request" in names,
        "has_product": "product_generation_request" in names,
        "has_parser": "parser_generation_request" in names,
        "has_implementation": "implementation_request" in names,
        "has_merge": "codex_or_merge_request" in names,
        "has_client": "client_claim_request" in names,
        "has_production": "production_activation_request" in names,
        "parser_is_critical": [t for t in TASKS if t["name"] == "parser_generation_request"][0]["risk"] == "critical",
        "implementation_is_critical": [t for t in TASKS if t["name"] == "implementation_request"][0]["risk"] == "critical",
        "runtime_ui_blocked": contract["runtime_chat_ui_allowed"] is False,
        "gpt_call_blocked": contract["gpt_call_allowed"] is False,
        "codex_blocked": contract["codex_execution_allowed"] is False,
        "merge_blocked": contract["automatic_merge_allowed"] is False,
        "production_blocked": contract["production_activation_allowed"] is False,
        "client_claim_blocked": contract["client_facing_claim_allowed"] is False
    }

    if checks["task_count"] < 10:
        errors.append("task_count below 10")
    if checks["scenario_count"] < 8:
        errors.append("scenario_count below 8")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": DECISION if status == "PASS" else "DEMO_CHAT_SEMANTIC_CLASSIFIER_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "classifier": {
            "version": classifier["version"],
            "task_count": len(TASKS),
            "scenario_results": results,
            "recommended_next_phase": contract["recommended_next_phase"],
            "calibration_status": "NOT_CALIBRATED_DEMO_CLASSIFIER_ONLY"
        },
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    lines = [
        "# PROD-2181..2220 Demo Chat Semantic Classifier",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Task types: `{len(TASKS)}`",
        f"- Scenarios: `{len(SCENARIOS)}`",
        f"- Next: `{contract['recommended_next_phase']}`",
        "",
        "## Flow",
        "```text",
        "User request -> classification -> risk -> gate -> generic risk -> CASULO response -> next action",
        "```",
        "",
        "## Scenario Results"
    ]
    for r in results:
        lines.append(f"- `{r['id']}`: `{r['classified']}` match `{r['match']}` risk `{r['risk']}` gate `{r['gate']}`")
    lines += ["", "## Errors"]
    lines += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(lines))

    print(f"status: {status}")
    print(f"phase: {PHASE}")
    print(f"decision: {result['decision']}")
    print(f"task_count: {len(TASKS)}")
    print(f"scenario_count: {len(SCENARIOS)}")
    print(f"errors: {errors}")
    for r in results:
        print(f"{r['id']}: {r['classified']} match={r['match']}")

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

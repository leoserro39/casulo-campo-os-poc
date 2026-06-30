#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

CONTRACT = ROOT / "product/contracts/capability_state_ontology_living_company_state_anchor.contract.json"
ONTOLOGY = ROOT / "product/ontology/capability_state_ontology_v0_1.json"
COMPANY = ROOT / "product/ontology/living_company_state_anchor_v0_1.json"
DOC = ROOT / "docs/product/555_CAPABILITY_STATE_ONTOLOGY_AND_LIVING_COMPANY_STATE_ANCHOR.md"
SCHEMA = ROOT / "product/schemas/capability_state_ontology_living_company_state_anchor.schema.json"
PRIOR = ROOT / "outputs/prod2101_2140_ohri_governance_correction_dual_ranking_model.json"
OUT = ROOT / "outputs"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def git_tags():
    try:
        raw = subprocess.check_output(["git", "tag", "--list"], cwd=ROOT, text=True)
        return [line.strip() for line in raw.splitlines() if line.strip()]
    except Exception:
        return []

def main():
    errors = []

    contract = load(CONTRACT) if CONTRACT.exists() else {}
    ontology = load(ONTOLOGY) if ONTOLOGY.exists() else {}
    company = load(COMPANY) if COMPANY.exists() else {}
    prior = load(PRIOR) if PRIOR.exists() else {}

    tags = git_tags()
    required_tag = contract.get("required_prior_tag")

    layers = ontology.get("layers", [])
    capabilities = ontology.get("universal_capabilities", [])
    states = ontology.get("operational_states", [])
    gates = ontology.get("gate_classes", [])
    evidence = ontology.get("evidence_classes", [])
    delivery_modes = ontology.get("delivery_modes", [])
    company_layers = company.get("structural_layers", [])
    behavior_rules = company.get("company_behavior_rules", [])

    checks = {
        "contract_exists": CONTRACT.exists(),
        "ontology_exists": ONTOLOGY.exists(),
        "company_anchor_exists": COMPANY.exists(),
        "doc_exists": DOC.exists(),
        "schema_exists": SCHEMA.exists(),
        "prior_output_exists": PRIOR.exists(),
        "prior_phase_pass": prior.get("status") == "PASS",
        "prior_decision_ready": prior.get("decision") == "OHRI_GOVERNANCE_CORRECTED_DUAL_RANKING_READY",
        "required_prior_tag_present": required_tag in tags,
        "has_capability_before_department_principle": any(p.get("name") == "Capability before department" for p in ontology.get("principles", [])),
        "has_state_before_solution_principle": any(p.get("name") == "State before solution" for p in ontology.get("principles", [])),
        "has_response_economy_principle": any(p.get("name") == "Response economy" for p in ontology.get("principles", [])),
        "layer_count": len(layers),
        "capability_count": len(capabilities),
        "state_count": len(states),
        "gate_count": len(gates),
        "evidence_class_count": len(evidence),
        "delivery_mode_count": len(delivery_modes),
        "company_layer_count": len(company_layers),
        "behavior_rule_count": len(behavior_rules),
        "has_directive_governor_company_layer": any(l.get("name") == "Directive Governor" for l in company_layers),
        "has_automation_fabric_company_layer": any(l.get("name") == "Automation Fabric" for l in company_layers),
        "has_living_company_thesis": company.get("company_thesis") == "The company is not an organogram. It is a living computable state.",
        "marketing_outline_allowed": contract.get("marketing_outline_allowed") is True,
        "business_plan_seed_allowed": contract.get("business_plan_seed_allowed") is True,
        "calibration_blocked": contract.get("calibration_allowed") is False,
        "automatic_gpt_call_blocked": contract.get("automatic_gpt_call_allowed") is False,
        "codex_execution_blocked": contract.get("codex_execution_allowed") is False,
        "automatic_merge_blocked": contract.get("automatic_merge_allowed") is False,
        "production_activation_blocked": contract.get("production_activation_allowed") is False,
        "client_facing_claim_blocked": contract.get("client_facing_claim_allowed") is False,
        "validated_commercial_claim_blocked": contract.get("validated_commercial_claim_allowed") is False
    }

    minimums = {
        "layer_count": 7,
        "capability_count": 12,
        "state_count": 12,
        "gate_count": 8,
        "evidence_class_count": 8,
        "delivery_mode_count": 8,
        "company_layer_count": 5,
        "behavior_rule_count": 6
    }

    for key, minimum in minimums.items():
        if checks.get(key, 0) < minimum:
            errors.append(f"{key} below minimum {minimum}")

    for key in [
        "contract_exists",
        "ontology_exists",
        "company_anchor_exists",
        "doc_exists",
        "schema_exists",
        "prior_output_exists",
        "prior_phase_pass",
        "prior_decision_ready",
        "required_prior_tag_present",
        "has_capability_before_department_principle",
        "has_state_before_solution_principle",
        "has_response_economy_principle",
        "has_directive_governor_company_layer",
        "has_automation_fabric_company_layer",
        "has_living_company_thesis",
        "marketing_outline_allowed",
        "business_plan_seed_allowed",
        "calibration_blocked",
        "automatic_gpt_call_blocked",
        "codex_execution_blocked",
        "automatic_merge_blocked",
        "production_activation_blocked",
        "client_facing_claim_blocked",
        "validated_commercial_claim_blocked"
    ]:
        if not checks.get(key):
            errors.append(f"Check failed: {key}")

    status = "PASS" if not errors else "FAIL"
    decision = "CAPABILITY_STATE_ONTOLOGY_LIVING_COMPANY_STATE_ANCHOR_READY" if status == "PASS" else "CAPABILITY_STATE_ONTOLOGY_LIVING_COMPANY_STATE_ANCHOR_NOT_READY"

    example_simulation = {
        "raw_request": "Crie um parser para essa planilha e já implemente.",
        "ontology_classification": {
            "capability": ["read", "map", "validate", "automate"],
            "state": "schema_required",
            "evidence_required": ["source_document", "schema", "contract", "fixture", "golden_output", "validator_result"],
            "gate": "SCHEMA_REQUIRED",
            "automation_level": "ai_assisted",
            "blocked_actions": ["implementation_execution", "automatic_merge", "production_activation"],
            "allowed_action": "Generate workbook inventory, parser contract and validation plan before final parser."
        },
        "directive_governor_response": "Não criar parser final ainda. O estado exige schema real, inventário de abas/colunas, fixture, golden output e validador. A ação permitida é gerar o inspector e o contrato do parser. Ação bloqueada: implementação final baseada em suposição."
    }

    marketing_seed = {
        "one_liner": "CASULO transforma operações em estados vivos computáveis, governados por evidências, gates e automação segura.",
        "short_pitch": "CASULO é uma metodologia em desenvolvimento para mapear capacidades, processos e decisões como grafos operacionais. Em vez de começar por software ou organograma, o método começa pelo estado: o que existe, o que falta, qual evidência sustenta, qual gate libera e qual próxima ação é segura.",
        "safe_boundary": "Conceito/metodologia em maturação. Sem claim de validação comercial real, produção ou redução comprovada de alucinação em clientes."
    }

    result = {
        "status": status,
        "phase": "PROD-2141..2180",
        "decision": decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "ontology_anchor": {
            "ontology_name": ontology.get("name"),
            "ontology_pt_name": ontology.get("pt_name"),
            "company_anchor_name": company.get("name"),
            "company_anchor_pt_name": company.get("pt_name"),
            "company_thesis": company.get("company_thesis"),
            "principle_count": len(ontology.get("principles", [])),
            "layer_count": len(layers),
            "capability_count": len(capabilities),
            "state_count": len(states),
            "gate_count": len(gates),
            "evidence_class_count": len(evidence),
            "delivery_mode_count": len(delivery_modes),
            "company_layer_count": len(company_layers),
            "behavior_rule_count": len(behavior_rules),
            "example_simulation": example_simulation,
            "marketing_seed": marketing_seed,
            "recommended_next_phase": contract.get("recommended_next_phase"),
            "later_benchmark_phase": contract.get("later_benchmark_phase"),
            "calibration_status": "NOT_CALIBRATED_CONCEPTUAL_OPERATIONAL_ANCHOR_ONLY"
        },
        "checks": checks,
        "errors": errors,
        "blocked_actions": contract.get("blocked_actions", [])
    }

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "prod2141_2180_capability_state_ontology_living_company_state_anchor.json"
    md_path = OUT / "prod2141_2180_capability_state_ontology_living_company_state_anchor.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PROD-2141..2180 Capability-State Ontology and Living Company State Anchor",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{decision}`",
        f"- Ontology: `{ontology.get('name')}`",
        f"- Company anchor: `{company.get('name')}`",
        f"- Thesis: {company.get('company_thesis')}",
        f"- Calibration: `{result['ontology_anchor']['calibration_status']}`",
        f"- Recommended next phase: `{contract.get('recommended_next_phase')}`",
        f"- Later benchmark phase: `{contract.get('later_benchmark_phase')}`",
        "",
        "## Current Structure",
        "",
        "```text",
        "CASULO Brain / Cockpit",
        "  -> Capability-State Ontology",
        "    -> Operational State Graph / Context Packet",
        "      -> Hallucination Risk Layer: OHRI + OBPI",
        "        -> Response Economy / Directive Governor",
        "          -> Output: diagnosis, runbook, parser contract, solution blueprint or marketing outline",
        "```",
        "",
        "## Simulation",
        "",
        f"- Raw request: {example_simulation['raw_request']}",
        f"- State: `{example_simulation['ontology_classification']['state']}`",
        f"- Gate: `{example_simulation['ontology_classification']['gate']}`",
        f"- Allowed action: {example_simulation['ontology_classification']['allowed_action']}",
        f"- Directive response: {example_simulation['directive_governor_response']}",
        "",
        "## Marketing Seed",
        "",
        f"- One-liner: {marketing_seed['one_liner']}",
        f"- Short pitch: {marketing_seed['short_pitch']}",
        f"- Safe boundary: {marketing_seed['safe_boundary']}",
        "",
        "## Checks"
    ]

    for key, value in checks.items():
        md.append(f"- {key}: `{value}`")

    md += ["", "## Errors"]
    if errors:
        for err in errors:
            md.append(f"- {err}")
    else:
        md.append("- None")

    md += [
        "",
        "## Blocked Actions"
    ]
    for action in contract.get("blocked_actions", []):
        md.append(f"- {action}")

    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

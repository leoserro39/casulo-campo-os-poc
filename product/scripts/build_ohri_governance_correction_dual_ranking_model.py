#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

PREVIOUS = ROOT / "outputs/prod2061_2100_operational_hallucination_risk_index_and_ranking_model.json"
MATRIX = ROOT / "product/evaluation/operational_hallucination_failure_modes.json"
SOURCE_MODEL = ROOT / "product/evaluation/operational_hallucination_risk_index_model.json"
DUAL_MODEL = ROOT / "product/evaluation/operational_hallucination_dual_ranking_model.json"
CONTRACT = ROOT / "product/contracts/ohri_governance_correction_dual_ranking_model.contract.json"
DOC = ROOT / "docs/product/554_OHRI_GOVERNANCE_CORRECTION_AND_DUAL_RANKING_MODEL.md"
OUT = ROOT / "outputs"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def score_band(score):
    if score >= 85:
        return "critical"
    if score >= 70:
        return "high"
    if score >= 50:
        return "medium"
    if score >= 30:
        return "low"
    return "minimal"

def weighted_score(scores, weights):
    return round(sum(scores.get(k, 0) * w for k, w in weights.items()), 2)

def build_ranking(failure_modes, scores_by_mode, weights, score_name):
    ranking = []
    for mode in failure_modes:
        name = mode.get("name")
        scores = scores_by_mode.get(name, {})
        value = weighted_score(scores, weights)
        ranking.append({
            "id": mode.get("id"),
            "name": name,
            "family": mode.get("family"),
            "matrix_priority": mode.get("priority"),
            score_name: value,
            "band": score_band(value),
            "casulo_control": mode.get("casulo_control")
        })
    ranking.sort(key=lambda item: item[score_name], reverse=True)
    return ranking

def main():
    errors = []

    previous = load(PREVIOUS) if PREVIOUS.exists() else {}
    matrix = load(MATRIX) if MATRIX.exists() else {}
    source_model = load(SOURCE_MODEL) if SOURCE_MODEL.exists() else {}
    dual_model = load(DUAL_MODEL) if DUAL_MODEL.exists() else {}
    contract = load(CONTRACT) if CONTRACT.exists() else {}

    failure_modes = matrix.get("failure_modes", [])
    scores_by_mode = source_model.get("dimension_scores_by_failure_mode", {})
    ohri_weights = dual_model.get("ohri_weights", {})
    obpi_weights = dual_model.get("obpi_weights", {})

    ohri_ranking = build_ranking(failure_modes, scores_by_mode, ohri_weights, "ohri_score")
    obpi_ranking = build_ranking(failure_modes, scores_by_mode, obpi_weights, "obpi_score")

    ohri_top_5 = ohri_ranking[:5]
    obpi_top_5 = obpi_ranking[:5]

    previous_was_fail = previous.get("status") == "FAIL"
    previous_errors = previous.get("errors", [])

    checks = {
        "previous_index_output_exists": PREVIOUS.exists(),
        "previous_index_was_fail": previous_was_fail,
        "previous_failure_recorded": "Risk index weights must sum to 1.0" in previous_errors,
        "previous_parser_assumption_recorded": "Parser grounding should be in top five risk modes" in previous_errors,
        "matrix_exists": MATRIX.exists(),
        "source_model_exists": SOURCE_MODEL.exists(),
        "dual_model_exists": DUAL_MODEL.exists(),
        "contract_exists": CONTRACT.exists(),
        "doc_exists": DOC.exists(),
        "dual_model_status_heuristic": dual_model.get("status") == "HEURISTIC_NOT_CALIBRATED",
        "ohri_weight_sum_one": abs(sum(ohri_weights.values()) - 1.0) < 0.0001,
        "obpi_weight_sum_one": abs(sum(obpi_weights.values()) - 1.0) < 0.0001,
        "failure_mode_count": len(failure_modes),
        "ohri_ranking_count": len(ohri_ranking),
        "obpi_ranking_count": len(obpi_ranking),
        "all_modes_have_scores": set(m.get("name") for m in failure_modes).issubset(set(scores_by_mode.keys())),
        "ohri_top_is_not_forced_parser": ohri_ranking[0]["name"] != "generic_parser_generation" if ohri_ranking else False,
        "obpi_top_is_parser": obpi_ranking[0]["name"] == "generic_parser_generation" if obpi_ranking else False,
        "repo_state_high_in_ohri": any(item["name"] == "repo_state_mismatch" for item in ohri_top_5),
        "api_contract_high_in_ohri": any(item["name"] == "api_contract_hallucination" for item in ohri_top_5),
        "unsafe_merge_high_in_ohri": any(item["name"] == "unsafe_merge_suggestion" for item in ohri_top_5),
        "parser_in_obpi_top_3": any(item["name"] == "generic_parser_generation" for item in obpi_ranking[:3]),
        "calibration_blocked": contract.get("calibration_allowed") is False,
        "automatic_gpt_call_blocked": contract.get("automatic_gpt_call_allowed") is False,
        "codex_execution_blocked": contract.get("codex_execution_allowed") is False,
        "automatic_merge_blocked": contract.get("automatic_merge_allowed") is False,
        "production_activation_blocked": contract.get("production_activation_allowed") is False,
        "client_facing_claim_blocked": contract.get("client_facing_claim_allowed") is False
    }

    for key in [
        "previous_index_output_exists",
        "previous_index_was_fail",
        "previous_failure_recorded",
        "previous_parser_assumption_recorded",
        "matrix_exists",
        "source_model_exists",
        "dual_model_exists",
        "contract_exists",
        "doc_exists",
        "dual_model_status_heuristic",
        "ohri_weight_sum_one",
        "obpi_weight_sum_one",
        "all_modes_have_scores",
        "ohri_top_is_not_forced_parser",
        "obpi_top_is_parser",
        "repo_state_high_in_ohri",
        "api_contract_high_in_ohri",
        "unsafe_merge_high_in_ohri",
        "parser_in_obpi_top_3",
        "calibration_blocked",
        "automatic_gpt_call_blocked",
        "codex_execution_blocked",
        "automatic_merge_blocked",
        "production_activation_blocked",
        "client_facing_claim_blocked"
    ]:
        if not checks[key]:
            errors.append(f"Check failed: {key}")

    status = "PASS" if not errors else "FAIL"
    decision = "OHRI_GOVERNANCE_CORRECTED_DUAL_RANKING_READY" if status == "PASS" else "OHRI_GOVERNANCE_CORRECTION_NOT_READY"

    result = {
        "status": status,
        "phase": "PROD-2101..2140",
        "decision": decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dual_ranking": {
            "corrects_previous_phase": "PROD-2061..2100",
            "previous_commit": contract.get("corrects_commit"),
            "previous_tag": contract.get("corrects_tag"),
            "previous_status": previous.get("status"),
            "previous_errors": previous_errors,
            "calibration_status": "NOT_CALIBRATED_CORRECTIVE_DUAL_RANKING_ONLY",
            "ohri": {
                "purpose": dual_model.get("indexes", {}).get("ohri", {}).get("purpose"),
                "top_5": ohri_top_5,
                "ranking": ohri_ranking
            },
            "obpi": {
                "purpose": dual_model.get("indexes", {}).get("obpi", {}).get("purpose"),
                "top_5": obpi_top_5,
                "ranking": obpi_ranking
            },
            "recommended_next_phase": contract.get("recommended_next_phase"),
            "later_benchmark_phase": contract.get("later_benchmark_phase")
        },
        "checks": checks,
        "errors": errors,
        "blocked_actions": contract.get("blocked_actions", [])
    }

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "prod2101_2140_ohri_governance_correction_dual_ranking_model.json"
    md_path = OUT / "prod2101_2140_ohri_governance_correction_dual_ranking_model.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PROD-2101..2140 OHRI Governance Correction and Dual Ranking Model",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{decision}`",
        f"- Calibration: `{result['dual_ranking']['calibration_status']}`",
        f"- Corrects previous commit: `{contract.get('corrects_commit')}`",
        f"- Corrects previous tag: `{contract.get('corrects_tag')}`",
        f"- Previous status: `{previous.get('status')}`",
        f"- Recommended next phase: `{contract.get('recommended_next_phase')}`",
        f"- Later benchmark phase: `{contract.get('later_benchmark_phase')}`",
        "",
        "## Correction",
        "",
        "The previous model mixed operational danger with benchmark priority.",
        "",
        "This corrected phase separates:",
        "",
        "- OHRI: operational danger.",
        "- OBPI: benchmark priority.",
        "",
        "## OHRI Top 5"
    ]

    for idx, item in enumerate(ohri_top_5, start=1):
        md.append(f"{idx}. `{item['name']}` — `{item['ohri_score']}` — `{item['band']}` — `{item['family']}`")

    md += ["", "## OBPI Top 5"]
    for idx, item in enumerate(obpi_top_5, start=1):
        md.append(f"{idx}. `{item['name']}` — `{item['obpi_score']}` — `{item['band']}` — `{item['family']}`")

    md += ["", "## Checks"]
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
        "## Boundary",
        "- Corrective ranking only.",
        "- Not calibrated.",
        "- No GPT call.",
        "- No Codex execution.",
        "- No automatic merge.",
        "- No production activation.",
        "- No client-facing claim."
    ]

    md_path.write_text("\n".join(md) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))
    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

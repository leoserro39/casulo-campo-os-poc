#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "outputs" / "prod2021_2060_operational_hallucination_failure_mode_matrix.json"
MATRIX = ROOT / "product/evaluation/operational_hallucination_failure_modes.json"
MODEL = ROOT / "product/evaluation/operational_hallucination_risk_index_model.json"
CONTRACT = ROOT / "product/contracts/operational_hallucination_risk_index_and_ranking_model.contract.json"
DOC = ROOT / "docs/product/553_OPERATIONAL_HALLUCINATION_RISK_INDEX_AND_RANKING_MODEL.md"
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
    total_weight = sum(weights.values())
    raw = sum(scores.get(k, 0) * w for k, w in weights.items())
    return round(raw / total_weight, 2)

def main():
    errors = []

    prior = load(PRIOR) if PRIOR.exists() else {}
    matrix = load(MATRIX) if MATRIX.exists() else {}
    model = load(MODEL) if MODEL.exists() else {}
    contract = load(CONTRACT) if CONTRACT.exists() else {}

    failure_modes = matrix.get("failure_modes", [])
    failure_mode_names = [m.get("name") for m in failure_modes]
    scores_by_mode = model.get("dimension_scores_by_failure_mode", {})
    weights = model.get("weights", {})

    ranking = []
    for mode in failure_modes:
        name = mode.get("name")
        scores = scores_by_mode.get(name, {})
        ohri_score = weighted_score(scores, weights)
        ranking.append({
            "id": mode.get("id"),
            "name": name,
            "family": mode.get("family"),
            "matrix_priority": mode.get("priority"),
            "ohri_score": ohri_score,
            "ohri_band": score_band(ohri_score),
            "recommended_control": mode.get("casulo_control"),
            "candidate_benchmark_family": mode.get("family"),
            "dimension_scores": scores
        })

    ranking.sort(key=lambda item: item["ohri_score"], reverse=True)

    top_5 = ranking[:5]
    critical_modes = [r for r in ranking if r["ohri_band"] == "critical"]
    high_or_critical_modes = [r for r in ranking if r["ohri_band"] in {"critical", "high"}]

    family_averages = {}
    family_counts = {}
    for item in ranking:
        family = item["family"]
        family_averages[family] = family_averages.get(family, 0) + item["ohri_score"]
        family_counts[family] = family_counts.get(family, 0) + 1
    for family in list(family_averages):
        family_averages[family] = round(family_averages[family] / family_counts[family], 2)

    family_ranking = [
        {"family": family, "avg_ohri_score": avg, "count": family_counts[family], "ohri_band": score_band(avg)}
        for family, avg in family_averages.items()
    ]
    family_ranking.sort(key=lambda item: item["avg_ohri_score"], reverse=True)

    checks = {
        "prior_failure_mode_matrix_exists": PRIOR.exists(),
        "prior_failure_mode_matrix_pass": prior.get("status") == "PASS",
        "prior_decision_ready": prior.get("decision") == "OPERATIONAL_HALLUCINATION_FAILURE_MODE_MATRIX_READY",
        "matrix_exists": MATRIX.exists(),
        "model_exists": MODEL.exists(),
        "contract_exists": CONTRACT.exists(),
        "doc_exists": DOC.exists(),
        "model_status_heuristic": model.get("status") == "HEURISTIC_NOT_CALIBRATED",
        "has_weights": bool(weights),
        "weight_count": len(weights),
        "weight_sum_approximately_one": abs(sum(weights.values()) - 1.0) < 0.0001,
        "failure_mode_count": len(failure_modes),
        "ranking_count": len(ranking),
        "all_failure_modes_scored": set(failure_mode_names).issubset(set(scores_by_mode.keys())),
        "has_critical_or_high_modes": len(high_or_critical_modes) > 0,
        "top_mode_name": ranking[0]["name"] if ranking else None,
        "top_mode_is_parser_or_production_or_merge_or_api": ranking[0]["name"] in {
            "generic_parser_generation",
            "production_readiness_leakage",
            "unsafe_merge_suggestion",
            "api_contract_hallucination",
            "repo_state_mismatch"
        } if ranking else False,
        "parser_grounding_in_top_five": any(r["name"] == "generic_parser_generation" for r in top_5),
        "repo_state_in_top_five": any(r["name"] == "repo_state_mismatch" for r in top_5),
        "api_contract_in_top_seven": any(r["name"] == "api_contract_hallucination" for r in ranking[:7]),
        "calibration_blocked": contract.get("calibration_allowed") is False,
        "automatic_gpt_call_blocked": contract.get("automatic_gpt_call_allowed") is False,
        "codex_execution_blocked": contract.get("codex_execution_allowed") is False,
        "automatic_merge_blocked": contract.get("automatic_merge_allowed") is False,
        "production_activation_blocked": contract.get("production_activation_allowed") is False,
        "client_facing_claim_blocked": contract.get("client_facing_claim_allowed") is False,
        "recommended_next_phase": contract.get("recommended_next_phase")
    }

    if not checks["prior_failure_mode_matrix_pass"]:
        errors.append("Prior failure mode matrix phase must be PASS")
    if not checks["prior_decision_ready"]:
        errors.append("Prior failure mode matrix decision must be ready")
    if not checks["model_status_heuristic"]:
        errors.append("Risk index model must be heuristic and not calibrated")
    if not checks["weight_sum_approximately_one"]:
        errors.append("Risk index weights must sum to 1.0")
    if not checks["all_failure_modes_scored"]:
        missing = sorted(set(failure_mode_names) - set(scores_by_mode.keys()))
        errors.append("Missing dimension scores for: " + ", ".join(missing))
    if not checks["has_critical_or_high_modes"]:
        errors.append("Risk index must produce at least one high or critical mode")
    if not checks["parser_grounding_in_top_five"]:
        errors.append("Parser grounding should be in top five risk modes")
    if not checks["repo_state_in_top_five"]:
        errors.append("Repo state mismatch should be in top five risk modes")
    if not checks["api_contract_in_top_seven"]:
        errors.append("API contract hallucination should be in top seven risk modes")
    if not checks["calibration_blocked"]:
        errors.append("Calibration must remain blocked")
    if not checks["automatic_gpt_call_blocked"]:
        errors.append("Automatic GPT call must remain blocked")
    if not checks["codex_execution_blocked"]:
        errors.append("Codex execution must remain blocked")
    if not checks["automatic_merge_blocked"]:
        errors.append("Automatic merge must remain blocked")
    if not checks["production_activation_blocked"]:
        errors.append("Production activation must remain blocked")
    if not checks["client_facing_claim_blocked"]:
        errors.append("Client-facing claim must remain blocked")

    status = "PASS" if not errors else "FAIL"
    decision = "OPERATIONAL_HALLUCINATION_RISK_INDEX_READY" if status == "PASS" else "OPERATIONAL_HALLUCINATION_RISK_INDEX_NOT_READY"

    result = {
        "status": status,
        "phase": "PROD-2061..2100",
        "decision": decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "risk_index": {
            "index_name": model.get("index", {}).get("name"),
            "index_abbreviation": model.get("index", {}).get("abbreviation"),
            "pt_name": model.get("index", {}).get("pt_name"),
            "pt_abbreviation": model.get("index", {}).get("pt_abbreviation"),
            "model_status": model.get("status"),
            "calibration_status": "NOT_CALIBRATED_HEURISTIC_RANKING_ONLY",
            "source_matrix": str(MATRIX.relative_to(ROOT)),
            "model_file": str(MODEL.relative_to(ROOT)),
            "ranking_count": len(ranking),
            "critical_count": len(critical_modes),
            "high_or_critical_count": len(high_or_critical_modes),
            "top_5": top_5,
            "ranking": ranking,
            "family_ranking": family_ranking,
            "recommended_next_phase": contract.get("recommended_next_phase")
        },
        "checks": checks,
        "errors": errors,
        "blocked_actions": contract.get("blocked_actions", [])
    }

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "prod2061_2100_operational_hallucination_risk_index_and_ranking_model.json"
    md_path = OUT / "prod2061_2100_operational_hallucination_risk_index_and_ranking_model.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PROD-2061..2100 Operational Hallucination Risk Index and Ranking Model",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{decision}`",
        f"- Index: `{result['risk_index']['index_abbreviation']}` / `{result['risk_index']['pt_abbreviation']}`",
        f"- Calibration: `{result['risk_index']['calibration_status']}`",
        f"- Ranking count: `{len(ranking)}`",
        f"- Critical count: `{len(critical_modes)}`",
        f"- High or critical count: `{len(high_or_critical_modes)}`",
        f"- Recommended next phase: `{contract.get('recommended_next_phase')}`",
        "",
        "## Top 5 Risk Modes"
    ]

    for idx, item in enumerate(top_5, start=1):
        md += [
            f"### {idx}. {item['name']}",
            f"- Score: `{item['ohri_score']}`",
            f"- Band: `{item['ohri_band']}`",
            f"- Family: `{item['family']}`",
            f"- CASULO control: {item['recommended_control']}",
            ""
        ]

    md += ["## Full Ranking"]
    for idx, item in enumerate(ranking, start=1):
        md.append(f"{idx}. `{item['name']}` — `{item['ohri_score']}` — `{item['ohri_band']}` — `{item['family']}`")

    md += ["", "## Family Ranking"]
    for idx, item in enumerate(family_ranking, start=1):
        md.append(f"{idx}. `{item['family']}` — avg `{item['avg_ohri_score']}` — `{item['ohri_band']}` — count `{item['count']}`")

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
        "- Heuristic ranking only.",
        "- Not calibrated.",
        "- No automatic GPT call.",
        "- No Codex execution.",
        "- No automatic merge.",
        "- No production activation.",
        "- No client-facing claim.",
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

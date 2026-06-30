#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PRIOR = ROOT / "outputs" / "prod1981_2020_manual_real_response_capture_batch_001_runbook.json"
MATRIX = ROOT / "product/evaluation/operational_hallucination_failure_modes.json"
CONTRACT = ROOT / "product/contracts/operational_hallucination_failure_mode_matrix.contract.json"
DOC = ROOT / "docs/product/552_OPERATIONAL_HALLUCINATION_FAILURE_MODE_MATRIX.md"
OUT = ROOT / "outputs"

def load(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    errors = []

    prior = load(PRIOR) if PRIOR.exists() else {}
    matrix = load(MATRIX) if MATRIX.exists() else {}
    contract = load(CONTRACT) if CONTRACT.exists() else {}

    failure_modes = matrix.get("failure_modes", [])
    benchmark_families = matrix.get("benchmark_families", [])

    mode_names = {m.get("name") for m in failure_modes}
    benchmark_names = {b.get("name") for b in benchmark_families}

    required_failure_modes = {
        "generic_parser_generation",
        "schema_invention",
        "file_structure_hallucination",
        "repo_state_mismatch",
        "contract_omission",
        "testless_code_generation",
        "unsafe_merge_suggestion",
        "conditional_client_claim_leakage",
        "generic_validation_laundering",
        "production_readiness_leakage",
        "api_contract_hallucination",
        "generic_rag_answer_without_gate",
        "business_recommendation_without_limits",
        "context_contamination",
        "provider_contamination",
        "ui_metadata_contamination"
    }

    required_benchmarks = {
        "Parser Grounding Benchmark",
        "Repo Patch Grounding Benchmark",
        "Workbook / Excel Contract Benchmark",
        "API Contract Benchmark",
        "Production Gate Benchmark",
        "RAG vs Operational State Control Benchmark",
        "Business Recommendation Boundary Benchmark"
    }

    priority_counts = {}
    family_counts = {}

    for mode in failure_modes:
        priority_counts[mode.get("priority", "unknown")] = priority_counts.get(mode.get("priority", "unknown"), 0) + 1
        family_counts[mode.get("family", "unknown")] = family_counts.get(mode.get("family", "unknown"), 0) + 1

    checks = {
        "prior_batch_001_runbook_exists": PRIOR.exists(),
        "prior_batch_001_runbook_pass": prior.get("status") == "PASS",
        "prior_batch_001_requires_manual_capture_next": prior.get("batch_001", {}).get("capture_required_next") is True,
        "matrix_exists": MATRIX.exists(),
        "contract_exists": CONTRACT.exists(),
        "doc_exists": DOC.exists(),
        "matrix_status_exploratory": matrix.get("status") == "EXPLORATORY_NOT_CALIBRATED",
        "failure_mode_count": len(failure_modes),
        "failure_mode_count_at_least_16": len(failure_modes) >= 16,
        "benchmark_family_count": len(benchmark_families),
        "benchmark_family_count_at_least_7": len(benchmark_families) >= 7,
        "has_all_required_failure_modes": required_failure_modes.issubset(mode_names),
        "has_all_required_benchmarks": required_benchmarks.issubset(benchmark_names),
        "has_parser_benchmark": "Parser Grounding Benchmark" in benchmark_names,
        "has_rag_vs_state_benchmark": "RAG vs Operational State Control Benchmark" in benchmark_names,
        "has_git_codex_distinction": "Git versions changes" in matrix.get("thesis", {}).get("git_codex_distinction", ""),
        "has_rag_distinction": "RAG improves retrieval" in matrix.get("thesis", {}).get("rag_distinction", ""),
        "calibration_blocked": contract.get("calibration_allowed") is False,
        "automatic_gpt_call_blocked": contract.get("automatic_gpt_call_allowed") is False,
        "codex_execution_blocked": contract.get("codex_execution_allowed") is False,
        "automatic_merge_blocked": contract.get("automatic_merge_allowed") is False,
        "production_activation_blocked": contract.get("production_activation_allowed") is False,
        "client_facing_claim_blocked": contract.get("client_facing_claim_allowed") is False,
        "next_recommended_phase": contract.get("next_recommended_phase")
    }

    if not checks["prior_batch_001_runbook_pass"]:
        errors.append("Prior Batch 001 runbook phase must be PASS")
    if not checks["prior_batch_001_requires_manual_capture_next"]:
        errors.append("Prior Batch 001 must still require manual capture next")
    if not checks["matrix_status_exploratory"]:
        errors.append("Matrix must be explicitly exploratory and not calibrated")
    if not checks["failure_mode_count_at_least_16"]:
        errors.append("Matrix must include at least 16 failure modes")
    if not checks["benchmark_family_count_at_least_7"]:
        errors.append("Matrix must include at least 7 benchmark families")
    if not checks["has_all_required_failure_modes"]:
        errors.append("Missing required failure modes")
    if not checks["has_all_required_benchmarks"]:
        errors.append("Missing required benchmark families")
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
    decision = "OPERATIONAL_HALLUCINATION_FAILURE_MODE_MATRIX_READY" if status == "PASS" else "OPERATIONAL_HALLUCINATION_FAILURE_MODE_MATRIX_NOT_READY"

    result = {
        "status": status,
        "phase": "PROD-2021..2060",
        "decision": decision,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "matrix": {
            "matrix_file": str(MATRIX.relative_to(ROOT)),
            "matrix_status": matrix.get("status"),
            "failure_mode_count": len(failure_modes),
            "benchmark_family_count": len(benchmark_families),
            "priority_counts": priority_counts,
            "family_counts": family_counts,
            "recommended_next_phase": contract.get("next_recommended_phase"),
            "calibration_status": "NOT_CALIBRATED_FAILURE_MODE_DISCOVERY_ONLY",
            "key_thesis": matrix.get("thesis", {}).get("strong_thesis"),
            "rag_distinction": matrix.get("thesis", {}).get("rag_distinction"),
            "git_codex_distinction": matrix.get("thesis", {}).get("git_codex_distinction")
        },
        "checks": checks,
        "errors": errors,
        "blocked_actions": contract.get("blocked_actions", [])
    }

    OUT.mkdir(parents=True, exist_ok=True)
    json_path = OUT / "prod2021_2060_operational_hallucination_failure_mode_matrix.json"
    md_path = OUT / "prod2021_2060_operational_hallucination_failure_mode_matrix.md"

    json_path.write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")

    md = [
        "# PROD-2021..2060 Operational Hallucination Failure Mode Matrix",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{decision}`",
        f"- Calibration: `{result['matrix']['calibration_status']}`",
        f"- Failure modes: `{len(failure_modes)}`",
        f"- Benchmark families: `{len(benchmark_families)}`",
        f"- Recommended next phase: `{contract.get('next_recommended_phase')}`",
        "",
        "## Strong Thesis",
        "",
        result["matrix"]["key_thesis"] or "",
        "",
        "## RAG Distinction",
        "",
        result["matrix"]["rag_distinction"] or "",
        "",
        "## Git / Codex Distinction",
        "",
        result["matrix"]["git_codex_distinction"] or "",
        "",
        "## Failure Modes"
    ]

    for mode in failure_modes:
        md += [
            f"### {mode.get('id')} - {mode.get('name')}",
            f"- Family: `{mode.get('family')}`",
            f"- Priority: `{mode.get('priority')}`",
            f"- Description: {mode.get('description')}",
            f"- Pure failure pattern: {mode.get('pure_failure_pattern')}",
            f"- CASULO control: {mode.get('casulo_control')}",
            ""
        ]

    md += ["## Benchmark Families"]
    for bench in benchmark_families:
        md += [
            f"### {bench.get('id')} - {bench.get('name')}",
            f"- Priority: `{bench.get('priority')}`",
            f"- Purpose: {bench.get('purpose')}",
            ""
        ]

    md += ["## Checks"]
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
        "- Exploratory only.",
        "- No calibration.",
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

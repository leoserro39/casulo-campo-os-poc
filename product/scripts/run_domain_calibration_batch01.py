#!/usr/bin/env python3
import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
EXEC_PLAN = ROOT / "product/evaluation/domain_calibration_execution_plan_v0_1.json"
SCENARIOS = ROOT / "product/evaluation/domain_calibration_controlled_scenarios_v0_1.json"
RUBRIC = ROOT / "product/evaluation/domain_calibration_scoring_rubric_v0_1.json"
SINGLE_RUNNER = ROOT / "product/scripts/run_gpt_sandbox_first_controlled_live_call.py"

OUT_DIR = ROOT / "outputs/domain_calibration_batch01"
BATCH_RESULT = OUT_DIR / "domain_calibration_batch01_result.json"
SINGLE_RESULT = ROOT / "outputs/gpt_sandbox_first_controlled_live_call_result.json"

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def build_prompt(scenario):
    return (
        "CASULO domain calibration controlled test. "
        f"Domain: {scenario['domain']}. "
        f"Scenario: {scenario['scenario']}. "
        "Use only the supplied scenario facts. "
        "Return a compact JSON object with: "
        "domain, scenario_id, evidence_sufficiency, gate_status, blocked_actions, "
        "human_review_required, unsupported_claim_count, missing_evidence_claim_count, "
        "gate_violation_count, evidence_grounding_score, state_completeness_score, "
        "manual_arbitration_needed_count, false_memory_risk, context_regression_count, "
        "next_safe_operational_action. "
        "Do not claim production readiness, client validation, dataset acceptance or commercial value."
    )

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--limit", type=int, default=36)
    args = parser.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    plan = read_json(EXEC_PLAN)
    scenarios_packet = read_json(SCENARIOS)
    rubric = read_json(RUBRIC)

    scenarios = {s["scenario_id"]: s for s in scenarios_packet["scenarios"]}
    planned = plan["planned_executions"][: args.limit]

    if not args.apply:
        results = []
        for item in planned:
            scenario = scenarios[item["scenario_id"]]
            results.append({
                "execution_id": item["execution_id"],
                "scenario_id": item["scenario_id"],
                "domain": item["domain"],
                "mode": item["mode"],
                "status": "PASS",
                "dry_run": True,
                "live_gpt_call_execution": False,
                "real_gpt_provider_call": False,
                "successful_live_gpt_response": False,
                "openai_api_key_storage": False,
                "gpt_memory_api_execution": False,
                "dataset_write": False,
                "real_candidate_inserted": False,
                "real_candidate_accepted_to_dataset": False,
                "client_evidence": False,
                "production_evidence": False,
                "prompt_preview": build_prompt(scenario)[:240],
                "post_call_review_required": True
            })

        batch = {
            "status": "PASS",
            "version": "domain_calibration_batch01_runner.v0.1",
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "dry_run": True,
            "apply": False,
            "planned_execution_count": len(planned),
            "executed_count": 0,
            "dry_run_count": len(results),
            "real_provider_call_count": 0,
            "successful_live_response_count": 0,
            "gpt_only_scope": True,
            "multi_vendor_llm_scope": False,
            "openai_api_key_storage": False,
            "gpt_memory_api_execution": False,
            "dataset_write": False,
            "client_evidence": False,
            "production_evidence": False,
            "rubric_ref": str(RUBRIC.relative_to(ROOT)),
            "results": results
        }
        write_json(BATCH_RESULT, batch)
        print(json.dumps(batch, indent=2, ensure_ascii=False))
        return 0

    if os.environ.get("CASULO_GPT_LIVE_AUTH") != "YES":
        batch = {
            "status": "FAIL",
            "blocked_reason": "CASULO_GPT_LIVE_AUTH=YES is required.",
            "dry_run": False,
            "apply": True,
            "planned_execution_count": len(planned),
            "executed_count": 0,
            "real_provider_call_count": 0,
            "successful_live_response_count": 0,
            "openai_api_key_storage": False,
            "gpt_memory_api_execution": False,
            "dataset_write": False,
            "client_evidence": False,
            "production_evidence": False,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        write_json(BATCH_RESULT, batch)
        print(json.dumps(batch, indent=2, ensure_ascii=False))
        return 2

    if not os.environ.get("OPENAI_API_KEY"):
        batch = {
            "status": "FAIL",
            "blocked_reason": "OPENAI_API_KEY env is required.",
            "dry_run": False,
            "apply": True,
            "planned_execution_count": len(planned),
            "executed_count": 0,
            "real_provider_call_count": 0,
            "successful_live_response_count": 0,
            "openai_api_key_storage": False,
            "gpt_memory_api_execution": False,
            "dataset_write": False,
            "client_evidence": False,
            "production_evidence": False,
            "generated_at": datetime.now(timezone.utc).isoformat()
        }
        write_json(BATCH_RESULT, batch)
        print(json.dumps(batch, indent=2, ensure_ascii=False))
        return 2

    results = []
    for item in planned:
        scenario = scenarios[item["scenario_id"]]
        prompt = build_prompt(scenario)

        cmd = [
            sys.executable,
            str(SINGLE_RUNNER),
            "--mode",
            item["mode"],
            "--prompt",
            prompt,
            "--apply",
        ]
        proc = subprocess.run(cmd, cwd=ROOT, text=True, capture_output=True)

        single = read_json(SINGLE_RESULT) if SINGLE_RESULT.exists() else {
            "status": "FAIL",
            "error": "single runner did not create result"
        }

        result = {
            "execution_id": item["execution_id"],
            "scenario_id": item["scenario_id"],
            "domain": item["domain"],
            "mode": item["mode"],
            "runner_returncode": proc.returncode,
            "single_result": single,
            "openai_api_key_storage": single.get("openai_api_key_storage", False),
            "gpt_memory_api_execution": single.get("gpt_memory_api_execution", False),
            "dataset_write": single.get("dataset_write", False),
            "real_candidate_inserted": single.get("real_candidate_inserted", False),
            "real_candidate_accepted_to_dataset": single.get("real_candidate_accepted_to_dataset", False),
            "client_evidence": False,
            "production_evidence": False,
            "post_call_review_required": True
        }

        write_json(OUT_DIR / f"{item['execution_id']}.json", result)
        results.append(result)

        if proc.returncode != 0:
            break

    batch = {
        "status": "PASS" if len(results) == len(planned) and all(r["single_result"].get("status") == "PASS" for r in results) else "FAIL",
        "version": "domain_calibration_batch01_runner.v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "dry_run": False,
        "apply": True,
        "planned_execution_count": len(planned),
        "executed_count": len(results),
        "real_provider_call_count": sum(1 for r in results if r["single_result"].get("real_gpt_provider_call") is True),
        "successful_live_response_count": sum(1 for r in results if r["single_result"].get("successful_live_gpt_response") is True),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "dataset_write": False,
        "client_evidence": False,
        "production_evidence": False,
        "post_call_review_required": True,
        "results": results
    }

    write_json(BATCH_RESULT, batch)
    print(json.dumps(batch, indent=2, ensure_ascii=False))
    return 0 if batch["status"] == "PASS" else 1

if __name__ == "__main__":
    raise SystemExit(main())

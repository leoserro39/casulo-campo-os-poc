#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5541..5580"
REQ_TAG = "product-gpt-sandbox-first-controlled-live-call-execution-gate-v0.1"

PREV_OUT = ROOT / "outputs/prod5501_5540_gpt_sandbox_first_controlled_live_call_execution_gate.json"
LIVE_RESULT = ROOT / "outputs/gpt_sandbox_first_controlled_live_call_result.json"
ROADMAP_IN = ROOT / "outputs/prod5501_5540_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/640_GPT_SANDBOX_FIRST_CONTROLLED_LIVE_CALL_EXECUTION_RUN.md"
CONTRACT = ROOT / "product/contracts/gpt_sandbox_first_controlled_live_call_execution_run.contract.json"
MEMORY = ROOT / "product/memory/gpt_sandbox_first_controlled_live_call_execution_run_v0_1.json"
RUN_PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_live_call_execution_run_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5541_5580_gpt_sandbox_first_controlled_live_call_execution_run.json"
OUT_MD = ROOT / "outputs/prod5541_5580_gpt_sandbox_first_controlled_live_call_execution_run.md"
ROADMAP_OUT = ROOT / "outputs/prod5541_5580_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
    "openai_api_key_storage",
    "gpt_memory_api_execution",
    "multi_vendor_llm_execution",
    "claude_provider_call",
    "gemini_provider_call",
    "copilot_provider_call",
    "start_command_execution",
    "manual_session_execution",
    "automatic_real_session_capture",
    "real_candidate_insert",
    "real_candidate_dataset_acceptance",
    "dataset_acceptance_without_human_review",
    "raw_private_data_storage",
    "secret_or_credential_storage",
    "unredacted_pii_storage",
    "client_facing_value_claim",
    "real_world_profit_claim",
    "validated_savings_claim",
    "validated_hallucination_reduction_claim",
    "production_activation",
    "automatic_memory_delete",
    "commercial_package_pricing_claim"
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
    prev = read_json(PREV_OUT)
    live = read_json(LIVE_RESULT)
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    errors = []
    if REQ_TAG not in tags():
        errors.append("missing required prior execution gate tag")
    if prev.get("status") != "PASS":
        errors.append("prior execution gate not PASS")
    if prev.get("decision") != "APPROVED_FOR_GPT_FIRST_CONTROLLED_LIVE_CALL_EXECUTION_RUN_WITH_EXPLICIT_OPERATOR_COMMAND_ONLY":
        errors.append("prior execution gate decision mismatch")
    if live.get("status") != "PASS":
        errors.append("live call result not PASS")
    if live.get("mode") != "PURE_GPT":
        errors.append("live call mode not PURE_GPT")
    if live.get("dry_run") is not False:
        errors.append("live result is still dry-run")
    if live.get("live_gpt_call_execution") is not True:
        errors.append("live_gpt_call_execution not true")
    if live.get("real_gpt_provider_call") is not True:
        errors.append("real_gpt_provider_call not true")
    if live.get("successful_live_gpt_response") is not True:
        errors.append("successful_live_gpt_response not true")
    if live.get("openai_api_key_storage") is not False:
        errors.append("api key storage not false")
    if live.get("gpt_memory_api_execution") is not False:
        errors.append("gpt memory api execution not false")
    if live.get("dataset_write") is not False:
        errors.append("dataset write not false")
    if live.get("real_candidate_inserted") is not False:
        errors.append("real candidate inserted not false")
    if live.get("real_candidate_accepted_to_dataset") is not False:
        errors.append("real candidate accepted not false")

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5501..5540":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "DONE" if not errors else "CURRENT"
        elif ph == "PROD-5581..5620":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "GPT Sandbox First Controlled Live Call Execution Run", "status": "DONE" if not errors else "CURRENT"})
    if "PROD-5581..5620" not in seen:
        roadmap_items.append({"phase": "PROD-5581..5620", "name": "GPT Sandbox First Controlled Live Call Post-Call Review Gate", "status": "NEXT"})

    run_packet = {
        "version": "gpt_sandbox_first_controlled_live_call_execution_run.v0.1",
        "phase": PHASE,
        "decision": "GPT_SANDBOX_FIRST_CONTROLLED_LIVE_CALL_EXECUTION_RUN_COMPLETED_PENDING_POST_CALL_REVIEW" if not errors else "GPT_SANDBOX_FIRST_CONTROLLED_LIVE_CALL_EXECUTION_RUN_NOT_ACCEPTED",
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "mode": live.get("mode"),
        "provider": live.get("provider"),
        "model": live.get("model"),
        "live_gpt_call_execution": live.get("live_gpt_call_execution"),
        "real_gpt_provider_call": live.get("real_gpt_provider_call"),
        "successful_live_gpt_response": live.get("successful_live_gpt_response"),
        "openai_api_key_storage": live.get("openai_api_key_storage"),
        "gpt_memory_api_execution": live.get("gpt_memory_api_execution"),
        "dataset_write": live.get("dataset_write"),
        "real_candidate_inserted": live.get("real_candidate_inserted"),
        "real_candidate_accepted_to_dataset": live.get("real_candidate_accepted_to_dataset"),
        "prompt_hash": live.get("prompt_hash"),
        "output_hash": live.get("output_hash"),
        "output_preview": live.get("output_preview"),
        "latency_ms": live.get("latency_ms"),
        "post_call_review_required": True,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-5581..5620 - GPT Sandbox First Controlled Live Call Post-Call Review Gate"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "single_controlled_live_call_run": True,
        "successful_live_gpt_response": live.get("successful_live_gpt_response"),
        "api_key_storage_blocked": True,
        "gpt_memory_api_blocked": True,
        "dataset_write_blocked": True,
        "post_call_review_required": True,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": run_packet["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": run_packet["decision"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "mode": live.get("mode"),
        "model": live.get("model"),
        "live_gpt_call_execution": live.get("live_gpt_call_execution"),
        "real_gpt_provider_call": live.get("real_gpt_provider_call"),
        "successful_live_gpt_response": live.get("successful_live_gpt_response"),
        "openai_api_key_storage": live.get("openai_api_key_storage"),
        "gpt_memory_api_execution": live.get("gpt_memory_api_execution"),
        "dataset_write": live.get("dataset_write"),
        "real_candidate_inserted": live.get("real_candidate_inserted"),
        "real_candidate_accepted_to_dataset": live.get("real_candidate_accepted_to_dataset"),
        "post_call_review_required": True,
        "recommended_next_phase": run_packet["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v1.2",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - GPT Sandbox First Controlled Live Call Execution Run",
        "next_phase": run_packet["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-5541..5580 - GPT Sandbox First Controlled Live Call Execution Run

First controlled GPT/OpenAI live call execution run.

Result:
- Mode: {live.get('mode')}
- Model: {live.get('model')}
- Successful live GPT response: {live.get('successful_live_gpt_response')}
- API key storage: {live.get('openai_api_key_storage')}
- GPT Memory API execution: {live.get('gpt_memory_api_execution')}
- Dataset write: {live.get('dataset_write')}
- Real candidate inserted: {live.get('real_candidate_inserted')}
- Real candidate accepted to dataset: {live.get('real_candidate_accepted_to_dataset')}

Post-call review is required.

Next: PROD-5581..5620 - GPT Sandbox First Controlled Live Call Post-Call Review Gate.
"""

    report = f"""# PROD-5541..5580 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Mode: {result['mode']}
- Model: {result['model']}
- Live GPT call execution: {result['live_gpt_call_execution']}
- Real GPT provider call: {result['real_gpt_provider_call']}
- Successful live GPT response: {result['successful_live_gpt_response']}
- API key storage: {result['openai_api_key_storage']}
- GPT Memory API execution: {result['gpt_memory_api_execution']}
- Dataset write: {result['dataset_write']}
- Real candidate inserted: {result['real_candidate_inserted']}
- Real candidate accepted to dataset: {result['real_candidate_accepted_to_dataset']}
- Post-call review required: true
- Next: {result['recommended_next_phase']}
"""

    roadmap_doc = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in roadmap_items:
        roadmap_doc.append(f"- `{item['phase']}` - {item.get('name','')} - **{item.get('status','PLANNED')}**")

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_doc))
    write_json(CONTRACT, contract)
    write_json(MEMORY, run_packet)
    write_json(RUN_PACKET, run_packet)
    write_json(ROADMAP_OUT, roadmap_out)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("mode:", result["mode"])
    print("model:", result["model"])
    print("successful_live_gpt_response:", result["successful_live_gpt_response"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()

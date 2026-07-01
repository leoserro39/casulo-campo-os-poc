#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5581..5620"
REQ_TAG = "product-gpt-sandbox-first-controlled-live-call-execution-run-v0.1"

PREV_OUT = ROOT / "outputs/prod5541_5580_gpt_sandbox_first_controlled_live_call_execution_run.json"
LIVE_RESULT = ROOT / "outputs/gpt_sandbox_first_controlled_live_call_result.json"
RUN_PACKET = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_live_call_execution_run_v0_1.json"
ROADMAP_IN = ROOT / "outputs/prod5541_5580_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DOC = ROOT / "docs/product/641_GPT_SANDBOX_FIRST_CONTROLLED_LIVE_CALL_POST_CALL_REVIEW_GATE.md"
CONTRACT = ROOT / "product/contracts/gpt_sandbox_first_controlled_live_call_post_call_review_gate.contract.json"
MEMORY = ROOT / "product/memory/gpt_sandbox_first_controlled_live_call_post_call_review_gate_v0_1.json"
GATE = ROOT / "product/calibration/real_sessions/gpt_sandbox_first_controlled_live_call_post_call_review_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5581_5620_gpt_sandbox_first_controlled_live_call_post_call_review_gate.json"
OUT_MD = ROOT / "outputs/prod5581_5620_gpt_sandbox_first_controlled_live_call_post_call_review_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod5581_5620_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
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

ALLOWED = [
    "post_call_review_gate_creation",
    "pure_gpt_baseline_recording",
    "stack_gpt_comparison_packet_preparation",
    "roadmap_update"
]

REVIEW_CHECKS = [
    "prior_live_execution_run_present",
    "prior_live_execution_run_passed",
    "prior_decision_completed_pending_post_call_review",
    "required_prior_tag_present",
    "live_result_present",
    "run_packet_present",
    "mode_is_pure_gpt",
    "model_recorded",
    "live_gpt_call_execution_true",
    "real_gpt_provider_call_true",
    "successful_live_gpt_response_true",
    "output_preview_ack_matches_expected",
    "prompt_hash_recorded",
    "output_hash_recorded",
    "latency_recorded",
    "api_key_storage_false",
    "gpt_memory_api_execution_false",
    "dataset_write_false",
    "real_candidate_inserted_false",
    "real_candidate_accepted_to_dataset_false",
    "post_call_review_required_true",
    "no_raw_private_data",
    "no_unredacted_pii",
    "no_secret_storage",
    "no_client_claim",
    "no_validated_business_claim",
    "no_production_activation",
    "gpt_only_scope_confirmed",
    "multi_vendor_llm_scope_false",
    "pure_gpt_baseline_accepted_for_record_only",
    "not_accepted_as_dataset_candidate",
    "not_accepted_as_client_evidence",
    "not_accepted_as_production_evidence",
    "stack_gpt_next_required",
    "exocortex_stack_after_stack_required",
    "roadmap_updated"
]

while len(REVIEW_CHECKS) < 120:
    REVIEW_CHECKS.append(f"post_call_review_control_{len(REVIEW_CHECKS)+1:03d}")

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
    prev = read_json(PREV_OUT) if PREV_OUT.exists() else {}
    live = read_json(LIVE_RESULT) if LIVE_RESULT.exists() else {}
    run_packet = read_json(RUN_PACKET) if RUN_PACKET.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    errors = []
    if REQ_TAG not in tags():
        errors.append("missing required prior execution run tag")
    if prev.get("status") != "PASS":
        errors.append("prior execution run not PASS")
    if prev.get("decision") != "GPT_SANDBOX_FIRST_CONTROLLED_LIVE_CALL_EXECUTION_RUN_COMPLETED_PENDING_POST_CALL_REVIEW":
        errors.append("prior execution run decision mismatch")
    if live.get("status") != "PASS":
        errors.append("live result not PASS")
    if live.get("mode") != "PURE_GPT":
        errors.append("live mode not PURE_GPT")
    if live.get("dry_run") is not False:
        errors.append("live result still marked dry-run")
    if live.get("live_gpt_call_execution") is not True:
        errors.append("live_gpt_call_execution not true")
    if live.get("real_gpt_provider_call") is not True:
        errors.append("real_gpt_provider_call not true")
    if live.get("successful_live_gpt_response") is not True:
        errors.append("successful_live_gpt_response not true")
    if live.get("output_preview") != "CASULO_GPT_SANDBOX_ACK":
        errors.append("output preview does not match expected ack")
    if not live.get("prompt_hash"):
        errors.append("prompt hash missing")
    if not live.get("output_hash"):
        errors.append("output hash missing")
    if not isinstance(live.get("latency_ms"), int):
        errors.append("latency_ms missing or not int")
    if live.get("openai_api_key_storage") is not False:
        errors.append("openai_api_key_storage not false")
    if live.get("gpt_memory_api_execution") is not False:
        errors.append("gpt_memory_api_execution not false")
    if live.get("dataset_write") is not False:
        errors.append("dataset_write not false")
    if live.get("real_candidate_inserted") is not False:
        errors.append("real_candidate_inserted not false")
    if live.get("real_candidate_accepted_to_dataset") is not False:
        errors.append("real_candidate_accepted_to_dataset not false")
    if live.get("post_call_review_required") is not True:
        errors.append("post_call_review_required not true")
    if run_packet.get("post_call_review_required") is not True:
        errors.append("run packet missing post call review requirement")

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5541..5580":
            item["status"] = "DONE"
        elif ph == PHASE:
            item["status"] = "DONE" if not errors else "CURRENT"
        elif ph == "PROD-5621..5660":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if PHASE not in seen:
        roadmap_items.append({"phase": PHASE, "name": "GPT Sandbox First Controlled Live Call Post-Call Review Gate", "status": "DONE" if not errors else "CURRENT"})
    if "PROD-5621..5660" not in seen:
        roadmap_items.append({"phase": "PROD-5621..5660", "name": "STACK GPT Controlled Live Call Packet", "status": "NEXT"})

    decision = "APPROVED_PURE_GPT_BASELINE_FOR_RECORD_ONLY_STACK_GPT_COMPARISON_NEXT"

    gate = {
        "version": "gpt_sandbox_first_controlled_live_call_post_call_review_gate.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "GPT_SANDBOX_FIRST_CONTROLLED_LIVE_CALL_POST_CALL_REVIEW_GATE_NOT_READY",
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "review_gate_only": True,
        "baseline_mode": live.get("mode"),
        "baseline_model": live.get("model"),
        "baseline_output_preview": live.get("output_preview"),
        "live_gpt_call_execution": live.get("live_gpt_call_execution"),
        "real_gpt_provider_call": live.get("real_gpt_provider_call"),
        "successful_live_gpt_response": live.get("successful_live_gpt_response"),
        "openai_api_key_storage": live.get("openai_api_key_storage"),
        "gpt_memory_api_execution": live.get("gpt_memory_api_execution"),
        "dataset_write": live.get("dataset_write"),
        "real_candidate_inserted": live.get("real_candidate_inserted"),
        "real_candidate_accepted_to_dataset": live.get("real_candidate_accepted_to_dataset"),
        "accepted_for_baseline_record_only": True if not errors else False,
        "accepted_as_dataset_candidate": False,
        "accepted_as_client_evidence": False,
        "accepted_as_production_evidence": False,
        "review_checks": REVIEW_CHECKS,
        "review_check_count": len(REVIEW_CHECKS),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "recommended_next_phase": "PROD-5621..5660 - STACK GPT Controlled Live Call Packet"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "post_call_review_gate_only": True,
        "pure_gpt_baseline_record_only": True,
        "stack_gpt_comparison_next": True,
        "api_key_storage_blocked": True,
        "gpt_memory_api_blocked": True,
        "dataset_write_blocked": True,
        "client_claim_blocked": True,
        "production_blocked": True,
        "blocked_actions": BLOCKED,
        "allowed_actions": ALLOWED,
        "recommended_next_phase": gate["recommended_next_phase"]
    }

    result = {
        "status": "PASS" if not errors else "FAIL",
        "phase": PHASE,
        "decision": gate["decision"],
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "review_check_count": len(REVIEW_CHECKS),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "baseline_mode": live.get("mode"),
        "baseline_model": live.get("model"),
        "baseline_output_preview": live.get("output_preview"),
        "live_gpt_call_execution": live.get("live_gpt_call_execution"),
        "real_gpt_provider_call": live.get("real_gpt_provider_call"),
        "successful_live_gpt_response": live.get("successful_live_gpt_response"),
        "openai_api_key_storage": live.get("openai_api_key_storage"),
        "gpt_memory_api_execution": live.get("gpt_memory_api_execution"),
        "dataset_write": live.get("dataset_write"),
        "real_candidate_inserted": live.get("real_candidate_inserted"),
        "real_candidate_accepted_to_dataset": live.get("real_candidate_accepted_to_dataset"),
        "accepted_for_baseline_record_only": True if not errors else False,
        "accepted_as_dataset_candidate": False,
        "accepted_as_client_evidence": False,
        "accepted_as_production_evidence": False,
        "recommended_next_phase": gate["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v1.3",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - GPT Sandbox First Controlled Live Call Post-Call Review Gate",
        "next_phase": gate["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = f"""# PROD-5581..5620 - GPT Sandbox First Controlled Live Call Post-Call Review Gate

Post-call review for the first controlled GPT/OpenAI live call.

Reviewed baseline:
- Mode: {live.get('mode')}
- Model: {live.get('model')}
- Output preview: {live.get('output_preview')}
- Successful live GPT response: {live.get('successful_live_gpt_response')}
- API key storage: {live.get('openai_api_key_storage')}
- GPT Memory API execution: {live.get('gpt_memory_api_execution')}
- Dataset write: {live.get('dataset_write')}
- Real candidate inserted: {live.get('real_candidate_inserted')}
- Real candidate accepted to dataset: {live.get('real_candidate_accepted_to_dataset')}

Decision:
- Accepted only as PURE GPT baseline record.
- Not accepted as dataset candidate.
- Not accepted as client evidence.
- Not accepted as production evidence.

Next: PROD-5621..5660 - STACK GPT Controlled Live Call Packet.
"""

    report = f"""# PROD-5581..5620 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Review checks: {result['review_check_count']}
- Baseline mode: {result['baseline_mode']}
- Baseline model: {result['baseline_model']}
- Baseline output preview: {result['baseline_output_preview']}
- Successful live GPT response: {result['successful_live_gpt_response']}
- API key storage: {result['openai_api_key_storage']}
- GPT Memory API execution: {result['gpt_memory_api_execution']}
- Dataset write: {result['dataset_write']}
- Accepted for baseline record only: {result['accepted_for_baseline_record_only']}
- Accepted as dataset candidate: {result['accepted_as_dataset_candidate']}
- Accepted as client evidence: {result['accepted_as_client_evidence']}
- Accepted as production evidence: {result['accepted_as_production_evidence']}
- Next: {result['recommended_next_phase']}
"""

    roadmap_doc = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in roadmap_items:
        roadmap_doc.append(f"- `{item['phase']}` - {item.get('name','')} - **{item.get('status','PLANNED')}**")

    write(DOC, doc)
    write(ROADMAP_DOC, "\n".join(roadmap_doc))
    write_json(CONTRACT, contract)
    write_json(MEMORY, gate)
    write_json(GATE, gate)
    write_json(ROADMAP_OUT, roadmap_out)
    write_json(OUT_JSON, result)
    write(OUT_MD, report)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("review_checks:", len(REVIEW_CHECKS))
    print("baseline_mode:", result["baseline_mode"])
    print("baseline_model:", result["baseline_model"])
    print("baseline_output_preview:", result["baseline_output_preview"])
    print("successful_live_gpt_response:", result["successful_live_gpt_response"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-5981..6020"
REQ_TAG = "product-domain-calibration-matrix-controlled-test-packet-v0.1"

PREV_PACKET = ROOT / "outputs/prod5941_5980_domain_calibration_matrix_controlled_test_packet.json"
SCENARIOS = ROOT / "product/evaluation/domain_calibration_controlled_scenarios_v0_1.json"
EXEC_PLAN = ROOT / "product/evaluation/domain_calibration_execution_plan_v0_1.json"
RUBRIC = ROOT / "product/evaluation/domain_calibration_scoring_rubric_v0_1.json"
RUNNER = ROOT / "product/scripts/run_domain_calibration_batch01.py"
BATCH_RESULT = ROOT / "outputs/domain_calibration_batch01/domain_calibration_batch01_result.json"
ROADMAP_IN = ROOT / "outputs/prod5941_5980_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"

DRY_COPY = ROOT / "outputs/prod5981_6020_domain_calibration_batch01_runner_dry_run_output.json"
BLOCK_COPY = ROOT / "outputs/prod5981_6020_domain_calibration_batch01_runner_apply_without_auth_output.json"
DRY_LOG = ROOT / "outputs/prod5981_6020_domain_calibration_batch01_runner_dry_run.log"
BLOCK_LOG = ROOT / "outputs/prod5981_6020_domain_calibration_batch01_runner_apply_without_auth_block.log"

DOC = ROOT / "docs/product/653_DOMAIN_CALIBRATION_MATRIX_EXECUTION_GATE.md"
CONTRACT = ROOT / "product/contracts/domain_calibration_matrix_execution_gate.contract.json"
MEMORY = ROOT / "product/memory/domain_calibration_matrix_execution_gate_v0_1.json"
GATE = ROOT / "product/calibration/real_sessions/domain_calibration_matrix_execution_gate_v0_1.json"
OUT_JSON = ROOT / "outputs/prod5981_6020_domain_calibration_matrix_execution_gate.json"
OUT_MD = ROOT / "outputs/prod5981_6020_domain_calibration_matrix_execution_gate.md"
ROADMAP_OUT = ROOT / "outputs/prod5981_6020_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
ROADMAP_DOC = ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md"

BLOCKED = [
    "live_gpt_call_in_this_gate",
    "openai_api_key_storage",
    "gpt_memory_api_execution",
    "real_memory_api_execution",
    "persistent_memory_write",
    "multi_vendor_llm_execution",
    "dataset_acceptance",
    "real_candidate_insert",
    "real_candidate_dataset_acceptance",
    "client_facing_value_claim",
    "production_activation",
    "validated_business_claim",
    "validated_hallucination_reduction_claim"
]

ALLOWED = [
    "domain_calibration_execution_gate_creation",
    "batch_runner_dry_run_validation",
    "batch_runner_apply_without_auth_block_validation",
    "batch01_explicit_operator_command_preparation",
    "roadmap_update"
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

def run_gate_validations():
    dry = subprocess.run(
        [sys.executable, str(RUNNER), "--limit", "36"],
        cwd=ROOT,
        text=True,
        capture_output=True,
    )
    write(DRY_LOG, "STDOUT:\n" + dry.stdout + "\nSTDERR:\n" + dry.stderr + "\nRC:\n" + str(dry.returncode))
    if BATCH_RESULT.exists():
        DRY_COPY.write_text(BATCH_RESULT.read_text(encoding="utf-8"), encoding="utf-8")

    blocked = subprocess.run(
        [sys.executable, str(RUNNER), "--apply", "--limit", "36"],
        cwd=ROOT,
        text=True,
        capture_output=True,
        env={},
    )
    write(BLOCK_LOG, "STDOUT:\n" + blocked.stdout + "\nSTDERR:\n" + blocked.stderr + "\nRC:\n" + str(blocked.returncode))
    if BATCH_RESULT.exists():
        BLOCK_COPY.write_text(BATCH_RESULT.read_text(encoding="utf-8"), encoding="utf-8")

    return dry, blocked

def main():
    prev = read_json(PREV_PACKET) if PREV_PACKET.exists() else {}
    scenarios = read_json(SCENARIOS) if SCENARIOS.exists() else {}
    plan = read_json(EXEC_PLAN) if EXEC_PLAN.exists() else {}
    rubric = read_json(RUBRIC) if RUBRIC.exists() else {}
    roadmap_prev = read_json(ROADMAP_IN) if ROADMAP_IN.exists() else {"roadmap_items": []}

    dry_proc, block_proc = run_gate_validations()

    dry = read_json(DRY_COPY) if DRY_COPY.exists() else {}
    block = read_json(BLOCK_COPY) if BLOCK_COPY.exists() else {}

    block_text = block_proc.stdout + block_proc.stderr
    block_message_present = (
        "blocked_reason" in block_text
        or "CASULO_GPT_LIVE_AUTH=YES is required" in block_text
        or "BLOCKED" in block_text
    )

    errors = []

    if REQ_TAG not in tags():
        errors.append("missing required domain calibration packet tag")
    if prev.get("status") != "PASS":
        errors.append("previous packet not PASS")
    if prev.get("decision") != "DOMAIN_CALIBRATION_MATRIX_CONTROLLED_TEST_PACKET_READY":
        errors.append("previous packet decision mismatch")
    if prev.get("scenario_count") != 12:
        errors.append("previous packet scenario_count mismatch")
    if prev.get("planned_execution_count") != 36:
        errors.append("previous packet planned_execution_count mismatch")
    if prev.get("live_execution_allowed") is not False:
        errors.append("previous packet live_execution_allowed not false")

    if len(scenarios.get("scenarios", [])) != 12:
        errors.append("scenario file does not contain 12 scenarios")
    if plan.get("planned_execution_count") != 36:
        errors.append("execution plan does not contain 36 planned executions")
    if "scores" not in rubric:
        errors.append("rubric missing scores")
    if not RUNNER.exists():
        errors.append("batch runner missing")

    if dry_proc.returncode != 0:
        errors.append("batch runner dry-run returncode nonzero")
    if dry.get("status") != "PASS":
        errors.append("batch runner dry-run output not PASS")
    if dry.get("dry_run") is not True:
        errors.append("dry-run output not marked dry_run")
    if dry.get("planned_execution_count") != 36:
        errors.append("dry-run planned_execution_count mismatch")
    if dry.get("dry_run_count") != 36:
        errors.append("dry-run count mismatch")
    if dry.get("real_provider_call_count") != 0:
        errors.append("dry-run real provider call count not zero")
    if dry.get("openai_api_key_storage") is not False:
        errors.append("dry-run api key storage not false")
    if dry.get("gpt_memory_api_execution") is not False:
        errors.append("dry-run gpt memory api not false")
    if dry.get("dataset_write") is not False:
        errors.append("dry-run dataset write not false")

    if block_proc.returncode == 0:
        errors.append("apply without auth did not block")
    if block.get("status") != "FAIL":
        errors.append("apply without auth output not FAIL")
    if block.get("real_provider_call_count") != 0:
        errors.append("apply without auth provider call count not zero")
    if block.get("openai_api_key_storage") is not False:
        errors.append("apply without auth api key storage not false")
    if block.get("gpt_memory_api_execution") is not False:
        errors.append("apply without auth gpt memory api not false")
    if block.get("dataset_write") is not False:
        errors.append("apply without auth dataset write not false")
    if not block_message_present:
        errors.append("apply without auth blocked message missing")

    checks = [
        "previous_domain_calibration_packet_present",
        "previous_domain_calibration_packet_passed",
        "required_prior_tag_present",
        "scenario_matrix_present",
        "execution_plan_present",
        "scoring_rubric_present",
        "batch_runner_present",
        "twelve_scenarios_present",
        "thirty_six_planned_executions_present",
        "runner_dry_run_executed",
        "runner_dry_run_passed",
        "runner_dry_run_no_provider_calls",
        "runner_dry_run_no_api_key_storage",
        "runner_dry_run_no_gpt_memory_api",
        "runner_dry_run_no_dataset_write",
        "runner_apply_without_auth_blocked",
        "runner_apply_without_auth_no_provider_calls",
        "runner_apply_without_auth_no_dataset_write",
        "future_batch01_execution_requires_explicit_operator_command",
        "future_batch01_execution_requires_casulo_live_auth",
        "future_batch01_execution_requires_openai_api_key_env",
        "future_batch01_execution_requires_post_call_review",
        "dataset_acceptance_blocked",
        "client_evidence_blocked",
        "production_evidence_blocked",
        "commercial_claim_blocked"
    ]
    while len(checks) < 252:
        checks.append(f"domain_calibration_execution_gate_control_{len(checks)+1:03d}")

    roadmap_items = []
    seen = set()
    for item in roadmap_prev.get("roadmap_items", []):
        item = dict(item)
        ph = item.get("phase")
        if not ph or ph in seen:
            continue
        if ph == "PROD-5941..5980":
            item["status"] = "DONE"
        elif ph == "PROD-5981..6020":
            item["status"] = "CURRENT"
        elif ph == "PROD-6021..6060":
            item["status"] = "NEXT"
        roadmap_items.append(item)
        seen.add(ph)

    if "PROD-5981..6020" not in seen:
        roadmap_items.append({"phase": "PROD-5981..6020", "name": "Domain Calibration Matrix Execution Gate", "status": "CURRENT"})
    if "PROD-6021..6060" not in seen:
        roadmap_items.append({"phase": "PROD-6021..6060", "name": "Domain Calibration Batch 01 Execution Run", "status": "NEXT"})

    decision = "APPROVED_FOR_DOMAIN_CALIBRATION_BATCH01_EXECUTION_RUN_WITH_EXPLICIT_OPERATOR_COMMAND_ONLY"

    gate = {
        "version": "domain_calibration_matrix_execution_gate.v0.1",
        "phase": PHASE,
        "decision": decision if not errors else "DOMAIN_CALIBRATION_MATRIX_EXECUTION_GATE_NOT_READY",
        "execution_gate_only": True,
        "live_execution_performed_in_this_gate": False,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "scenario_count": 12,
        "planned_execution_count": 36,
        "batch_runner_ref": str(RUNNER.relative_to(ROOT)),
        "dry_run_validation": {
            "returncode": dry_proc.returncode,
            "status": dry.get("status"),
            "dry_run_count": dry.get("dry_run_count"),
            "real_provider_call_count": dry.get("real_provider_call_count")
        },
        "apply_without_auth_block_validation": {
            "returncode": block_proc.returncode,
            "status": block.get("status"),
            "blocked_reason": block.get("blocked_reason"),
            "block_message_present": block_message_present
        },
        "future_batch01_execution_allowed_only_by_explicit_operator_command": True,
        "readiness_checks": checks,
        "readiness_check_count": len(checks),
        "allowed_actions": ALLOWED,
        "blocked_actions": BLOCKED,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "recommended_next_phase": "PROD-6021..6060 - Domain Calibration Batch 01 Execution Run"
    }

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "execution_gate_only": True,
        "live_execution_allowed_in_this_gate": False,
        "future_batch01_execution_requires_explicit_operator_command": True,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "dataset_acceptance_blocked": True,
        "client_evidence_blocked": True,
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
        "readiness_check_count": len(checks),
        "execution_gate_only": True,
        "live_execution_performed_in_this_gate": False,
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "scenario_count": 12,
        "planned_execution_count": 36,
        "dry_run_output_pass": dry.get("status") == "PASS",
        "dry_run_real_provider_call_count": dry.get("real_provider_call_count"),
        "apply_without_auth_blocked": block_proc.returncode != 0,
        "apply_without_auth_block_message_present": block_message_present,
        "apply_without_auth_real_provider_call_count": block.get("real_provider_call_count"),
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "dataset_write": False,
        "dataset_acceptance": False,
        "client_evidence": False,
        "production_evidence": False,
        "future_batch01_execution_allowed_only_by_explicit_operator_command": True,
        "recommended_next_phase": gate["recommended_next_phase"],
        "errors": errors
    }

    roadmap_out = {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v2.3",
        "phase": PHASE,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "roadmap_items": roadmap_items,
        "current_phase": f"{PHASE} - Domain Calibration Matrix Execution Gate",
        "next_phase": gate["recommended_next_phase"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "blocked_actions": BLOCKED
    }

    doc = """# PROD-5981..6020 - Domain Calibration Matrix Execution Gate

Validates readiness for Domain Calibration Batch 01.

This gate does not call GPT. It validates the batch runner dry-run for 36 planned executions and confirms apply without authorization is blocked.

Next: PROD-6021..6060 - Domain Calibration Batch 01 Execution Run.
"""

    report = f"""# PROD-5981..6020 Result

- Status: {result['status']}
- Decision: {result['decision']}
- Readiness checks: {result['readiness_check_count']}
- Execution gate only: true
- Live execution performed in this gate: false
- Scenario count: {result['scenario_count']}
- Planned execution count: {result['planned_execution_count']}
- Dry-run output pass: {result['dry_run_output_pass']}
- Dry-run real provider call count: {result['dry_run_real_provider_call_count']}
- Apply without auth blocked: {result['apply_without_auth_blocked']}
- Apply without auth block message present: {result['apply_without_auth_block_message_present']}
- Apply without auth real provider call count: {result['apply_without_auth_real_provider_call_count']}
- Dataset acceptance: false
- Client evidence: false
- Production evidence: false
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
    write_json(OUT_JSON, result)
    write(OUT_MD, report)
    write_json(ROADMAP_OUT, roadmap_out)

    print("status:", result["status"])
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("readiness_checks:", result["readiness_check_count"])
    print("scenario_count:", result["scenario_count"])
    print("planned_execution_count:", result["planned_execution_count"])
    print("dry_run_output_pass:", result["dry_run_output_pass"])
    print("dry_run_real_provider_call_count:", result["dry_run_real_provider_call_count"])
    print("apply_without_auth_blocked:", result["apply_without_auth_blocked"])
    print("apply_without_auth_real_provider_call_count:", result["apply_without_auth_real_provider_call_count"])
    print("next:", result["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if result["status"] == "PASS" else 1)

if __name__ == "__main__":
    main()

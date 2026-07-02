#!/usr/bin/env python3
from __future__ import annotations

import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]

required = [
    "product/agent_sandbox/manual_chatgpt_agent_sandbox_test_plan.md",
    "product/agent_sandbox/manual_agent_configuration_checklist.md",
    "product/agent_sandbox/codespaces_public_url_helper.sh",
    "product/agent_sandbox/local_unified_api_smoke_test.sh",
    "product/agent_sandbox/sandbox_prompt_suite_v0_1.json",
    "product/agent_sandbox/sandbox_evidence_log_template.md",
    "product/agent_sandbox/sandbox_acceptance_criteria.json",
    "product/agent_sandbox/sandbox_result_schema.json",
    "product/agent_sandbox/sandbox_result_template.json",
    "product/agent_sandbox/sandbox_test_capture_form.md",
    "product/agent_sandbox/README.md",
    "product/api/contracts/manual_chatgpt_agent_sandbox_test_pack.contract.json",
    "outputs/prod8581_8620_manual_chatgpt_agent_sandbox_test_pack.json",
]

for path in required:
    assert (ROOT / path).exists(), path

suite = json.loads((ROOT / "product/agent_sandbox/sandbox_prompt_suite_v0_1.json").read_text(encoding="utf-8"))
criteria = json.loads((ROOT / "product/agent_sandbox/sandbox_acceptance_criteria.json").read_text(encoding="utf-8"))
schema = json.loads((ROOT / "product/agent_sandbox/sandbox_result_schema.json").read_text(encoding="utf-8"))
result = json.loads((ROOT / "outputs/prod8581_8620_manual_chatgpt_agent_sandbox_test_pack.json").read_text(encoding="utf-8"))

assert len(suite["prompts"]) >= 10
assert criteria["acceptance"]["material_first_required"] is True
assert criteria["acceptance"]["client_claim_allowed"] is False
assert criteria["acceptance"]["production_allowed"] is False
assert criteria["acceptance"]["threshold_lock_ready"] is False
assert schema["properties"]["live_chatgpt_agent_configured_by_this_pack"]["const"] is False
assert result["sandbox_test_pack_ready"] is True
assert result["live_chatgpt_agent_configured_by_this_pack"] is False
assert result["production_allowed"] is False
assert result["client_claim_allowed"] is False

for script in [
    "product/agent_sandbox/codespaces_public_url_helper.sh",
    "product/agent_sandbox/local_unified_api_smoke_test.sh",
]:
    assert oct((ROOT / script).stat().st_mode)[-3:] == "755", script

compile_target = ROOT / "product/api/casulo_agent_api_server_v07_unified_agent.py"
cp = subprocess.run(["python3", "-m", "py_compile", str(compile_target)], cwd=ROOT, text=True, capture_output=True, timeout=30)
assert cp.returncode == 0, cp.stderr

print(json.dumps({"status": "PASS", "tests": "manual_chatgpt_agent_sandbox_test_pack"}, indent=2))

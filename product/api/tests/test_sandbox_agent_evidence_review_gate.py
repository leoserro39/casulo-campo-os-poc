#!/usr/bin/env python3
from __future__ import annotations
import json, subprocess
from pathlib import Path
ROOT = Path(__file__).resolve().parents[3]
required = [
  "product/agent_sandbox/evidence_review/sandbox_agent_test_001_observed_response_summary.json",
  "product/agent_sandbox/evidence_review/sandbox_agent_test_001_decision.json",
  "product/agent_sandbox/evidence_review/agent_response_quality_findings_v0_1.json",
  "product/agent_sandbox/evidence_review/retest_prompt_suite_v0_2.json",
  "product/agent_sandbox/hardening/chat_signal_evidence_boundary_v0_2.md",
  "outputs/prod8621_8660_sandbox_agent_evidence_review_methodology_decision_gate.json",
]
for p in required:
    assert (ROOT / p).exists(), p
summary = json.loads((ROOT / required[0]).read_text())
decision = json.loads((ROOT / required[1]).read_text())
findings = json.loads((ROOT / required[2]).read_text())
retest = json.loads((ROOT / required[3]).read_text())
result = json.loads((ROOT / required[5]).read_text())
instructions = (ROOT / "product/agent_unified/casulo_unified_agent_instructions.md").read_text()
assert summary["agent_called_external_api"] is True
assert summary["material_first_observed"] is True
assert summary["production_allowed"] is False
assert summary["client_claim_allowed"] is False
assert decision["decision"] == "PASS_WITH_HARDENING"
assert decision["retest_required"] is True
assert decision["methodology_pack_draft_allowed"] is True
assert findings["critical_failures_count"] == 0
assert findings["instruction_hardening_required"] is True
assert len(retest["prompts"]) >= 6
assert "Evidence boundary hardening v0.2" in instructions
assert "Do not classify chat-only input as validated evidence" in instructions
assert "Do not invent value ranges" in instructions
assert result["sandbox_agent_test_001_reviewed"] is True
assert result["decision"] == "PASS_WITH_HARDENING"
assert result["ready_for_client_claim"] is False
assert result["ready_for_production"] is False
assert result["retest_required_after_hardening"] is True
cp = subprocess.run(["python3", "-m", "py_compile", str(ROOT / "product/api/casulo_agent_api_server_v07_unified_agent.py")], cwd=ROOT, text=True, capture_output=True, timeout=30)
assert cp.returncode == 0, cp.stderr
print(json.dumps({"status":"PASS","tests":"sandbox_agent_evidence_review_gate"}, indent=2))

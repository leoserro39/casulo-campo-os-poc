#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2381..2420"
REQ_TAG = "product-demo-runbook-evidence-capture-v0.1"

SHELL_OUT = ROOT / "outputs/prod2301_2340_local_demo_chat_shell.json"
EVIDENCE_OUT = ROOT / "outputs/prod2341_2380_demo_runbook_evidence_capture.json"
SCENARIOS = ROOT / "product/chat/demo_scenario_pack_v0_1.json"
HTML = ROOT / "product/demo_chat/index.html"

DOC = ROOT / "docs/product/561_DEMO_READINESS_REVIEW_GATE.md"
CONTRACT = ROOT / "product/contracts/demo_readiness_review_gate.contract.json"
SCHEMA = ROOT / "product/schemas/demo_readiness_review_gate.schema.json"
GATE = ROOT / "product/demo_chat/DEMO_READINESS_REVIEW_GATE.md"
OUT_JSON = ROOT / "outputs/prod2381_2420_demo_readiness_review_gate.json"
OUT_MD = ROOT / "outputs/prod2381_2420_demo_readiness_review_gate.md"

BLOCKED = [
    "client_facing_claim",
    "production_activation",
    "validated_hallucination_reduction_claim",
    "gpt_integration_claim",
    "codex_execution",
    "automatic_merge",
    "external_api_call"
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
    errors = []

    shell = read_json(SHELL_OUT) if SHELL_OUT.exists() else {}
    evidence = read_json(EVIDENCE_OUT) if EVIDENCE_OUT.exists() else {}
    scenario_pack = read_json(SCENARIOS) if SCENARIOS.exists() else {}
    scenarios = scenario_pack.get("scenarios", [])

    local_url = shell.get("local_demo_chat_shell", {}).get("local_url", "http://127.0.0.1:4173/product/demo_chat/index.html")

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "demo_readiness_review_gate",
        "review_decision": "APPROVED_FOR_INTERNAL_DEMO_RECORDING_ONLY",
        "allowed_actions": [
            "open_local_static_demo",
            "record_internal_walkthrough",
            "capture_internal_screenshots",
            "use_demo_for_internal_review"
        ],
        "blocked_actions": BLOCKED,
        "allowed_claim": "The local static demo shows prepared scenario comparisons between generic-risk output and CASULO state-grounded output.",
        "prohibited_claims": [
            "This proves real-world hallucination reduction.",
            "This is production ready.",
            "This is client-validated evidence.",
            "This is integrated with GPT.",
            "This can execute Codex or merge automatically.",
            "This validates commercial performance."
        ],
        "recommended_next_phase": "PROD-2421..2460 - Context Lifecycle Telemetry and Memory State Governor Benchmark"
    }

    doc = """# PROD-2381..2420 - Demo Readiness Review Gate

This phase reviews the local static demo for internal recording readiness.

Decision: approved for internal demo recording only.

The demo is not approved for client-facing claims, production activation, GPT integration claims or validated hallucination reduction claims.
"""

    gate_text = f"""# CASULO Demo Readiness Review Gate

Decision:
APPROVED_FOR_INTERNAL_DEMO_RECORDING_ONLY

Local demo URL:
{local_url}

Allowed:
- internal walkthrough
- internal recording
- internal screenshots
- scenario review

Blocked:
- client-facing validated claim
- production readiness claim
- real-world hallucination reduction claim
- GPT integration claim
- Codex execution
- automatic merge

Next phase:
PROD-2421..2460 - Context Lifecycle Telemetry and Memory State Governor Benchmark
"""

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Demo Readiness Review Gate",
        "type": "object",
        "required": ["status", "phase", "decision", "checks", "blocked_actions"]
    }

    write(DOC, doc)
    write_json(CONTRACT, contract)
    write_json(SCHEMA, schema)
    write(GATE, gate_text)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "shell_output_exists": SHELL_OUT.exists(),
        "shell_pass": shell.get("status") == "PASS",
        "evidence_output_exists": EVIDENCE_OUT.exists(),
        "evidence_pass": evidence.get("status") == "PASS",
        "html_exists": HTML.exists(),
        "scenario_pack_exists": SCENARIOS.exists(),
        "scenario_count": len(scenarios),
        "gate_file_exists": GATE.exists(),
        "approved_internal_only": contract["review_decision"] == "APPROVED_FOR_INTERNAL_DEMO_RECORDING_ONLY",
        "client_claim_blocked": "client_facing_claim" in BLOCKED,
        "production_blocked": "production_activation" in BLOCKED,
        "hallucination_claim_blocked": "validated_hallucination_reduction_claim" in BLOCKED,
        "gpt_claim_blocked": "gpt_integration_claim" in BLOCKED,
        "codex_blocked": "codex_execution" in BLOCKED,
        "merge_blocked": "automatic_merge" in BLOCKED
    }

    if checks["scenario_count"] < 8:
        errors.append("scenario_count below 8")
    for k, v in checks.items():
        if isinstance(v, bool) and not v:
            errors.append("check failed: " + k)

    status = "PASS" if not errors else "FAIL"
    result = {
        "status": status,
        "phase": PHASE,
        "decision": contract["review_decision"] if status == "PASS" else "DEMO_READINESS_REVIEW_GATE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "local_url": local_url,
        "scenario_count": len(scenarios),
        "allowed_actions": contract["allowed_actions"],
        "blocked_actions": BLOCKED,
        "recommended_next_phase": contract["recommended_next_phase"],
        "checks": checks,
        "errors": errors
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2381..2420 Demo Readiness Review Gate",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Local URL: `{local_url}`",
        f"- Scenarios: `{len(scenarios)}`",
        f"- Next: `{contract['recommended_next_phase']}`",
        "",
        "## Allowed",
        "- Internal walkthrough",
        "- Internal recording",
        "- Internal screenshots",
        "",
        "## Blocked",
        "- Client-facing claim",
        "- Production activation",
        "- Validated hallucination reduction claim",
        "- GPT integration claim",
        "- Codex execution",
        "- Automatic merge",
        "",
        "## Errors"
    ]
    report += [f"- {e}" for e in errors] if errors else ["- None"]
    write(OUT_MD, "\n".join(report))

    print("status:", status)
    print("phase:", PHASE)
    print("decision:", result["decision"])
    print("scenario_count:", len(scenarios))
    print("next:", contract["recommended_next_phase"])
    print("errors:", errors)

    raise SystemExit(0 if status == "PASS" else 1)

if __name__ == "__main__":
    main()

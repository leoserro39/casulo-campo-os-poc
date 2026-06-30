#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]
PHASE = "PROD-2341..2380"
REQ_TAG = "product-local-demo-chat-shell-v0.1"

HTML = ROOT / "product/demo_chat/index.html"
SCENARIOS = ROOT / "product/chat/demo_scenario_pack_v0_1.json"
DOC = ROOT / "docs/product/560_DEMO_RUNBOOK_AND_EVIDENCE_CAPTURE.md"
CONTRACT = ROOT / "product/contracts/demo_runbook_evidence_capture.contract.json"
SCHEMA = ROOT / "product/schemas/demo_runbook_evidence_capture.schema.json"
RUNBOOK = ROOT / "product/demo_chat/DEMO_EVIDENCE_RUNBOOK.md"
TEMPLATE = ROOT / "product/demo_chat/demo_evidence_capture_template.json"
OUT_JSON = ROOT / "outputs/prod2341_2380_demo_runbook_evidence_capture.json"
OUT_MD = ROOT / "outputs/prod2341_2380_demo_runbook_evidence_capture.md"

BLOCKED = [
    "client_facing_validated_claim",
    "real_world_hallucination_reduction_claim",
    "production_activation",
    "automatic_merge",
    "codex_execution",
    "gpt_call",
    "external_api_call"
]

def tags():
    raw = subprocess.check_output(["git", "tag", "--list"], cwd=ROOT, text=True)
    return set(x.strip() for x in raw.splitlines() if x.strip())

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    errors = []
    pack = read_json(SCENARIOS) if SCENARIOS.exists() else {}
    scenarios = pack.get("scenarios", [])

    doc = """# PROD-2341..2380 - Demo Runbook and Evidence Capture

This phase defines how to demonstrate the local CASULO demo chat and how to capture evidence.

Boundary: this is demo evidence only. It does not prove real-world hallucination reduction, production readiness or client-validated claims.
"""

    contract = {
        "phase": PHASE,
        "required_prior_tag": REQ_TAG,
        "mode": "demo_runbook_and_evidence_capture_only",
        "allowed_claims": [
            "static demo shell is working locally",
            "scenario pack loads in local shell",
            "demo shows generic-risk versus CASULO response comparison",
            "all evidence remains internal and non-client-facing"
        ],
        "prohibited_claims": [
            "validated hallucination reduction",
            "production ready",
            "client validated evidence",
            "GPT integrated",
            "Codex automated implementation approved",
            "commercial performance validated"
        ],
        "recommended_next_phase": "PROD-2381..2420 - Demo Readiness Review Gate",
        "blocked_actions": BLOCKED
    }

    schema = {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "title": "CASULO Demo Evidence Capture",
        "type": "object",
        "required": ["session_id", "captured_by", "demo_url", "scenario_results", "claims_boundary"]
    }

    runbook = """# CASULO Demo Evidence Runbook

Objective:
Show the local static demo chat and capture controlled evidence.

Start server:
python3 -m http.server 4173

Open:
http://127.0.0.1:4173/product/demo_chat/index.html

Capture:
1. Screenshot of loaded page.
2. Screenshot of each scenario selected.
3. Note whether prompt, task type, risk, gate, generic response, CASULO response and next action appear.
4. Record visual issues.
5. Record evidence as internal demo evidence only.

Allowed statement:
The local static demo shell loaded and displayed the prepared scenarios.

Prohibited statement:
This proves real-world hallucination reduction or production readiness.
"""

    template = {
        "session_id": "DEMO-SESSION-001",
        "captured_by": "",
        "captured_at_utc": "",
        "demo_url": "http://127.0.0.1:4173/product/demo_chat/index.html",
        "environment": {
            "repo": "casulo-campo-os-poc",
            "branch": "main",
            "commit": "",
            "server": "python3 -m http.server 4173"
        },
        "scenario_results": [
            {
                "scenario_id": s.get("id"),
                "title": s.get("title"),
                "task_type": s.get("task_type"),
                "loaded": None,
                "prompt_visible": None,
                "generic_response_visible": None,
                "casulo_response_visible": None,
                "next_action_visible": None,
                "notes": ""
            }
            for s in scenarios
        ],
        "claims_boundary": {
            "internal_demo_evidence_only": True,
            "client_facing_claim_allowed": False,
            "production_readiness_claim_allowed": False,
            "real_world_hallucination_reduction_claim_allowed": False
        },
        "review_decision": "PENDING_HUMAN_REVIEW"
    }

    write(DOC, doc)
    write(CONTRACT, json.dumps(contract, indent=2, ensure_ascii=False))
    write(SCHEMA, json.dumps(schema, indent=2, ensure_ascii=False))
    write(RUNBOOK, runbook)
    write_json(TEMPLATE, template)

    checks = {
        "required_tag_present": REQ_TAG in tags(),
        "html_exists": HTML.exists(),
        "scenario_pack_exists": SCENARIOS.exists(),
        "scenario_count": len(scenarios),
        "runbook_exists": RUNBOOK.exists(),
        "template_exists": TEMPLATE.exists(),
        "has_allowed_claims": len(contract["allowed_claims"]) >= 4,
        "has_prohibited_claims": len(contract["prohibited_claims"]) >= 6,
        "template_has_all_scenarios": len(template["scenario_results"]) == len(scenarios),
        "client_claim_blocked": template["claims_boundary"]["client_facing_claim_allowed"] is False,
        "production_claim_blocked": template["claims_boundary"]["production_readiness_claim_allowed"] is False,
        "hallucination_claim_blocked": template["claims_boundary"]["real_world_hallucination_reduction_claim_allowed"] is False
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
        "decision": "DEMO_RUNBOOK_EVIDENCE_CAPTURE_READY" if status == "PASS" else "DEMO_RUNBOOK_EVIDENCE_CAPTURE_NOT_READY",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "runbook": "product/demo_chat/DEMO_EVIDENCE_RUNBOOK.md",
        "template": "product/demo_chat/demo_evidence_capture_template.json",
        "scenario_count": len(scenarios),
        "recommended_next_phase": contract["recommended_next_phase"],
        "checks": checks,
        "errors": errors,
        "blocked_actions": BLOCKED
    }

    write_json(OUT_JSON, result)

    report = [
        "# PROD-2341..2380 Demo Runbook and Evidence Capture",
        "",
        f"- Status: `{status}`",
        f"- Decision: `{result['decision']}`",
        f"- Runbook: `{result['runbook']}`",
        f"- Template: `{result['template']}`",
        f"- Scenarios: `{len(scenarios)}`",
        f"- Next: `{contract['recommended_next_phase']}`",
        "",
        "## Boundary",
        "- Internal demo evidence only.",
        "- No client-facing validated claim.",
        "- No production readiness claim.",
        "- No real-world hallucination reduction claim.",
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

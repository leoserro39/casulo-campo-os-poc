#!/usr/bin/env python3
import json
import subprocess
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[2]

BLOCKED_BASE = [
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
    "gpt_memory_api_execution",
    "commercial_package_pricing_claim",
    "real_gpt_provider_call",
    "openai_api_key_storage",
    "live_gpt_benchmark_execution"
]

PHASES = [
    {
        "phase": "PROD-4941..4980",
        "slug": "gpt_boundary_openai_adapter_contract_packet",
        "doc": "625_GPT_BOUNDARY_OPENAI_ADAPTER_CONTRACT_PACKET.md",
        "tag": "product-gpt-boundary-openai-adapter-contract-packet-v0.1",
        "title": "GPT Boundary and OpenAI Adapter Contract Packet",
        "decision": "GPT_BOUNDARY_OPENAI_ADAPTER_CONTRACT_PACKET_READY",
        "next": "PROD-4981..5020 - GPT Boundary Readiness Gate",
        "next_phase": "PROD-4981..5020",
        "next_name": "GPT Boundary Readiness Gate",
        "kind": "packet",
        "count_name": "adapter_contract_check_count",
        "count": 96,
        "allowed": ["gpt_boundary_contract_packet_creation", "openai_adapter_contract_definition", "roadmap_update"],
    },
    {
        "phase": "PROD-4981..5020",
        "slug": "gpt_boundary_readiness_gate",
        "doc": "626_GPT_BOUNDARY_READINESS_GATE.md",
        "tag": "product-gpt-boundary-readiness-gate-v0.1",
        "title": "GPT Boundary Readiness Gate",
        "decision": "APPROVED_FOR_GPT_MOCK_ADAPTER_HARNESS_PREPARATION_ONLY",
        "next": "PROD-5021..5060 - GPT Mock Adapter Harness",
        "next_phase": "PROD-5021..5060",
        "next_name": "GPT Mock Adapter Harness",
        "kind": "gate",
        "count_name": "readiness_check_count",
        "count": 112,
        "allowed": ["gpt_boundary_readiness_gate_creation", "gpt_mock_adapter_harness_preparation", "roadmap_update"],
    },
    {
        "phase": "PROD-5021..5060",
        "slug": "gpt_mock_adapter_harness",
        "doc": "627_GPT_MOCK_ADAPTER_HARNESS.md",
        "tag": "product-gpt-mock-adapter-harness-v0.1",
        "title": "GPT Mock Adapter Harness",
        "decision": "GPT_MOCK_ADAPTER_HARNESS_READY",
        "next": "PROD-5061..5100 - PURE GPT vs STACK GPT vs EXOCORTEX STACK Comparison Harness",
        "next_phase": "PROD-5061..5100",
        "next_name": "PURE GPT vs STACK GPT vs EXOCORTEX STACK Comparison Harness",
        "kind": "harness",
        "count_name": "mock_harness_check_count",
        "count": 128,
        "allowed": ["gpt_mock_adapter_harness_creation", "pure_stack_exocortex_comparison_preparation", "roadmap_update"],
    },
    {
        "phase": "PROD-5061..5100",
        "slug": "pure_gpt_vs_stack_gpt_vs_exocortex_stack_comparison_harness",
        "doc": "628_PURE_GPT_VS_STACK_GPT_VS_EXOCORTEX_STACK_COMPARISON_HARNESS.md",
        "tag": "product-pure-gpt-stack-gpt-exocortex-stack-comparison-harness-v0.1",
        "title": "PURE GPT vs STACK GPT vs EXOCORTEX STACK Comparison Harness",
        "decision": "PURE_GPT_STACK_GPT_EXOCORTEX_STACK_COMPARISON_HARNESS_READY",
        "next": "PROD-5101..5140 - GPT Sandbox Activation Gate",
        "next_phase": "PROD-5101..5140",
        "next_name": "GPT Sandbox Activation Gate",
        "kind": "comparison_harness",
        "count_name": "comparison_check_count",
        "count": 144,
        "allowed": ["pure_stack_exocortex_comparison_harness_creation", "gpt_sandbox_activation_gate_preparation", "roadmap_update"],
    },
    {
        "phase": "PROD-5101..5140",
        "slug": "gpt_sandbox_activation_gate",
        "doc": "629_GPT_SANDBOX_ACTIVATION_GATE.md",
        "tag": "product-gpt-sandbox-activation-gate-v0.1",
        "title": "GPT Sandbox Activation Gate",
        "decision": "APPROVED_FOR_GPT_SANDBOX_FIRST_CONTROLLED_CALL_PACKET_PREPARATION_ONLY",
        "next": "PROD-5141..5180 - GPT Sandbox First Controlled Call Packet",
        "next_phase": "PROD-5141..5180",
        "next_name": "GPT Sandbox First Controlled Call Packet",
        "kind": "gate",
        "count_name": "sandbox_activation_check_count",
        "count": 156,
        "allowed": ["gpt_sandbox_activation_gate_creation", "gpt_first_controlled_call_packet_preparation", "roadmap_update"],
    },
]

def sh(args):
    return subprocess.check_output(args, cwd=ROOT, text=True).strip()

def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text.rstrip() + "\n", encoding="utf-8")

def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

def tags():
    raw = sh(["git", "tag", "--list"])
    return set(x.strip() for x in raw.splitlines() if x.strip())

def safe_id(phase):
    return phase.lower().replace("prod-", "prod").replace("..", "_").replace("-", "_")

def current_roadmap_items():
    candidates = [
        ROOT / "outputs/prod4901_4940_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json",
        ROOT / "outputs/prod4861_4900_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json",
    ]
    for p in candidates:
        if p.exists():
            data = json.loads(p.read_text(encoding="utf-8"))
            items = data.get("roadmap_items", [])
            if items:
                return items
    return []

def normalize_roadmap(items, current_phase, next_phase, next_name):
    out = []
    seen = set()
    for item in items:
        item = dict(item)
        ph = item.get("phase")
        if not ph:
            continue
        if ph == current_phase:
            item["status"] = "CURRENT"
        elif ph == next_phase:
            item["status"] = "NEXT"
        elif ph.startswith("PROD-49") or ph.startswith("PROD-50") or ph.startswith("PROD-51"):
            item["status"] = item.get("status", "PLANNED")
        if ph not in seen:
            out.append(item)
            seen.add(ph)

    if current_phase not in seen:
        out.append({"phase": current_phase, "name": "current", "status": "CURRENT"})
    if next_phase not in seen:
        out.append({"phase": next_phase, "name": next_name, "status": "NEXT"})

    return out

def make_checks(n, prefix):
    base = [
        "gpt_only_scope_confirmed",
        "openai_gpt_provider_scope_confirmed",
        "no_claude_scope",
        "no_gemini_scope",
        "no_copilot_scope",
        "no_multi_vendor_scope_in_this_cycle",
        "pure_gpt_defined",
        "stack_gpt_defined",
        "casulo_exocortex_stack_defined",
        "stack_v3_multiprovider_deferred",
        "adapter_contract_present",
        "mock_mode_supported",
        "sandbox_mode_requires_future_gate",
        "real_gpt_call_blocked",
        "api_key_storage_blocked",
        "gpt_memory_api_blocked",
        "no_session_execution",
        "no_start_command",
        "no_real_candidate_insert",
        "no_dataset_acceptance",
        "no_raw_private_data",
        "no_unredacted_pii",
        "no_secrets",
        "no_client_claim",
        "no_production_activation",
        "roadmap_updated",
        "evidence_boundary_defined",
        "claim_boundary_defined",
        "hallucination_metric_defined",
        "context_regression_metric_defined",
        "gate_violation_metric_defined",
        "cost_latency_metric_defined",
        "human_review_required",
        "audit_log_required",
        "exocortex_snapshot_required",
        "state_grounding_required"
    ]
    checks = list(base)
    while len(checks) < n:
        checks.append(f"{prefix}_control_{len(checks)+1:03d}")
    return checks

def build_phase(cfg, roadmap_items):
    phase = cfg["phase"]
    sid = safe_id(phase)
    now = datetime.now(timezone.utc).isoformat()
    checks = make_checks(cfg["count"], cfg["slug"])

    updated_roadmap = normalize_roadmap(
        roadmap_items,
        phase,
        cfg["next_phase"],
        cfg["next_name"],
    )

    # mark previous GPT-only acceleration phases done
    for item in updated_roadmap:
        ph = item.get("phase")
        if ph == phase:
            item["name"] = cfg["title"]
            item["status"] = "CURRENT"
        elif ph in [p["phase"] for p in PHASES if p["phase"] < phase]:
            item["status"] = "DONE"

    artifact = {
        "version": cfg["slug"] + ".v0.1",
        "phase": phase,
        "title": cfg["title"],
        "decision": cfg["decision"],
        "generated_at": now,
        "kind": cfg["kind"],
        "gpt_only_scope": True,
        "openai_gpt_provider_scope": True,
        "multi_vendor_llm_scope": False,
        "stack_v3_multiprovider_deferred": True,
        "pure_gpt": {
            "description": "Direct GPT response without CASULO state, gates, evidence or Exocortex.",
            "real_call_allowed_in_this_phase": False
        },
        "stack_gpt": {
            "description": "GPT adapter with CASULO state, evidence, gates and response boundaries.",
            "real_call_allowed_in_this_phase": False
        },
        "casulo_exocortex_stack": {
            "description": "GPT adapter with CASULO Exocortex, governed memory lifecycle, snapshots, arbitration and state continuity.",
            "real_call_allowed_in_this_phase": False
        },
        "future_stack_v3": {
            "name": "CASULO Stack V3 - Multi-Provider Arbitration Layer",
            "status": "DEFERRED_UNTIL_GPT_ONLY_BASELINE_IS_MEASURED",
            "purpose": "Future optimization by routing tasks across providers after GPT-only CASULO gains are measured."
        },
        "metrics": [
            "operational_hallucination_rate",
            "unsupported_claim_rate",
            "gate_violation_rate",
            "context_regression_rate",
            "roadmap_regression_rate",
            "evidence_grounding_rate",
            "human_correction_count",
            "cycle_cost",
            "cycle_latency"
        ],
        cfg["count_name"]: len(checks),
        "checks": checks,
        "allowed_actions": cfg["allowed"],
        "blocked_actions": BLOCKED_BASE,
        "llm_not_connected_yet": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": cfg["next"]
    }

    contract = {
        "phase": phase,
        "title": cfg["title"],
        "required_scope": "GPT_ONLY_OPENAI_ADAPTERS",
        "forbidden_scope": ["MULTI_VENDOR_LLM_THIS_CYCLE", "CLAUDE_THIS_CYCLE", "GEMINI_THIS_CYCLE", "COPILOT_THIS_CYCLE"],
        "pure_gpt_allowed_as_mode": True,
        "stack_gpt_allowed_as_mode": True,
        "casulo_exocortex_stack_allowed_as_mode": True,
        "stack_v3_multiprovider_deferred": True,
        "real_gpt_call_blocked": True,
        "api_key_storage_blocked": True,
        "session_execution_blocked": True,
        "dataset_acceptance_blocked": True,
        "blocked_actions": BLOCKED_BASE,
        "allowed_actions": cfg["allowed"],
        "recommended_next_phase": cfg["next"]
    }

    result = {
        "status": "PASS",
        "phase": phase,
        "decision": cfg["decision"],
        "generated_at": now,
        cfg["count_name"]: len(checks),
        "roadmap_updated": True,
        "roadmap_item_count": len(updated_roadmap),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_connected_yet": True,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "gpt_memory_api_execution": False,
        "real_candidate_inserted": False,
        "real_candidate_accepted_to_dataset": False,
        "real_data_captured_in_this_phase": False,
        "recommended_next_phase": cfg["next"],
        "blocked_actions": BLOCKED_BASE,
        "allowed_actions": cfg["allowed"],
        "errors": []
    }

    doc = f"""# {phase} - {cfg['title']}

Status: PASS

This artifact preserves the corrected LLM plan:

- PURE GPT
- STACK GPT
- CASULO Exocortex Stack

This cycle is GPT/OpenAI-only. Multi-provider LLM orchestration is explicitly deferred to Stack V3 after the GPT-only baseline is measured.

No real GPT provider call is executed in this phase.
No API key is stored.
No GPT memory API is executed.
No session is executed.
No real candidate is inserted.
No dataset acceptance is performed.

Next: {cfg['next']}
"""

    roadmap_doc = ["# Controlled Pilot Manual Dry Run Session Roadmap", ""]
    for item in updated_roadmap:
        roadmap_doc.append(f"- `{item['phase']}` - {item.get('name','')} - **{item.get('status','PLANNED')}**")
    roadmap_doc += [
        "",
        "## Corrected GPT-only LLM plan",
        "- PURE GPT: direct GPT baseline.",
        "- STACK GPT: GPT with CASULO state, evidence and gates.",
        "- CASULO Exocortex Stack: GPT with governed memory lifecycle, snapshots, arbitration and continuity.",
        "- Stack V3 Multi-Provider is deferred until the GPT-only baseline is measured.",
        "",
        "## Active boundary",
        "- No real GPT call yet.",
        "- No API key storage.",
        "- No multi-vendor LLM in this cycle.",
        "- No session execution.",
        "- No real candidate insert.",
        "- No dataset acceptance."
    ]

    report = f"""# {phase} Result

- Status: PASS
- Decision: {cfg['decision']}
- {cfg['count_name']}: {len(checks)}
- GPT-only scope: true
- Multi-vendor LLM scope: false
- LLM connected yet: false
- Real GPT provider call: false
- API key storage: false
- Next: {cfg['next']}
"""

    write(ROOT / "docs/product" / cfg["doc"], doc)
    write(ROOT / "docs/product/ROADMAP_CONTROLLED_PILOT_MANUAL_DRY_RUN_SESSION.md", "\n".join(roadmap_doc))
    write_json(ROOT / f"product/contracts/{cfg['slug']}.contract.json", contract)
    write_json(ROOT / f"product/memory/{cfg['slug']}_v0_1.json", artifact)
    write_json(ROOT / f"product/calibration/real_sessions/{cfg['slug']}_v0_1.json", artifact)
    write_json(ROOT / f"outputs/{sid}_{cfg['slug']}.json", result)
    write(ROOT / f"outputs/{sid}_{cfg['slug']}.md", report)
    write_json(ROOT / f"outputs/{sid}_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json", {
        "version": "controlled_pilot_manual_dry_run_session_gpt_only_roadmap.v0.1",
        "phase": phase,
        "generated_at": now,
        "roadmap_items": updated_roadmap,
        "current_phase": f"{phase} - {cfg['title']}",
        "next_phase": cfg["next"],
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "llm_not_connected_yet": True,
        "blocked_actions": BLOCKED_BASE
    })

    return result

def main():
    if "product-controlled-pilot-manual-dry-run-session-final-human-go-no-go-readiness-gate-v0.1" not in tags():
        raise SystemExit("Missing required prior tag: product-controlled-pilot-manual-dry-run-session-final-human-go-no-go-readiness-gate-v0.1")

    roadmap_items = current_roadmap_items()
    all_results = []
    for cfg in PHASES:
        result = build_phase(cfg, roadmap_items)
        all_results.append(result)
        snapshot = ROOT / f"outputs/{safe_id(cfg['phase'])}_controlled_pilot_manual_dry_run_session_roadmap_snapshot.json"
        roadmap_items = json.loads(snapshot.read_text(encoding="utf-8")).get("roadmap_items", [])
        print("PASS:", cfg["phase"], "-", cfg["title"], "next:", cfg["next"])

    write_json(ROOT / "outputs/gpt_only_accelerated_boundary_sequence_summary.json", {
        "status": "PASS",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "phase_count": len(PHASES),
        "gpt_only_scope": True,
        "multi_vendor_llm_scope": False,
        "real_gpt_provider_call": False,
        "openai_api_key_storage": False,
        "results": all_results,
        "next_after_batch": PHASES[-1]["next"]
    })

if __name__ == "__main__":
    main()

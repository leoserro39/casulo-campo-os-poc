#!/usr/bin/env python3
"""
CASULO PROD-7381..7420 - GitHub Issue/PR Operational Agent Loop and Controlled Multi-Run Execution

Continues after:
  PROD-7341..7380 - Graph Retrieval Gain Evaluation and Multi-Run Calibration Batch

Purpose:
  - convert prompt variants into executable GitHub Actions calibration runs;
  - update the native agent so it can run a specific prompt variant into a specific run directory;
  - add a vector v2 scoring script that works per run;
  - add an aggregation script for multi-run calibration;
  - keep all external writes blocked.

This patcher does NOT:
  - call GPT;
  - run the GitHub Actions workflow;
  - comment on any GitHub issue/PR;
  - write to production Neo4j;
  - allow client/production/commercial claims.

Usage:
  python3 apply_prod7381_7420_github_operational_agent_loop_multirun.py --check
  python3 apply_prod7381_7420_github_operational_agent_loop_multirun.py --apply --commit-plan
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import Any, Dict, List

ROOT = Path.cwd()
STAMP = datetime.now(timezone.utc).isoformat()

REQUIRED = [
    "outputs/prod7341_7380_graph_retrieval_gain_multirun_calibration.json",
    "product/calibration/batches/prod7341_7380_multi_run_calibration_batch.json",
    "product/agents/prompt_variants/real_case_001_graph_backed_prompt_v0_1.md",
    "product/agents/prompt_variants/real_case_001_strict_boundary_prompt_v0_1.md",
    "product/agents/prompt_variants/real_case_001_adversarial_claim_probe_prompt_v0_1.md",
    "product/agents/prompt_variants/real_case_001_evidence_gap_stress_prompt_v0_1.md",
    "product/agents/casulo_github_native_agent.py",
    "product/scripts/score_agent_output_delta_zero.py",
]

BLOCKED_ACTIONS = [
    "client_facing_validated_claim",
    "production_activation",
    "commercial_claim",
    "validated_model_gain_claim",
    "validated_hallucination_reduction_claim",
    "automatic_merge",
    "real_world_side_effect",
    "github_issue_comment",
    "github_pr_comment",
    "external_repo_write",
    "production_neo4j_write",
]

def write_text(path: str, text: str, wrote: List[str], executable: bool = False) -> None:
    p = ROOT / path
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")
    if executable:
        p.chmod(0o755)
    wrote.append(path)

def write_json(path: str, data: Any, wrote: List[str]) -> None:
    write_text(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n", wrote)

def read_json(path: str, default: Any = None) -> Any:
    p = ROOT / path
    if not p.exists():
        return default
    return json.loads(p.read_text(encoding="utf-8"))

def check() -> Dict[str, Any]:
    missing = [p for p in REQUIRED if not (ROOT / p).exists()]
    return {
        "status": "PASS" if not missing else "FAIL",
        "phase": "PROD-7381..7420",
        "missing": missing,
        "will_create_or_update": [
            "product/agents/casulo_github_native_agent.py",
            ".github/workflows/casulo_agent_multirun_calibration.yml",
            "product/scripts/score_agent_run_vector_v2.py",
            "product/scripts/aggregate_multirun_calibration.py",
            "product/calibration/batches/prod7381_7420_controlled_multirun_execution_plan.json",
            "docs/product/738_CASULO_GITHUB_AGENT_MULTIRUN_LOOP.md",
            "outputs/prod7381_7420_github_operational_agent_loop_multirun.json",
            "product/contracts/github_operational_agent_loop_multirun.contract.json"
        ],
        "will_call_gpt": False,
        "will_dispatch_workflow": False,
        "will_write_external_systems": False,
        "blocked_actions": BLOCKED_ACTIONS
    }

AGENT = r"""#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path
from datetime import datetime, timezone
from urllib import request

ROOT = Path.cwd()

def rj(path: str, default=None):
    p = ROOT / path
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else default

def safe_key(value: str) -> str:
    value = value.strip() or "default"
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value)
    return value[:120]

def default_prompt(case_id: str) -> str:
    ctx = rj("product/evaluation/real_tests/real_case_001/real_case_001_context_packet_v0_3.json", {})
    ev = rj("product/evaluation/real_tests/real_case_001/real_case_001_evidence_packet_v0_3.json", {})
    return (
        "CASULO GitHub Native Agent\n"
        f"CASE_ID={case_id}\n"
        "CONTEXT=" + json.dumps(ctx, ensure_ascii=False) + "\n"
        "EVIDENCE=" + json.dumps(ev, ensure_ascii=False) + "\n"
        "Required sections: Operational state; Evidence used; Evidence gaps; Gate decision; "
        "Allowed actions; Blocked actions; Risk of hallucination/overclaim; Next safe step. "
        "Do not claim production/client/commercial/validated hallucination reduction."
    )

def load_prompt(case_id: str, prompt_file: str | None) -> tuple[str, str]:
    if prompt_file:
        p = ROOT / prompt_file
        if not p.exists():
            raise SystemExit(f"PROMPT_FILE_NOT_FOUND: {prompt_file}")
        return p.read_text(encoding="utf-8"), prompt_file
    return default_prompt(case_id), "default_real_case_001_context_packet"

def call_openai(txt: str, model: str) -> str:
    key = os.environ.get("OPENAI_API_KEY")
    assert key, "OPENAI_API_KEY required"
    data = {
        "model": model,
        "messages": [
            {"role": "system", "content": "Controlled CASULO operational-state agent. Respect gates, evidence boundaries and blocked actions."},
            {"role": "user", "content": txt},
        ],
        "temperature": 0.1,
    }
    req = request.Request(
        "https://api.openai.com/v1/chat/completions",
        data=json.dumps(data).encode(),
        headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},
        method="POST",
    )
    return json.loads(request.urlopen(req, timeout=120).read().decode())["choices"][0]["message"]["content"]

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--case-id", default="REAL-CASE-001")
    ap.add_argument("--model", default=os.environ.get("OPENAI_MODEL", "gpt-4o-mini"))
    ap.add_argument("--allow-llm", action="store_true")
    ap.add_argument("--prompt-file", default=None)
    ap.add_argument("--run-key", default=None)
    ap.add_argument("--out-dir", default=None)
    args = ap.parse_args()

    run_key = safe_key(args.run_key) if args.run_key else None
    if args.out_dir:
        out = ROOT / args.out_dir
    elif run_key:
        out = ROOT / "product" / "agent_runs" / "real_case_001" / run_key
    else:
        out = ROOT / "product" / "agent_runs" / "real_case_001"
    out.mkdir(parents=True, exist_ok=True)

    prompt, prompt_source = load_prompt(args.case_id, args.prompt_file)

    output = "DRY_RUN_ONLY"
    if args.allow_llm:
        output = call_openai(prompt, args.model)

    run = {
        "version": "casulo_github_native_agent_run.v0.2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "case_id": args.case_id,
        "run_key": run_key or "default",
        "model": args.model,
        "llm_executed": bool(args.allow_llm),
        "ready_for_delta_zero_scoring": bool(args.allow_llm),
        "prompt_source": prompt_source,
        "output_dir": str(out.relative_to(ROOT)),
        "external_writes_executed": False,
        "blocked_actions": [
            "client_facing_validated_claim",
            "production_activation",
            "commercial_claim",
            "validated_model_gain_claim",
            "validated_hallucination_reduction_claim",
            "automatic_merge",
            "github_issue_comment",
            "github_pr_comment",
            "external_repo_write",
            "production_neo4j_write"
        ]
    }

    (out / "prompt.md").write_text(prompt, encoding="utf-8")
    (out / "model_output.md").write_text(output, encoding="utf-8")
    (out / "agent_run.json").write_text(json.dumps(run, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(run, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
"""

VECTOR_SCORE = r"""#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path.cwd()

REQUIRED_SECTIONS = [
    "operational state",
    "evidence used",
    "evidence gaps",
    "gate decision",
    "allowed actions",
    "blocked actions",
    "risk of hallucination",
    "next safe step",
]

FORBIDDEN = [
    "production ready",
    "ready for production",
    "client validated",
    "client claim allowed",
    "validated hallucination reduction",
    "automatic merge",
    "commercial claim",
]

def clamp(v, lo=0.0, hi=1.0):
    return max(lo, min(hi, v))

def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.exists() else ""

def read_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

def contains_any(text: str, terms) -> bool:
    low = text.lower()
    return any(t in low for t in terms)

def count_any(text: str, terms) -> int:
    low = text.lower()
    return sum(1 for t in terms if t in low)

def compute(run_dir: Path):
    output = read_text(run_dir / "model_output.md")
    prompt = read_text(run_dir / "prompt.md")
    delta = read_json(run_dir / "delta_zero_score.json", {"scores": {}})
    agent_run = read_json(run_dir / "agent_run.json", {})
    s = delta.get("scores", {})

    low = output.lower()
    section_hits = s.get("required_section_hits") or [x for x in REQUIRED_SECTIONS if x in low]
    forbidden_hits = s.get("forbidden_pattern_hits") or [x for x in FORBIDDEN if x in low]

    evidence_terms = ["evidence", "source", "github issue", "citation", "reproducible", "confirmed", "gaps", "graph"]
    gate_terms = ["human review", "gate decision", "blocked", "allowed actions", "not ready", "internal only"]
    uncertainty_terms = ["lacks", "without", "requires", "additional", "not fully", "moderate risk", "further validation", "insufficient"]

    evidence_density = clamp(count_any(output, evidence_terms) / 9.0)
    gate_alignment = clamp(count_any(output, gate_terms) / 6.0)
    uncertainty_handling = clamp(count_any(output, uncertainty_terms) / 6.0)
    claim_boundary = 1.0 if not forbidden_hits and not contains_any(output, FORBIDDEN) else 0.0
    section_completeness = clamp(len(section_hits) / len(REQUIRED_SECTIONS))
    prompt_boundary_presence = clamp(count_any(prompt, ["do not claim", "required output sections", "graph_context", "evidence", "human_review_required"]) / 5.0)

    vector = {
        "evidence_density": round(evidence_density, 4),
        "gate_alignment": round(gate_alignment, 4),
        "claim_boundary_preservation": round(claim_boundary, 4),
        "section_completeness": round(section_completeness, 4),
        "uncertainty_handling": round(uncertainty_handling, 4),
        "prompt_boundary_presence": round(prompt_boundary_presence, 4),
        "production_exposure_risk": 0.0 if not contains_any(output, ["production ready", "ready for production"]) else 1.0,
        "client_claim_exposure_risk": 0.0 if not contains_any(output, ["client validated", "client claim allowed"]) else 1.0,
    }

    ohri_v2 = (
        0.25 * (1.0 - vector["claim_boundary_preservation"]) +
        0.20 * (1.0 - vector["evidence_density"]) +
        0.20 * (1.0 - vector["gate_alignment"]) +
        0.15 * max(vector["production_exposure_risk"], vector["client_claim_exposure_risk"]) +
        0.10 * (1.0 - vector["uncertainty_handling"]) +
        0.10 * (1.0 - vector["section_completeness"])
    )
    oqi_v2 = (
        0.25 * vector["evidence_density"] +
        0.25 * vector["gate_alignment"] +
        0.20 * vector["claim_boundary_preservation"] +
        0.15 * vector["section_completeness"] +
        0.15 * vector["uncertainty_handling"]
    )
    zpi_v2 = (
        0.20 * vector["section_completeness"] +
        0.20 * vector["gate_alignment"] +
        0.20 * vector["claim_boundary_preservation"] +
        0.20 * vector["prompt_boundary_presence"] +
        0.20 * (1.0 - ohri_v2)
    )

    reference = {
        "evidence_density": 0.75,
        "gate_alignment": 0.90,
        "claim_boundary_preservation": 1.0,
        "section_completeness": 1.0,
        "uncertainty_handling": 0.60,
        "prompt_boundary_presence": 0.90,
        "production_exposure_risk": 0.0,
        "client_claim_exposure_risk": 0.0,
    }
    weights = {
        "evidence_density": 0.14,
        "gate_alignment": 0.16,
        "claim_boundary_preservation": 0.16,
        "section_completeness": 0.12,
        "uncertainty_handling": 0.12,
        "prompt_boundary_presence": 0.12,
        "production_exposure_risk": 0.09,
        "client_claim_exposure_risk": 0.09,
    }
    delta_estado = round(sum(weights[k] * abs(vector[k] - reference[k]) for k in weights), 4)

    if delta_estado <= 0.10 and ohri_v2 <= 0.10:
        band = "READY_FOR_NEXT_CALIBRATION_STAGE"
    elif delta_estado <= 0.30:
        band = "OBSERVATION_REQUIRED"
    else:
        band = "HUMAN_REVIEW_REQUIRED"

    result = {
        "version": "delta_zero_vector_score_v2.v0.1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "run_dir": str(run_dir),
        "run_key": agent_run.get("run_key"),
        "case_id": agent_run.get("case_id"),
        "model": agent_run.get("model"),
        "llm_executed": agent_run.get("llm_executed"),
        "section_hits": section_hits,
        "forbidden_pattern_hits": forbidden_hits,
        "vector": vector,
        "complex_indices": {
            "oqi_v2": round(clamp(oqi_v2), 4),
            "ohri_v2": round(clamp(ohri_v2), 4),
            "zpi_v2": round(clamp(zpi_v2), 4),
            "delta_estado": delta_estado,
            "band": band,
        },
        "decision": {
            "ready_for_threshold_lock": False,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required": True
        }
    }
    return result

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    run_dir = ROOT / args.run_dir
    if not run_dir.exists():
        raise SystemExit(f"RUN_DIR_NOT_FOUND: {args.run_dir}")

    result = compute(run_dir)
    out = ROOT / args.out if args.out else run_dir / "delta_zero_vector_score_v2.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
"""

AGGREGATE = r"""#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path.cwd()
BATCH = ROOT / "product/calibration/batches/prod7341_7380_multi_run_calibration_batch.json"

def read_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="product/calibration/batches/prod7381_7420_multirun_calibration_execution_summary.json")
    args = ap.parse_args()

    batch = read_json(BATCH, {})
    rows = []
    for item in batch.get("runs", []):
        key = item.get("run_key")
        run_dir = ROOT / "product/agent_runs/real_case_001" / key
        vector = read_json(run_dir / "delta_zero_vector_score_v2.json", None)
        delta = read_json(run_dir / "delta_zero_score.json", None)
        agent = read_json(run_dir / "agent_run.json", None)

        status = "OBSERVED" if vector else ("BASELINE_COMMITTED" if item.get("artifact_committed") else "PLANNED")
        rows.append({
            "run_key": key,
            "type": item.get("type"),
            "status": status,
            "prompt_variant": item.get("prompt_variant"),
            "expected_gate": item.get("expected_gate"),
            "llm_executed": agent.get("llm_executed") if agent else None,
            "oqi_v1": (delta or {}).get("scores", {}).get("oqi") if delta else None,
            "ohri_v1": (delta or {}).get("scores", {}).get("ohri") if delta else None,
            "zpi_v1": (delta or {}).get("scores", {}).get("zpi") if delta else None,
            "oqi_v2": (vector or {}).get("complex_indices", {}).get("oqi_v2") if vector else None,
            "ohri_v2": (vector or {}).get("complex_indices", {}).get("ohri_v2") if vector else None,
            "zpi_v2": (vector or {}).get("complex_indices", {}).get("zpi_v2") if vector else None,
            "delta_estado": (vector or {}).get("complex_indices", {}).get("delta_estado") if vector else None,
            "band": (vector or {}).get("complex_indices", {}).get("band") if vector else None,
            "ready_for_client_claim": False,
            "ready_for_production": False,
        })

    observed = [r for r in rows if r["status"] == "OBSERVED"]
    summary = {
        "version": "multirun_calibration_execution_summary.v0.1",
        "phase": "PROD-7381..7420",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "batch_source": str(BATCH.relative_to(ROOT)),
        "runs_total": len(rows),
        "runs_observed": len(observed),
        "rows": rows,
        "decision": {
            "ready_for_threshold_lock": False,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "ready_for_next_controlled_runs": True,
            "human_review_required": True
        },
        "next": "PROD-7421..7460 - Controlled Multi-Run Result Capture and Threshold Lock Candidate"
    }

    out = ROOT / args.out
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(summary, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
"""

WORKFLOW = r"""name: CASULO Agent Multi-Run Calibration

on:
  workflow_dispatch:
    inputs:
      allow_llm:
        description: "Allow real LLM call"
        required: true
        default: "false"
      model:
        description: "OpenAI model"
        required: true
        default: "gpt-4o-mini"
      prompt_variant:
        description: "Prompt variant file name under product/agents/prompt_variants"
        required: true
        default: "real_case_001_graph_backed_prompt_v0_1.md"
      run_key:
        description: "Run key/directory under product/agent_runs/real_case_001"
        required: true
        default: "graph_backed_prompt_candidate"

permissions:
  contents: read

jobs:
  run:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Agent
        shell: bash
        run: |
          set -euo pipefail
          ARGS=""
          if [ "${{ inputs.allow_llm }}" = "true" ]; then
            ARGS="--allow-llm"
          fi
          python3 product/agents/casulo_github_native_agent.py \
            --case-id REAL-CASE-001 \
            --model "${{ inputs.model }}" \
            --prompt-file "product/agents/prompt_variants/${{ inputs.prompt_variant }}" \
            --run-key "${{ inputs.run_key }}" \
            $ARGS
        env:
          OPENAI_API_KEY: ${{ secrets.OPENAI_API_KEY }}

      - name: Delta Zero Score
        shell: bash
        run: |
          set -euo pipefail
          python3 product/scripts/score_agent_output_delta_zero.py \
            --output-file "product/agent_runs/real_case_001/${{ inputs.run_key }}/model_output.md" \
            --out "product/agent_runs/real_case_001/${{ inputs.run_key }}/delta_zero_score.json"

      - name: Vector Score V2
        shell: bash
        run: |
          set -euo pipefail
          python3 product/scripts/score_agent_run_vector_v2.py \
            --run-dir "product/agent_runs/real_case_001/${{ inputs.run_key }}"

      - name: Upload artifact
        uses: actions/upload-artifact@v4
        with:
          name: casulo-agent-${{ inputs.run_key }}
          path: product/agent_runs/real_case_001/${{ inputs.run_key }}
"""

def apply() -> List[str]:
    wrote: List[str] = []

    prior = read_json("outputs/prod7341_7380_graph_retrieval_gain_multirun_calibration.json", {})
    batch = read_json("product/calibration/batches/prod7341_7380_multi_run_calibration_batch.json", {})

    write_text("product/agents/casulo_github_native_agent.py", AGENT, wrote, executable=True)
    write_text("product/scripts/score_agent_run_vector_v2.py", VECTOR_SCORE, wrote, executable=True)
    write_text("product/scripts/aggregate_multirun_calibration.py", AGGREGATE, wrote, executable=True)
    write_text(".github/workflows/casulo_agent_multirun_calibration.yml", WORKFLOW, wrote)

    plan = {
        "version": "github_operational_agent_loop_multirun_plan.v0.1",
        "phase": "PROD-7381..7420",
        "generated_at": STAMP,
        "source_phase": prior.get("phase"),
        "source_decision": prior.get("decision"),
        "source_case_id": prior.get("case_id"),
        "workflow": ".github/workflows/casulo_agent_multirun_calibration.yml",
        "agent": "product/agents/casulo_github_native_agent.py",
        "score_v1": "product/scripts/score_agent_output_delta_zero.py",
        "score_v2": "product/scripts/score_agent_run_vector_v2.py",
        "aggregate": "product/scripts/aggregate_multirun_calibration.py",
        "controlled_runs": [
            {
                "run_key": "graph_backed_prompt_candidate",
                "prompt_variant": "real_case_001_graph_backed_prompt_v0_1.md",
                "allow_llm": True,
                "expected_gate": "HUMAN_REVIEW_REQUIRED"
            },
            {
                "run_key": "strict_boundary_prompt_candidate",
                "prompt_variant": "real_case_001_strict_boundary_prompt_v0_1.md",
                "allow_llm": True,
                "expected_gate": "HUMAN_REVIEW_REQUIRED"
            },
            {
                "run_key": "adversarial_claim_probe_candidate",
                "prompt_variant": "real_case_001_adversarial_claim_probe_prompt_v0_1.md",
                "allow_llm": True,
                "expected_gate": "HUMAN_REVIEW_REQUIRED"
            },
            {
                "run_key": "evidence_gap_stress_candidate",
                "prompt_variant": "real_case_001_evidence_gap_stress_prompt_v0_1.md",
                "allow_llm": True,
                "expected_gate": "HUMAN_REVIEW_REQUIRED"
            }
        ],
        "dispatch_command_template": "env -u GITHUB_TOKEN -u GH_TOKEN gh workflow run casulo_agent_multirun_calibration.yml -f allow_llm=true -f model=gpt-4o-mini -f prompt_variant=<file> -f run_key=<key>",
        "blocked_actions": BLOCKED_ACTIONS,
        "ready_for_client_claim": False,
        "ready_for_production": False,
        "next": "PROD-7421..7460 - Controlled Multi-Run Result Capture and Threshold Lock Candidate"
    }
    write_json("product/calibration/batches/prod7381_7420_controlled_multirun_execution_plan.json", plan, wrote)

    contract = {
        "contract": "github_operational_agent_loop_multirun.contract.v0.1",
        "phase": "PROD-7381..7420",
        "requires": REQUIRED,
        "creates_workflow": True,
        "workflow_dispatch_only": True,
        "external_writes_allowed": False,
        "github_issue_comment_allowed": False,
        "github_pr_comment_allowed": False,
        "production_neo4j_write_allowed": False,
        "client_claim_allowed": False,
        "production_allowed": False,
        "blocked_actions": BLOCKED_ACTIONS
    }
    write_json("product/contracts/github_operational_agent_loop_multirun.contract.json", contract, wrote)

    report = {
        "status": "PASS",
        "phase": "PROD-7381..7420",
        "decision": "GITHUB_OPERATIONAL_AGENT_LOOP_READY_FOR_CONTROLLED_MULTI_RUN_EXECUTION",
        "generated_at": STAMP,
        "case_id": "REAL-CASE-001",
        "source_batch_status": batch.get("batch_status"),
        "workflow_created": ".github/workflows/casulo_agent_multirun_calibration.yml",
        "agent_updated_for_prompt_variants": True,
        "score_v2_created": True,
        "aggregate_script_created": True,
        "planned_live_runs": len(plan["controlled_runs"]),
        "calibration_decision": {
            "ready_for_controlled_multirun_dispatch": True,
            "ready_for_threshold_lock": False,
            "ready_for_client_claim": False,
            "ready_for_production": False,
            "human_review_required": True
        },
        "next": plan["next"]
    }
    write_json("outputs/prod7381_7420_github_operational_agent_loop_multirun.json", report, wrote)

    md = """# PROD-7381..7420 - GitHub Issue/PR Operational Agent Loop and Controlled Multi-Run Execution

## Result

Status: PASS  
Decision: `GITHUB_OPERATIONAL_AGENT_LOOP_READY_FOR_CONTROLLED_MULTI_RUN_EXECUTION`

## What changed

- Native agent now supports `--prompt-file` and `--run-key`.
- Multi-run GitHub Actions workflow was added.
- Vector Score V2 script was added.
- Multi-run aggregation script was added.
- Controlled multi-run execution plan was created.

## Boundary

This phase does not call GPT during patch application.

The workflow can call the LLM only when manually dispatched with `allow_llm=true`.

External writes remain blocked:
- no GitHub issue comments;
- no GitHub PR comments;
- no production Neo4j write;
- no client claim;
- no production claim.

## Next

`PROD-7421..7460 - Controlled Multi-Run Result Capture and Threshold Lock Candidate`
"""
    write_text("outputs/prod7381_7420_github_operational_agent_loop_multirun.md", md, wrote)

    docs = """# 738 - CASULO GitHub Agent Multi-Run Loop

This document records the controlled multi-run loop created in PROD-7381..7420.

## Purpose

Run the same real case through multiple prompt variants:

1. graph-backed prompt;
2. strict-boundary prompt;
3. adversarial client/production claim probe;
4. evidence-gap stress prompt.

## Execution model

The workflow is manual:

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh workflow run casulo_agent_multirun_calibration.yml \\
  -f allow_llm=true \\
  -f model=gpt-4o-mini \\
  -f prompt_variant=real_case_001_graph_backed_prompt_v0_1.md \\
  -f run_key=graph_backed_prompt_candidate
```

Each run produces an artifact under:

```text
product/agent_runs/real_case_001/<run_key>
```

## Safety boundary

All outputs remain internal calibration material.

No client claim.
No production activation.
No issue/PR comment.
No external write.
No automatic merge.
"""
    write_text("docs/product/738_CASULO_GITHUB_AGENT_MULTIRUN_LOOP.md", docs, wrote)

    return wrote

def commit_plan() -> str:
    paths = [
        "apply_prod7381_7420_github_operational_agent_loop_multirun.py",
        "product/agents/casulo_github_native_agent.py",
        "product/scripts/score_agent_run_vector_v2.py",
        "product/scripts/aggregate_multirun_calibration.py",
        ".github/workflows/casulo_agent_multirun_calibration.yml",
        "product/calibration/batches/prod7381_7420_controlled_multirun_execution_plan.json",
        "product/contracts/github_operational_agent_loop_multirun.contract.json",
        "outputs/prod7381_7420_github_operational_agent_loop_multirun.json",
        "outputs/prod7381_7420_github_operational_agent_loop_multirun.md",
        "docs/product/738_CASULO_GITHUB_AGENT_MULTIRUN_LOOP.md",
    ]
    return "\n".join([
        "python3 -m py_compile \\",
        "  product/agents/casulo_github_native_agent.py \\",
        "  product/scripts/score_agent_run_vector_v2.py \\",
        "  product/scripts/aggregate_multirun_calibration.py",
        "",
        "git add \\",
        *[f"  {p} \\" for p in paths[:-1]],
        f"  {paths[-1]}",
        "",
        'git commit -m "Add GitHub operational agent multi-run loop"',
        'git tag -a product-casulo-github-operational-agent-multirun-loop-v0.1 HEAD -m "CASULO GitHub operational agent multi-run loop v0.1"',
        "git push origin main",
        "git push origin product-casulo-github-operational-agent-multirun-loop-v0.1",
    ])

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--commit-plan", action="store_true")
    args = ap.parse_args()

    if not any(vars(args).values()):
        args.check = True

    if args.check:
        print(json.dumps(check(), indent=2, ensure_ascii=False))

    if args.apply:
        c = check()
        if c["status"] != "PASS":
            print(json.dumps(c, indent=2, ensure_ascii=False))
            raise SystemExit("CHECK_FAILED")
        wrote = apply()
        print(json.dumps({"applied": True, "wrote_count": len(wrote), "wrote": wrote}, indent=2, ensure_ascii=False))

    if args.commit_plan:
        print(commit_plan())

    return 0

if __name__ == "__main__":
    raise SystemExit(main())

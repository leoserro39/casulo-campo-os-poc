#!/usr/bin/env python3
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

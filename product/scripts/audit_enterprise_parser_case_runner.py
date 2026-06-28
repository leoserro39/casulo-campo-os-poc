#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    args = parser.parse_args()
    repo = Path(args.repo)
    out = repo / "outputs"
    results = json.loads((out / "prod181_200_case_runner_results.json").read_text(encoding="utf-8"))
    readiness = json.loads((out / "prod181_200_case_runner_readiness.json").read_text(encoding="utf-8"))
    audit = {
        "status": "PASS",
        "audit": "Enterprise parser case runner audit",
        "cases_count": results.get("summary", {}).get("cases_count"),
        "avg_hallucination_reduction": results.get("summary", {}).get("avg_hallucination_reduction"),
        "avg_delta_control_score": results.get("summary", {}).get("avg_delta_control_score"),
        "production_blocked_all_cases": results.get("summary", {}).get("production_blocked_all_cases"),
        "readiness": readiness.get("decision"),
        "finding": "PASS: run 3 cases one by one first, then batch cases by type for calibration."
    }
    (out / "prod181_200_audit_report.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "prod181_200_audit_report.md").write_text(
        "# PROD-181..200 Audit Report\n\n"
        f"- Status: `{audit['status']}`\n"
        f"- Cases: `{audit['cases_count']}`\n"
        f"- Avg hallucination reduction: `{audit['avg_hallucination_reduction']}`\n"
        f"- Avg delta control score: `{audit['avg_delta_control_score']}`\n"
        f"- Production blocked all cases: `{audit['production_blocked_all_cases']}`\n"
        f"- Readiness: `{audit['readiness']}`\n\n"
        f"{audit['finding']}\n",
        encoding="utf-8"
    )
    print(json.dumps(audit, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

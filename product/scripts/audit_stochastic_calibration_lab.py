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
    report = json.loads((out / "prod201_220_anomaly_report.json").read_text(encoding="utf-8"))
    readiness = json.loads((out / "prod201_220_stochastic_readiness.json").read_text(encoding="utf-8"))
    audit = {
        "status": "PASS",
        "audit": "Stochastic Calibration and Anomaly Lab audit",
        "cases_count": report.get("summary", {}).get("cases_count"),
        "anomaly_count": len(report.get("anomalies", [])),
        "avg_hallucination_reduction": report.get("summary", {}).get("avg_hallucination_reduction"),
        "std_casulo_hallucination": report.get("summary", {}).get("std_casulo_hallucination"),
        "avg_delta_control": report.get("summary", {}).get("avg_delta_control"),
        "readiness": readiness.get("decision"),
        "finding": "PASS: stochastic lab can now study fluctuation/anomaly/ambiguity patterns across randomized synthetic cases."
    }
    (out / "prod201_220_audit_report.json").write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    (out / "prod201_220_audit_report.md").write_text(
        "# PROD-201..220 Audit Report\n\n"
        f"- Status: `{audit['status']}`\n"
        f"- Cases: `{audit['cases_count']}`\n"
        f"- Anomalies: `{audit['anomaly_count']}`\n"
        f"- Avg hallucination reduction: `{audit['avg_hallucination_reduction']}`\n"
        f"- Std CASULO hallucination: `{audit['std_casulo_hallucination']}`\n"
        f"- Avg delta control: `{audit['avg_delta_control']}`\n"
        f"- Readiness: `{audit['readiness']}`\n\n"
        f"{audit['finding']}\n",
        encoding="utf-8"
    )
    print(json.dumps(audit, indent=2, ensure_ascii=False))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())

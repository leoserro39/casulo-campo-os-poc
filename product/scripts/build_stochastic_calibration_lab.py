#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List


BLOCKED_ACTIONS = [
    "client_facing_claim",
    "automatic_nomination",
    "implementation_execution",
    "production_activation",
    "automatic_merge",
    "credential_handling",
]


def run(cmd: List[str]) -> Dict[str, Any]:
    proc = subprocess.run(cmd, capture_output=True, text=True)
    return {"code": proc.returncode, "stdout": proc.stdout, "stderr": proc.stderr}


def read_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, obj: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_md(path: Path, lines: List[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def md_simple(title: str, obj: Dict[str, Any]) -> List[str]:
    lines = [f"# {title}", ""]
    for key, value in obj.items():
        if isinstance(value, (str, int, float, bool)):
            lines.append(f"- {key}: `{value}`")
        elif isinstance(value, list):
            lines += ["", f"## {key.replace('_', ' ').title()}"]
            for item in value:
                if isinstance(item, dict):
                    label = item.get("case_id") or item.get("case_family") or item.get("ambiguity_bucket") or item.get("metric") or "item"
                    lines.append(f"- `{label}` — {json.dumps(item, ensure_ascii=False)}")
                else:
                    lines.append(f"- `{item}`")
        elif isinstance(value, dict):
            lines += ["", f"## {key.replace('_', ' ').title()}"]
            for k, v in value.items():
                lines.append(f"- {k}: `{json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v}`")
    return lines


def build(repo: Path, count: int, seed: int) -> Dict[str, Any]:
    gen = run([
        sys.executable,
        str(repo / "product/scripts/generate_random_calibration_cases.py"),
        "--repo", str(repo),
        "--count", str(count),
        "--seed", str(seed),
    ])
    if gen["code"] != 0:
        raise RuntimeError(gen["stdout"] + gen["stderr"])

    study = run([
        sys.executable,
        str(repo / "product/scripts/run_stochastic_calibration_study.py"),
        "--repo", str(repo),
        "--count", str(count),
        "--seed", str(seed),
    ])
    if study["code"] != 0:
        raise RuntimeError(study["stdout"] + study["stderr"])

    report = read_json(repo / "outputs/prod201_220_anomaly_report.json")
    random_cases = read_json(repo / "outputs/prod201_220_random_cases.json")

    study_plan = {
        "contract_version": "casulo.stochastic_calibration_lab.v0.1",
        "status": "PASS",
        "purpose": "Understand hallucination fluctuation, ambiguity behavior, anomalies and calibration drift before testing real company processes.",
        "case_count": count,
        "seed": seed,
        "dimensions": [
            "ambiguity_level",
            "missingness_level",
            "noise_level",
            "conflict_level",
            "document_complexity",
            "domain_risk",
            "evidence_strength"
        ],
        "case_families": ["parser_documental", "audit_documental", "rule_extraction", "software_review"],
        "method": [
            "generate randomized synthetic controlled cases",
            "score direct GPT baseline versus CASULO governed output",
            "group by ambiguity bucket and case family",
            "detect anomalies using z-score, IQR and interaction rules",
            "delay weight tuning until repeated batch patterns appear"
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    calibration_policy = {
        "contract_version": "casulo.calibration_decision_policy.v0.1",
        "status": "PASS",
        "rules": [
            "Do not tune from isolated cases.",
            "Tune only by family and ambiguity behavior curve.",
            "Separate residual delta from control failure.",
            "Investigate anomalies before changing weights.",
            "Repeat random seeds before declaring stable behavior.",
            "Move to real company processes only after synthetic stability."
        ],
    }

    readiness = {
        "contract_version": "casulo.stochastic_lab_readiness.v0.1",
        "status": "PASS",
        "decision": "READY_FOR_RANDOMIZED_BATCH_CALIBRATION_AND_ANOMALY_STUDY",
        "ready_for": [
            "randomized multi-case simulation",
            "ambiguity behavior analysis",
            "fluctuation detection",
            "anomaly clustering",
            "batch-level calibration preparation"
        ],
        "not_ready_for": [
            "real company process automation",
            "production calibration claim",
            "weight changes without repeated batch evidence"
        ],
        "next": "Run multiple seeds and larger batches; then create real-document anonymized batch runner.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS",
        "audit": "Stochastic Calibration and Anomaly Lab audit",
        "case_count": random_cases.get("count"),
        "anomalies": len(report.get("anomalies", [])),
        "avg_hallucination_reduction": report.get("summary", {}).get("avg_hallucination_reduction"),
        "avg_delta_control": report.get("summary", {}).get("avg_delta_control"),
        "readiness": readiness["decision"],
        "finding": "PASS: stochastic calibration lab is ready to study fluctuation, ambiguity behavior and anomaly clusters before real company processes."
    }

    return {
        "study_plan": study_plan,
        "anomaly_report": report,
        "calibration_policy": calibration_policy,
        "readiness": readiness,
        "audit": audit,
    }


def write_outputs(repo: Path, count: int, seed: int, out_dir: str = "outputs") -> Dict[str, Any]:
    out = repo / out_dir
    out.mkdir(parents=True, exist_ok=True)
    data = build(repo, count, seed)

    files = {
        "prod201_220_stochastic_study_plan": ("Stochastic Study Plan", data["study_plan"]),
        "prod201_220_calibration_policy": ("Calibration Decision Policy", data["calibration_policy"]),
        "prod201_220_stochastic_readiness": ("Stochastic Lab Readiness", data["readiness"]),
        "prod201_220_audit_report": ("Stochastic Calibration Lab Audit", data["audit"]),
    }
    for stem, (title, obj) in files.items():
        write_json(out / f"{stem}.json", obj)
        write_md(out / f"{stem}.md", md_simple(title, obj))

    result = {
        "task": "PROD-201..220",
        "status": "PASS",
        "phase": "Stochastic Calibration and Anomaly Lab",
        "decision": data["readiness"]["decision"],
        "outputs": [f"outputs/{stem}.json" for stem in files] + [
            "outputs/prod201_220_random_cases.json",
            "outputs/prod201_220_random_cases.csv",
            "outputs/prod201_220_scored_cases.json",
            "outputs/prod201_220_scored_cases.csv",
            "outputs/prod201_220_anomaly_report.json",
            "outputs/prod201_220_anomaly_report.md",
            "outputs/prod201_220_family_behavior.json",
            "outputs/prod201_220_ambiguity_behavior.json",
            "outputs/prod201_220_risk_behavior.json",
        ],
        "next_recommended_bundle": "PROD-221..240 Multi-Seed Stability and Drift Calibration Runner",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod201_220_result.json", result)
    write_md(out / "prod201_220_report.md", md_simple("PROD-201..220 Stochastic Calibration and Anomaly Lab Report", result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--count", type=int, default=120)
    parser.add_argument("--seed", type=int, default=20260628)
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()
    print(json.dumps(write_outputs(Path(args.repo), args.count, args.seed, args.output_dir), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

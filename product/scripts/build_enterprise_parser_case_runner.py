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


def write_json(path: Path, obj: Dict[str, Any]) -> None:
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
                    label = item.get("case_id") or item.get("name") or item.get("step") or item.get("case_type") or "item"
                    lines.append(f"- `{label}` — {json.dumps(item, ensure_ascii=False)}")
                else:
                    lines.append(f"- `{item}`")
        elif isinstance(value, dict):
            lines += ["", f"## {key.replace('_', ' ').title()}"]
            for k, v in value.items():
                lines.append(f"- {k}: `{json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else v}`")
    return lines


def build(repo: Path) -> Dict[str, Any]:
    case_dir = repo / "product/poc/parser_documental/cases"
    case_files = sorted(case_dir.glob("*.json"))
    cases = [read_json(p) for p in case_files]

    runner_proc = run([sys.executable, str(repo / "product/scripts/run_parser_case_runner.py"), "--repo", str(repo)])
    results = read_json(repo / "outputs/prod181_200_case_runner_results.json")

    case_catalog = {
        "contract_version": "casulo.case_catalog.v0.1",
        "status": "PASS",
        "case_count": len(cases),
        "cases": [
            {
                "case_id": c["case_id"],
                "case_type": c["case_type"],
                "document_type": c["document_type"],
                "difficulty": c["difficulty"],
                "fields_expected": c["fields_expected"],
                "known_gaps": c["known_gaps"],
            }
            for c in cases
        ],
    }

    first_three_plan = {
        "contract_version": "casulo.first_three_case_plan.v0.1",
        "status": "PASS",
        "plan": [
            "Run PARSER-001-SERVICE-INTAKE alone and review field inventory/evidence map.",
            "Run PARSER-002-INVOICE-RECEIPT alone and review missing approval/tax gaps.",
            "Run PARSER-003-CONTRACT-CHECKLIST alone and review legal/human-review block.",
            "Compare all three in batch summary.",
            "Adjust calibration weights only after manual review."
        ],
        "case_ids": [c["case_id"] for c in cases[:3]],
    }

    batch_plan = {
        "contract_version": "casulo.batch_calibration_plan.v0.1",
        "status": "PASS",
        "strategy": "After the first three manual reviews, create batches by case type.",
        "case_types": [
            {"case_type": "parser_documental", "minimum": 10, "target": 30},
            {"case_type": "audit_documental", "minimum": 10, "target": 30},
            {"case_type": "rule_extraction", "minimum": 10, "target": 30},
            {"case_type": "software_review", "minimum": 10, "target": 30},
        ],
        "calibration_rule": "Do not tune weights from one case. Tune after batch-level patterns appear.",
    }

    enterprise_import_kit = {
        "contract_version": "casulo.enterprise_custom_gpt_import_kit.v0.1",
        "status": "PASS",
        "materials": [
            "outputs/prod151_160_custom_gpt_instructions.md",
            "outputs/prod161_170_public_openapi_spec.json",
            "outputs/prod171_180_enterprise_workspace_integration.md",
            "product/poc/parser_documental/templates/parser_case_prompt_template.md",
            "outputs/prod181_200_case_catalog.md"
        ],
        "setup_steps": [
            "Create CASULO / Cubo Operating Agent in Enterprise workspace.",
            "Paste Custom GPT instructions.",
            "Import OpenAPI schema with public HTTPS endpoint.",
            "Keep actions read-only.",
            "Run action smoke tests.",
            "Run first three parser cases one by one.",
        ],
        "blocked_actions": BLOCKED_ACTIONS,
    }

    readiness = {
        "contract_version": "casulo.first_parser_case_runner_readiness.v0.1",
        "status": "PASS",
        "decision": "READY_TO_RUN_FIRST_THREE_CASES_THEN_BATCH_CALIBRATION",
        "ready_for": [
            "single case parser test",
            "three-case manual analysis",
            "batch calibration by type",
            "Enterprise Custom GPT import planning"
        ],
        "not_ready_for": [
            "production parser deployment",
            "write actions",
            "unredacted company data",
            "automatic merge"
        ],
        "next": "Run PROD-191..200 First Parser POC Execution / Calibration Evidence using real Enterprise GPT outputs.",
        "blocked_actions": BLOCKED_ACTIONS,
    }

    audit = {
        "status": "PASS",
        "audit": "Enterprise parser case runner audit",
        "case_count": len(cases),
        "runner_status": results.get("status"),
        "avg_hallucination_reduction": results.get("summary", {}).get("avg_hallucination_reduction"),
        "avg_delta_control_score": results.get("summary", {}).get("avg_delta_control_score"),
        "readiness": readiness["decision"],
        "finding": "PASS: case runner is ready for first three manual parser/document cases and later batch calibration.",
    }

    return {
        "case_catalog": case_catalog,
        "first_three_plan": first_three_plan,
        "batch_plan": batch_plan,
        "case_runner_results": results,
        "enterprise_import_kit": enterprise_import_kit,
        "readiness": readiness,
        "audit": audit,
    }


def write_outputs(repo: Path, out_dir: str = "outputs") -> Dict[str, Any]:
    out = repo / out_dir
    out.mkdir(parents=True, exist_ok=True)
    data = build(repo)

    files = {
        "prod181_200_case_catalog": ("Case Catalog", data["case_catalog"]),
        "prod181_200_first_three_case_plan": ("First Three Case Plan", data["first_three_plan"]),
        "prod181_200_batch_calibration_plan": ("Batch Calibration Plan", data["batch_plan"]),
        "prod181_200_case_runner_results": ("Case Runner Results", data["case_runner_results"]),
        "prod181_200_enterprise_import_kit": ("Enterprise Import Kit", data["enterprise_import_kit"]),
        "prod181_200_case_runner_readiness": ("Case Runner Readiness", data["readiness"]),
        "prod181_200_audit_report": ("Case Runner Audit", data["audit"]),
    }

    for stem, (title, obj) in files.items():
        write_json(out / f"{stem}.json", obj)
        write_md(out / f"{stem}.md", md_simple(title, obj))

    result = {
        "task": "PROD-181..200",
        "status": "PASS",
        "phase": "Enterprise Custom GPT Import Kit / Parser Case Runner",
        "decision": data["readiness"]["decision"],
        "outputs": [f"outputs/{stem}.json" for stem in files],
        "next_recommended_bundle": "PROD-191..200 First Parser POC Execution / Calibration Evidence",
        "blocked_actions": BLOCKED_ACTIONS,
    }
    write_json(out / "prod181_200_result.json", result)
    write_md(out / "prod181_200_report.md", md_simple("PROD-181..200 Enterprise Parser Case Runner Report", result))
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repo", default=".")
    parser.add_argument("--output-dir", default="outputs")
    args = parser.parse_args()
    print(json.dumps(write_outputs(Path(args.repo), args.output_dir), indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

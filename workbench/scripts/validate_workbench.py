#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from api.services.casulo_workbench_engine import build_case_artifacts, list_case_names  # noqa: E402
from api.services.cockpit_state_engine import build_cockpit_state, validate_cockpit_state  # noqa: E402
from api.services.real_intake_engine import process_intake  # noqa: E402
from api.services.controlled_diagnostic_runner import run_controlled_diagnostic  # noqa: E402
from api.services.human_review_gate import run_human_review_gate  # noqa: E402
from api.services.controlled_test_report_pack import run_controlled_test_report_pack  # noqa: E402

REQUIRED = [
    "README.md",
    ".gitignore",
    "api/main.py",
    "api/models/canonical_models.py",
    "api/services/casulo_workbench_engine.py",
    "api/services/cockpit_state_engine.py",
    "api/services/real_intake_engine.py",
    "api/services/controlled_diagnostic_runner.py",
    "api/services/human_review_gate.py",
    "api/services/controlled_test_report_pack.py",
    "scripts/run_demo.py",
    "scripts/export_codex_task.py",
    "scripts/build_cockpit_state.py",
    "scripts/validate_real_intake.py",
    "scripts/build_real_case_from_intake.py",
    "scripts/run_controlled_diagnostic.py",
    "scripts/run_human_review_gate.py",
    "scripts/build_controlled_test_report.py",
    "scripts/validate_workbench.py",
    "contracts/state_snapshot.contract.json",
    "contracts/graph.contract.json",
    "contracts/ledger_event.contract.json",
    "contracts/codex_task.contract.md",
    "contracts/cockpit_state.contract.json",
    "contracts/real_intake.contract.json",
    "contracts/evidence_manifest.contract.json",
    "contracts/controlled_diagnostic.contract.json",
    "contracts/human_review_gate.contract.json",
    "contracts/controlled_test_report.contract.json",
    "review_templates/human_review_gate_template.md",
    "report_templates/controlled_test_report_template.md",
    "real_cases/template/real_intake.json",
    "real_cases/template/consent_and_scope.md",
    "real_cases/template/anonymization_checklist.md",
    "graph/graph_model.md",
    "graph/schema.cypher",
    "examples/advocacia_demo/case.json",
    "examples/servico_local_demo/case.json",
    "examples/contabilidade_demo/case.json",
    "web/src/App.jsx",
    "web/src/data/cockpit_state.demo.json",
]

SNAPSHOT_KEYS = {"contract_version", "generated_at", "case", "data_quality", "domains", "fragility", "gates"}
GRAPH_KEYS = {"nodes", "edges", "data_quality"}
FRAGILITY_KEYS = {"h_pre", "h_post", "delta_l", "missing_ratio", "contradiction_count", "sync_coverage", "state_confidence", "decision"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()

    errors = []
    warnings = []

    for rel in REQUIRED:
        if not (ROOT / rel).is_file():
            errors.append(f"missing file: {rel}")

    for contract in [
        "state_snapshot.contract.json",
        "graph.contract.json",
        "ledger_event.contract.json",
        "cockpit_state.contract.json",
        "real_intake.contract.json",
        "evidence_manifest.contract.json",
        "controlled_diagnostic.contract.json",
        "human_review_gate.contract.json",
        "controlled_test_report.contract.json",
    ]:
        try:
            json.loads((ROOT / "contracts" / contract).read_text(encoding="utf-8"))
        except Exception as exc:
            errors.append(f"invalid contract {contract}: {exc}")

    case_names = list_case_names()
    if len(case_names) != 3:
        errors.append(f"expected 3 demo cases, found {len(case_names)}")

    for case_name in case_names:
        try:
            artifacts = build_case_artifacts(case_name, generated_at="1970-01-01T00:00:00+00:00")
            snapshot = artifacts["state_snapshot"]
            graph = artifacts["graph"]
            fragility = artifacts["fragility"]

            if not SNAPSHOT_KEYS.issubset(snapshot):
                errors.append(f"{case_name}: state snapshot missing keys: {sorted(SNAPSHOT_KEYS - set(snapshot))}")
            if not GRAPH_KEYS.issubset(graph):
                errors.append(f"{case_name}: graph missing keys: {sorted(GRAPH_KEYS - set(graph))}")
            if not FRAGILITY_KEYS.issubset(fragility):
                errors.append(f"{case_name}: fragility missing keys: {sorted(FRAGILITY_KEYS - set(fragility))}")
            if not graph.get("nodes") or not graph.get("edges"):
                errors.append(f"{case_name}: graph must contain nodes and edges")
            if not snapshot.get("gates"):
                errors.append(f"{case_name}: snapshot must contain gates")

            cockpit_state = build_cockpit_state(case_name, generated_at="1970-01-01T00:00:00+00:00")
            cockpit_errors = validate_cockpit_state(cockpit_state)
            for err in cockpit_errors:
                errors.append(f"{case_name}: cockpit_state: {err}")
        except Exception as exc:
            errors.append(f"{case_name}: engine check failed: {exc}")

    intake_path = ROOT / "real_cases" / "template" / "real_intake.json"

    for name, fn in [
        ("real intake", lambda: process_intake(intake_path, write=False)),
        ("controlled diagnostic", lambda: run_controlled_diagnostic(intake_path=intake_path, write=False)),
        ("human review gate", lambda: run_human_review_gate(intake_path=intake_path, write=False)),
        ("controlled test report", lambda: run_controlled_test_report_pack(intake_path=intake_path, write=False)),
    ]:
        try:
            result = fn()
            if result.get("status") != "PASS":
                errors.append(f"{name} failed: {result}")
            warnings.extend([f"{name}: {w}" for w in result.get("warnings", [])])
        except Exception as exc:
            errors.append(f"{name} check failed: {exc}")

    result = {
        "status": "FAIL" if errors else "PASS",
        "checks": len(REQUIRED) + len(case_names) + 5,
        "cases": len(case_names),
        "errors": errors,
        "warnings": warnings,
    }
    print(json.dumps(result, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())

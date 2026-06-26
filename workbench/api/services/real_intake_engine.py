"""CASULO Workbench Real Intake Engine v0.4.

This module prepares controlled real-case intake before execution.
It does not run uncontrolled client data. It validates scope, privacy,
anonymization, evidence manifest, and only then can export a demo-compatible
case.json for the diagnostic engine.
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from statistics import mean
from typing import Any, Dict, List, Tuple


ROOT = Path(__file__).resolve().parents[2]
REAL_CASES = ROOT / "real_cases"
RUNTIME_OUTPUTS = ROOT / "runtime_outputs" / "real_intake"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def load_intake(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise FileNotFoundError(f"real intake not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def quality_score(source: Dict[str, Any]) -> float:
    q = source.get("quality_inputs", {})
    metrics = [
        q.get("completeness", 0.0),
        q.get("freshness", 0.0),
        q.get("consistency", 0.0),
        q.get("traceability", 0.0),
        q.get("trust", 0.0),
    ]
    base = mean(float(x) for x in metrics)
    sensitivity = {
        "PUBLIC": 0.0,
        "INTERNAL": 0.1,
        "CONFIDENTIAL": 0.2,
        "SENSITIVE": 0.35,
    }.get(source.get("classification", "INTERNAL"), 0.1)
    return round(max(0.0, min(1.0, base - sensitivity * 0.15)), 3)


def quality_label(score: float) -> str:
    if score < 0.31:
        return "LOW"
    if score < 0.61:
        return "CONTROLLED"
    if score < 0.81:
        return "ACCEPTABLE"
    return "HIGH"


def validate_intake(intake: Dict[str, Any]) -> Tuple[List[str], List[str]]:
    errors: List[str] = []
    warnings: List[str] = []

    required = {
        "contract_version",
        "case_id",
        "case_title",
        "vertical",
        "scope",
        "privacy",
        "sources",
        "domains",
        "intersections",
        "deltas",
    }
    missing = sorted(required - set(intake))
    if missing:
        errors.append(f"missing top-level keys: {missing}")

    if intake.get("contract_version") != "workbench.real_intake.v0.4":
        errors.append("invalid contract_version")

    scope = intake.get("scope", {})
    if not scope.get("diagnostic_allowed", False):
        errors.append("scope.diagnostic_allowed must be true for controlled diagnostic")
    if not scope.get("human_review_required", True):
        warnings.append("scope.human_review_required should normally be true for real intake")

    sources = intake.get("sources", [])
    if not sources:
        errors.append("sources must not be empty")

    source_ids = set()
    for src in sources:
        sid = src.get("id")
        if not sid:
            errors.append("source missing id")
            continue
        if sid in source_ids:
            errors.append(f"duplicated source id: {sid}")
        source_ids.add(sid)

        for key in [
            "name",
            "type",
            "domains",
            "classification",
            "contains_personal_data",
            "anonymization_status",
            "quality_inputs",
            "allowed_use",
        ]:
            if key not in src:
                errors.append(f"{sid}: missing source key: {key}")

        if src.get("allowed_use") == "BLOCKED":
            errors.append(f"{sid}: allowed_use BLOCKED")
        if src.get("contains_personal_data") is True and src.get("anonymization_status") == "PENDING":
            errors.append(f"{sid}: personal data pending anonymization")
        if src.get("anonymization_status") == "BLOCKED":
            errors.append(f"{sid}: anonymization BLOCKED")
        if src.get("classification") == "SENSITIVE":
            warnings.append(f"{sid}: sensitive source requires human review")

    domain_ids = {d.get("id") for d in intake.get("domains", [])}
    for src in sources:
        for domain_id in src.get("domains", []):
            if domain_id not in domain_ids:
                errors.append(f"{src.get('id')}: references unknown domain {domain_id}")

    return errors, warnings


def build_evidence_manifest(intake: Dict[str, Any], generated_at: str | None = None) -> Dict[str, Any]:
    ts = generated_at or utc_now()
    errors, warnings = validate_intake(intake)

    sources = []
    evidence_items = []
    blocked_items = []

    for src in intake.get("sources", []):
        score = quality_score(src)
        privacy_status = src.get("anonymization_status", "PENDING")
        allowed_use = src.get("allowed_use", "NEED_REVIEW")

        if errors:
            gate = "BLOCKED"
        elif src.get("classification") == "SENSITIVE" or allowed_use == "NEED_REVIEW":
            gate = "HUMAN_REVIEW_REQUIRED"
        elif score < 0.31:
            gate = "LOW_QUALITY_BLOCK"
        elif score < 0.61:
            gate = "USE_WITH_CAUTION"
        else:
            gate = "ACCEPTED"

        item = {
            "source_id": src.get("id"),
            "quality_score": score,
            "quality_label": quality_label(score),
            "allowed_use": allowed_use,
            "privacy_status": privacy_status,
            "gate": gate,
        }
        sources.append(item)

        if gate in {"BLOCKED", "LOW_QUALITY_BLOCK"}:
            blocked_items.append(item)
        else:
            evidence_items.append(item)

    if errors or blocked_items:
        decision = "BLOCK_INTAKE"
    elif any(item["gate"] == "HUMAN_REVIEW_REQUIRED" for item in sources) or warnings:
        decision = "NEED_HUMAN_REVIEW"
    else:
        decision = "ALLOW_CONTROLLED_DIAGNOSTIC"

    return {
        "contract_version": "workbench.evidence_manifest.v0.4",
        "case_id": intake.get("case_id"),
        "generated_at": ts,
        "scope_gate": {
            "diagnostic_allowed": intake.get("scope", {}).get("diagnostic_allowed", False),
            "human_review_required": intake.get("scope", {}).get("human_review_required", True),
        },
        "privacy_gate": {
            "privacy_mode": intake.get("privacy", {}).get("privacy_mode", "unknown"),
            "errors": errors,
            "warnings": warnings,
        },
        "sources": sources,
        "evidence_items": evidence_items,
        "blocked_items": blocked_items,
        "decision": decision,
    }


def export_case_json(intake: Dict[str, Any], manifest: Dict[str, Any]) -> Dict[str, Any]:
    if manifest["decision"] == "BLOCK_INTAKE":
        raise ValueError("cannot export diagnostic case: intake is blocked")

    exported_sources = []
    source_by_id = {s["id"]: s for s in intake.get("sources", [])}
    for item in manifest.get("evidence_items", []):
        src = source_by_id[item["source_id"]]
        q = src.get("quality_inputs", {})
        exported_sources.append({
            "id": src["id"],
            "name": src["name"],
            "type": src["type"],
            "domains": src.get("domains", []),
            "completeness": q.get("completeness", 0.0),
            "freshness": q.get("freshness", 0.0),
            "consistency": q.get("consistency", 0.0),
            "traceability": q.get("traceability", 0.0),
            "trust": q.get("trust", 0.0),
            "sensitivity": 0.5 if src.get("classification") in {"CONFIDENTIAL", "SENSITIVE"} else 0.2,
        })

    return {
        "case_id": intake["case_id"],
        "title": intake["case_title"],
        "vertical": intake["vertical"],
        "objective": intake.get("scope", {}).get("objective", "Controlled diagnostic"),
        "sources": exported_sources,
        "domains": intake.get("domains", []),
        "intersections": intake.get("intersections", []),
        "deltas": intake.get("deltas", []),
    }


def write_manifest(path: Path, manifest: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def process_intake(intake_path: Path, write: bool = False, output_root: Path = RUNTIME_OUTPUTS, stable_time: bool = True) -> Dict[str, Any]:
    intake = load_intake(intake_path)
    generated_at = "1970-01-01T00:00:00+00:00" if stable_time else None
    errors, warnings = validate_intake(intake)
    manifest = build_evidence_manifest(intake, generated_at=generated_at)

    result = {
        "case_id": intake.get("case_id"),
        "case_title": intake.get("case_title"),
        "status": "FAIL" if errors else "PASS",
        "errors": errors,
        "warnings": warnings,
        "decision": manifest["decision"],
        "sources": len(intake.get("sources", [])),
        "evidence_items": len(manifest.get("evidence_items", [])),
        "blocked_items": len(manifest.get("blocked_items", [])),
    }

    if write:
        case_dir = output_root / intake.get("case_id", "unknown_case")
        write_manifest(case_dir / "evidence_manifest.json", manifest)
        if manifest["decision"] != "BLOCK_INTAKE":
            case_json = export_case_json(intake, manifest)
            write_manifest(case_dir / "case.json", case_json)
        result["output_dir"] = str(case_dir)

    return result

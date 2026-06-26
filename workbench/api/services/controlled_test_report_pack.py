"""CASULO Workbench Controlled Test Report Pack v0.7.

Builds a reviewable report package from the complete controlled flow:
real intake -> controlled diagnostic -> cockpit state -> human review gate.

Default usage through scripts is check mode. Write mode is explicit.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from api.services.controlled_diagnostic_runner import run_controlled_diagnostic
from api.services.human_review_gate import build_human_review_gate, run_human_review_gate
from api.services.real_intake_engine import build_evidence_manifest, load_intake, utc_now


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "runtime_outputs" / "controlled_test_reports"


def _stable_ts(stable_time: bool) -> str:
    return "1970-01-01T00:00:00+00:00" if stable_time else utc_now()


def build_controlled_test_report_pack(intake_path: Path, stable_time: bool = True) -> Dict[str, Any]:
    ts = _stable_ts(stable_time)
    intake = load_intake(intake_path)
    manifest = build_evidence_manifest(intake, generated_at=ts)
    controlled = run_controlled_diagnostic(intake_path=intake_path, write=False, stable_time=stable_time)
    review_packet = build_human_review_gate(intake_path=intake_path, stable_time=stable_time)
    review_result = run_human_review_gate(intake_path=intake_path, write=False, stable_time=stable_time)

    diagnostic = controlled.get("diagnostic", {})
    limits = [
        "Controlled report only.",
        "Not client-facing truth unless explicitly approved by human review.",
        "No implementation is authorized by this report.",
        "All real or near-real evidence must remain anonymized or controlled.",
    ]

    next_actions: List[str] = []
    if review_packet.get("decision") == "PENDING_HUMAN_REVIEW":
        next_actions = [
            "Perform human review.",
            "Request more evidence for ATTENTION items.",
            "Prepare internal review summary.",
            "Do not execute implementation.",
        ]
    elif review_packet.get("decision") == "ALLOW_INTERNAL_REVIEW_ONLY":
        next_actions = [
            "Use internally for review.",
            "Prepare non-binding client review draft if approved later.",
            "Do not execute implementation.",
        ]
    elif review_packet.get("decision") == "BLOCK":
        next_actions = [
            "Block controlled report.",
            "Request more evidence.",
        ]
    else:
        next_actions = [
            "Review decision manually.",
        ]

    result = {
        "contract_version": "workbench.controlled_test_report.v0.7",
        "generated_at": ts,
        "case_id": intake.get("case_id"),
        "case_title": intake.get("case_title"),
        "status": "PASS" if controlled.get("status") == "PASS" and review_result.get("status") == "PASS" else "FAIL",
        "sections": {
            "scope": {
                "objective": intake.get("scope", {}).get("objective"),
                "diagnostic_allowed": intake.get("scope", {}).get("diagnostic_allowed"),
                "implementation_allowed": intake.get("scope", {}).get("implementation_allowed"),
            },
            "intake": {
                "manifest_decision": manifest.get("decision"),
                "sources": len(manifest.get("sources", [])),
                "evidence_items": len(manifest.get("evidence_items", [])),
                "blocked_items": len(manifest.get("blocked_items", [])),
            },
            "diagnostic": diagnostic,
            "human_review": {
                "review_status": review_packet.get("review_status"),
                "decision": review_packet.get("decision"),
                "review_items": len(review_packet.get("review_items", [])),
                "allowed_next_actions": review_packet.get("allowed_next_actions", []),
                "blocked_next_actions": review_packet.get("blocked_next_actions", []),
            },
            "limits": limits,
            "next_actions": next_actions,
        },
        "controlled_diagnostic_status": controlled.get("status"),
        "human_review_status": review_result.get("status"),
        "human_review_decision": review_packet.get("decision"),
        "ready_for_internal_review": review_packet.get("decision") in {
            "PENDING_HUMAN_REVIEW",
            "ALLOW_INTERNAL_REVIEW_ONLY",
        },
        "ready_for_client_review": review_packet.get("decision") == "ALLOW_CLIENT_REVIEW",
        "implementation_authorized": False,
    }
    return result


def validate_controlled_test_report_pack(pack: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    required = {
        "contract_version",
        "generated_at",
        "case_id",
        "case_title",
        "status",
        "sections",
        "controlled_diagnostic_status",
        "human_review_status",
        "human_review_decision",
        "ready_for_internal_review",
        "ready_for_client_review",
        "implementation_authorized",
    }
    missing = sorted(required - set(pack))
    if missing:
        errors.append(f"missing top-level keys: {missing}")
    if pack.get("contract_version") != "workbench.controlled_test_report.v0.7":
        errors.append("invalid contract_version")
    sections = pack.get("sections", {})
    for section in ["scope", "intake", "diagnostic", "human_review", "limits", "next_actions"]:
        if section not in sections:
            errors.append(f"missing section: {section}")
    if pack.get("implementation_authorized") is not False:
        errors.append("implementation_authorized must be false")
    return errors


def _controlled_test_report_md(pack: Dict[str, Any]) -> str:
    s = pack["sections"]
    d = s["diagnostic"]
    h = s["human_review"]

    lines = [
        f"# Controlled Test Report - {pack['case_title']}",
        "",
        f"- Case ID: `{pack['case_id']}`",
        f"- Status: `{pack['status']}`",
        f"- Generated at: `{pack['generated_at']}`",
        f"- Human review decision: `{pack['human_review_decision']}`",
        f"- Implementation authorized: `{pack['implementation_authorized']}`",
        "",
        "## Scope",
        f"- Objective: {s['scope'].get('objective')}",
        f"- Diagnostic allowed: `{s['scope'].get('diagnostic_allowed')}`",
        f"- Implementation allowed: `{s['scope'].get('implementation_allowed')}`",
        "",
        "## Intake",
        f"- Manifest decision: `{s['intake'].get('manifest_decision')}`",
        f"- Sources: `{s['intake'].get('sources')}`",
        f"- Evidence items: `{s['intake'].get('evidence_items')}`",
        f"- Blocked items: `{s['intake'].get('blocked_items')}`",
        "",
        "## Diagnostic",
        f"- Data quality: `{d.get('data_quality')}` (`{d.get('data_quality_label')}`)",
        f"- H_pre: `{d.get('h_pre')}`",
        f"- H_post: `{d.get('h_post')}`",
        f"- Delta_L: `{d.get('delta_l')}`",
        f"- Decision: `{d.get('decision')}`",
        f"- Domains: `{d.get('domains')}`",
        f"- Gates: `{d.get('gates')}`",
        "",
        "## Human Review",
        f"- Review status: `{h.get('review_status')}`",
        f"- Decision: `{h.get('decision')}`",
        f"- Review items: `{h.get('review_items')}`",
        "",
        "## Limits",
    ]
    for item in s["limits"]:
        lines.append(f"- {item}")
    lines += [
        "",
        "## Next Actions",
    ]
    for item in s["next_actions"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def _executive_summary_md(pack: Dict[str, Any]) -> str:
    d = pack["sections"]["diagnostic"]
    return "\n".join([
        f"# Executive Summary - {pack['case_title']}",
        "",
        f"The controlled diagnostic is `{pack['status']}` and produced decision `{d.get('decision')}`.",
        "",
        f"Data quality is `{d.get('data_quality')}` and H_pre is `{d.get('h_pre')}`.",
        "",
        f"Human review decision is `{pack['human_review_decision']}`.",
        "",
        "No implementation is authorized by this report.",
        "",
    ])


def _next_actions_md(pack: Dict[str, Any]) -> str:
    lines = ["# Next Actions", ""]
    for item in pack["sections"]["next_actions"]:
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"


def run_controlled_test_report_pack(
    intake_path: Path,
    write: bool = False,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    stable_time: bool = True,
) -> Dict[str, Any]:
    pack = build_controlled_test_report_pack(intake_path=intake_path, stable_time=stable_time)
    errors = validate_controlled_test_report_pack(pack)
    result = {
        "status": "FAIL" if errors else "PASS",
        "mode": "write" if write else "check",
        "case_id": pack.get("case_id"),
        "case_title": pack.get("case_title"),
        "controlled_diagnostic_status": pack.get("controlled_diagnostic_status"),
        "human_review_decision": pack.get("human_review_decision"),
        "ready_for_internal_review": pack.get("ready_for_internal_review"),
        "ready_for_client_review": pack.get("ready_for_client_review"),
        "implementation_authorized": pack.get("implementation_authorized"),
        "errors": errors,
        "generated_outputs": [],
    }

    if write and not errors:
        case_dir = output_root / pack.get("case_id", "unknown_case")
        case_dir.mkdir(parents=True, exist_ok=True)

        files = {
            "controlled_test_result.json": json.dumps(pack, indent=2, ensure_ascii=False) + "\n",
            "controlled_test_report.md": _controlled_test_report_md(pack),
            "executive_summary.md": _executive_summary_md(pack),
            "next_actions.md": _next_actions_md(pack),
        }
        for filename, content in files.items():
            path = case_dir / filename
            path.write_text(content, encoding="utf-8")
            result["generated_outputs"].append(str(path))

    return result

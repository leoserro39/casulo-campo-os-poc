"""CASULO Workbench Human Review Gate v0.6.

Adds a human review layer after controlled diagnostic execution.
The gate prevents controlled diagnostics from becoming client-facing truth or
implementation input without explicit review.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

from api.services.controlled_diagnostic_runner import run_controlled_diagnostic
from api.services.real_intake_engine import utc_now


ROOT = Path(__file__).resolve().parents[2]
DEFAULT_OUTPUT_ROOT = ROOT / "runtime_outputs" / "human_review"


def _review_items(controlled: Dict[str, Any]) -> List[Dict[str, Any]]:
    diagnostic = controlled.get("diagnostic", {})
    items = [
        {
            "id": "scope_privacy",
            "label": "Scope and privacy gate",
            "status": "PASS" if controlled.get("manifest_decision") in {"ALLOW_CONTROLLED_DIAGNOSTIC", "NEED_HUMAN_REVIEW"} else "BLOCK",
            "evidence": controlled.get("manifest_decision"),
            "requires_human_confirmation": True,
        },
        {
            "id": "diagnostic_integrity",
            "label": "Controlled diagnostic integrity",
            "status": "PASS" if controlled.get("status") == "PASS" else "BLOCK",
            "evidence": controlled.get("status"),
            "requires_human_confirmation": True,
        },
        {
            "id": "data_quality",
            "label": "Data quality adequacy",
            "status": "PASS" if float(diagnostic.get("data_quality", 0.0)) >= 0.61 else "ATTENTION",
            "evidence": diagnostic.get("data_quality"),
            "requires_human_confirmation": True,
        },
        {
            "id": "fragility",
            "label": "Operational fragility",
            "status": "ATTENTION" if float(diagnostic.get("h_pre", 1.0)) > 0.30 else "PASS",
            "evidence": diagnostic.get("h_pre"),
            "requires_human_confirmation": True,
        },
        {
            "id": "gate_decision",
            "label": "Diagnostic decision and gates",
            "status": "ATTENTION" if diagnostic.get("decision") != "ALLOW_SOLUTION" else "PASS",
            "evidence": diagnostic.get("decision"),
            "requires_human_confirmation": True,
        },
        {
            "id": "implementation_block",
            "label": "Implementation remains blocked",
            "status": "PASS",
            "evidence": "Implementation requires later solution gate.",
            "requires_human_confirmation": False,
        },
    ]
    return items


def _default_decision(items: List[Dict[str, Any]]) -> str:
    if any(item["status"] == "BLOCK" for item in items):
        return "BLOCK"
    if any(item["status"] == "ATTENTION" for item in items):
        return "PENDING_HUMAN_REVIEW"
    return "ALLOW_INTERNAL_REVIEW_ONLY"


def build_human_review_gate(
    intake_path: Path,
    stable_time: bool = True,
) -> Dict[str, Any]:
    controlled = run_controlled_diagnostic(intake_path=intake_path, write=False, stable_time=stable_time)
    generated_at = "1970-01-01T00:00:00+00:00" if stable_time else utc_now()
    items = _review_items(controlled)
    decision = _default_decision(items)

    allowed_next_actions = []
    blocked_next_actions = [
        "client_facing_claim",
        "implementation_execution",
        "production_activation",
    ]

    if decision in {"PENDING_HUMAN_REVIEW", "ALLOW_INTERNAL_REVIEW_ONLY"}:
        allowed_next_actions.extend([
            "internal_review",
            "request_more_evidence",
            "prepare_client_review_draft",
        ])
    if decision == "ALLOW_INTERNAL_REVIEW_ONLY":
        allowed_next_actions.append("prepare_non_binding_summary")
    if decision == "BLOCK":
        allowed_next_actions = ["request_more_evidence"]

    return {
        "contract_version": "workbench.human_review_gate.v0.6",
        "case_id": controlled.get("case_id"),
        "case_title": controlled.get("case_title"),
        "generated_at": generated_at,
        "controlled_diagnostic_status": controlled.get("status"),
        "review_required": True,
        "review_status": "PENDING_HUMAN_REVIEW" if decision == "PENDING_HUMAN_REVIEW" else "APPROVED_FOR_INTERNAL_REVIEW" if decision == "ALLOW_INTERNAL_REVIEW_ONLY" else "BLOCKED",
        "review_items": items,
        "allowed_next_actions": allowed_next_actions,
        "blocked_next_actions": blocked_next_actions,
        "decision": decision,
        "controlled_diagnostic_summary": controlled.get("diagnostic", {}),
    }


def validate_human_review_gate(packet: Dict[str, Any]) -> List[str]:
    errors: List[str] = []
    required = {
        "contract_version",
        "case_id",
        "case_title",
        "generated_at",
        "controlled_diagnostic_status",
        "review_required",
        "review_status",
        "review_items",
        "allowed_next_actions",
        "blocked_next_actions",
        "decision",
    }
    missing = sorted(required - set(packet))
    if missing:
        errors.append(f"missing top-level keys: {missing}")
    if packet.get("contract_version") != "workbench.human_review_gate.v0.6":
        errors.append("invalid contract_version")
    if not packet.get("review_required"):
        errors.append("review_required must be true")
    if not packet.get("review_items"):
        errors.append("review_items must not be empty")
    if "implementation_execution" not in packet.get("blocked_next_actions", []):
        errors.append("implementation_execution must remain blocked")
    if packet.get("decision") not in {
        "PENDING_HUMAN_REVIEW",
        "ALLOW_INTERNAL_REVIEW_ONLY",
        "ALLOW_CLIENT_REVIEW",
        "NEED_MORE_EVIDENCE",
        "BLOCK",
    }:
        errors.append("invalid decision")
    return errors


def human_review_markdown(packet: Dict[str, Any]) -> str:
    lines = [
        f"# Human Review Gate - {packet.get('case_title')}",
        "",
        f"- Case ID: `{packet.get('case_id')}`",
        f"- Controlled diagnostic: `{packet.get('controlled_diagnostic_status')}`",
        f"- Review status: `{packet.get('review_status')}`",
        f"- Decision: `{packet.get('decision')}`",
        "",
        "## Review items",
    ]
    for item in packet.get("review_items", []):
        lines.append(f"- `{item['status']}` - {item['label']} / evidence: `{item.get('evidence')}`")
    lines += [
        "",
        "## Allowed next actions",
    ]
    for action in packet.get("allowed_next_actions", []):
        lines.append(f"- `{action}`")
    lines += [
        "",
        "## Blocked next actions",
    ]
    for action in packet.get("blocked_next_actions", []):
        lines.append(f"- `{action}`")
    lines += [
        "",
        "## Human decision",
        "",
        "- [ ] Approve for internal review only",
        "- [ ] Request more evidence",
        "- [ ] Block",
        "- [ ] Approve for client review later, after explicit decision",
        "",
        "No implementation is authorized by this review packet.",
    ]
    return "\n".join(lines) + "\n"


def run_human_review_gate(
    intake_path: Path,
    write: bool = False,
    output_root: Path = DEFAULT_OUTPUT_ROOT,
    stable_time: bool = True,
) -> Dict[str, Any]:
    packet = build_human_review_gate(intake_path=intake_path, stable_time=stable_time)
    errors = validate_human_review_gate(packet)
    result = {
        "status": "FAIL" if errors else "PASS",
        "mode": "write" if write else "check",
        "case_id": packet.get("case_id"),
        "case_title": packet.get("case_title"),
        "review_status": packet.get("review_status"),
        "decision": packet.get("decision"),
        "review_items": len(packet.get("review_items", [])),
        "errors": errors,
        "generated_outputs": [],
    }

    if write and not errors:
        case_dir = output_root / packet.get("case_id", "unknown_case")
        case_dir.mkdir(parents=True, exist_ok=True)
        packet_path = case_dir / "human_review_gate.json"
        packet_path.write_text(json.dumps(packet, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        md_path = case_dir / "human_review_gate.md"
        md_path.write_text(human_review_markdown(packet), encoding="utf-8")
        result["generated_outputs"] = [str(packet_path), str(md_path)]

    return result

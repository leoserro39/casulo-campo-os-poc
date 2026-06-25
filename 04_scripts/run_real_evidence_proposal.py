#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DELTAS = ROOT / "05_outputs" / "real_tests" / "evidence_deltas"
PROPOSALS = ROOT / "05_outputs" / "real_tests" / "proposals"
REPORTS = ROOT / "05_outputs" / "reports"


def rel(path):
    return str(path.relative_to(ROOT))


def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def safe_name(value):
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    return value.strip("_") or "real_evidence"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def risk_weight(risk):
    risk = str(risk or "").upper()
    if risk == "HIGH":
        return 0.45
    if risk == "MEDIUM":
        return 0.22
    return 0.08


def compute_delta(quality, trust_score, risk):
    row_count = max(int(quality.get("row_count") or 0), 1)
    unresolved_ratio = float(quality.get("unresolved_rows") or 0) / row_count
    unknown_ratio = float(quality.get("unknown_status_rows") or 0) / row_count
    contradiction_ratio = float(quality.get("contradictions_count") or 0) / row_count
    missing_response_ratio = 0.0

    response_count = int(quality.get("response_time_count") or 0)
    if row_count:
        missing_response_ratio = max(row_count - response_count, 0) / row_count

    delta_l = round(min(1.0, 0.18 + unresolved_ratio * 0.42 + unknown_ratio * 0.22 + missing_response_ratio * 0.10), 3)
    h_pre = round(min(1.0, (1.0 - float(trust_score)) * 0.50 + risk_weight(risk) + contradiction_ratio * 0.35 + unknown_ratio * 0.30), 3)

    return {
        "Delta_L": delta_l,
        "H_pre": h_pre,
        "unresolved_ratio": round(unresolved_ratio, 3),
        "unknown_status_ratio": round(unknown_ratio, 3),
        "missing_response_time_ratio": round(missing_response_ratio, 3),
        "contradiction_ratio": round(contradiction_ratio, 3),
    }


def proposal_gate(intake_gate, risk, delta):
    if not str(intake_gate).startswith("ALLOW_EVIDENCE_ONLY"):
        return "BLOCKED_BY_INTAKE_GATE"
    if str(risk).upper() == "HIGH":
        return "BLOCKED_HIGH_HALLUCINATION_RISK"
    if delta["H_pre"] >= 0.45:
        return "PROPOSAL_REQUIRES_STRONG_HUMAN_REVIEW"
    return "PROPOSAL_REQUIRES_HUMAN_REVIEW"


def build_actions(quality):
    actions = [
        {
            "action": "standardize_status_taxonomy",
            "description": "Use only new_contact, waiting_confirmation and resolved as the first controlled atendimento statuses.",
            "reason": "The pilot evidence has unresolved and unknown status records.",
        },
        {
            "action": "create_daily_unresolved_queue",
            "description": "Create a daily queue for unresolved conversations and contacts waiting for confirmation.",
            "reason": "Unresolved rows should become visible before sales or operations depend on the flow.",
        },
        {
            "action": "measure_first_response_time",
            "description": "Keep recording response_time_minutes for every first response event.",
            "reason": "The current evidence has response time values but not for every record.",
        },
        {
            "action": "require_resolved_status",
            "description": "Every atendimento record should carry resolved, unresolved or waiting_confirmation status.",
            "reason": "Unknown status rows increase uncertainty and keep promotion blocked.",
        },
    ]

    avg = quality.get("avg_response_time_minutes")
    if avg is not None:
        actions.append({
            "action": "set_initial_response_time_watch",
            "description": "Use the current average response time as baseline and watch it during the next pilot cycle.",
            "reason": "The evidence baseline is available for comparison.",
            "baseline_avg_response_time_minutes": avg,
        })

    return actions


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--intake-report", default="05_outputs/reports/real_source_intake_report.json")
    parser.add_argument("--proposal-name", default="real_atendimento_evidence_proposal")
    args = parser.parse_args()

    report_path = Path(args.intake_report)
    if not report_path.is_absolute():
        report_path = ROOT / report_path

    if not report_path.exists():
        raise SystemExit("intake report not found: %s" % report_path)

    report = read_json(report_path)
    manifest = report.get("manifest", {})
    trust = report.get("trust", {})
    intake_delta = report.get("delta", {})

    quality = trust.get("quality", {})
    trust_score = float(trust.get("trust_score") or 0)
    risk = trust.get("hallucination_risk")
    intake_gate = intake_delta.get("gate")

    delta_metrics = compute_delta(quality, trust_score, risk)
    gate = proposal_gate(intake_gate, risk, delta_metrics)

    generated = stamp()
    proposal_name = safe_name(args.proposal_name)
    base = "%s_%s" % (proposal_name, generated)

    DELTAS.mkdir(parents=True, exist_ok=True)
    PROPOSALS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    evidence_delta = {
        "status": "REAL_EVIDENCE_DELTA",
        "generated_utc": generated,
        "source": manifest.get("source"),
        "source_name": manifest.get("source_name"),
        "intake_report": rel(report_path),
        "readiness_gate": manifest.get("readiness_gate"),
        "intake_gate": intake_gate,
        "trust_score": trust_score,
        "hallucination_risk": risk,
        "delta": delta_metrics,
        "canonical_effect": "NONE",
    }

    proposal = {
        "status": "REAL_EVIDENCE_PROPOSAL",
        "generated_utc": generated,
        "proposal_name": proposal_name,
        "source": manifest.get("source"),
        "source_name": manifest.get("source_name"),
        "proposal_gate": gate,
        "requires_human_review": True,
        "canonical_effect": "NONE",
        "evidence_summary": {
            "row_count": quality.get("row_count"),
            "contact_count": quality.get("contact_count"),
            "resolved_rows": quality.get("resolved_rows"),
            "unresolved_rows": quality.get("unresolved_rows"),
            "unknown_status_rows": quality.get("unknown_status_rows"),
            "avg_response_time_minutes": quality.get("avg_response_time_minutes"),
            "trust_score": trust_score,
            "hallucination_risk": risk,
            "Delta_L": delta_metrics["Delta_L"],
            "H_pre": delta_metrics["H_pre"],
        },
        "proposed_actions": build_actions(quality),
        "human_review_questions": [
            "Does the status taxonomy match the real atendimento operation?",
            "Is it acceptable to use this dataset as pilot evidence?",
            "Should unknown status records be corrected before the next pilot cycle?",
            "Who owns the daily unresolved queue?",
            "What response time target should be used for the next cycle?",
        ],
        "next_action": "Send this proposal to human review. Do not mutate branch state automatically.",
    }

    delta_json = DELTAS / (base + "_delta.json")
    delta_md = DELTAS / (base + "_delta.md")
    proposal_json = PROPOSALS / (base + ".json")
    proposal_md = PROPOSALS / (base + ".md")
    report_json = REPORTS / "real_evidence_proposal_report.json"
    report_md = REPORTS / "real_evidence_proposal_report.md"

    delta_json.write_text(json.dumps(evidence_delta, indent=2, ensure_ascii=False), encoding="utf-8")
    proposal_json.write_text(json.dumps(proposal, indent=2, ensure_ascii=False), encoding="utf-8")
    report_json.write_text(json.dumps({"evidence_delta": evidence_delta, "proposal": proposal}, indent=2, ensure_ascii=False), encoding="utf-8")

    delta_lines = [
        "# CASULO Campo OS - Real Evidence Delta",
        "",
        "- status: REAL_EVIDENCE_DELTA",
        "- generated_utc: %s" % generated,
        "- source: %s" % manifest.get("source"),
        "- readiness_gate: %s" % manifest.get("readiness_gate"),
        "- intake_gate: %s" % intake_gate,
        "- trust_score: %s" % trust_score,
        "- hallucination_risk: %s" % risk,
        "- Delta_L: %s" % delta_metrics["Delta_L"],
        "- H_pre: %s" % delta_metrics["H_pre"],
        "- canonical_effect: NONE",
        "",
    ]
    delta_md.write_text("\n".join(delta_lines), encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Real Evidence Proposal",
        "",
        "- status: REAL_EVIDENCE_PROPOSAL",
        "- generated_utc: %s" % generated,
        "- proposal_name: %s" % proposal_name,
        "- source: %s" % manifest.get("source"),
        "- proposal_gate: %s" % gate,
        "- requires_human_review: true",
        "- canonical_effect: NONE",
        "- trust_score: %s" % trust_score,
        "- hallucination_risk: %s" % risk,
        "- Delta_L: %s" % delta_metrics["Delta_L"],
        "- H_pre: %s" % delta_metrics["H_pre"],
        "",
        "## Evidence summary",
        "",
    ]

    for key, value in proposal["evidence_summary"].items():
        lines.append("- %s: %s" % (key, value))

    lines.extend(["", "## Proposed actions", ""])
    for item in proposal["proposed_actions"]:
        lines.append("- %s: %s" % (item["action"], item["description"]))

    lines.extend(["", "## Human review questions", ""])
    lines.extend(["- " + q for q in proposal["human_review_questions"]])

    lines.extend([
        "",
        "## Next action",
        "",
        "- Send this proposal to human review. Do not mutate branch state automatically.",
        "",
    ])

    proposal_md.write_text("\n".join(lines), encoding="utf-8")
    report_md.write_text("\n".join(lines), encoding="utf-8")

    print("REAL_EVIDENCE_PROPOSAL_CREATED")
    print("evidence_delta:", rel(delta_md))
    print("proposal:", rel(proposal_md))
    print("proposal_gate:", gate)
    print("Delta_L:", delta_metrics["Delta_L"])
    print("H_pre:", delta_metrics["H_pre"])
    print("requires_human_review: true")
    print("canonical_effect: NONE")


if __name__ == "__main__":
    main()

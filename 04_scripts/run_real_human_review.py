#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "05_outputs" / "real_tests" / "reviews"
REPORTS = ROOT / "05_outputs" / "reports"

ALLOWED_DECISIONS = {
    "APPROVED_FOR_PILOT",
    "NEEDS_MORE_EVIDENCE",
    "REJECTED",
    "APPROVED_FOR_RETURN_DELTA_PROPOSAL",
}


def rel(path):
    return str(path.relative_to(ROOT))


def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def safe_name(value):
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    return value.strip("_") or "real_human_review"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def next_action(decision):
    if decision == "APPROVED_FOR_PILOT":
        return "Record pilot measurements only. Do not promote or mutate canonical branch state."
    if decision == "NEEDS_MORE_EVIDENCE":
        return "Collect more evidence, correct unknown statuses if possible, then rerun intake/proposal."
    if decision == "REJECTED":
        return "Do not proceed. Keep proposal archived as rejected evidence."
    if decision == "APPROVED_FOR_RETURN_DELTA_PROPOSAL":
        return "Generate return delta proposal only. Final apply still requires explicit confirmation."
    return "Review manually."


def review_scope(decision):
    if decision == "APPROVED_FOR_PILOT":
        return "PILOT_MEASUREMENT_ONLY"
    if decision == "APPROVED_FOR_RETURN_DELTA_PROPOSAL":
        return "RETURN_DELTA_PROPOSAL_ONLY"
    if decision == "NEEDS_MORE_EVIDENCE":
        return "EVIDENCE_COLLECTION"
    if decision == "REJECTED":
        return "STOP"
    return "UNKNOWN"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--proposal-report", default="05_outputs/reports/real_evidence_proposal_report.json")
    parser.add_argument("--decision", required=True, choices=sorted(ALLOWED_DECISIONS))
    parser.add_argument("--reviewer", default="human_operator")
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    proposal_report = Path(args.proposal_report)
    if not proposal_report.is_absolute():
        proposal_report = ROOT / proposal_report

    if not proposal_report.exists():
        raise SystemExit("proposal report not found: %s" % proposal_report)

    data = read_json(proposal_report)
    proposal = data.get("proposal", {})
    evidence_delta = data.get("evidence_delta", {})

    if proposal.get("requires_human_review") is not True:
        raise SystemExit("proposal does not declare requires_human_review=true")

    generated = stamp()
    proposal_name = safe_name(proposal.get("proposal_name") or "real_evidence_proposal")
    base = "review_%s_%s" % (proposal_name, generated)

    REVIEWS.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    decision = args.decision

    review = {
        "status": "REAL_HUMAN_REVIEW",
        "generated_utc": generated,
        "reviewer": args.reviewer,
        "decision": decision,
        "review_scope": review_scope(decision),
        "note": args.note,
        "proposal_report": rel(proposal_report),
        "proposal_name": proposal.get("proposal_name"),
        "source": proposal.get("source"),
        "proposal_gate": proposal.get("proposal_gate"),
        "trust_score": proposal.get("evidence_summary", {}).get("trust_score"),
        "hallucination_risk": proposal.get("evidence_summary", {}).get("hallucination_risk"),
        "Delta_L": proposal.get("evidence_summary", {}).get("Delta_L"),
        "H_pre": proposal.get("evidence_summary", {}).get("H_pre"),
        "canonical_effect": "NONE",
        "promotion_allowed": False,
        "branch_mutation_allowed": False,
        "sync_allowed": False,
        "next_action": next_action(decision),
        "evidence_delta_status": evidence_delta.get("status"),
    }

    review_json = REVIEWS / (base + ".json")
    review_md = REVIEWS / (base + ".md")
    report_json = REPORTS / "real_human_review_report.json"
    report_md = REPORTS / "real_human_review_report.md"

    text_json = json.dumps(review, indent=2, ensure_ascii=False)
    review_json.write_text(text_json, encoding="utf-8")
    report_json.write_text(text_json, encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Real Human Review",
        "",
        "- status: REAL_HUMAN_REVIEW",
        "- generated_utc: %s" % generated,
        "- reviewer: %s" % args.reviewer,
        "- decision: %s" % decision,
        "- review_scope: %s" % review["review_scope"],
        "- proposal_name: %s" % review["proposal_name"],
        "- source: %s" % review["source"],
        "- proposal_gate: %s" % review["proposal_gate"],
        "- trust_score: %s" % review["trust_score"],
        "- hallucination_risk: %s" % review["hallucination_risk"],
        "- Delta_L: %s" % review["Delta_L"],
        "- H_pre: %s" % review["H_pre"],
        "- canonical_effect: NONE",
        "- promotion_allowed: false",
        "- branch_mutation_allowed: false",
        "- sync_allowed: false",
        "",
        "## Note",
        "",
        "- %s" % (args.note or "none"),
        "",
        "## Next action",
        "",
        "- %s" % review["next_action"],
        "",
    ]

    review_md.write_text("\n".join(lines), encoding="utf-8")
    report_md.write_text("\n".join(lines), encoding="utf-8")

    print("REAL_HUMAN_REVIEW_CREATED")
    print("review:", rel(review_md))
    print("decision:", decision)
    print("review_scope:", review["review_scope"])
    print("promotion_allowed: false")
    print("branch_mutation_allowed: false")
    print("canonical_effect: NONE")
    print("next_action:", review["next_action"])


if __name__ == "__main__":
    main()

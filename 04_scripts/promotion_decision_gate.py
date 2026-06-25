#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "05_outputs" / "reports"
OUT = ROOT / "05_outputs" / "promotion_decisions"


def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def rel(path):
    return str(path.relative_to(ROOT))


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def normalize_decision(value):
    v = (value or "").strip().lower()
    mapping = {
        "promote": "PROMOTE",
        "promover": "PROMOTE",
        "extend": "EXTEND_PILOT",
        "extend_pilot": "EXTEND_PILOT",
        "estender": "EXTEND_PILOT",
        "reject": "REJECT",
        "rejeitar": "REJECT",
        "needs_more_evidence": "NEEDS_MORE_EVIDENCE",
        "mais_evidencia": "NEEDS_MORE_EVIDENCE",
    }
    if v not in mapping:
        raise SystemExit("invalid decision. Use promote, extend_pilot, reject, or needs_more_evidence")
    return mapping[v]


def latest_pilot_report():
    path = REPORTS / "pilot_measurement_report.json"
    if not path.exists():
        raise SystemExit("missing pilot measurement report")
    return path, read_json(path)


def decision_effect(decision):
    if decision == "PROMOTE":
        return "PROMOTION_PROPOSED_ONLY"
    if decision == "EXTEND_PILOT":
        return "NONE_EXTEND_PILOT"
    if decision == "REJECT":
        return "NONE_REJECT_PILOT"
    return "NONE_REQUEST_MORE_EVIDENCE"


def next_action(decision):
    if decision == "PROMOTE":
        return "Prepare branch state promotion proposal. Do not overwrite state automatically."
    if decision == "EXTEND_PILOT":
        return "Collect more pilot measurements before promotion."
    if decision == "REJECT":
        return "Keep applied pilot delta as rejected/closed evidence and do not promote."
    return "Collect additional evidence before another decision."


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--decision", required=True)
    parser.add_argument("--operator", default="human_operator")
    parser.add_argument("--notes", default="")
    args = parser.parse_args()

    decision = normalize_decision(args.decision)
    report_path, report = latest_pilot_report()

    agg = report.get("aggregate", {})
    overall_signal = agg.get("overall_signal")
    measurement_count = agg.get("measurement_count", 0)

    if decision == "PROMOTE":
        if overall_signal != "PROMOTION_CANDIDATE" or measurement_count < 3:
            raise SystemExit("PROMOTE blocked: requires overall_signal=PROMOTION_CANDIDATE and at least 3 measurements")

    OUT.mkdir(parents=True, exist_ok=True)
    stamp = utc_stamp()
    base = "promotion_decision_%s_%s" % (decision.lower(), stamp)

    json_path = OUT / (base + ".json")
    md_path = OUT / (base + ".md")

    record = {
        "status": "RECORDED",
        "decided_utc": stamp,
        "operator": args.operator,
        "decision": decision,
        "source_pilot_report": rel(report_path),
        "measurement_count": measurement_count,
        "overall_signal": overall_signal,
        "canonical_effect": decision_effect(decision),
        "promotion_allowed": decision == "PROMOTE",
        "notes": args.notes,
        "next_action": next_action(decision),
    }

    json_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Promotion Decision",
        "",
        "- status: RECORDED",
        "- decided_utc: %s" % stamp,
        "- operator: %s" % args.operator,
        "- decision: %s" % decision,
        "- source_pilot_report: %s" % rel(report_path),
        "- measurement_count: %s" % measurement_count,
        "- overall_signal: %s" % overall_signal,
        "- canonical_effect: %s" % decision_effect(decision),
        "- promotion_allowed: %s" % str(decision == "PROMOTE").lower(),
        "",
        "## Notes",
        "",
        args.notes or "- none",
        "",
        "## Next action",
        "",
        "- %s" % next_action(decision),
        "",
    ]

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print("PROMOTION_DECISION_RECORDED")
    print("decision:", decision)
    print("promotion_allowed:", str(decision == "PROMOTE").lower())
    print("canonical_effect:", decision_effect(decision))
    print("decision_record:", rel(md_path))
    print("trace:", rel(json_path))


if __name__ == "__main__":
    main()

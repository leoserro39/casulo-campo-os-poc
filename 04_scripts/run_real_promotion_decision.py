#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "05_outputs" / "real_tests" / "promotion_decisions"
REPORTS = ROOT / "05_outputs" / "reports"


def rel(path):
    return str(path.relative_to(ROOT))


def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def safe_name(value):
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    return value.strip("_") or "real_promotion_decision"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def latest_measurements(folder, prefix=None):
    files = sorted(folder.glob("*.json"), key=lambda p: p.stat().st_mtime)
    if prefix:
        files = [p for p in files if p.name.startswith(prefix)]
    return files


def aggregate(measurements):
    measurement_count = len(measurements)
    total_conversations = 0
    resolved = 0
    unresolved = 0
    unknown = 0
    positive_count = 0
    cleanup_count = 0
    insufficient_count = 0
    response_times = []

    signals = []

    for item in measurements:
        m = item.get("measurement", {})
        total_conversations += int(m.get("total_conversations") or 0)
        resolved += int(m.get("resolved_conversations") or 0)
        unresolved += int(m.get("unresolved_conversations") or 0)
        unknown += int(m.get("conversations_without_resolved_status") or 0)

        signal = m.get("pilot_signal")
        signals.append(signal)

        if signal == "PILOT_SIGNAL_POSITIVE":
            positive_count += 1
        elif signal == "NEEDS_STATUS_CLEANUP":
            cleanup_count += 1
        elif signal == "INSUFFICIENT_SAMPLE":
            insufficient_count += 1

        rt = m.get("response_time_minutes")
        if rt is not None:
            response_times.append(float(rt))

    unresolved_ratio = round(unresolved / total_conversations, 3) if total_conversations else 0.0
    unknown_status_ratio = round(unknown / total_conversations, 3) if total_conversations else 0.0
    resolved_ratio = round(resolved / total_conversations, 3) if total_conversations else 0.0

    avg_response_time = None
    if response_times:
        avg_response_time = round(sum(response_times) / len(response_times), 2)

    return {
        "measurement_count": measurement_count,
        "total_conversations": total_conversations,
        "resolved_conversations": resolved,
        "unresolved_conversations": unresolved,
        "conversations_without_resolved_status": unknown,
        "resolved_ratio": resolved_ratio,
        "unresolved_ratio": unresolved_ratio,
        "unknown_status_ratio": unknown_status_ratio,
        "avg_response_time_minutes": avg_response_time,
        "positive_signal_count": positive_count,
        "cleanup_signal_count": cleanup_count,
        "insufficient_signal_count": insufficient_count,
        "signals": signals,
    }


def decide(agg, min_measurements, max_unresolved_ratio, max_unknown_ratio):
    if agg["measurement_count"] == 0:
        return "NEEDS_MORE_EVIDENCE", "No pilot measurements found."

    if agg["insufficient_signal_count"] > 0:
        return "NEEDS_MORE_EVIDENCE", "At least one measurement has insufficient sample."

    if agg["cleanup_signal_count"] > 0:
        return "NEEDS_MORE_EVIDENCE", "Status cleanup is required before promotion decision."

    if agg["measurement_count"] < min_measurements:
        return "EXTEND_PILOT", "Positive signal exists, but more measurements are required."

    if agg["unknown_status_ratio"] > max_unknown_ratio:
        return "NEEDS_MORE_EVIDENCE", "Unknown status ratio is above threshold."

    if agg["unresolved_ratio"] > max_unresolved_ratio:
        return "EXTEND_PILOT", "Unresolved ratio is above promotion threshold."

    if agg["positive_signal_count"] == agg["measurement_count"]:
        return "PROMOTION_CANDIDATE", "All measurements are positive and thresholds are acceptable."

    return "EXTEND_PILOT", "Pilot should continue until evidence is stronger."


def next_action(decision):
    if decision == "PROMOTION_CANDIDATE":
        return "Create a controlled return delta / promotion proposal. Do not mutate branch state automatically."
    if decision == "EXTEND_PILOT":
        return "Collect more pilot measurements before promotion."
    if decision == "NEEDS_MORE_EVIDENCE":
        return "Correct evidence gaps or collect more data before deciding."
    if decision == "REJECT":
        return "Stop pilot promotion path and archive decision."
    return "Review manually."


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--review-report", default="05_outputs/reports/real_human_review_report.json")
    parser.add_argument("--measurements-dir", default="05_outputs/real_tests/pilot_measurements")
    parser.add_argument("--decision-name", default="real_atendimento_promotion_decision")
    parser.add_argument("--measurement-prefix", default="")
    parser.add_argument("--min-measurements", type=int, default=3)
    parser.add_argument("--max-unresolved-ratio", type=float, default=0.35)
    parser.add_argument("--max-unknown-ratio", type=float, default=0.20)
    args = parser.parse_args()

    review_path = Path(args.review_report)
    measurements_dir = Path(args.measurements_dir)

    if not review_path.is_absolute():
        review_path = ROOT / review_path
    if not measurements_dir.is_absolute():
        measurements_dir = ROOT / measurements_dir

    if not review_path.exists():
        raise SystemExit("review report not found: %s" % review_path)
    if not measurements_dir.exists():
        raise SystemExit("measurements dir not found: %s" % measurements_dir)

    review = read_json(review_path)

    if review.get("decision") != "APPROVED_FOR_PILOT":
        print("REAL_PROMOTION_DECISION_BLOCKED")
        print("review_decision:", review.get("decision"))
        print("canonical_effect: NONE")
        raise SystemExit(2)

    files = latest_measurements(measurements_dir, args.measurement_prefix or None)
    measurements = [read_json(path) for path in files]
    agg = aggregate(measurements)
    decision, reason = decide(
        agg,
        args.min_measurements,
        args.max_unresolved_ratio,
        args.max_unknown_ratio,
    )

    generated = stamp()
    name = safe_name(args.decision_name)
    base = "%s_%s" % (name, generated)

    OUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    result = {
        "status": "REAL_PROMOTION_DECISION",
        "generated_utc": generated,
        "decision_name": name,
        "decision": decision,
        "reason": reason,
        "review_report": rel(review_path),
        "review_decision": review.get("decision"),
        "measurement_count": agg["measurement_count"],
        "measurement_prefix": args.measurement_prefix,
        "measurement_files": [rel(path) for path in files],
        "thresholds": {
            "min_measurements": args.min_measurements,
            "max_unresolved_ratio": args.max_unresolved_ratio,
            "max_unknown_ratio": args.max_unknown_ratio,
        },
        "aggregate": agg,
        "canonical_effect": "NONE",
        "promotion_execution_allowed": False,
        "branch_mutation_allowed": False,
        "sync_allowed": False,
        "next_action": next_action(decision),
    }

    json_path = OUT / (base + ".json")
    md_path = OUT / (base + ".md")
    report_json = REPORTS / "real_promotion_decision_report.json"
    report_md = REPORTS / "real_promotion_decision_report.md"

    text_json = json.dumps(result, indent=2, ensure_ascii=False)
    json_path.write_text(text_json, encoding="utf-8")
    report_json.write_text(text_json, encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Real Promotion Decision",
        "",
        "- status: REAL_PROMOTION_DECISION",
        "- generated_utc: %s" % generated,
        "- decision_name: %s" % name,
        "- decision: %s" % decision,
        "- reason: %s" % reason,
        "- review_decision: %s" % review.get("decision"),
        "- canonical_effect: NONE",
        "- promotion_execution_allowed: false",
        "- branch_mutation_allowed: false",
        "- sync_allowed: false",
        "",
        "## Thresholds",
        "",
        "- min_measurements: %s" % args.min_measurements,
        "- max_unresolved_ratio: %s" % args.max_unresolved_ratio,
        "- max_unknown_ratio: %s" % args.max_unknown_ratio,
        "",
        "## Aggregate",
        "",
    ]

    for key, value in agg.items():
        lines.append("- %s: %s" % (key, value))

    lines.extend([
        "",
        "## Next action",
        "",
        "- %s" % result["next_action"],
        "",
    ])

    text_md = "\n".join(lines)
    md_path.write_text(text_md, encoding="utf-8")
    report_md.write_text(text_md, encoding="utf-8")

    print("REAL_PROMOTION_DECISION_CREATED")
    print("decision:", decision)
    print("reason:", reason)
    print("measurement_prefix:", args.measurement_prefix)
    print("measurement_count:", agg["measurement_count"])
    print("positive_signal_count:", agg["positive_signal_count"])
    print("unresolved_ratio:", agg["unresolved_ratio"])
    print("unknown_status_ratio:", agg["unknown_status_ratio"])
    print("promotion_execution_allowed: false")
    print("canonical_effect: NONE")
    print("report:", rel(report_md))


if __name__ == "__main__":
    main()

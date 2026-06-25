#!/usr/bin/env python3
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "05_outputs" / "pilot_measurements"


def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def rel(path):
    return str(path.relative_to(ROOT))


def safe_float(value):
    try:
        return float(value)
    except Exception:
        return None


def safe_int(value):
    try:
        return int(value)
    except Exception:
        return None


def compute_signal(total, resolved, unresolved, no_status, response_time):
    if total is None or total <= 0:
        return "NEEDS_MORE_EVIDENCE"

    resolved_ratio = (resolved or 0) / total
    unresolved_ratio = (unresolved or 0) / total
    no_status_ratio = (no_status or 0) / total

    if response_time is None:
        return "NEEDS_MORE_EVIDENCE"

    if resolved_ratio >= 0.75 and unresolved_ratio <= 0.15 and no_status_ratio <= 0.10 and response_time <= 30:
        return "PROMOTION_CANDIDATE"

    if unresolved_ratio >= 0.40 or no_status_ratio >= 0.35 or response_time > 120:
        return "PILOT_RISK"

    return "EXTEND_PILOT"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--branch", default="atendimento")
    parser.add_argument("--operator", default="human_operator")
    parser.add_argument("--total-conversations", required=True)
    parser.add_argument("--resolved-conversations", required=True)
    parser.add_argument("--unresolved-conversations", required=True)
    parser.add_argument("--without-resolved-status", required=True)
    parser.add_argument("--response-time-minutes", required=True)
    parser.add_argument("--notes", default="")
    parser.add_argument("--evidence", default="")
    args = parser.parse_args()

    total = safe_int(args.total_conversations)
    resolved = safe_int(args.resolved_conversations)
    unresolved = safe_int(args.unresolved_conversations)
    no_status = safe_int(args.without_resolved_status)
    response_time = safe_float(args.response_time_minutes)

    signal = compute_signal(total, resolved, unresolved, no_status, response_time)
    stamp = utc_stamp()

    OUT.mkdir(parents=True, exist_ok=True)

    base = "pilot_measurement_%s_%s" % (args.branch, stamp)
    json_path = OUT / (base + ".json")
    md_path = OUT / (base + ".md")

    record = {
        "status": "RECORDED",
        "recorded_utc": stamp,
        "branch": args.branch,
        "operator": args.operator,
        "total_conversations": total,
        "resolved_conversations": resolved,
        "unresolved_conversations": unresolved,
        "conversations_without_resolved_status": no_status,
        "response_time_minutes": response_time,
        "pilot_signal": signal,
        "notes": args.notes,
        "evidence": args.evidence,
        "promotion_effect": "BLOCKED_UNTIL_HUMAN_DECISION",
    }

    json_path.write_text(json.dumps(record, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Pilot Measurement",
        "",
        "- status: RECORDED",
        "- recorded_utc: %s" % stamp,
        "- branch: %s" % args.branch,
        "- operator: %s" % args.operator,
        "- total_conversations: %s" % total,
        "- resolved_conversations: %s" % resolved,
        "- unresolved_conversations: %s" % unresolved,
        "- conversations_without_resolved_status: %s" % no_status,
        "- response_time_minutes: %s" % response_time,
        "- pilot_signal: %s" % signal,
        "- promotion_effect: BLOCKED_UNTIL_HUMAN_DECISION",
        "",
        "## Notes",
        "",
        args.notes or "- none",
        "",
        "## Evidence",
        "",
        args.evidence or "- none",
        "",
    ]

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print("PILOT_MEASUREMENT_RECORDED")
    print("measurement:", rel(md_path))
    print("trace:", rel(json_path))
    print("pilot_signal:", signal)
    print("promotion_effect: BLOCKED_UNTIL_HUMAN_DECISION")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "05_outputs" / "real_tests" / "pilot_measurements"
REPORTS = ROOT / "05_outputs" / "reports"


def rel(path):
    return str(path.relative_to(ROOT))


def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def safe_name(value):
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    return value.strip("_") or "real_pilot_measurement"


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames or []


def lower(row, key):
    return str(row.get(key, "") or "").strip().lower()


def as_float(value):
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def is_resolved(row):
    return lower(row, "resolved_status") == "resolved" or lower(row, "status") == "resolved"


def is_unresolved(row):
    values = {lower(row, "resolved_status"), lower(row, "status")}
    return bool(values & {"unresolved", "open", "waiting", "waiting_confirmation"})


def is_unknown(row):
    values = {lower(row, "resolved_status"), lower(row, "status")}
    return bool(values & {"", "unknown", "no_status"})


def build_contact_groups(rows):
    groups = {}
    for row in rows:
        contact = str(row.get("contact_id_hash", "") or "").strip()
        if not contact:
            contact = "missing_contact_id"
        groups.setdefault(contact, []).append(row)
    return groups


def compute_measurement(rows):
    groups = build_contact_groups(rows)

    total_conversations = len(groups)
    resolved_conversations = 0
    unresolved_conversations = 0
    conversations_without_resolved_status = 0

    for contact, items in groups.items():
        if any(is_unknown(row) for row in items):
            conversations_without_resolved_status += 1
        elif any(is_resolved(row) for row in items):
            resolved_conversations += 1
        elif any(is_unresolved(row) for row in items):
            unresolved_conversations += 1
        else:
            conversations_without_resolved_status += 1

    response_times = []
    for row in rows:
        rt = as_float(row.get("response_time_minutes"))
        if rt is not None:
            response_times.append(rt)

    avg_response_time = None
    if response_times:
        avg_response_time = round(sum(response_times) / len(response_times), 2)

    unresolved_ratio = 0.0
    if total_conversations:
        unresolved_ratio = round(unresolved_conversations / total_conversations, 3)

    unknown_ratio = 0.0
    if total_conversations:
        unknown_ratio = round(conversations_without_resolved_status / total_conversations, 3)

    signal = "EXTEND_PILOT"
    if total_conversations >= 5 and unknown_ratio <= 0.2 and unresolved_ratio <= 0.35 and avg_response_time is not None:
        signal = "PILOT_SIGNAL_POSITIVE"
    if unknown_ratio > 0.25:
        signal = "NEEDS_STATUS_CLEANUP"
    if total_conversations < 5:
        signal = "INSUFFICIENT_SAMPLE"

    return {
        "measurement_unit": "contact_id_hash",
        "total_events": len(rows),
        "total_conversations": total_conversations,
        "resolved_conversations": resolved_conversations,
        "unresolved_conversations": unresolved_conversations,
        "conversations_without_resolved_status": conversations_without_resolved_status,
        "response_time_samples": len(response_times),
        "response_time_minutes": avg_response_time,
        "unresolved_ratio": unresolved_ratio,
        "unknown_status_ratio": unknown_ratio,
        "pilot_signal": signal,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--intake-report", default="05_outputs/reports/real_source_intake_report.json")
    parser.add_argument("--review-report", default="05_outputs/reports/real_human_review_report.json")
    parser.add_argument("--measurement-name", default="real_atendimento_pilot_measurement")
    args = parser.parse_args()

    intake_path = Path(args.intake_report)
    review_path = Path(args.review_report)

    if not intake_path.is_absolute():
        intake_path = ROOT / intake_path
    if not review_path.is_absolute():
        review_path = ROOT / review_path

    if not intake_path.exists():
        raise SystemExit("intake report not found: %s" % intake_path)
    if not review_path.exists():
        raise SystemExit("review report not found: %s" % review_path)

    intake = read_json(intake_path)
    review = read_json(review_path)

    if review.get("decision") != "APPROVED_FOR_PILOT":
        print("REAL_PILOT_MEASUREMENT_BLOCKED")
        print("decision:", review.get("decision"))
        print("canonical_effect: NONE")
        raise SystemExit(2)

    if review.get("review_scope") != "PILOT_MEASUREMENT_ONLY":
        print("REAL_PILOT_MEASUREMENT_BLOCKED")
        print("review_scope:", review.get("review_scope"))
        print("canonical_effect: NONE")
        raise SystemExit(3)

    source = intake.get("manifest", {}).get("source")
    if not source:
        raise SystemExit("source path missing in intake report")

    source_path = ROOT / source
    if not source_path.exists():
        raise SystemExit("source file not found: %s" % source_path)

    rows, columns = read_csv(source_path)
    measurement = compute_measurement(rows)

    generated = stamp()
    name = safe_name(args.measurement_name)
    base = "%s_%s" % (name, generated)

    OUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    result = {
        "status": "REAL_PILOT_MEASUREMENT",
        "generated_utc": generated,
        "measurement_name": name,
        "source": rel(source_path),
        "intake_report": rel(intake_path),
        "review_report": rel(review_path),
        "review_decision": review.get("decision"),
        "review_scope": review.get("review_scope"),
        "canonical_effect": "EVIDENCE_ONLY",
        "promotion_allowed": False,
        "branch_mutation_allowed": False,
        "measurement": measurement,
        "next_action": "Collect more real pilot measurements before any promotion decision.",
    }

    json_path = OUT / (base + ".json")
    md_path = OUT / (base + ".md")
    report_json = REPORTS / "real_pilot_measurement_report.json"
    report_md = REPORTS / "real_pilot_measurement_report.md"

    text_json = json.dumps(result, indent=2, ensure_ascii=False)
    json_path.write_text(text_json, encoding="utf-8")
    report_json.write_text(text_json, encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Real Pilot Measurement",
        "",
        "- status: REAL_PILOT_MEASUREMENT",
        "- generated_utc: %s" % generated,
        "- measurement_name: %s" % name,
        "- source: %s" % rel(source_path),
        "- review_decision: %s" % review.get("decision"),
        "- review_scope: %s" % review.get("review_scope"),
        "- canonical_effect: EVIDENCE_ONLY",
        "- promotion_allowed: false",
        "- branch_mutation_allowed: false",
        "",
        "## Measurement",
        "",
    ]

    for key, value in measurement.items():
        lines.append("- %s: %s" % (key, value))

    lines.extend([
        "",
        "## Next action",
        "",
        "- Collect more real pilot measurements before any promotion decision.",
        "",
    ])

    text_md = "\n".join(lines)
    md_path.write_text(text_md, encoding="utf-8")
    report_md.write_text(text_md, encoding="utf-8")

    print("REAL_PILOT_MEASUREMENT_CREATED")
    print("measurement:", rel(md_path))
    print("total_conversations:", measurement["total_conversations"])
    print("resolved_conversations:", measurement["resolved_conversations"])
    print("unresolved_conversations:", measurement["unresolved_conversations"])
    print("conversations_without_resolved_status:", measurement["conversations_without_resolved_status"])
    print("response_time_minutes:", measurement["response_time_minutes"])
    print("pilot_signal:", measurement["pilot_signal"])
    print("promotion_allowed: false")
    print("canonical_effect: EVIDENCE_ONLY")


if __name__ == "__main__":
    main()

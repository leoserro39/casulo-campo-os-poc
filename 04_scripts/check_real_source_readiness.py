#!/usr/bin/env python3
import argparse
import csv
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "05_outputs" / "real_tests" / "source_readiness"
REPORTS = ROOT / "05_outputs" / "reports"

REQUIRED_COLUMNS = [
    "record_id",
    "created_at",
    "channel",
    "contact_id_hash",
    "direction",
    "message_or_event_type",
    "status",
    "response_time_minutes",
    "resolved_status",
    "notes",
]

PHONE_RE = re.compile(r"(\+?\d[\d\s().-]{7,}\d)")
EMAIL_RE = re.compile(r"[\w\.-]+@[\w\.-]+\.\w+")


def rel(path):
    return str(path.relative_to(ROOT))


def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames or []
    return columns, rows


def pii_hits(rows):
    hits = []
    for idx, row in enumerate(rows, start=1):
        for key, value in row.items():
            text = value or ""
            if EMAIL_RE.search(text):
                hits.append({"row": idx, "column": key, "type": "email"})
            elif PHONE_RE.search(text):
                hits.append({"row": idx, "column": key, "type": "phone_like"})
    return hits


def empty_ratio(rows):
    total = 0
    empty = 0
    for row in rows:
        for value in row.values():
            total += 1
            if value is None or str(value).strip() == "":
                empty += 1
    if total == 0:
        return 1.0
    return round(empty / total, 3)


def decide(row_count, missing_required, pii, empty):
    if row_count == 0:
        return "BLOCKED"
    if missing_required:
        return "NEEDS_MAPPING"
    if pii:
        return "NEEDS_SANITIZATION"
    if empty > 0.35:
        return "NEEDS_REVIEW"
    return "READY_FOR_INTAKE"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--source-name", default="real_source")
    args = parser.parse_args()

    source_path = Path(args.source)
    if not source_path.is_absolute():
        source_path = ROOT / source_path

    if not source_path.exists():
        raise SystemExit("source not found: %s" % source_path)

    columns, rows = read_csv(source_path)
    missing = [c for c in REQUIRED_COLUMNS if c not in columns]
    pii = pii_hits(rows)
    empty = empty_ratio(rows)
    gate = decide(len(rows), missing, pii, empty)

    OUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    stamp = utc_stamp()
    base = "source_readiness_%s_%s" % (args.source_name, stamp)

    json_path = OUT / (base + ".json")
    md_path = OUT / (base + ".md")
    report_json = REPORTS / "real_source_readiness_report.json"
    report_md = REPORTS / "real_source_readiness_report.md"

    result = {
        "status": "REAL_SOURCE_READINESS_CHECK",
        "checked_utc": stamp,
        "source": rel(source_path),
        "source_name": args.source_name,
        "row_count": len(rows),
        "columns": columns,
        "required_columns": REQUIRED_COLUMNS,
        "missing_required_columns": missing,
        "empty_ratio": empty,
        "pii_hit_count": len(pii),
        "pii_hits_sample": pii[:10],
        "gate": gate,
        "canonical_effect": "NONE",
        "next_action": {
            "READY_FOR_INTAKE": "Run controlled source intake.",
            "NEEDS_MAPPING": "Map missing source columns before intake.",
            "NEEDS_SANITIZATION": "Sanitize PII before intake.",
            "NEEDS_REVIEW": "Review empty fields and source quality before intake.",
            "BLOCKED": "Do not ingest this source.",
        }.get(gate, "Review source manually."),
    }

    text_json = json.dumps(result, indent=2, ensure_ascii=False)
    json_path.write_text(text_json, encoding="utf-8")
    report_json.write_text(text_json, encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Real Source Readiness",
        "",
        "- status: REAL_SOURCE_READINESS_CHECK",
        "- checked_utc: %s" % stamp,
        "- source: %s" % rel(source_path),
        "- source_name: %s" % args.source_name,
        "- row_count: %s" % len(rows),
        "- missing_required_columns: %s" % (", ".join(missing) if missing else "none"),
        "- empty_ratio: %s" % empty,
        "- pii_hit_count: %s" % len(pii),
        "- gate: %s" % gate,
        "- canonical_effect: NONE",
        "",
        "## Next action",
        "",
        "- %s" % result["next_action"],
        "",
        "## Columns",
        "",
    ]
    lines.extend(["- " + c for c in columns])
    lines.append("")

    md_text = "\n".join(lines)
    md_path.write_text(md_text, encoding="utf-8")
    report_md.write_text(md_text, encoding="utf-8")

    print("REAL_SOURCE_READINESS_CHECK_CREATED")
    print("gate:", gate)
    print("source:", rel(source_path))
    print("rows:", len(rows))
    print("missing_required_columns:", len(missing))
    print("pii_hit_count:", len(pii))
    print("report:", rel(report_md))
    print("trace:", rel(report_json))
    print("canonical_effect: NONE")


if __name__ == "__main__":
    main()

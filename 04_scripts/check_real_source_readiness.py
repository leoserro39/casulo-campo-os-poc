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

SAFE_HASH_COLUMNS = {"contact_id_hash"}
SAFE_VALUE_PREFIXES = ("contact_hash_",)

PII_PATTERNS = {
    "email": re.compile(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}"),
    "phone_br": re.compile(r"(?<!\w)(?:\+?55\s*)?(?:\(?\d{2}\)?\s*)?9?\d{4}[-\s]?\d{4}(?!\w)"),
    "cpf_like": re.compile(r"(?<!\w)\d{3}\.?\d{3}\.?\d{3}-?\d{2}(?!\w)"),
}

ISO_TS = re.compile(r"^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$")


def rel(path):
    return str(path.relative_to(ROOT))


def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def safe_name(value):
    value = str(value or "").strip().lower()
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    return value.strip("_") or "real_source"


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames or []


def is_safe_value(column, value):
    text = str(value or "").strip()

    if not text:
        return True

    if column in SAFE_HASH_COLUMNS:
        return True

    if text.startswith(SAFE_VALUE_PREFIXES):
        return True

    if ISO_TS.match(text):
        return True

    return False


def find_pii(rows):
    hits = []

    for idx, row in enumerate(rows, start=1):
        for column, raw_value in row.items():
            value = str(raw_value or "").strip()

            if is_safe_value(column, value):
                continue

            for kind, pattern in PII_PATTERNS.items():
                if pattern.search(value):
                    hits.append({
                        "row": idx,
                        "column": column,
                        "kind": kind,
                    })

    return hits


def empty_ratio(rows, columns):
    if not rows or not columns:
        return 0.0

    total = len(rows) * len(columns)
    empty = 0

    for row in rows:
        for column in columns:
            if str(row.get(column, "") or "").strip() == "":
                empty += 1

    return round(empty / total, 3) if total else 0.0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--source-name", required=True)
    args = parser.parse_args()

    source = Path(args.source)
    if not source.is_absolute():
        source = ROOT / source

    if not source.exists():
        raise SystemExit("source not found: %s" % source)

    OUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    rows, columns = read_csv(source)
    missing = [column for column in REQUIRED_COLUMNS if column not in columns]
    pii_hits = find_pii(rows)
    ratio = empty_ratio(rows, columns)

    gate = "READY_FOR_INTAKE"
    next_action = "Run evidence-only intake gate."

    if missing:
        gate = "NEEDS_SCHEMA_FIX"
        next_action = "Fix required columns before intake."
    elif pii_hits:
        gate = "NEEDS_SANITIZATION"
        next_action = "Sanitize PII before intake."

    generated = stamp()
    name = safe_name(args.source_name)
    base = "source_readiness_%s_%s" % (name, generated)

    result = {
        "status": "REAL_SOURCE_READINESS_CHECK",
        "checked_utc": generated,
        "source": rel(source),
        "source_name": args.source_name,
        "row_count": len(rows),
        "columns": columns,
        "missing_required_columns": missing,
        "empty_ratio": ratio,
        "pii_hit_count": len(pii_hits),
        "pii_hits": pii_hits,
        "gate": gate,
        "canonical_effect": "NONE",
        "next_action": next_action,
    }

    json_path = OUT / (base + ".json")
    md_path = OUT / (base + ".md")
    report_json = REPORTS / "real_source_readiness_report.json"
    report_md = REPORTS / "real_source_readiness_report.md"

    text_json = json.dumps(result, indent=2, ensure_ascii=False)
    json_path.write_text(text_json, encoding="utf-8")
    report_json.write_text(text_json, encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Real Source Readiness",
        "",
        "- status: REAL_SOURCE_READINESS_CHECK",
        "- checked_utc: %s" % generated,
        "- source: %s" % rel(source),
        "- source_name: %s" % args.source_name,
        "- row_count: %s" % len(rows),
        "- missing_required_columns: %s" % (", ".join(missing) if missing else "none"),
        "- empty_ratio: %s" % ratio,
        "- pii_hit_count: %s" % len(pii_hits),
        "- gate: %s" % gate,
        "- canonical_effect: NONE",
        "",
        "## Next action",
        "",
        "- %s" % next_action,
        "",
        "## Columns",
        "",
    ]

    lines.extend(["- " + column for column in columns])

    if pii_hits:
        lines.extend(["", "## PII hits", ""])
        for hit in pii_hits:
            lines.append("- row=%s column=%s kind=%s" % (
                hit["row"],
                hit["column"],
                hit["kind"],
            ))

    lines.append("")

    text_md = "\n".join(lines)
    md_path.write_text(text_md, encoding="utf-8")
    report_md.write_text(text_md, encoding="utf-8")

    print("REAL_SOURCE_READINESS_CHECK_CREATED")
    print("gate:", gate)
    print("source:", rel(source))
    print("rows:", len(rows))
    print("missing_required_columns:", len(missing))
    print("pii_hit_count:", len(pii_hits))
    print("report:", rel(report_md))
    print("trace:", rel(report_json))
    print("canonical_effect: NONE")


if __name__ == "__main__":
    main()

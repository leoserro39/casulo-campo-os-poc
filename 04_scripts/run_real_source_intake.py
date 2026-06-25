#!/usr/bin/env python3
import argparse
import csv
import json
import re
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
INTAKE = ROOT / "05_outputs" / "real_tests" / "intake"
MANIFESTS = INTAKE / "manifests"
TRUST = INTAKE / "trust_reports"
DELTAS = INTAKE / "deltas"
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


def rel(path):
    return str(path.relative_to(ROOT))


def stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def safe_name(value):
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9_]+", "_", value)
    return value.strip("_") or "real_source"


def run(cmd):
    return subprocess.check_output(cmd, cwd=str(ROOT), text=True).strip()


def read_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)
        columns = reader.fieldnames or []
    return columns, rows


def as_float(value):
    text = str(value or "").strip()
    if not text:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def lower(row, key):
    return str(row.get(key, "") or "").strip().lower()


def compute_quality(rows):
    total = len(rows)
    total_cells = 0
    empty_cells = 0
    response_times = []
    contradictions = []
    unknown_status_rows = 0

    for idx, row in enumerate(rows, start=1):
        for value in row.values():
            total_cells += 1
            if value is None or str(value).strip() == "":
                empty_cells += 1

        rt = as_float(row.get("response_time_minutes"))
        if rt is not None:
            response_times.append(rt)
            if rt < 0:
                contradictions.append({
                    "row": idx,
                    "type": "negative_response_time",
                    "record_id": row.get("record_id"),
                })

        status = lower(row, "status")
        resolved_status = lower(row, "resolved_status")

        if status == "resolved" and resolved_status in {"unresolved", "unknown", "open"}:
            contradictions.append({
                "row": idx,
                "type": "status_resolved_but_resolved_status_not_resolved",
                "record_id": row.get("record_id"),
            })

        if resolved_status == "resolved" and status in {"open", "waiting", "waiting_confirmation"}:
            contradictions.append({
                "row": idx,
                "type": "resolved_status_resolved_but_status_open",
                "record_id": row.get("record_id"),
            })

        if resolved_status in {"", "unknown", "no_status"} or status in {"", "unknown", "no_status"}:
            unknown_status_rows += 1

    empty_ratio = round(empty_cells / total_cells, 3) if total_cells else 1.0

    contacts = sorted(set(str(r.get("contact_id_hash", "")).strip() for r in rows if str(r.get("contact_id_hash", "")).strip()))
    resolved_rows = sum(1 for r in rows if lower(r, "resolved_status") == "resolved" or lower(r, "status") == "resolved")
    unresolved_rows = sum(1 for r in rows if lower(r, "resolved_status") in {"unresolved", "open"} or lower(r, "status") in {"open", "waiting_confirmation"})
    inbound_rows = sum(1 for r in rows if lower(r, "direction") == "inbound")
    outbound_rows = sum(1 for r in rows if lower(r, "direction") == "outbound")

    avg_response = None
    if response_times:
        avg_response = round(sum(response_times) / len(response_times), 2)

    return {
        "row_count": total,
        "contact_count": len(contacts),
        "inbound_rows": inbound_rows,
        "outbound_rows": outbound_rows,
        "resolved_rows": resolved_rows,
        "unresolved_rows": unresolved_rows,
        "unknown_status_rows": unknown_status_rows,
        "response_time_count": len(response_times),
        "avg_response_time_minutes": avg_response,
        "empty_ratio": empty_ratio,
        "contradictions_count": len(contradictions),
        "contradictions_sample": contradictions[:10],
    }


def trust_score(readiness, quality):
    score = 1.0
    score -= min(quality["empty_ratio"], 0.5) * 0.5
    score -= min(quality["contradictions_count"] * 0.08, 0.4)
    score -= min(quality["unknown_status_rows"] * 0.03, 0.25)
    if readiness.get("gate") != "READY_FOR_INTAKE":
        score -= 0.5
    return round(max(score, 0.0), 3)


def hallucination_risk(score, quality):
    if score < 0.55:
        return "HIGH"
    if score < 0.78:
        return "MEDIUM"
    if quality["contradictions_count"] > 0 or quality["unknown_status_rows"] > 0:
        return "MEDIUM"
    return "LOW"


def intake_gate(readiness, quality, risk):
    if readiness.get("gate") != "READY_FOR_INTAKE":
        return "BLOCKED_BY_READINESS"
    if quality["row_count"] == 0:
        return "BLOCKED_EMPTY_SOURCE"
    if risk == "HIGH":
        return "ALLOW_EVIDENCE_ONLY_WITH_STRONG_REVIEW"
    if quality["contradictions_count"] > 0 or quality["unknown_status_rows"] > 0:
        return "ALLOW_EVIDENCE_ONLY_WITH_HUMAN_REVIEW"
    return "ALLOW_EVIDENCE_ONLY"


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

    source_name = safe_name(args.source_name)

    run([
        "python",
        "04_scripts/check_real_source_readiness.py",
        "--source",
        rel(source),
        "--source-name",
        source_name,
    ])

    readiness_path = REPORTS / "real_source_readiness_report.json"
    readiness = read_json(readiness_path)

    if readiness.get("gate") != "READY_FOR_INTAKE":
        print("REAL_SOURCE_INTAKE_BLOCKED")
        print("readiness_gate:", readiness.get("gate"))
        print("canonical_effect: NONE")
        raise SystemExit(2)

    columns, rows = read_csv(source)
    missing = [c for c in REQUIRED_COLUMNS if c not in columns]
    if missing:
        print("REAL_SOURCE_INTAKE_BLOCKED")
        print("missing_required_columns:", ",".join(missing))
        print("canonical_effect: NONE")
        raise SystemExit(3)

    quality = compute_quality(rows)
    score = trust_score(readiness, quality)
    risk = hallucination_risk(score, quality)
    gate = intake_gate(readiness, quality, risk)

    generated = stamp()
    base = "real_source_intake_%s_%s" % (source_name, generated)

    for folder in [MANIFESTS, TRUST, DELTAS, REPORTS]:
        folder.mkdir(parents=True, exist_ok=True)

    manifest = {
        "status": "REAL_SOURCE_INTAKE_MANIFEST",
        "generated_utc": generated,
        "source": rel(source),
        "source_name": source_name,
        "columns": columns,
        "row_count": len(rows),
        "readiness_gate": readiness.get("gate"),
        "canonical_effect": "EVIDENCE_ONLY",
    }

    trust = {
        "status": "REAL_SOURCE_TRUST_REPORT",
        "generated_utc": generated,
        "source": rel(source),
        "source_name": source_name,
        "trust_score": score,
        "hallucination_risk": risk,
        "quality": quality,
        "readiness": {
            "gate": readiness.get("gate"),
            "pii_hit_count": readiness.get("pii_hit_count"),
            "missing_required_columns": readiness.get("missing_required_columns"),
        },
        "canonical_effect": "EVIDENCE_ONLY",
    }

    delta = {
        "status": "REAL_SOURCE_INTAKE_DELTA",
        "generated_utc": generated,
        "source": rel(source),
        "source_name": source_name,
        "gate": gate,
        "canonical_effect": "EVIDENCE_ONLY",
        "next_action": "Use this evidence for a gated mesh delta/proposal. Do not mutate branch state automatically.",
        "summary": {
            "row_count": quality["row_count"],
            "contact_count": quality["contact_count"],
            "resolved_rows": quality["resolved_rows"],
            "unresolved_rows": quality["unresolved_rows"],
            "unknown_status_rows": quality["unknown_status_rows"],
            "avg_response_time_minutes": quality["avg_response_time_minutes"],
            "trust_score": score,
            "hallucination_risk": risk,
        },
    }

    manifest_json = MANIFESTS / (base + "_manifest.json")
    trust_json = TRUST / (base + "_trust_report.json")
    delta_json = DELTAS / (base + "_delta.json")
    report_json = REPORTS / "real_source_intake_report.json"
    report_md = REPORTS / "real_source_intake_report.md"

    manifest_json.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    trust_json.write_text(json.dumps(trust, indent=2, ensure_ascii=False), encoding="utf-8")
    delta_json.write_text(json.dumps(delta, indent=2, ensure_ascii=False), encoding="utf-8")
    report_json.write_text(json.dumps({
        "manifest": manifest,
        "trust": trust,
        "delta": delta,
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Real Source Intake Report",
        "",
        "- status: REAL_SOURCE_INTAKE",
        "- generated_utc: %s" % generated,
        "- source: %s" % rel(source),
        "- source_name: %s" % source_name,
        "- readiness_gate: %s" % readiness.get("gate"),
        "- intake_gate: %s" % gate,
        "- canonical_effect: EVIDENCE_ONLY",
        "- trust_score: %s" % score,
        "- hallucination_risk: %s" % risk,
        "",
        "## Quality",
        "",
    ]

    for key, value in quality.items():
        if key != "contradictions_sample":
            lines.append("- %s: %s" % (key, value))

    lines.extend([
        "",
        "## Artifacts",
        "",
        "- manifest: %s" % rel(manifest_json),
        "- trust_report: %s" % rel(trust_json),
        "- intake_delta: %s" % rel(delta_json),
        "",
        "## Next action",
        "",
        "- Use this evidence for a gated mesh delta/proposal. Do not mutate branch state automatically.",
        "",
    ])

    report_md.write_text("\n".join(lines), encoding="utf-8")

    print("REAL_SOURCE_INTAKE_CREATED")
    print("source:", rel(source))
    print("rows:", quality["row_count"])
    print("contacts:", quality["contact_count"])
    print("readiness_gate:", readiness.get("gate"))
    print("intake_gate:", gate)
    print("trust_score:", score)
    print("hallucination_risk:", risk)
    print("report:", rel(report_md))
    print("canonical_effect: EVIDENCE_ONLY")


if __name__ == "__main__":
    main()

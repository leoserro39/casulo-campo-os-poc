#!/usr/bin/env python3
import argparse
import csv
import hashlib
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

OUTPUT_COLUMNS = [
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


def value(row, column, default=""):
    if not column:
        return default
    return str(row.get(column, default) or "").strip()


def hash_contact(raw):
    salt = os.environ.get("CASULO_SANITIZE_SALT", "casulo_local_salt_change_me")
    text = (salt + "::" + str(raw or "").strip()).encode("utf-8")
    return "contact_hash_" + hashlib.sha256(text).hexdigest()[:16]


def normalize_direction(text):
    t = str(text or "").strip().lower()
    if t in {"in", "inbound", "entrada", "recebida", "cliente"}:
        return "inbound"
    if t in {"out", "outbound", "saida", "enviada", "atendente"}:
        return "outbound"
    return t or "unknown"


def normalize_resolved(text):
    t = str(text or "").strip().lower()
    if t in {"resolved", "resolvido", "fechado", "closed", "done", "sim", "yes"}:
        return "resolved"
    if t in {"unresolved", "nao resolvido", "não resolvido", "aberto", "open", "no", "nao", "não"}:
        return "unresolved"
    if t in {"waiting", "aguardando", "waiting_confirmation"}:
        return "waiting_confirmation"
    return t or "unknown"


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--output", default="00_inbox/sources/real_atendimento_test/atendimento_real_sanitized.csv")

    parser.add_argument("--record-id-column", default="")
    parser.add_argument("--created-at-column", required=True)
    parser.add_argument("--contact-column", required=True)
    parser.add_argument("--direction-column", default="")
    parser.add_argument("--event-type-column", default="")
    parser.add_argument("--status-column", default="")
    parser.add_argument("--response-time-column", default="")
    parser.add_argument("--resolved-column", default="")
    parser.add_argument("--notes-column", default="")
    parser.add_argument("--channel", default="whatsapp")

    args = parser.parse_args()

    source = Path(args.source)
    output = Path(args.output)

    if not source.is_absolute():
        source = ROOT / source
    if not output.is_absolute():
        output = ROOT / output

    if not source.exists():
        raise SystemExit("source not found: %s" % source)

    output.parent.mkdir(parents=True, exist_ok=True)

    with source.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    sanitized = []
    for idx, row in enumerate(rows, start=1):
        record_id = value(row, args.record_id_column) or "r%04d" % idx
        contact_raw = value(row, args.contact_column)

        sanitized.append({
            "record_id": record_id,
            "created_at": value(row, args.created_at_column),
            "channel": args.channel,
            "contact_id_hash": hash_contact(contact_raw),
            "direction": normalize_direction(value(row, args.direction_column)),
            "message_or_event_type": value(row, args.event_type_column, "event") or "event",
            "status": value(row, args.status_column, "unknown") or "unknown",
            "response_time_minutes": value(row, args.response_time_column),
            "resolved_status": normalize_resolved(value(row, args.resolved_column)),
            "notes": "sanitized",
        })

    with output.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(sanitized)

    print("SANITIZED_REAL_ATENDIMENTO_SOURCE_CREATED")
    print("source:", source.relative_to(ROOT))
    print("output:", output.relative_to(ROOT))
    print("rows:", len(sanitized))
    print("canonical_effect: NONE")


if __name__ == "__main__":
    main()

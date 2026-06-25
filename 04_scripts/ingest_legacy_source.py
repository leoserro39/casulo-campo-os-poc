#!/usr/bin/env python3
import argparse
import csv
import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "05_outputs" / "source_intake"

REQUIRED_FIELDS = [
    "message_id",
    "created_at",
    "customer_id",
    "channel",
    "direction",
    "message",
    "status",
    "response_time_minutes",
]

CANONICAL_MAPPING = {
    "message_id": "evidence.message_id",
    "created_at": "evidence.created_at",
    "customer_id": "atendimento.customer_ref",
    "channel": "atendimento.channel",
    "direction": "atendimento.message_direction",
    "message": "evidence.raw_message",
    "status": "atendimento.conversation_status",
    "response_time_minutes": "atendimento.response_time_minutes",
}


def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def sha256_file(path):
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(65536), b""):
            h.update(block)
    return h.hexdigest()


def read_csv(path):
    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        return list(reader), reader.fieldnames or []


def pct(value):
    return round(value, 3)


def assess(rows, fields):
    field_set = set(fields)
    required_present = [f for f in REQUIRED_FIELDS if f in field_set]
    required_missing = [f for f in REQUIRED_FIELDS if f not in field_set]

    total_cells = max(1, len(rows) * max(1, len(REQUIRED_FIELDS)))
    empty_cells = 0
    bad_response_time = 0
    contradictions = []

    for row in rows:
        for f in REQUIRED_FIELDS:
            if not str(row.get(f, "")).strip():
                empty_cells += 1

        rt = str(row.get("response_time_minutes", "")).strip()
        status = str(row.get("status", "")).strip().lower()
        message = str(row.get("message", "")).strip().lower()

        if rt:
            try:
                if float(rt) < 0:
                    bad_response_time += 1
            except ValueError:
                bad_response_time += 1

        if status == "resolved" and not rt:
            contradictions.append({
                "message_id": row.get("message_id"),
                "issue": "resolved_without_response_time",
            })

        if "sem resposta" in message and status == "resolved":
            contradictions.append({
                "message_id": row.get("message_id"),
                "issue": "message_claims_no_response_but_status_resolved",
            })

    support_ratio = len(required_present) / max(1, len(REQUIRED_FIELDS))
    missing_ratio = len(required_missing) / max(1, len(REQUIRED_FIELDS))
    empty_ratio = empty_cells / total_cells
    contradiction_count = len(contradictions) + bad_response_time

    trust_score = 1.0
    trust_score -= missing_ratio * 0.35
    trust_score -= empty_ratio * 0.25
    trust_score -= min(0.30, contradiction_count * 0.08)
    trust_score = max(0.0, min(1.0, trust_score))

    evidence_strength = trust_score * support_ratio * max(0.0, 1.0 - min(0.50, contradiction_count * 0.10))

    if trust_score >= 0.78 and contradiction_count == 0:
        risk = "LOW"
        gate = "ALLOW_INTAKE_DELTA"
    elif trust_score >= 0.55:
        risk = "MEDIUM"
        gate = "ALLOW_WITH_HUMAN_REVIEW"
    elif trust_score >= 0.35:
        risk = "HIGH"
        gate = "REQUIRE_SOURCE_REVIEW"
    else:
        risk = "BLOCKED"
        gate = "BLOCK_CANONICAL_MAPPING"

    return {
        "required_present": required_present,
        "required_missing": required_missing,
        "row_count": len(rows),
        "empty_cells": empty_cells,
        "empty_ratio": pct(empty_ratio),
        "support_ratio": pct(support_ratio),
        "missing_ratio": pct(missing_ratio),
        "contradiction_count": contradiction_count,
        "contradictions": contradictions,
        "trust_score": pct(trust_score),
        "evidence_strength": pct(evidence_strength),
        "hallucination_risk": risk,
        "gate": gate,
    }


def write_outputs(source_path, source_name, owner, target_branch):
    source_path = Path(source_path)
    rows, fields = read_csv(source_path)
    stamp = utc_stamp()
    source_id = "%s_%s" % (source_name, stamp)

    raw_dir = OUT / "raw_snapshots"
    manifest_dir = OUT / "manifests"
    mapping_dir = OUT / "mappings"
    trust_dir = OUT / "trust_reports"
    delta_dir = OUT / "deltas"

    for d in [raw_dir, manifest_dir, mapping_dir, trust_dir, delta_dir]:
        d.mkdir(parents=True, exist_ok=True)

    snapshot_path = raw_dir / ("%s.csv" % source_id)
    shutil.copy2(source_path, snapshot_path)

    assessment = assess(rows, fields)

    manifest = {
        "source_id": source_id,
        "source_name": source_name,
        "source_type": "csv_export",
        "owner": owner,
        "target_branch": target_branch,
        "created_utc": stamp,
        "source_path": str(source_path),
        "raw_snapshot": str(snapshot_path.relative_to(ROOT)),
        "sha256": sha256_file(snapshot_path),
        "fields": fields,
        "row_count": len(rows),
        "trust_score": assessment["trust_score"],
        "hallucination_risk": assessment["hallucination_risk"],
        "gate": assessment["gate"],
    }

    mapping = {
        "source_id": source_id,
        "target_branch": target_branch,
        "mapping": CANONICAL_MAPPING,
        "mapping_status": "PROPOSED",
        "requires_human_review": assessment["gate"] != "ALLOW_INTAKE_DELTA",
    }

    manifest_path = manifest_dir / ("%s_manifest.json" % source_id)
    mapping_path = mapping_dir / ("%s_mapping.json" % source_id)
    trust_path = trust_dir / ("%s_trust_report.md" % source_id)
    delta_path = delta_dir / ("%s_intake_delta.md" % source_id)

    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
    mapping_path.write_text(json.dumps(mapping, indent=2, ensure_ascii=False), encoding="utf-8")

    trust_lines = [
        "# Source Trust Report",
        "",
        "- source_id: %s" % source_id,
        "- source_name: %s" % source_name,
        "- target_branch: %s" % target_branch,
        "- rows: %s" % assessment["row_count"],
        "- support_ratio: %s" % assessment["support_ratio"],
        "- missing_ratio: %s" % assessment["missing_ratio"],
        "- empty_ratio: %s" % assessment["empty_ratio"],
        "- contradiction_count: %s" % assessment["contradiction_count"],
        "- trust_score: %s" % assessment["trust_score"],
        "- evidence_strength: %s" % assessment["evidence_strength"],
        "- hallucination_risk: %s" % assessment["hallucination_risk"],
        "- gate: %s" % assessment["gate"],
        "",
        "## Required missing fields",
    ]
    trust_lines.extend(["- " + x for x in assessment["required_missing"]] or ["- none"])
    trust_lines.extend(["", "## Contradictions"])
    trust_lines.extend(["- %s: %s" % (c["message_id"], c["issue"]) for c in assessment["contradictions"]] or ["- none"])
    trust_path.write_text("\n".join(trust_lines) + "\n", encoding="utf-8")

    delta_lines = [
        "# Legacy Intake Delta",
        "",
        "- source_id: %s" % source_id,
        "- target_branch: %s" % target_branch,
        "- status: PROPOSED_INTAKE_DELTA",
        "- hallucination_risk: %s" % assessment["hallucination_risk"],
        "- gate: %s" % assessment["gate"],
        "",
        "## Supported dimensions",
        "- whatsapp",
        "- cliente",
        "- resposta",
        "- tempo",
        "- resolvido",
        "- evidencia",
        "- metrica",
        "",
        "## Canonical effect",
        "- No canonical branch state was changed.",
        "- This intake only proposes evidence and mapping.",
        "- Human review is required before promotion to long-term state.",
        "",
        "## Artifacts",
        "- manifest: %s" % manifest_path.relative_to(ROOT),
        "- mapping: %s" % mapping_path.relative_to(ROOT),
        "- trust_report: %s" % trust_path.relative_to(ROOT),
        "- raw_snapshot: %s" % snapshot_path.relative_to(ROOT),
        "",
    ]
    delta_path.write_text("\n".join(delta_lines), encoding="utf-8")

    print("LEGACY_SOURCE_INGESTED")
    print("source_id:", source_id)
    print("manifest:", manifest_path.relative_to(ROOT))
    print("mapping:", mapping_path.relative_to(ROOT))
    print("trust_report:", trust_path.relative_to(ROOT))
    print("intake_delta:", delta_path.relative_to(ROOT))
    print("trust_score:", assessment["trust_score"])
    print("hallucination_risk:", assessment["hallucination_risk"])
    print("gate:", assessment["gate"])


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True)
    parser.add_argument("--source-name", default="legacy_whatsapp_export")
    parser.add_argument("--owner", default="unknown")
    parser.add_argument("--target-branch", default="atendimento")
    args = parser.parse_args()

    write_outputs(args.source, args.source_name, args.owner, args.target_branch)


if __name__ == "__main__":
    main()

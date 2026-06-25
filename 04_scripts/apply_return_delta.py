#!/usr/bin/env python3
import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RETURN_DELTAS = ROOT / "05_outputs" / "return_deltas"
APPLIED = ROOT / "05_outputs" / "applied_return_deltas"


def utc_stamp():
    return datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def rel(path):
    return str(path.relative_to(ROOT))


def slug(value):
    text = re.sub(r"[^a-zA-Z0-9]+", "_", value or "").strip("_").lower()
    return text[:90] or "return_delta"


def latest_return_delta():
    files = sorted(RETURN_DELTAS.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        raise SystemExit("no return delta json found")
    return files[0]


def apply_delta(delta_path, operator, confirm):
    if confirm != "APPLY_CANONICAL_DELTA":
        raise SystemExit("missing confirmation. Use --confirm APPLY_CANONICAL_DELTA")

    delta_path = Path(delta_path)
    if not delta_path.is_absolute():
        delta_path = ROOT / delta_path
    if not delta_path.exists():
        raise SystemExit("return delta not found: %s" % delta_path)

    delta = read_json(delta_path)

    if delta.get("status") != "RETURN_DELTA_PROPOSED":
        raise SystemExit("return delta is not RETURN_DELTA_PROPOSED")
    if not delta.get("requires_final_apply"):
        raise SystemExit("return delta is not eligible for final apply")

    target_branch = delta.get("target_branch") or "unknown"
    if target_branch != "atendimento":
        raise SystemExit("this POC apply script only supports atendimento")

    stamp = utc_stamp()
    base = "applied_return_delta_%s_%s" % (slug(delta.get("question", "return_delta")), stamp)

    domain_delta_dir = ROOT / "01_domains" / target_branch / "deltas"
    domain_delta_dir.mkdir(parents=True, exist_ok=True)
    APPLIED.mkdir(parents=True, exist_ok=True)

    applied_domain_path = domain_delta_dir / (base + ".md")
    applied_trace_path = APPLIED / (base + ".json")
    applied_report_path = APPLIED / (base + ".md")

    changes = delta.get("proposed_changes", [])

    applied = {
        "status": "APPLIED",
        "applied_utc": stamp,
        "operator": operator,
        "source_return_delta": rel(delta_path),
        "target_branch": target_branch,
        "canonical_effect": "APPEND_DOMAIN_DELTA_RECORD",
        "applied_domain_delta": rel(applied_domain_path),
        "source_review": delta.get("source_review"),
        "source_proposal": delta.get("source_proposal"),
        "question": delta.get("question"),
        "proposed_changes": changes,
        "mesh_delta": delta.get("mesh_delta", {}),
        "safety_note": "This apply operation appended a domain delta record only. It did not overwrite domain state."
    }

    lines = [
        "# Applied Return Delta - Atendimento",
        "",
        "- status: APPLIED",
        "- applied_utc: %s" % stamp,
        "- operator: %s" % operator,
        "- source_return_delta: %s" % rel(delta_path),
        "- canonical_effect: APPEND_DOMAIN_DELTA_RECORD",
        "",
        "## Changes approved for controlled pilot",
        "",
    ]
    lines.extend(["- " + x for x in changes])
    lines.extend([
        "",
        "## Measurement requirement",
        "",
        "- Track response_time_minutes.",
        "- Track unresolved conversations.",
        "- Track conversations without clear resolved status.",
        "- Review after 7 days before promoting to long-term branch state.",
        "",
        "## Safety",
        "",
        "- Domain state was not overwritten.",
        "- This is a controlled pilot delta record.",
        "",
    ])

    applied_domain_path.write_text("\n".join(lines), encoding="utf-8")
    applied_trace_path.write_text(json.dumps(applied, indent=2, ensure_ascii=False), encoding="utf-8")

    report_lines = [
        "# CASULO Campo OS - Applied Return Delta",
        "",
        "- status: APPLIED",
        "- applied_utc: %s" % stamp,
        "- operator: %s" % operator,
        "- target_branch: %s" % target_branch,
        "- canonical_effect: APPEND_DOMAIN_DELTA_RECORD",
        "- applied_domain_delta: %s" % rel(applied_domain_path),
        "- source_return_delta: %s" % rel(delta_path),
        "",
        "## Result",
        "",
        "- A controlled pilot delta was appended to the target branch.",
        "- No existing canonical state file was overwritten.",
        "",
    ]
    applied_report_path.write_text("\n".join(report_lines), encoding="utf-8")

    print("RETURN_DELTA_APPLIED")
    print("applied_domain_delta:", rel(applied_domain_path))
    print("trace:", rel(applied_trace_path))
    print("report:", rel(applied_report_path))
    print("canonical_effect: APPEND_DOMAIN_DELTA_RECORD")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--latest-return-delta", action="store_true")
    parser.add_argument("--return-delta")
    parser.add_argument("--operator", default="human_operator")
    parser.add_argument("--confirm", required=True)
    args = parser.parse_args()

    if args.latest_return_delta:
        delta_path = latest_return_delta()
    elif args.return_delta:
        delta_path = Path(args.return_delta)
    else:
        raise SystemExit("use --latest-return-delta or --return-delta PATH")

    apply_delta(delta_path, args.operator, args.confirm)


if __name__ == "__main__":
    main()

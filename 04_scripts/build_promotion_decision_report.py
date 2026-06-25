#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DECISIONS = ROOT / "05_outputs" / "promotion_decisions"
REPORTS = ROOT / "05_outputs" / "reports"


def rel(path):
    return str(path.relative_to(ROOT))


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def collect():
    rows = []
    for path in sorted(DECISIONS.glob("*.json"), key=lambda p: p.stat().st_mtime):
        data = read_json(path)
        rows.append({
            "path": rel(path),
            "decided_utc": data.get("decided_utc"),
            "operator": data.get("operator"),
            "decision": data.get("decision"),
            "measurement_count": data.get("measurement_count"),
            "overall_signal": data.get("overall_signal"),
            "promotion_allowed": data.get("promotion_allowed"),
            "canonical_effect": data.get("canonical_effect"),
            "next_action": data.get("next_action"),
        })
    return rows


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)

    rows = collect()
    latest = rows[-1] if rows else None

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PROMOTION_DECISION_REPORT",
        "decision_count": len(rows),
        "latest_decision": latest,
        "promotion_status": latest.get("decision") if latest else "NO_DECISION",
        "promotion_allowed": bool(latest.get("promotion_allowed")) if latest else False,
        "decisions": rows,
    }

    json_path = REPORTS / "promotion_decision_report.json"
    md_path = REPORTS / "promotion_decision_report.md"

    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Promotion Decision Report",
        "",
        "- generated_utc: %s" % report["generated_utc"],
        "- decision_count: %s" % report["decision_count"],
        "- promotion_status: %s" % report["promotion_status"],
        "- promotion_allowed: %s" % str(report["promotion_allowed"]).lower(),
        "",
        "## Decisions",
        "",
    ]

    if not rows:
        lines.append("- none")
    else:
        for row in rows:
            lines.append(
                "- %s | decision=%s | signal=%s | measurements=%s | promotion_allowed=%s | canonical_effect=%s | path=%s"
                % (
                    row.get("decided_utc"),
                    row.get("decision"),
                    row.get("overall_signal"),
                    row.get("measurement_count"),
                    str(row.get("promotion_allowed")).lower(),
                    row.get("canonical_effect"),
                    row.get("path"),
                )
            )

    lines.extend([
        "",
        "## Current interpretation",
        "",
    ])

    if latest:
        lines.append("- Latest decision: %s." % latest.get("decision"))
        lines.append("- Next action: %s" % latest.get("next_action"))
    else:
        lines.append("- No promotion decision has been recorded.")

    lines.append("")
    md_path.write_text("\n".join(lines), encoding="utf-8")

    print("PROMOTION_DECISION_REPORT_CREATED")
    print("report:", rel(md_path))
    print("json:", rel(json_path))
    print("decision_count:", report["decision_count"])
    print("promotion_status:", report["promotion_status"])
    print("promotion_allowed:", str(report["promotion_allowed"]).lower())


if __name__ == "__main__":
    main()

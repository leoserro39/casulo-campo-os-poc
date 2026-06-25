#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MEASUREMENTS = ROOT / "05_outputs" / "pilot_measurements"
REPORTS = ROOT / "05_outputs" / "reports"


def rel(path):
    return str(path.relative_to(ROOT))


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def collect_measurements():
    rows = []
    for path in sorted(MEASUREMENTS.glob("*.json"), key=lambda p: p.stat().st_mtime):
        data = read_json(path)
        rows.append({
            "path": rel(path),
            "recorded_utc": data.get("recorded_utc"),
            "branch": data.get("branch"),
            "operator": data.get("operator"),
            "total_conversations": data.get("total_conversations"),
            "resolved_conversations": data.get("resolved_conversations"),
            "unresolved_conversations": data.get("unresolved_conversations"),
            "conversations_without_resolved_status": data.get("conversations_without_resolved_status"),
            "response_time_minutes": data.get("response_time_minutes"),
            "pilot_signal": data.get("pilot_signal"),
            "promotion_effect": data.get("promotion_effect"),
        })
    return rows


def aggregate(rows):
    if not rows:
        return {
            "measurement_count": 0,
            "overall_signal": "NO_MEASUREMENTS",
            "promotion_allowed": False,
        }

    signals = [r.get("pilot_signal") for r in rows]

    if "PILOT_RISK" in signals:
        overall = "PILOT_RISK"
    elif "PROMOTION_CANDIDATE" in signals and len(rows) >= 3:
        overall = "PROMOTION_CANDIDATE"
    elif "PROMOTION_CANDIDATE" in signals:
        overall = "EXTEND_PILOT"
    elif "EXTEND_PILOT" in signals:
        overall = "EXTEND_PILOT"
    else:
        overall = "NEEDS_MORE_EVIDENCE"

    return {
        "measurement_count": len(rows),
        "overall_signal": overall,
        "promotion_allowed": False,
        "promotion_rule": "Promotion is blocked until explicit human decision in v1.3.",
    }


def main():
    REPORTS.mkdir(parents=True, exist_ok=True)

    rows = collect_measurements()
    agg = aggregate(rows)

    report = {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": "PILOT_MEASUREMENT_REPORT",
        "aggregate": agg,
        "measurements": rows,
    }

    json_path = REPORTS / "pilot_measurement_report.json"
    md_path = REPORTS / "pilot_measurement_report.md"

    json_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Pilot Measurement Report",
        "",
        "- generated_utc: %s" % report["generated_utc"],
        "- measurement_count: %s" % agg["measurement_count"],
        "- overall_signal: %s" % agg["overall_signal"],
        "- promotion_allowed: false",
        "- promotion_rule: Promotion is blocked until explicit human decision in v1.3.",
        "",
        "## Measurements",
        "",
    ]

    if not rows:
        lines.append("- none")
    else:
        for row in rows:
            lines.append(
                "- %s | branch=%s | total=%s | resolved=%s | unresolved=%s | no_status=%s | response_time=%s | signal=%s | path=%s"
                % (
                    row.get("recorded_utc"),
                    row.get("branch"),
                    row.get("total_conversations"),
                    row.get("resolved_conversations"),
                    row.get("unresolved_conversations"),
                    row.get("conversations_without_resolved_status"),
                    row.get("response_time_minutes"),
                    row.get("pilot_signal"),
                    row.get("path"),
                )
            )

    lines.extend([
        "",
        "## Next action",
        "",
        "- Continue collecting measurements during the pilot window.",
        "- Do not promote to long-term branch state before v1.3 Promotion Decision Gate.",
        "",
    ])

    md_path.write_text("\n".join(lines), encoding="utf-8")

    print("PILOT_MEASUREMENT_REPORT_CREATED")
    print("report:", rel(md_path))
    print("json:", rel(json_path))
    print("measurement_count:", agg["measurement_count"])
    print("overall_signal:", agg["overall_signal"])
    print("promotion_allowed: false")


if __name__ == "__main__":
    main()

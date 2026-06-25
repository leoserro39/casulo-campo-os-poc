#!/usr/bin/env python3
import json
from datetime import datetime, timezone
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "05_outputs" / "reports"
COCKPIT = ROOT / "05_outputs" / "cockpit"


def rel(path):
    return str(path.relative_to(ROOT))


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def collect(pattern):
    return sorted(ROOT.glob(pattern), key=lambda p: p.stat().st_mtime)


def latest(paths):
    if not paths:
        return None
    return sorted(paths, key=lambda p: p.stat().st_mtime, reverse=True)[0]


def build_awareness():
    applied_json = collect("05_outputs/applied_return_deltas/*.json")
    domain_deltas = collect("01_domains/*/deltas/*.md")
    return_deltas = collect("05_outputs/return_deltas/*.json")
    reviews = collect("05_outputs/reviews/*.json")
    proposals = collect("05_outputs/proposals/*.json")

    latest_applied = latest(applied_json)
    latest_domain = latest(domain_deltas)
    latest_data = read_json(latest_applied) if latest_applied else {}

    status = "APPLIED_DELTA_ACTIVE" if applied_json and domain_deltas else "NO_APPLIED_DELTA"

    return {
        "generated_utc": datetime.now(timezone.utc).isoformat(),
        "status": status,
        "return_delta_count": len(return_deltas),
        "applied_return_delta_count": len(applied_json),
        "domain_delta_count": len(domain_deltas),
        "review_count": len(reviews),
        "proposal_count": len(proposals),
        "latest_applied_return_delta": rel(latest_applied) if latest_applied else None,
        "latest_domain_delta": rel(latest_domain) if latest_domain else None,
        "latest_applied_summary": {
            "operator": latest_data.get("operator"),
            "target_branch": latest_data.get("target_branch"),
            "canonical_effect": latest_data.get("canonical_effect"),
            "source_return_delta": latest_data.get("source_return_delta"),
            "source_review": latest_data.get("source_review"),
            "source_proposal": latest_data.get("source_proposal"),
            "question": latest_data.get("question"),
        },
    }


def write_json_and_md(awareness):
    REPORTS.mkdir(parents=True, exist_ok=True)
    COCKPIT.mkdir(parents=True, exist_ok=True)

    json_path = REPORTS / "applied_delta_awareness.json"
    md_path = REPORTS / "POC_V1_1_APPLIED_DELTA_AWARENESS.md"
    cube_summary_path = COCKPIT / "operational_cube_v11_summary.md"

    json_path.write_text(json.dumps(awareness, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# CASULO Campo OS - POC v1.1 Applied Delta Awareness",
        "",
        "- generated_utc: %s" % awareness["generated_utc"],
        "- status: %s" % awareness["status"],
        "- return_delta_count: %s" % awareness["return_delta_count"],
        "- applied_return_delta_count: %s" % awareness["applied_return_delta_count"],
        "- domain_delta_count: %s" % awareness["domain_delta_count"],
        "- review_count: %s" % awareness["review_count"],
        "- proposal_count: %s" % awareness["proposal_count"],
        "- latest_applied_return_delta: %s" % awareness["latest_applied_return_delta"],
        "- latest_domain_delta: %s" % awareness["latest_domain_delta"],
        "",
        "## Latest applied summary",
        "",
    ]

    for key, value in awareness["latest_applied_summary"].items():
        lines.append("- %s: %s" % (key, value))

    lines += [
        "",
        "## Interpretation",
        "",
        "- Return Delta promotion is active in the POC.",
        "- The applied effect is append-only, not overwrite.",
        "- The target branch has a controlled applied delta record.",
        "- The next maturity step is measuring the pilot before long-term promotion.",
        "",
    ]

    md_path.write_text("\n".join(lines), encoding="utf-8")

    cube_lines = [
        "# CASULO Campo OS - Operational Cube v1.1 Summary",
        "",
        "- generated_utc: %s" % awareness["generated_utc"],
        "- status: %s" % awareness["status"],
        "- applied_return_delta_count: %s" % awareness["applied_return_delta_count"],
        "- domain_delta_count: %s" % awareness["domain_delta_count"],
        "- latest_domain_delta: %s" % awareness["latest_domain_delta"],
        "",
        "## New cockpit layer",
        "",
        "- Applied Return Delta is explicitly visible.",
        "- The original cube remains available at 05_outputs/cockpit/operational_cube.html.",
        "- The v1.1 cube is available at 05_outputs/cockpit/operational_cube_v11.html.",
        "",
    ]

    cube_summary_path.write_text("\n".join(cube_lines), encoding="utf-8")

    return json_path, md_path, cube_summary_path


def write_html(awareness):
    base_html = COCKPIT / "operational_cube.html"
    out_html = COCKPIT / "operational_cube_v11.html"
    summary = awareness["latest_applied_summary"]

    panel_lines = [
        '<section class="panel">',
        '<h2>Applied Return Delta</h2>',
        '<p>Camada v1.1: mostra quando um Return Delta aprovado entrou de forma controlada na ramificacao.</p>',
        '<div class="axis">',
        '<div>status: %s</div>' % escape(str(awareness["status"])),
        '<div>applied_return_delta_count: %s</div>' % escape(str(awareness["applied_return_delta_count"])),
        '<div>domain_delta_count: %s</div>' % escape(str(awareness["domain_delta_count"])),
        '<div>canonical_effect: %s</div>' % escape(str(summary.get("canonical_effect"))),
        '<div>latest_domain_delta: %s</div>' % escape(str(awareness["latest_domain_delta"])),
        '</div>',
        '</section>',
    ]
    panel = "\n".join(panel_lines)

    if base_html.exists():
        html = base_html.read_text(encoding="utf-8")
        html = html.replace("CASULO Campo OS - Operational Cube", "CASULO Campo OS - Operational Cube v1.1")
        html = html.replace(
            "Cubo Operacional de Estado. Projecao derivada do repo, nao fonte canonica.",
            "Cubo Operacional de Estado v1.1. Projecao derivada do repo, com Applied Return Delta Awareness."
        )
        html = html.replace('<div class="cube">', panel + '\n<div class="cube">')
    else:
        html = "<!doctype html><html><body>%s</body></html>" % panel

    out_html.write_text(html, encoding="utf-8")
    return out_html


def main():
    awareness = build_awareness()
    json_path, md_path, cube_summary_path = write_json_and_md(awareness)
    html_path = write_html(awareness)

    print("APPLIED_DELTA_AWARENESS_CREATED")
    print("status:", awareness["status"])
    print("applied_return_delta_count:", awareness["applied_return_delta_count"])
    print("domain_delta_count:", awareness["domain_delta_count"])
    print("report:", rel(md_path))
    print("json:", rel(json_path))
    print("cube_v11:", rel(html_path))
    print("cube_v11_summary:", rel(cube_summary_path))


if __name__ == "__main__":
    main()

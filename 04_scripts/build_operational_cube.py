#!/usr/bin/env python3
import json
from html import escape
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path(__file__).resolve().parents[1]
REPORTS = ROOT / "05_outputs" / "reports"
OUT = ROOT / "05_outputs" / "cockpit"
TIMELINE = REPORTS / "state_timeline.json"


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def rel(path):
    return str(path.relative_to(ROOT))


def event_title(ev):
    return (
        ev.get("source_id")
        or ev.get("question")
        or ev.get("path")
        or ev.get("type")
        or "event"
    )


def event_state(ev):
    text = " ".join(str(ev.get(k, "")) for k in [
        "gate",
        "status",
        "hallucination_risk",
        "type",
    ]).upper()

    if "BLOCK" in text or "HIGH" in text:
        return "blocked"
    if "HUMAN" in text or "REVIEW" in text or "MEDIUM" in text:
        return "review"
    if "PROPOSED" in text:
        return "proposed"
    if "ALLOW" in text or "LOW" in text:
        return "allow"
    return "planned"


def face_for(ev):
    typ = ev.get("type")
    if typ == "source_intake":
        return "source_intake"
    if typ == "mesh_delta":
        return "delta_engine"
    if typ == "proposal":
        return "manifestation"
    return "timeline"


def build_cube(timeline):
    events = timeline.get("events", [])

    faces = {
        "source_intake": {
            "title": "Source Intake",
            "description": "Legados, APIs, snapshots, manifests e trust.",
            "events": [],
        },
        "delta_engine": {
            "title": "Delta Engine",
            "description": "Delta_L, H_pre, dimensoes comuns e faltantes.",
            "events": [],
        },
        "manifestation": {
            "title": "Manifestation",
            "description": "Propostas controladas geradas pela malha.",
            "events": [],
        },
        "human_gate": {
            "title": "Human Gate",
            "description": "Itens aguardando revisao humana.",
            "events": [],
        },
        "sync_layer": {
            "title": "Sync Layer",
            "description": "Contratos de sincronizacao entre ramificacoes.",
            "events": [],
            "planned_note": "Planned: cross-branch sync delta and protection gate.",
        },
        "timeline": {
            "title": "State Timeline",
            "description": "Sequencia operacional consolidada.",
            "events": [],
        },
    }

    for ev in events:
        faces[face_for(ev)]["events"].append(ev)
        faces["timeline"]["events"].append(ev)

        gate = str(ev.get("gate", "")).upper()
        risk = str(ev.get("hallucination_risk", "")).upper()
        status = str(ev.get("status", "")).upper()
        if "HUMAN" in gate or "REVIEW" in gate or risk in ("MEDIUM", "HIGH", "BLOCKED") or status == "PROPOSED":
            faces["human_gate"]["events"].append(ev)

    return faces


def render_card(ev):
    state = event_state(ev)
    title = escape(str(event_title(ev)))
    path = escape(str(ev.get("path", "")))
    parts = []

    for key in [
        "type",
        "domain",
        "target_branch",
        "status",
        "gate",
        "Delta_L",
        "H_pre",
        "trust_score",
        "hallucination_risk",
    ]:
        value = ev.get(key)
        if value is not None:
            parts.append("<span>%s=%s</span>" % (escape(key), escape(str(value))))

    return """
      <article class="card %s">
        <strong>%s</strong>
        <div class="meta">%s</div>
        <small>%s</small>
      </article>
    """ % (state, title, " ".join(parts), path)


def render_face(face_id, face):
    state_counts = {"allow": 0, "review": 0, "proposed": 0, "blocked": 0, "planned": 0}
    for ev in face.get("events", []):
        state_counts[event_state(ev)] += 1

    cards = "".join(render_card(ev) for ev in face.get("events", [])[:8])
    if not cards:
        note = face.get("planned_note", "No events yet.")
        cards = '<article class="card planned"><strong>%s</strong><div class="meta">status=planned</div></article>' % escape(note)

    chips = "".join(
        '<span class="chip %s">%s %s</span>' % (k, k, v)
        for k, v in state_counts.items()
        if v
    )

    return """
    <section class="face" id="%s">
      <header>
        <h2>%s</h2>
        <p>%s</p>
        <div class="chips">%s</div>
      </header>
      <div class="cards">%s</div>
    </section>
    """ % (
        escape(face_id),
        escape(face["title"]),
        escape(face["description"]),
        chips,
        cards,
    )


def write_outputs(timeline, faces):
    OUT.mkdir(parents=True, exist_ok=True)
    generated = datetime.now(timezone.utc).isoformat()

    cube = {
        "generated_utc": generated,
        "source": rel(TIMELINE),
        "faces": faces,
        "summary": {
            "source_intake_count": timeline.get("source_intake_count", 0),
            "mesh_delta_count": timeline.get("mesh_delta_count", 0),
            "proposal_count": timeline.get("proposal_count", 0),
            "event_count": len(timeline.get("events", [])),
            "human_gate_count": len(faces["human_gate"]["events"]),
        },
    }

    json_path = OUT / "operational_cube.json"
    html_path = OUT / "operational_cube.html"
    summary_path = OUT / "operational_cube_summary.md"

    json_path.write_text(json.dumps(cube, indent=2, ensure_ascii=False), encoding="utf-8")

    face_html = "\n".join(render_face(fid, face) for fid, face in faces.items())

    html = """<!doctype html>
<html lang="pt-BR">
<head>
<meta charset="utf-8">
<title>CASULO Campo OS - Operational Cube</title>
<style>
:root {
  --bg: #0b1020;
  --panel: #121a30;
  --line: #26314f;
  --text: #e9eefc;
  --muted: #9ba8c7;
  --allow: #25b36a;
  --review: #d6a11f;
  --proposed: #3f82ff;
  --blocked: #d94a4a;
  --planned: #7b8194;
}
body {
  margin: 0;
  font-family: Arial, sans-serif;
  background: radial-gradient(circle at top, #1d2a50, var(--bg));
  color: var(--text);
}
.main {
  padding: 28px;
}
.top {
  display: grid;
  grid-template-columns: 1.4fr 1fr;
  gap: 18px;
  margin-bottom: 18px;
}
.panel, .face {
  background: rgba(18, 26, 48, .92);
  border: 1px solid var(--line);
  border-radius: 18px;
  box-shadow: 0 10px 30px rgba(0,0,0,.25);
}
.panel {
  padding: 20px;
}
h1, h2 {
  margin: 0 0 8px 0;
}
p {
  color: var(--muted);
}
.cube {
  display: grid;
  grid-template-columns: repeat(3, minmax(220px, 1fr));
  gap: 16px;
}
.face {
  min-height: 280px;
  padding: 16px;
  position: relative;
  overflow: hidden;
}
.face:before {
  content: "";
  position: absolute;
  inset: 0;
  background: linear-gradient(140deg, rgba(255,255,255,.07), transparent 42%);
  pointer-events: none;
}
.cards {
  display: grid;
  gap: 10px;
  position: relative;
}
.card {
  border-left: 5px solid var(--planned);
  background: rgba(255,255,255,.045);
  border-radius: 12px;
  padding: 10px;
}
.card.allow { border-left-color: var(--allow); }
.card.review { border-left-color: var(--review); }
.card.proposed { border-left-color: var(--proposed); }
.card.blocked { border-left-color: var(--blocked); }
.card.planned { border-left-color: var(--planned); }
.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 8px 0;
}
.meta span, .chip {
  font-size: 12px;
  color: var(--text);
  border: 1px solid var(--line);
  border-radius: 99px;
  padding: 3px 8px;
  background: rgba(255,255,255,.06);
}
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin: 8px 0 12px 0;
}
.chip.allow { border-color: var(--allow); }
.chip.review { border-color: var(--review); }
.chip.proposed { border-color: var(--proposed); }
.chip.blocked { border-color: var(--blocked); }
small {
  color: var(--muted);
  word-break: break-word;
}
.axis {
  display: grid;
  gap: 8px;
}
.axis div {
  padding: 8px 10px;
  border: 1px solid var(--line);
  border-radius: 10px;
  background: rgba(255,255,255,.04);
}
@media (max-width: 900px) {
  .top, .cube { grid-template-columns: 1fr; }
}
</style>
</head>
<body>
<div class="main">
  <div class="top">
    <section class="panel">
      <h1>CASULO Campo OS - Operational Cube</h1>
      <p>Cubo Operacional de Estado. Projecao derivada do repo, nao fonte canonica.</p>
      <p>Generated: GENERATED_AT</p>
    </section>
    <section class="panel">
      <h2>State Axis</h2>
      <div class="axis">
        <div>source intake -> trust -> mapping</div>
        <div>mesh delta -> Delta_L/H_pre -> gate</div>
        <div>manifestation -> proposal -> human review</div>
        <div>return delta -> canonical state after approval</div>
      </div>
    </section>
  </div>
  <div class="cube">
    FACE_HTML
  </div>
</div>
</body>
</html>
"""
    html = html.replace("GENERATED_AT", escape(generated)).replace("FACE_HTML", face_html)
    html_path.write_text(html, encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Operational Cube Summary",
        "",
        "- generated_utc: %s" % generated,
        "- source: %s" % rel(TIMELINE),
        "- source_intake_count: %s" % cube["summary"]["source_intake_count"],
        "- mesh_delta_count: %s" % cube["summary"]["mesh_delta_count"],
        "- proposal_count: %s" % cube["summary"]["proposal_count"],
        "- event_count: %s" % cube["summary"]["event_count"],
        "- human_gate_count: %s" % cube["summary"]["human_gate_count"],
        "",
        "## Faces",
    ]

    for fid, face in faces.items():
        lines.append("- %s: %s events" % (face["title"], len(face.get("events", []))))

    summary_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print("OPERATIONAL_CUBE_CREATED")
    print("html:", rel(html_path))
    print("json:", rel(json_path))
    print("summary:", rel(summary_path))
    print("events:", cube["summary"]["event_count"])
    print("human_gate_count:", cube["summary"]["human_gate_count"])


def main():
    timeline = read_json(TIMELINE)
    faces = build_cube(timeline)
    write_outputs(timeline, faces)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "05_outputs" / "proposals"


def run_script(script, question):
    cmd = [sys.executable, str(ROOT / "04_scripts" / script), "--ask", question]
    proc = subprocess.run(cmd, cwd=str(ROOT), text=True, capture_output=True)
    if proc.stdout.strip():
        print(proc.stdout.rstrip())
    if proc.stderr.strip():
        print(proc.stderr.rstrip(), file=sys.stderr)
    if proc.returncode != 0:
        raise SystemExit(proc.returncode)
    return proc.stdout


def parse_path(stdout, label):
    prefix = label + ":"
    for line in stdout.splitlines():
        if line.startswith(prefix):
            return ROOT / line.split(":", 1)[1].strip()
    return None


def latest_matching(folder, pattern):
    files = sorted(folder.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def make_blocked_artifact(question, delta):
    OUT.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    safe = "".join(c.lower() if c.isalnum() else "_" for c in question).strip("_")[:80] or "proposal"
    md = OUT / ("proposal_blocked_%s_%s.md" % (safe, stamp))
    js = OUT / ("proposal_blocked_%s_%s.json" % (safe, stamp))

    lines = [
        "# CASULO Campo OS Proposal Gate",
        "",
        "- status: NOT_PROPOSED",
        "- generated_utc: %s" % stamp,
        "- question: %s" % question,
        "- inferred_domain: %s" % delta.get("inferred_domain"),
        "- Delta_L: %s" % delta.get("Delta_L"),
        "- H_pre: %s" % delta.get("H_pre"),
        "- gate: %s" % delta.get("gate"),
        "",
        "## Reason",
        "- The mesh delta gate did not allow a strong proposal.",
        "",
        "## Missing dimensions",
    ]
    lines.extend(["- " + x for x in delta.get("missing_dimensions", [])] or ["- none"])
    lines.extend([
        "",
        "## Next action",
        "- %s" % delta.get("next_action", "Ask for more evidence or reduce scope."),
        "",
    ])

    md.write_text("\n".join(lines), encoding="utf-8")
    js.write_text(json.dumps({
        "status": "NOT_PROPOSED",
        "question": question,
        "inferred_domain": delta.get("inferred_domain"),
        "Delta_L": delta.get("Delta_L"),
        "H_pre": delta.get("H_pre"),
        "gate": delta.get("gate"),
        "missing_dimensions": delta.get("missing_dimensions", []),
        "next_action": delta.get("next_action"),
        "proposal_md": str(md.relative_to(ROOT)),
    }, indent=2, ensure_ascii=False), encoding="utf-8")

    print("PROPOSAL_BLOCKED_BY_DELTA")
    print("proposal:", md.relative_to(ROOT))
    print("trace:", js.relative_to(ROOT))
    print("gate:", delta.get("gate"))


def append_delta_to_proposal(proposal_md, proposal_json, delta_path, delta):
    section = [
        "",
        "## Mesh Delta Gate",
        "- mesh_delta: %s" % str(delta_path.relative_to(ROOT)),
        "- Delta_L: %s" % delta.get("Delta_L"),
        "- H_pre: %s" % delta.get("H_pre"),
        "- gate: %s" % delta.get("gate"),
        "- support_ratio: %s" % delta.get("support_ratio"),
        "- missing_ratio: %s" % delta.get("missing_ratio"),
        "",
    ]

    text = proposal_md.read_text(encoding="utf-8")
    if "## Mesh Delta Gate" not in text:
        proposal_md.write_text(text.rstrip() + "\n" + "\n".join(section), encoding="utf-8")

    data = json.loads(proposal_json.read_text(encoding="utf-8"))
    data["mesh_delta"] = {
        "path": str(delta_path.relative_to(ROOT)),
        "Delta_L": delta.get("Delta_L"),
        "H_pre": delta.get("H_pre"),
        "gate": delta.get("gate"),
        "support_ratio": delta.get("support_ratio"),
        "missing_ratio": delta.get("missing_ratio"),
        "missing_dimensions": delta.get("missing_dimensions", []),
    }
    proposal_json.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")

    print("PROPOSAL_GATED_BY_DELTA")
    print("proposal:", proposal_md.relative_to(ROOT))
    print("trace:", proposal_json.relative_to(ROOT))
    print("delta:", delta_path.relative_to(ROOT))
    print("gate:", delta.get("gate"))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--ask", required=True)
    args = parser.parse_args()
    question = args.ask

    delta_stdout = run_script("compute_mesh_delta.py", question)
    delta_trace = parse_path(delta_stdout, "trace") or latest_matching(ROOT / "05_outputs" / "deltas", "*.json")
    if not delta_trace or not delta_trace.exists():
        raise SystemExit("missing delta trace")

    delta = json.loads(delta_trace.read_text(encoding="utf-8"))
    gate = delta.get("gate")

    if gate != "ALLOW_PROPOSAL":
        make_blocked_artifact(question, delta)
        return

    before = set((ROOT / "05_outputs" / "proposals").glob("*.md"))
    proposal_stdout = run_script("propose_from_mesh.py", question)
    proposal_md = parse_path(proposal_stdout, "proposal")
    proposal_json = parse_path(proposal_stdout, "trace")

    if not proposal_md:
        after = set((ROOT / "05_outputs" / "proposals").glob("*.md"))
        created = list(after - before)
        proposal_md = sorted(created, key=lambda p: p.stat().st_mtime, reverse=True)[0]

    if not proposal_json:
        proposal_json = proposal_md.with_suffix(".json")

    append_delta_to_proposal(proposal_md, proposal_json, delta_trace, delta)


if __name__ == "__main__":
    main()

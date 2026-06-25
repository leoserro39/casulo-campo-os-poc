#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "05_outputs" / "real_tests" / "cycle_snapshots"
REPORTS = ROOT / "05_outputs" / "reports"


def rel(path):
    return str(path.relative_to(ROOT))


def run(cmd):
    try:
        return subprocess.check_output(cmd, cwd=str(ROOT), text=True).strip()
    except Exception:
        return ""


def read_json(path):
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}


def latest(pattern):
    files = sorted(ROOT.glob(pattern), key=lambda p: p.stat().st_mtime, reverse=True)
    return files[0] if files else None


def artifact(name, pattern):
    path = latest(pattern)
    return {
        "name": name,
        "path": rel(path) if path else None,
        "data": read_json(path) if path else {},
    }


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    generated = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%SZ")
    commit = run(["git", "rev-parse", "--short", "HEAD"])
    branch = run(["git", "branch", "--show-current"])
    recent_commits = run(["git", "log", "--oneline", "-12"]).splitlines()

    readiness = artifact("readiness", "05_outputs/reports/real_source_readiness_report.json")
    intake = artifact("intake", "05_outputs/reports/real_source_intake_report.json")
    proposal = artifact("proposal", "05_outputs/reports/real_evidence_proposal_report.json")
    review = artifact("human_review", "05_outputs/reports/real_human_review_report.json")
    measurement = artifact("pilot_measurement", "05_outputs/reports/real_pilot_measurement_report.json")
    promotion = artifact("promotion_decision", "05_outputs/reports/real_promotion_decision_report.json")

    promo_data = promotion["data"]
    measurement_data = measurement["data"].get("measurement", {})
    proposal_data = proposal["data"].get("proposal", {})
    intake_data = intake["data"].get("delta", {})

    gates = [
        {
            "gate": "Gate 1 - Readiness",
            "status": readiness["data"].get("gate"),
            "canonical_effect": readiness["data"].get("canonical_effect"),
        },
        {
            "gate": "Gate 2 - Intake",
            "status": intake_data.get("gate"),
            "canonical_effect": intake_data.get("canonical_effect"),
        },
        {
            "gate": "Gate 3 - Proposal",
            "status": proposal_data.get("proposal_gate"),
            "canonical_effect": proposal_data.get("canonical_effect"),
        },
        {
            "gate": "Gate 4 - Human Review",
            "status": review["data"].get("decision"),
            "canonical_effect": review["data"].get("canonical_effect"),
        },
        {
            "gate": "Gate 5 - Pilot Measurement",
            "status": measurement_data.get("pilot_signal"),
            "canonical_effect": measurement["data"].get("canonical_effect"),
        },
        {
            "gate": "Gate 6 - Promotion Decision",
            "status": promo_data.get("decision"),
            "canonical_effect": promo_data.get("canonical_effect"),
        },
    ]

    snapshot = {
        "status": "REAL_TEST_CYCLE_SNAPSHOT",
        "generated_utc": generated,
        "cycle": "real_atendimento_sample_cycle_001",
        "branch": branch,
        "commit": commit,
        "source_of_truth": "git",
        "canonical_effect": "NONE",
        "cycle_result": promo_data.get("decision"),
        "cycle_reason": promo_data.get("reason"),
        "promotion_execution_allowed": False,
        "branch_mutation_allowed": False,
        "gates": gates,
        "measurement_summary": {
            "total_conversations": measurement_data.get("total_conversations"),
            "resolved_conversations": measurement_data.get("resolved_conversations"),
            "unresolved_conversations": measurement_data.get("unresolved_conversations"),
            "conversations_without_resolved_status": measurement_data.get("conversations_without_resolved_status"),
            "response_time_minutes": measurement_data.get("response_time_minutes"),
            "pilot_signal": measurement_data.get("pilot_signal"),
        },
        "artifacts": {
            "readiness": readiness["path"],
            "intake": intake["path"],
            "proposal": proposal["path"],
            "human_review": review["path"],
            "pilot_measurement": measurement["path"],
            "promotion_decision": promotion["path"],
        },
        "next_action": "Collect at least two more real pilot measurements before any promotion candidate decision.",
        "recent_commits": recent_commits,
    }

    json_path = OUT / "real_atendimento_sample_cycle_001_snapshot.json"
    md_path = OUT / "REAL_ATENDIMENTO_SAMPLE_CYCLE_001_SNAPSHOT.md"
    report_json = REPORTS / "real_test_cycle_snapshot_report.json"
    report_md = REPORTS / "real_test_cycle_snapshot_report.md"

    text_json = json.dumps(snapshot, indent=2, ensure_ascii=False)
    json_path.write_text(text_json, encoding="utf-8")
    report_json.write_text(text_json, encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Real Test Cycle Snapshot",
        "",
        "- status: REAL_TEST_CYCLE_SNAPSHOT",
        "- generated_utc: %s" % generated,
        "- cycle: real_atendimento_sample_cycle_001",
        "- branch: %s" % branch,
        "- commit: %s" % commit,
        "- source_of_truth: git",
        "- canonical_effect: NONE",
        "- cycle_result: %s" % snapshot["cycle_result"],
        "- cycle_reason: %s" % snapshot["cycle_reason"],
        "- promotion_execution_allowed: false",
        "- branch_mutation_allowed: false",
        "",
        "## Gates",
        "",
    ]

    for gate in gates:
        lines.append("- %s: %s | canonical_effect=%s" % (
            gate["gate"],
            gate["status"],
            gate["canonical_effect"],
        ))

    lines.extend(["", "## Measurement summary", ""])
    for key, value in snapshot["measurement_summary"].items():
        lines.append("- %s: %s" % (key, value))

    lines.extend(["", "## Artifacts", ""])
    for key, value in snapshot["artifacts"].items():
        lines.append("- %s: %s" % (key, value))

    lines.extend([
        "",
        "## Next action",
        "",
        "- %s" % snapshot["next_action"],
        "",
        "## Recent commits",
        "",
    ])
    lines.extend(["- " + item for item in recent_commits])
    lines.append("")

    text_md = "\n".join(lines)
    md_path.write_text(text_md, encoding="utf-8")
    report_md.write_text(text_md, encoding="utf-8")

    print("REAL_TEST_CYCLE_SNAPSHOT_CREATED")
    print("snapshot:", rel(md_path))
    print("report:", rel(report_md))
    print("cycle_result:", snapshot["cycle_result"])
    print("promotion_execution_allowed: false")
    print("canonical_effect: NONE")
    print("next_action:", snapshot["next_action"])


if __name__ == "__main__":
    main()

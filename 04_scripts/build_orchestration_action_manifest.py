#!/usr/bin/env python3
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "05_outputs" / "orchestration"
REPORTS = ROOT / "05_outputs" / "reports"


def rel(path):
    return str(path.relative_to(ROOT))


def run(cmd):
    try:
        return subprocess.check_output(cmd, cwd=str(ROOT), text=True).strip()
    except Exception:
        return ""


def exists(path):
    return (ROOT / path).exists()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    REPORTS.mkdir(parents=True, exist_ok=True)

    commit = run(["git", "rev-parse", "--short", "HEAD"])
    branch = run(["git", "branch", "--show-current"])
    generated = datetime.now(timezone.utc).isoformat()

    allowed = [
        {
            "action": "read_context_packet",
            "mode": "read_only",
            "input": "05_outputs/context_packets/context_memory_packet_latest.json",
            "canonical_effect": "NONE",
            "allowed_for": ["human", "ChatGPT", "Codex", "Devin", "n8n", "MCP"],
        },
        {
            "action": "read_graph_projection",
            "mode": "read_only",
            "input": "05_outputs/graph_projection/casulo_graph_projection.json",
            "canonical_effect": "NONE",
            "allowed_for": ["human", "ChatGPT", "Neo4j importer", "n8n", "MCP"],
        },
        {
            "action": "build_reports",
            "mode": "derived_write",
            "canonical_effect": "NONE",
            "allowed_for": ["human", "n8n", "MCP"],
        },
        {
            "action": "record_pilot_measurement",
            "mode": "append_evidence",
            "script": "04_scripts/record_pilot_measurement.py",
            "canonical_effect": "EVIDENCE_ONLY",
            "requires": ["operator", "measurement values"],
            "allowed_for": ["human", "n8n form", "MCP controlled tool"],
        },
        {
            "action": "request_human_review",
            "mode": "append_request",
            "canonical_effect": "NONE",
            "allowed_for": ["human", "ChatGPT", "n8n", "MCP"],
        },
        {
            "action": "propose_sync_review",
            "mode": "proposal_only",
            "script": "04_scripts/build_cross_branch_sync_delta.py",
            "canonical_effect": "NONE",
            "requires_human_review": True,
            "allowed_for": ["human", "ChatGPT", "n8n", "MCP"],
        },
    ]

    conditional = [
        {
            "action": "apply_return_delta",
            "mode": "controlled_mutation",
            "script": "04_scripts/apply_return_delta.py",
            "canonical_effect": "APPEND_DOMAIN_DELTA_RECORD",
            "requires": ["explicit confirmation", "approved review", "return delta"],
            "confirmation": "APPLY_CANONICAL_DELTA",
            "allowed_for": ["human only", "MCP only if explicit human confirmation is passed"],
        },
        {
            "action": "register_promotion_decision",
            "mode": "human_decision",
            "script": "04_scripts/promotion_decision_gate.py",
            "canonical_effect": "NONE unless future promote flow is explicitly added",
            "requires": ["human operator", "pilot report"],
            "allowed_for": ["human only"],
        },
    ]

    forbidden = [
        "auto_promote_branch_state",
        "auto_sync_branches",
        "overwrite_domain_state",
        "mutate_from_graph_projection",
        "mutate_from_llm_answer_without_review",
        "treat_neo4j_as_source_of_truth",
        "delete_or_rewrite_evidence_history",
    ]

    readiness = {
        "context_packet_exists": exists("05_outputs/context_packets/context_memory_packet_latest.json"),
        "graph_projection_exists": exists("05_outputs/graph_projection/casulo_graph_projection.json"),
        "pilot_report_exists": exists("05_outputs/reports/pilot_measurement_report.json"),
        "promotion_report_exists": exists("05_outputs/reports/promotion_decision_report.json"),
        "sync_report_exists": exists("05_outputs/reports/cross_branch_sync_delta_report.json"),
    }

    manifest = {
        "generated_utc": generated,
        "status": "ORCHESTRATION_ACTION_MANIFEST",
        "branch": branch,
        "commit": commit,
        "source_of_truth": "git",
        "canonical_effect": "NONE",
        "orchestrators": ["human", "ChatGPT", "Codex", "Devin", "n8n", "MCP"],
        "allowed_actions": allowed,
        "conditional_actions": conditional,
        "forbidden_actions": forbidden,
        "readiness": readiness,
        "next_safe_action": "Expose only read/report/measurement/review-request tools first. Keep mutation tools human-confirmed.",
    }

    json_path = OUT / "action_manifest.json"
    md_path = OUT / "action_manifest.md"
    report_json = REPORTS / "orchestration_action_manifest.json"
    report_md = REPORTS / "orchestration_action_manifest.md"

    text_json = json.dumps(manifest, indent=2, ensure_ascii=False)
    json_path.write_text(text_json, encoding="utf-8")
    report_json.write_text(text_json, encoding="utf-8")

    lines = [
        "# CASULO Campo OS - Orchestration Action Manifest",
        "",
        "- generated_utc: %s" % generated,
        "- status: ORCHESTRATION_ACTION_MANIFEST",
        "- branch: %s" % branch,
        "- commit: %s" % commit,
        "- source_of_truth: git",
        "- canonical_effect: NONE",
        "",
        "## Readiness",
        "",
    ]

    for key, value in readiness.items():
        lines.append("- %s: %s" % (key, value))

    lines.extend(["", "## Allowed actions", ""])
    for item in allowed:
        lines.append("- %s | mode=%s | canonical_effect=%s" % (
            item["action"],
            item["mode"],
            item["canonical_effect"],
        ))

    lines.extend(["", "## Conditional actions", ""])
    for item in conditional:
        lines.append("- %s | mode=%s | canonical_effect=%s" % (
            item["action"],
            item["mode"],
            item["canonical_effect"],
        ))

    lines.extend(["", "## Forbidden actions", ""])
    for item in forbidden:
        lines.append("- %s" % item)

    lines.extend([
        "",
        "## Next safe action",
        "",
        "- %s" % manifest["next_safe_action"],
        "",
    ])

    text_md = "\n".join(lines)
    md_path.write_text(text_md, encoding="utf-8")
    report_md.write_text(text_md, encoding="utf-8")

    print("ORCHESTRATION_ACTION_MANIFEST_CREATED")
    print("manifest:", rel(md_path))
    print("json:", rel(json_path))
    print("report:", rel(report_md))
    print("allowed_actions:", len(allowed))
    print("conditional_actions:", len(conditional))
    print("forbidden_actions:", len(forbidden))
    print("canonical_effect: NONE")


if __name__ == "__main__":
    main()

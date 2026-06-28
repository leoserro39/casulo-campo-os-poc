from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[2]
REPO_ROOT = ROOT.parent
OUTPUTS = REPO_ROOT / "outputs"


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: Dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def audit() -> Dict[str, Any]:
    return load_json(OUTPUTS / "wb014_runtime_evidence_audit_result.json")


def handoff() -> Dict[str, Any]:
    return load_json(OUTPUTS / "wb015_internal_review_handoff.json")


def build_client_review_readiness(output_dir: Path = OUTPUTS) -> Dict[str, Any]:
    h = handoff()
    c = h.get("controlled_report", {})
    hr = h.get("human_review", {})
    ready = bool(c.get("ready_for_client_review")) and hr.get("decision") == "ALLOW_CLIENT_REVIEW"
    result = {
        "contract_version": "workbench.client_review_readiness.v1.1",
        "case_id": h.get("case_id"),
        "status": "PASS",
        "ready_for_internal_review": c.get("ready_for_internal_review"),
        "ready_for_client_review": ready,
        "implementation_authorized": False,
        "gate": "BLOCK_CLIENT_REVIEW" if not ready else "ALLOW_CLIENT_REVIEW",
        "reasons": [
            "Human review decision is not ALLOW_CLIENT_REVIEW.",
            "Client-facing claim remains blocked.",
            "Implementation remains blocked.",
        ] if not ready else ["Human review explicitly allowed client review."],
        "allowed_actions": [
            "internal_review",
            "request_more_evidence",
            "prepare_non_binding_internal_demo"
        ],
        "blocked_actions": [
            "client_facing_claim",
            "implementation_execution",
            "production_activation"
        ],
    }
    write_json(output_dir / "wb016_client_review_readiness.json", result)
    write_text(output_dir / "wb016_client_review_readiness.md", client_review_md(result))
    return result


def client_review_md(result: Dict[str, Any]) -> str:
    lines = [
        f"# WB-016 Client Review Readiness - {result.get('case_id')}",
        "",
        f"- Gate: `{result.get('gate')}`",
        f"- Ready for internal review: `{result.get('ready_for_internal_review')}`",
        f"- Ready for client review: `{result.get('ready_for_client_review')}`",
        f"- Implementation authorized: `{result.get('implementation_authorized')}`",
        "",
        "## Reasons",
    ]
    for item in result.get("reasons", []):
        lines.append(f"- {item}")
    lines += ["", "## Allowed Actions"]
    for item in result.get("allowed_actions", []):
        lines.append(f"- `{item}`")
    lines += ["", "## Blocked Actions"]
    for item in result.get("blocked_actions", []):
        lines.append(f"- `{item}`")
    return "\n".join(lines) + "\n"


def build_cockpit_story_replay(output_dir: Path = OUTPUTS) -> Dict[str, Any]:
    a = audit()
    h = handoff()
    d = a.get("summaries", {}).get("diagnostic", {})
    events = [
        {"step": 1, "event": "intake_loaded", "meaning": "Controlled intake accepted for diagnostic lane."},
        {"step": 2, "event": "evidence_manifest_allowed", "meaning": f"Manifest decision: {d.get('manifest_decision')}."},
        {"step": 3, "event": "state_snapshot_created", "meaning": "State snapshot generated from controlled case."},
        {"step": 4, "event": "graph_projected", "meaning": "Operational graph generated for domain intersections."},
        {"step": 5, "event": "diagnostic_computed", "meaning": f"Decision: {d.get('decision')} / DQ {d.get('data_quality')} / H_pre {d.get('h_pre')}."},
        {"step": 6, "event": "human_review_gate", "meaning": f"Human review decision: {h.get('human_review', {}).get('decision')}."},
        {"step": 7, "event": "controlled_report_generated", "meaning": "Internal controlled report assembled."},
        {"step": 8, "event": "runtime_evidence_audited", "meaning": f"{a.get('files_checked')} runtime files checked."},
        {"step": 9, "event": "internal_handoff_created", "meaning": "Sanitized internal handoff pack generated."},
    ]
    result = {
        "contract_version": "workbench.cockpit_story_replay.v1.2",
        "case_id": a.get("case_id"),
        "status": "PASS",
        "events": events,
        "summary": {
            "data_quality": d.get("data_quality"),
            "h_pre": d.get("h_pre"),
            "h_post": d.get("h_post"),
            "delta_l": d.get("delta_l"),
            "decision": d.get("decision"),
            "ready_for_internal_review": h.get("controlled_report", {}).get("ready_for_internal_review"),
            "ready_for_client_review": h.get("controlled_report", {}).get("ready_for_client_review"),
            "implementation_authorized": h.get("controlled_report", {}).get("implementation_authorized"),
        },
    }
    write_json(output_dir / "wb017_cockpit_story_replay.json", result)
    write_text(output_dir / "wb017_cockpit_story_replay.md", story_replay_md(result))
    return result


def story_replay_md(result: Dict[str, Any]) -> str:
    lines = [f"# WB-017 Cockpit Story Replay - {result.get('case_id')}", ""]
    for event in result.get("events", []):
        lines.append(f"{event['step']}. `{event['event']}` — {event['meaning']}")
    lines += ["", "## Summary"]
    for k, v in result.get("summary", {}).items():
        lines.append(f"- `{k}`: `{v}`")
    return "\n".join(lines) + "\n"


def build_micrograph_event_timeline(output_dir: Path = OUTPUTS) -> Dict[str, Any]:
    replay = build_cockpit_story_replay(output_dir)
    timeline = []
    for item in replay.get("events", []):
        timeline.append({
            "micrograph_event_id": f"mg_evt_{item['step']:02d}",
            "phase": item["event"],
            "trigger": "controlled_poc_lane",
            "authorized_region": "controlled_runtime_summary",
            "gate": "PASS" if item["event"] not in {"human_review_gate"} else "PENDING_HUMAN_REVIEW",
            "return_delta": item["meaning"],
        })
    result = {
        "contract_version": "workbench.micrograph_event_timeline.v1.3",
        "case_id": replay.get("case_id"),
        "status": "PASS",
        "timeline": timeline,
        "event_count": len(timeline),
    }
    write_json(output_dir / "wb018_micrograph_event_timeline.json", result)
    write_text(output_dir / "wb018_micrograph_event_timeline.md", timeline_md(result))
    return result


def timeline_md(result: Dict[str, Any]) -> str:
    lines = [f"# WB-018 Micrograph Event Timeline - {result.get('case_id')}", ""]
    for item in result.get("timeline", []):
        lines.append(f"- `{item['micrograph_event_id']}` / `{item['phase']}` / gate `{item['gate']}`: {item['return_delta']}")
    return "\n".join(lines) + "\n"


def build_cube_cupula_ui_state(output_dir: Path = OUTPUTS) -> Dict[str, Any]:
    a = audit()
    h = handoff()
    d = a.get("summaries", {}).get("diagnostic", {})
    result = {
        "contract_version": "workbench.cube_cupula_ui_state.v1.4",
        "case_id": a.get("case_id"),
        "status": "PASS",
        "metaphor": "operational_cube_solver",
        "principle": "Each cube move must correspond to evidence, gate, delta or state change.",
        "cupula": {
            "role": "selects and reorganizes the operational state field",
            "events": [
                "domain_activation",
                "evidence_manifest",
                "risk_propagation",
                "gate_block",
                "return_delta",
                "state_update"
            ],
        },
        "cube": {
            "role": "structures active execution and shows the operational cube being solved",
            "faces": {
                "objective": "controlled diagnostic from sanitized intake",
                "evidence": f"{a.get('files_checked')} runtime evidence files audited",
                "risk": f"H_pre {d.get('h_pre')} -> H_post {d.get('h_post')}",
                "tasks": "internal review / more evidence / no implementation",
                "deltas": f"Delta_L {d.get('delta_l')}",
                "gates": h.get("human_review", {}).get("blocked_next_actions", []),
            },
            "state": {
                "data_quality": d.get("data_quality"),
                "decision": d.get("decision"),
                "ready_for_internal_review": h.get("controlled_report", {}).get("ready_for_internal_review"),
                "ready_for_client_review": h.get("controlled_report", {}).get("ready_for_client_review"),
                "implementation_authorized": h.get("controlled_report", {}).get("implementation_authorized"),
            },
        },
        "chat_axial": {
            "role": "intention input and human decision point",
            "allowed_commands": [
                "explain current state",
                "show blocked gates",
                "show next delta",
                "request more evidence",
                "prepare internal review"
            ],
        },
    }
    write_json(output_dir / "wb019_cube_cupula_ui_state.json", result)
    write_text(output_dir / "wb019_cube_cupula_ui_state.md", cube_md(result))
    return result


def cube_md(result: Dict[str, Any]) -> str:
    lines = [
        f"# WB-019 Cube/Cupula UI State - {result.get('case_id')}",
        "",
        f"- Metaphor: `{result.get('metaphor')}`",
        f"- Principle: {result.get('principle')}",
        "",
        "## Cupula",
        f"- Role: {result['cupula']['role']}",
        "",
        "## Cube Faces",
    ]
    for face, value in result.get("cube", {}).get("faces", {}).items():
        lines.append(f"- `{face}`: `{value}`")
    lines += ["", "## Cube State"]
    for k, v in result.get("cube", {}).get("state", {}).items():
        lines.append(f"- `{k}`: `{v}`")
    return "\n".join(lines) + "\n"


def build_poc_completion(output_dir: Path = OUTPUTS) -> Dict[str, Any]:
    readiness = build_client_review_readiness(output_dir)
    replay = build_cockpit_story_replay(output_dir)
    timeline = build_micrograph_event_timeline(output_dir)
    cube = build_cube_cupula_ui_state(output_dir)
    result = {
        "contract_version": "workbench.poc_completion.v1.5",
        "status": "PASS",
        "poc_status": "CONTROLLED_INTERNAL_POC_COMPLETE",
        "completed_tasks": [
            "WB-016 Client Review Readiness Gate",
            "WB-017 Cockpit Story Replay",
            "WB-018 Micrograph Event Timeline",
            "WB-019 Cube/Cupula UI State Contract",
            "WB-020 POC Completion Report"
        ],
        "readiness": {
            "internal_review": readiness.get("ready_for_internal_review"),
            "client_review": readiness.get("ready_for_client_review"),
            "implementation_authorized": readiness.get("implementation_authorized"),
        },
        "story_events": len(replay.get("events", [])),
        "micrograph_events": timeline.get("event_count"),
        "cube_state": cube.get("cube", {}).get("state", {}),
        "definition_of_done": [
            "Controlled runtime evidence audited.",
            "Internal handoff created.",
            "Client review gate blocks external use until explicit approval.",
            "Cockpit replay explains the lane.",
            "Micrograph timeline exists.",
            "Cube/Cupula state contract exists.",
        ],
        "not_done": [
            "Production cloud runtime.",
            "Real tenant/auth/security.",
            "Real client approval.",
            "Implementation authorization.",
            "3D polished UI."
        ],
    }
    write_json(output_dir / "wb020_poc_completion_report.json", result)
    write_text(output_dir / "wb020_poc_completion_report.md", poc_md(result))
    return result


def poc_md(result: Dict[str, Any]) -> str:
    lines = [
        "# WB-020 POC Completion Report",
        "",
        f"- Status: `{result.get('status')}`",
        f"- POC status: `{result.get('poc_status')}`",
        "",
        "## Completed Tasks",
    ]
    for item in result.get("completed_tasks", []):
        lines.append(f"- {item}")
    lines += ["", "## Readiness"]
    for k, v in result.get("readiness", {}).items():
        lines.append(f"- `{k}`: `{v}`")
    lines += ["", "## Definition of Done"]
    for item in result.get("definition_of_done", []):
        lines.append(f"- {item}")
    lines += ["", "## Not Done"]
    for item in result.get("not_done", []):
        lines.append(f"- {item}")
    return "\n".join(lines) + "\n"

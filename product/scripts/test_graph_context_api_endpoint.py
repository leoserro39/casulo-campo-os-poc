#!/usr/bin/env python3
import json
import subprocess
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "outputs"

def fetch(url):
    with urllib.request.urlopen(url, timeout=20) as r:
        return json.loads(r.read().decode("utf-8"))

def main():
    port = 8098
    proc = subprocess.Popen(
        ["python", "product/api/graph_context_api.py", "--host", "127.0.0.1", "--port", str(port)],
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        time.sleep(2)
        health = fetch(f"http://127.0.0.1:{port}/api/health")
        context = fetch(f"http://127.0.0.1:{port}/api/graph/context?query=missing%20evidence%20human%20review&limit=5")

        status = "PASS" if health.get("status") == "PASS" and context.get("status") == "PASS" else "FAIL"

        result = {
            "status": status,
            "phase": "PROD-1381..1420",
            "health": health,
            "context_status": context.get("status"),
            "context_result_count": context.get("response", {}).get("context_packet", {}).get("result_count"),
            "blocked_actions": context.get("blocked_actions", [])
        }

        (OUT / "prod1381_1420_graph_context_api_test.json").write_text(
            json.dumps(result, indent=2, ensure_ascii=False),
            encoding="utf-8"
        )

        md = [
            "# PROD-1381..1420 Graph Context API Endpoint Test",
            "",
            f"- Status: `{status}`",
            f"- Health status: `{health.get('status')}`",
            f"- Context status: `{context.get('status')}`",
            f"- Context result count: `{result['context_result_count']}`",
            "",
            "## Boundary",
            "- Local HTTP only.",
            "- Read-only graph context.",
            "- No GPT call.",
            "- No Codex execution.",
            "- No production connection.",
            "",
            "## Blocked Actions"
        ]
        for action in result["blocked_actions"]:
            md.append(f"- {action}")

        (OUT / "prod1381_1420_graph_context_api_test.md").write_text(
            "\n".join(md) + "\n",
            encoding="utf-8"
        )

        print(json.dumps(result, indent=2, ensure_ascii=False))

    finally:
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except Exception:
            proc.kill()

if __name__ == "__main__":
    main()

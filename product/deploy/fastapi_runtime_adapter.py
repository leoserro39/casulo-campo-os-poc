from __future__ import annotations

from pathlib import Path
from typing import Any, Callable, Dict

try:
    from fastapi import FastAPI
except Exception as exc:  # pragma: no cover
    raise RuntimeError("FastAPI is required for this adapter. Install with: pip install fastapi uvicorn") from exc

from product.api.services.product_runtime_service import ProductRuntimeService


REPO_ROOT = Path(__file__).resolve().parents[2]
service = ProductRuntimeService(REPO_ROOT)

app = FastAPI(
    title="CASULO / Cubo Operational Runtime",
    version="0.1.0",
    description="Prototype public HTTPS runtime adapter for Custom GPT Actions. Read-only endpoints only.",
)


def route(path: str, fn: Callable[[], Dict[str, Any]]) -> None:
    async def endpoint() -> Dict[str, Any]:
        return fn()
    app.get(path)(endpoint)


route("/api/health", service.health)
route("/api/product/status", service.product_status)

route("/api/casulo/readiness/technical-memo", service.technical_readiness_memo)
route("/api/casulo/readiness/chat-agent-model", service.chat_agent_operating_model)
route("/api/casulo/readiness/target-stack", service.target_stack)
route("/api/casulo/readiness/codex-github-bridge", service.codex_github_bridge)
route("/api/casulo/readiness/poc-service-blueprint", service.poc_service_blueprint)
route("/api/casulo/readiness/incubator-pack", service.incubator_technical_pack)
route("/api/casulo/readiness/audit", service.technical_readiness_audit)

route("/api/casulo/poc-calibration/results", service.poc_calibration_results)
route("/api/casulo/poc-calibration/delta-control", service.delta_control_report)

route("/api/casulo/agent/openapi-spec", service.custom_gpt_openapi_spec)
route("/api/casulo/agent/custom-gpt-instructions", service.custom_gpt_instructions)
route("/api/casulo/agent/action-manifest", service.action_manifest)
route("/api/casulo/agent/tool-router", service.tool_router)
route("/api/casulo/agent/security-policy", service.connector_security_policy)
route("/api/casulo/agent/readiness", service.connector_readiness)
route("/api/casulo/agent/audit", service.connector_audit)


@app.get("/")
async def root() -> Dict[str, Any]:
    return {
        "status": "PASS",
        "service": "CASULO / Cubo Operational Runtime",
        "mode": "prototype_public_https_adapter_read_only",
        "docs": "/docs",
        "openapi": "/openapi.json",
    }

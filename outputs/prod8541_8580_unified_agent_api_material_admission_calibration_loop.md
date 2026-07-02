# PROD-8541..8580 - Unified Agent API with Material Admission and Calibration Loop

Status: PASS  
Decision: `UNIFIED_AGENT_API_WITH_MATERIAL_ADMISSION_AND_CALIBRATION_LOOP_READY_FOR_SANDBOX_AGENT_TEST`

```json
{
  "unified_agent_api_ready": true,
  "material_first_agent_flow_ready": true,
  "material_admission_before_diagnostic_required": true,
  "exocortex_context_rebuild_integrated": true,
  "operational_services_integrated": true,
  "controlled_calibration_loop_integrated": true,
  "graph_view_lite_integrated": true,
  "unified_openapi_ready": true,
  "manual_sandbox_agent_test_runbook_ready": true,
  "live_chatgpt_agent_configured_now": false,
  "public_action_server_deployed": false,
  "micrograph_runtime_current_poc": false,
  "threshold_lock_ready": false,
  "client_claim_allowed": false,
  "production_allowed": false,
  "commercial_claim_allowed": false,
  "cockpit_priority": "DEFERRED"
}
```

## Endpoints

- `GET /health`
- `GET /openapi.json`
- `GET /materials/taxonomy`
- `GET /materials/dimensions`
- `POST /materials/admit`
- `POST /materials/profile`
- `POST /materials/gate`
- `POST /agent/diagnostic`
- `POST /agent/monitoring`
- `POST /agent/solutions`
- `POST /agent/calibration`
- `GET /calibration-loop/cases`
- `POST /calibration-loop/run`
- `GET /graph/mermaid`

## Next

`PROD-8581..8620 - Manual ChatGPT Agent Sandbox Test Pack`

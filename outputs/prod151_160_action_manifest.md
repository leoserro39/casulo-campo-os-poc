# Custom GPT Action Manifest

- contract_version: `casulo.custom_gpt_actions_manifest.v0.1`
- status: `PASS`
- mode: `read_only_actions_prototype`
- requires_public_https_for_real_custom_gpt: `True`
- local_base_url: `http://127.0.0.1:8097`

## Actions
- `getProductStatus` — {"operation_id": "getProductStatus", "method": "get", "path": "/api/product/status", "summary": "Return CASULO/Cubo runtime status and readiness checks.", "tag": "status"}
- `getTechnicalReadinessMemo` — {"operation_id": "getTechnicalReadinessMemo", "method": "get", "path": "/api/casulo/readiness/technical-memo", "summary": "Return technical readiness memo.", "tag": "readiness"}
- `getChatAgentModel` — {"operation_id": "getChatAgentModel", "method": "get", "path": "/api/casulo/readiness/chat-agent-model", "summary": "Return chat agent operating model.", "tag": "agent"}
- `getTargetStack` — {"operation_id": "getTargetStack", "method": "get", "path": "/api/casulo/readiness/target-stack", "summary": "Return target stack plan.", "tag": "stack"}
- `getCodexGithubBridge` — {"operation_id": "getCodexGithubBridge", "method": "get", "path": "/api/casulo/readiness/codex-github-bridge", "summary": "Return Codex/GitHub bridge plan.", "tag": "development"}
- `getPocServiceBlueprint` — {"operation_id": "getPocServiceBlueprint", "method": "get", "path": "/api/casulo/readiness/poc-service-blueprint", "summary": "Return controlled POC service blueprint.", "tag": "poc"}
- `getPocCalibrationResults` — {"operation_id": "getPocCalibrationResults", "method": "get", "path": "/api/casulo/poc-calibration/results", "summary": "Return POC calibration results.", "tag": "calibration"}
- `getPocCalibrationDeltaControl` — {"operation_id": "getPocCalibrationDeltaControl", "method": "get", "path": "/api/casulo/poc-calibration/delta-control", "summary": "Return delta control report.", "tag": "calibration"}
- `getIncubatorPack` — {"operation_id": "getIncubatorPack", "method": "get", "path": "/api/casulo/readiness/incubator-pack", "summary": "Return incubator technical pack.", "tag": "incubator"}
- `getReadinessAudit` — {"operation_id": "getReadinessAudit", "method": "get", "path": "/api/casulo/readiness/audit", "summary": "Return technical readiness audit.", "tag": "audit"}

## Security Policy
- auth_mode: `none_for_local_prototype`
- production_auth_required: `True`
- data_policy: `redacted_or_anonymized_only`
- write_actions: `blocked_in_this_prototype`

## Blocked Actions
- `client_facing_claim`
- `automatic_nomination`
- `implementation_execution`
- `production_activation`
- `automatic_merge`
- `credential_handling`

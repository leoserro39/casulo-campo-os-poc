# CASULO ChatGPT Agent Action Manifest

Status: `READY_FOR_MANUAL_AGENT_CONFIGURATION`  
Decision: `CHATGPT_AGENT_ACTIONS_INTEGRATION_PACK_READY_FOR_MANUAL_AGENT_CONFIGURATION`

## Files

- Instructions: `product/agent_integration/chatgpt_agent_final_instructions.md`
- Knowledge pack: `product/agent_integration/chatgpt_agent_final_knowledge_pack.md`
- OpenAPI JSON: `product/agent_integration/chatgpt_agent_openapi_consolidated.json`
- OpenAPI YAML: `product/agent_integration/chatgpt_agent_openapi_consolidated.yaml`
- Test suite: `product/agent_integration/action_test_suite.json`

## Endpoints

- `GET /health`
- `POST /exocortex/context/rebuild`
- `POST /diagnostic/draft`
- `POST /services/diagnostic`
- `POST /services/monitoring`
- `POST /services/solutions`
- `POST /services/calibration`
- `GET /graph/mermaid`

## Boundary

This is a manual configuration pack. It does not configure a live ChatGPT Agent by itself.

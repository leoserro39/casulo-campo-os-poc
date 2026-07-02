# Manual Configuration Runbook

## Purpose

Prepare the manual configuration package for a future ChatGPT Agent/GPT action setup.

## Steps

1. Start local unified API:
   ```bash
   python3 product/api/casulo_agent_api_server_v05_unified.py --host 0.0.0.0 --port 8421
   ```

2. Expose it through a public HTTPS endpoint only when ready for manual Action testing.

3. Use:
   - `product/agent_integration/chatgpt_agent_final_instructions.md`
   - `product/agent_integration/chatgpt_agent_final_knowledge_pack.md`
   - `product/agent_integration/chatgpt_agent_openapi_consolidated.yaml`

4. Run action test prompts.

## Boundary

This pack does not deploy or configure a live ChatGPT Agent automatically.

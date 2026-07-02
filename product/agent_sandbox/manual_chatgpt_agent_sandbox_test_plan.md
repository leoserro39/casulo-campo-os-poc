# Manual ChatGPT Agent Sandbox Test Plan

## Objective

Run the first manual sandbox test for CASULO Agent using the unified material-first API.

## Scope

This is an internal sandbox test only.

The test validates:

1. The server starts locally.
2. The Codespaces public URL is generated.
3. The OpenAPI schema is configured manually in the Agent/GPT builder.
4. The Agent calls material admission before diagnostic.
5. The Agent keeps production, client and commercial claims blocked.
6. The Agent records outputs as evidence, not as validation proof.

## Test sequence

1. Start the unified server on port 8541.
2. Generate the public URL.
3. Replace `https://REPLACE_WITH_PUBLIC_ACTION_SERVER` in the OpenAPI schema with the public URL.
4. Configure the Agent manually with:
   - instructions from `product/agent_unified/casulo_unified_agent_instructions.md`;
   - knowledge from `product/agent_unified/casulo_unified_agent_knowledge_pack.md`;
   - schema from `product/agent_unified/casulo_unified_agent_openapi.yaml`.
5. Run prompts from `sandbox_prompt_suite_v0_1.json`.
6. Capture responses in `sandbox_evidence_log_template.md`.
7. Mark results against `sandbox_acceptance_criteria.json`.

## Boundary

This pack does not configure a live Agent automatically.

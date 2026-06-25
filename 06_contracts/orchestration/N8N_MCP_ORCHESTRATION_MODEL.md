# CASULO Campo OS - n8n MCP Orchestration Model

## Position

n8n is an orchestration and adapter layer for CASULO Campo OS.

n8n must not become the canonical source of truth.

Git remains the source of truth for:
- contracts
- source manifests
- mappings
- evidence
- deltas
- proposals
- reviews
- approved state changes

## Why n8n

n8n is useful for:
- connecting legacy systems
- consuming APIs
- scheduling intake jobs
- receiving webhooks
- reading spreadsheets or exports
- invoking CASULO scripts
- sending approval requests
- publishing status updates
- exposing controlled tools through MCP

## Core rule

External systems do not write directly into canonical branch state.

Every external input must pass through:

source
-> n8n adapter workflow
-> source manifest
-> raw snapshot
-> source trust assessment
-> canonical mapping
-> sanity gate
-> evidence ledger
-> mesh delta
-> proposal/review
-> return delta

## MCP role

MCP can expose controlled CASULO/n8n tools to agents.

Allowed MCP-style tools may include:
- register_source_manifest
- create_raw_snapshot
- run_source_trust_check
- map_source_to_branch
- compute_mesh_delta
- generate_controlled_proposal
- request_human_review
- publish_state_timeline

MCP must not expose unrestricted state mutation.

## Human gate

Any operation that changes canonical state must require review.

Examples:
- approving a proposal
- applying a return delta
- changing branch state
- creating a task packet for implementation
- sending data to an external system

## Recommended consulting use

A consulting project should begin with:
1. source inventory
2. source trust registry
3. adapter plan
4. canonical mapping
5. intake risk report
6. first controlled snapshot

Only after this should the project generate proposals or operational automation.

## Anti-patterns

Avoid:
- treating n8n as the brain
- treating MCP as unlimited access
- writing directly to canonical state
- converting every legacy system into static documents only
- trusting legacy data without source trust
- letting an agent execute external actions without human gate

## Target POC integration

The POC should eventually support:

legacy source
-> n8n workflow
-> CASULO source intake artifact
-> mesh delta
-> gated proposal
-> human review
-> Git-tracked return delta
-> state timeline

# CASULO Campo OS - POC Final Snapshot

- generated_utc: 2026-06-25T19:34:01.092094+00:00
- latest_commit: ff23b76
- proposal_count: 3
- mesh_delta_count: 3
- source_intake_count: 1
- trust_report_count: 1
- timeline_event_count: 7
- cube_human_gate_count: 4
- cockpit: 05_outputs/cockpit/operational_cube.html

## Proven capabilities

- Git as source of truth
- repo-as-mesh operational structure
- local RAG chunks and derived graph
- operator chat
- mesh delta computation
- Delta_L and H_pre gate
- delta-gated proposal generation
- legacy source intake
- source trust report
- hallucination risk signal
- state timeline
- operational cube cockpit projection

## Current gates

- Source intake legacy WhatsApp requires human review.
- Proposals are PROPOSED and not canonical state.
- Sync Layer is planned, not active.
- Return Delta promotion is planned, not active.

## Next recommended phase

POC vNext: Review Gate + Return Delta promotion.

## Recent commits

- ff23b76 Add operational cube cockpit projection
- c7149f4 Add state timeline report for POC cockpit
- 2335642 Add legacy source demo and intake artifacts
- 451f1fb Add legacy source intake with trust and hallucination risk
- c80a117 Document n8n MCP orchestration model
- 1b90fc4 Keep single gated proposal proof artifact
- b4a27c4 Gate proposal generation with mesh delta
- c4eda4b Ignore Python cache artifacts
- 988a91f Add mesh delta computation for operational proposals
- 57492f8 Add mesh delta computer task prompt
- ff2d146 Record controlled atendimento WhatsApp proposal
- 427fd34 Add operator chat for mesh queries and proposal generation

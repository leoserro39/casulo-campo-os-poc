# Cockpit Chat Handoff Requirements

Goal: Prepare next phase: a local/static cockpit chat scaffold for diagnostic reports, monitoring and simple solution recommendations.

## Minimum surfaces

- Status header: phase, gate, readiness, blocked claims
- Chat panel: operator asks state/diagnostic/monitoring/solution questions
- Evidence panel: key evidence refs and graph state summary
- Diagnostic report panel
- Monitoring summary panel
- Simple solution options panel
- Boundary panel: allowed and blocked actions

## Runtime boundary

```json
{
  "static_or_local_only": true,
  "no_live_gpt_required": true,
  "no_neo4j_write": true,
  "no_production_action": true,
  "no_client_claim": true
}
```

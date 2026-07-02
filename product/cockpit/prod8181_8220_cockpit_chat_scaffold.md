# Cockpit Chat Scaffold

Local/static cockpit for Exocortex Foundation demo.

## Surfaces

- Status Header: Show phase, gate, readiness and blocked claims.
- Cockpit Chat: Operator asks for state, diagnostic report, monitoring summary or simple solution options.
- Evidence Panel: Show runtime context packet evidence refs and graph summary.
- Diagnostic Report Panel: Show supported facts, gaps, risks, gate, allowed and blocked actions.
- Monitoring Panel: Show current state, readiness, blocked claims, risk and follow-up.
- Simple Solution Panel: Show internal/reviewable solution options only.
- Boundary Panel: Keep client, production and commercial claims blocked.

## Runtime mode

```json
{
  "static_local_only": true,
  "deterministic_canned_responses": true,
  "live_gpt": false,
  "codex_execution": false,
  "neo4j_write": false,
  "production": false
}
```

# n8n MCP Orchestration Register

Status: PLANNED

## Decision

CASULO Campo OS may use n8n as an adapter and orchestration layer for legacy systems, APIs, scheduled jobs, webhooks and human approval workflows.

## Rule

n8n is not the source of truth. Git remains canonical.

## Expected value

n8n can reduce integration cost by connecting external systems and producing controlled intake artifacts for CASULO.

## Required safeguards

- source manifest
- raw snapshot
- source trust assessment
- canonical mapping
- sanity gate
- human approval for state-changing actions
- no direct mutation of canonical state
- audit trail in Git

## Future POC task

Create a simulated n8n intake workflow contract for a legacy WhatsApp/CRM export.

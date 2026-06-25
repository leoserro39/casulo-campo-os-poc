# CASULO Campo OS - Roadmap

## Current milestone

CASULO Campo OS POC v1.1 is active.

The POC has demonstrated:

- Git as source of truth
- repo-as-mesh structure
- source intake from legacy data
- source trust scoring
- hallucination risk signal
- mesh delta computation
- Delta_L and H_pre gate
- gated proposal generation
- human review gate
- return delta proposal
- controlled return delta application
- operational cube cockpit
- applied delta awareness

## v1.0 - Closed micrograph loop

Status: DONE

Purpose:

Prove that a micrograph can activate the mesh, compute delta, manifest a proposal, pass human review and return a controlled delta to the target branch.

Delivered:

- proposal generation
- mesh delta gate
- human review
- return delta proposal
- applied domain delta

## v1.1 - Applied Delta Awareness

Status: DONE

Purpose:

Make the cockpit aware that a return delta has actually been applied.

Delivered:

- applied_delta_awareness report
- operational_cube_v11
- applied delta counts
- domain delta visibility

## v1.2 - Pilot Measurement Loop

Status: NEXT

Purpose:

Measure the controlled pilot before long-term promotion.

Target branch:

- atendimento

Pilot measurements:

- response_time_minutes
- unresolved_conversations
- conversations_without_resolved_status
- total_conversations
- resolved_conversations
- notes/evidence

Outputs:

- pilot measurement records
- pilot measurement report
- pilot readiness signal

Decision after measurement:

- promote_to_branch_state
- extend_pilot
- rollback_or_reject
- request_more_evidence

## v1.3 - Promotion Decision Gate

Status: PLANNED

Purpose:

Decide whether the applied pilot delta becomes long-term branch state.

Required inputs:

- applied return delta
- pilot measurements
- human decision
- minimum evidence threshold

Possible decisions:

- PROMOTE
- EXTEND_PILOT
- REJECT
- NEEDS_MORE_EVIDENCE

## v1.4 - Cross-Branch Sync Delta

Status: PLANNED

Purpose:

Model synchronization between branches without leaking context freely.

Initial branches:

- atendimento
- vendas
- operacao
- gestao

Sync rules:

- only validated deltas can sync
- conflicting state requires review
- sync does not overwrite branch state automatically

## v1.5 - Context Memory Packet

Status: PLANNED

Purpose:

Generate compact context packages for humans, agents or automation tools.

Packet contents:

- current state
- latest deltas
- pending gates
- applied changes
- evidence references
- next safe action

## v1.6 - Neo4j / Graph Projection

Status: PLANNED

Purpose:

Publish the repo mesh as a graph projection.

Rule:

Graph is derived from Git artifacts.
Graph is not the source of truth.

## v1.7 - n8n / MCP Practical Orchestration

Status: PLANNED

Purpose:

Expose controlled actions and workflows.

Allowed actions:

- read state
- generate report
- request review
- submit measurement
- trigger gated proposal

Forbidden by default:

- unrestricted canonical mutation
- unreviewed promotion
- silent overwrite

## v2.0 - Multi-case CASULO Campo OS

Status: FUTURE

Purpose:

Generalize the POC from the atendimento WhatsApp demo into a repeatable consulting operating system.

Targets:

- multiple source types
- multiple cases
- repeatable onboarding
- source manifests
- evidence ledger
- operational cockpit
- human arbitration

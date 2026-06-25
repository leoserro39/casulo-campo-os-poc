# CASULO Campo OS - n8n / MCP Practical Orchestration

## Purpose

This contract defines safe orchestration actions for n8n, MCP, agents and human-operated workflows.

## Rule

Git remains the source of truth.
Repo artifacts are canonical.
n8n, MCP and agents are orchestrators, not authorities.

## Allowed action classes

- read context packet
- read graph projection
- build reports
- record pilot measurement
- request human review
- propose sync review

## Conditional action classes

- apply return delta only with explicit final confirmation
- register promotion decision only from human operator
- generate branch update proposal without applying it

## Forbidden action classes

- automatic branch promotion
- silent canonical mutation
- automatic cross-branch sync
- overwriting domain state
- treating Neo4j/graph as source of truth
- mutating from LLM output without review

## Safety

Any external workflow must write traceable artifacts.
Any canonical mutation must require an explicit gate.
Any promotion must require human decision.
Any sync must require human review.

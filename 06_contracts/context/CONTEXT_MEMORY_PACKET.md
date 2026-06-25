# CASULO Campo OS - Context Memory Packet

## Purpose

The Context Memory Packet is a compact operational handoff.

It is designed for:

- human operators
- ChatGPT sessions
- Codex/Devin agents
- n8n/MCP workflows
- future automation layers

## Rule

The packet is derived from repo artifacts.
It is not the source of truth.
Git remains the source of truth.

## Contents

The packet must include:

- current repo commit
- current POC version
- completed milestones
- latest applied delta
- latest pilot measurement
- latest promotion decision
- latest sync delta
- pending gates
- next safe action

## Safety

The packet must not mutate canonical state.
The packet must not promote pilots.
The packet must not apply sync deltas.
The packet must only summarize and hand off context.

# CASULO Campo OS - Operational Cube Cockpit Spec

## Purpose

The Operational Cube is a cockpit view for CASULO Campo OS.

It does not replace the canonical state.
It visualizes the current operational mesh, gates, deltas, source intake, proposals and pending review points.

## Concept

Each cube face represents an operational dimension:

- Source Intake
- Delta Engine
- Manifestation / Proposals
- Human Gate
- Sync Layer
- State Timeline

Each cube card represents an artifact or event:

- source manifest
- source trust report
- mesh delta
- proposal
- review gate
- sync condition
- state timeline event

## Rule

Git remains the source of truth.
The cube is a derived cockpit projection.

## Status colors

- allow: evidence supports controlled action
- review: human review is required
- proposed: proposal exists but is not canonical state
- blocked: action is blocked
- planned: layer exists as planned capability

## Target behavior

The cube must help answer:

- What entered the mesh?
- What was trusted or not trusted?
- What delta was computed?
- What proposal was generated?
- What is waiting for human review?
- What can move forward?
- What is still only planned?

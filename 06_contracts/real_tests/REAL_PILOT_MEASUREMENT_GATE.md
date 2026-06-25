# CASULO Campo OS - Real Pilot Measurement Gate

## Purpose

This gate records pilot measurements from real operational evidence after human approval.

## Rule

Real pilot measurement may run only after human review decision:

- APPROVED_FOR_PILOT

## Measurement unit

The first controlled measurement groups atendimento events by:

- contact_id_hash

## Required inputs

- real source intake report
- real human review report
- sanitized source CSV

## Canonical effect

- EVIDENCE_ONLY

## Promotion rule

Pilot measurement does not promote branch state.

Promotion remains blocked until an explicit promotion decision gate is executed with enough measurements.

## Safety

This gate must not:

- mutate branch state
- apply return delta
- promote pilot
- sync branches
- expose raw personal data

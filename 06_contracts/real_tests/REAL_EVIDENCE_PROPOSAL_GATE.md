# CASULO Campo OS - Real Evidence Proposal Gate

## Purpose

This gate creates a proposal from real source intake evidence.

## Rule

Real evidence may generate a proposal only after gated intake exists.

The proposal must not mutate canonical state.

## Required input

- real source intake report
- readiness gate READY_FOR_INTAKE
- intake gate allowing evidence-only usage

## Outputs

Expected outputs:

- real evidence delta
- real evidence proposal
- proposal report

## Canonical effect

- NONE

## Human review

All real evidence proposals require human review before any return delta, pilot change or branch update.

## Safety

The proposal must not:

- apply a return delta
- promote a pilot
- sync branches
- overwrite branch state
- expose raw personal data

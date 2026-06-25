# CASULO Campo OS - Real Human Review Gate

## Purpose

This gate records human review of a proposal generated from real operational evidence.

## Rule

A real evidence proposal cannot move to pilot execution, return delta or promotion flow without human review.

## Allowed decisions

- APPROVED_FOR_PILOT
- NEEDS_MORE_EVIDENCE
- REJECTED
- APPROVED_FOR_RETURN_DELTA_PROPOSAL

## Default safety

Approval for pilot does not mean canonical promotion.

## Canonical effect

- NONE

## Safety

The review must not:

- mutate branch state
- promote a pilot
- apply return delta
- sync branches automatically
- overwrite source evidence

## Next possible actions

If APPROVED_FOR_PILOT:

- record pilot measurements
- continue evidence collection
- keep promotion blocked

If NEEDS_MORE_EVIDENCE:

- collect more data
- correct unknown statuses
- rerun readiness/intake/proposal

If REJECTED:

- archive proposal as rejected evidence

If APPROVED_FOR_RETURN_DELTA_PROPOSAL:

- generate a return delta proposal only
- still require final apply confirmation

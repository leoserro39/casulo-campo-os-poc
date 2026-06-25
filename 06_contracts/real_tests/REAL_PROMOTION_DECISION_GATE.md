# CASULO Campo OS - Real Promotion Decision Gate

## Purpose

This gate evaluates real pilot measurements and records a promotion decision.

## Rule

A real pilot measurement signal is not enough to promote branch state automatically.

Promotion requires:

- enough pilot measurements
- acceptable unresolved ratio
- acceptable unknown status ratio
- explicit human-controlled decision
- no automatic branch mutation

## Possible decisions

- PROMOTION_CANDIDATE
- EXTEND_PILOT
- NEEDS_MORE_EVIDENCE
- REJECT

## Default safety

Even PROMOTION_CANDIDATE does not mutate branch state.

It only means the pilot may be eligible for a future controlled return delta / promotion workflow.

## Canonical effect

- NONE

## Safety

This gate must not:

- mutate branch state
- apply return delta
- sync branches
- overwrite evidence
- treat one positive measurement as permanent state

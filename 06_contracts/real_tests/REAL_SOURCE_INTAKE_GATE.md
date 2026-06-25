# CASULO Campo OS - Real Source Intake Gate

## Purpose

This gate controls the first intake of real operational data.

## Rule

Real source intake may only run after source readiness returns:

- READY_FOR_INTAKE

## Source of truth

Git remains the source of truth.

The real source intake creates evidence artifacts only.

## Canonical effect

- NONE
- EVIDENCE_ONLY

## Block conditions

The intake must stop if:

- source readiness is not READY_FOR_INTAKE
- required columns are missing
- PII is detected
- the file is unreadable
- row count is zero

## Outputs

Expected outputs:

- real source manifest
- real source trust report
- real source intake delta
- real source intake report

## Safety

The wrapper must not:

- mutate branch state
- promote a pilot
- apply return delta
- sync branches
- overwrite domain files

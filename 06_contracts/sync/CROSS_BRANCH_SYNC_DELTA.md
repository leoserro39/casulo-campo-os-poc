# CASULO Campo OS - Cross-Branch Sync Delta

## Purpose

Cross-Branch Sync Delta models how a validated change in one branch may affect other branches.

It does not copy context freely.
It does not overwrite branch state.
It does not apply automatically.

## Source branch

- atendimento

## Initial target branches

- vendas
- operacao
- gestao

## Rule

Only applied or reviewed deltas can generate sync candidates.

## Sync candidate types

- awareness: another branch should know that a delta exists
- metric_dependency: another branch may need a metric created by the delta
- process_dependency: another branch may need to adjust process
- governance_dependency: another branch may need monitoring or review

## Safety

- canonical_effect is NONE
- sync deltas are proposal artifacts only
- target branch update requires future human review
- conflicts require explicit arbitration

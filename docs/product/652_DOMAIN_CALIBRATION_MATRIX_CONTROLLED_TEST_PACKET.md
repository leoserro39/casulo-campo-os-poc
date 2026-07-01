# PROD-5941..5980 - Domain Calibration Matrix Controlled Test Packet

Prepares the first controlled domain calibration matrix.

This phase does not call GPT. It prepares scenarios, execution plan and scoring rubric.

## Scope

- GPT/OpenAI-only.
- No multi-vendor.
- No live call in this phase.
- No dataset acceptance.
- No client evidence.
- No production evidence.
- No commercial claim.

## Planned calibration shape

- Domains: 6
- Scenarios: 12
- Modes per scenario: 3
- Planned executions: 36

Modes:
- PURE_GPT
- STACK_GPT
- CASULO_EXOCORTEX_STACK

## Domains

- Financeiro / Administrativo
- Governança documental
- Jurídico / Escritório
- Pequenos negócios de campo
- TIC/SI / ITSM
- VesselFlow / Operação marítima

## What we will measure

- unsupported claim count;
- missing evidence claim count;
- gate violation count;
- evidence grounding score;
- state completeness score;
- manual arbitration need;
- false memory risk;
- context regression;
- latency and cost deltas.

## Next

`PROD-5981..6020 - Domain Calibration Matrix Execution Gate`

# PROD-6021..6060 - Domain Calibration Batch 01 Execution Run

First real controlled domain calibration batch.

## Result

- Executed calls: 36
- Real provider calls: 36
- Successful live responses: 36
- Domains: 6
- Scenarios: 12
- Modes: PURE_GPT, STACK_GPT, CASULO_EXOCORTEX_STACK

## Latency by mode

{
  "PURE_GPT": {
    "count": 12,
    "min": 3921,
    "max": 6364,
    "avg": 4819.67
  },
  "STACK_GPT": {
    "count": 12,
    "min": 4177,
    "max": 5827,
    "avg": 4728.25
  },
  "CASULO_EXOCORTEX_STACK": {
    "count": 12,
    "min": 4127,
    "max": 6199,
    "avg": 4726.67
  }
}

## Latency by domain

{
  "TIC/SI / ITSM": {
    "count": 6,
    "min": 4616,
    "max": 6364,
    "avg": 5105.33
  },
  "VesselFlow / Operação marítima": {
    "count": 6,
    "min": 4127,
    "max": 5196,
    "avg": 4651.17
  },
  "Jurídico / Escritório": {
    "count": 6,
    "min": 4177,
    "max": 6199,
    "avg": 5016.33
  },
  "Financeiro / Administrativo": {
    "count": 6,
    "min": 3921,
    "max": 5827,
    "avg": 4643.5
  },
  "Pequenos negócios de campo": {
    "count": 6,
    "min": 4249,
    "max": 4927,
    "avg": 4568.67
  },
  "Governança documental": {
    "count": 6,
    "min": 4169,
    "max": 4812,
    "avg": 4564.17
  }
}

## Boundary

These outputs are calibration records only. They are not dataset candidates, client evidence, production evidence or commercial claims.

Next: PROD-6061..6100 - Domain Calibration Batch 01 Review Gate.

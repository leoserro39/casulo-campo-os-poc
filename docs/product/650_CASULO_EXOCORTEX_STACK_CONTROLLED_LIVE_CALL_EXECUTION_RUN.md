# PROD-5861..5900 - CASULO Exocortex Stack Controlled Live Call Execution Run

First controlled CASULO_EXOCORTEX_STACK live call.

## Result

- Mode: CASULO_EXOCORTEX_STACK
- Model: gpt-5.5-2026-04-23
- Output preview: `CASULO_EXOCORTEX_STACK_SANDBOX_ACK`
- Latency: 4334 ms
- Live GPT call execution: True
- Real GPT provider call: True
- GPT Memory API execution: False
- Real memory API execution: false
- Persistent memory write: false
- Dataset write: False

## Comparison basis

- PURE latency: 4285 ms
- STACK latency: 4001 ms
- EXOCORTEX latency: 4334 ms
- EXOCORTEX minus PURE: 49 ms
- EXOCORTEX minus STACK: 333 ms

This is still ACK-only. It is not domain validation, dataset evidence, client evidence or production evidence.

Next: PROD-5901..5940.

# Public HTTPS Runtime Deployment Plan

- contract_version: `casulo.public_https_runtime.v0.1`
- status: `PASS`
- public_base_url: `http://127.0.0.1:8098`
- https_ready: `False`

## Deployment Modes
- `local_only` — {"mode": "local_only", "use": "developer validation", "url_type": "http://127.0.0.1"}
- `secure_tunnel_for_demo` — {"mode": "secure_tunnel_for_demo", "use": "temporary Custom GPT demo", "url_type": "https://temporary"}
- `prototype_cloud_api` — {"mode": "prototype_cloud_api", "use": "controlled POC demo", "url_type": "https://stable"}
- `production_hardened_later` — {"mode": "production_hardened_later", "use": "after auth, persistence, audit and security", "url_type": "https://stable_auth"}
- recommendation: `Use local runtime for now. Use secure public HTTPS tunnel or prototype cloud only for controlled Custom GPT Action testing.`

## Blocked Actions
- `client_facing_claim`
- `automatic_nomination`
- `implementation_execution`
- `production_activation`
- `automatic_merge`
- `credential_handling`

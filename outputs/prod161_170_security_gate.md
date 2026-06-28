# Deploy Security Gate

- contract_version: `casulo.deploy_security_gate.v0.1`
- status: `PASS`
- decision: `PUBLIC_HTTPS_PROTOTYPE_ALLOWED_ONLY_FOR_READ_ONLY_REDACTED_DATA`

## Allowed
- `read-only readiness queries`
- `read-only calibration queries`
- `read-only incubator/technical pack queries`
- `read-only audit queries`

## Blocked
- `client_facing_claim`
- `automatic_nomination`
- `implementation_execution`
- `production_activation`
- `automatic_merge`
- `credential_handling`
- `write_actions`
- `file_upload_to_public_runtime`
- `unredacted_data_ingestion`
- `public credential handling`
- `automatic code execution`

## Requires Before External Use
- `public HTTPS`
- `no secrets`
- `redacted/anonymized data`
- `human review`
- `access control if used beyond demo`

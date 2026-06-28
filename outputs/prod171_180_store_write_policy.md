# Store Write Policy

- contract_version: `casulo.store_write_policy.v0.1`
- status: `PASS`

## Allowed Writes
- `append local JSONL state metadata`
- `append evidence metadata`
- `append graph candidate metadata`
- `append audit records`

## Blocked Writes
- `client_facing_claim`
- `automatic_nomination`
- `implementation_execution`
- `production_activation`
- `automatic_merge`
- `credential_handling`
- `raw_secret_storage`
- `unredacted_sensitive_storage`
- `production_db_mutation`
- `external_write_actions`
- rule: `Enterprise chat/actions may read store summaries. Writes remain local/internal until auth and audit are hardened.`

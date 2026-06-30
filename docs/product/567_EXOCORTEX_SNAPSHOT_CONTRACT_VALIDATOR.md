# PROD-2621..2660 - Exocortex Snapshot Contract Validator

Defines and validates the minimum contract for CASULO Exocortex snapshots.

A valid snapshot must contain state checksum, evidence pointers, claim boundary, gate, response mode, lifecycle action, Exocortex signals and blocked actions.

Boundary: validator only. No automatic memory deletion, no real memory mutation and no GPT memory API execution.

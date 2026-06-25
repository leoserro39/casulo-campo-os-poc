# CASULO Campo OS - Source Trust Rules

External and legacy sources enter CASULO as evidence, not truth.

A source is stronger when it has:
- known owner
- stable structure
- required fields
- recent snapshot
- low missing values
- low contradiction count
- clear target branch
- clear canonical mapping
- reproducible extraction

A source is weaker when it has:
- unknown owner
- missing required fields
- many empty values
- inconsistent status
- contradictory records
- unclear mapping
- manual copy without snapshot
- no update frequency
- no review owner

Risk levels:
- LOW: trusted source, enough evidence, low missing values, no contradictions
- MEDIUM: usable source, but some fields or dimensions are missing
- HIGH: weak source, relevant gaps, unclear mapping, or contradictions
- BLOCKED: insufficient or contradictory evidence

No source can update canonical branch state without a validated delta and review gate.

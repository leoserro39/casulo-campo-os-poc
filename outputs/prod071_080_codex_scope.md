# PROD-071..080 Codex Scope

- Status: `PASS`
- Decision: `CODEX_ALLOWED_ONLY_AS_CONTROLLED_DRAFT_EXECUTOR`

## Role
Codex or equivalent coding agent may draft tests, documentation, small patches and review summaries only inside an explicit branch/task scope.

## Allowed Actions
- read supplied repository context
- draft tests
- draft documentation
- draft architecture notes
- draft small non-production patches
- summarize evidence gaps
- prepare pull request text

## Blocked Actions
- production deployment
- automatic merge
- handling real credentials
- client-facing claim
- modifying security-sensitive logic without explicit human review
- changing infrastructure or deployment target without approval

## Required Controls
- explicit task id
- branch or patch scope
- test command
- evidence output path
- human reviewer
- gate decision

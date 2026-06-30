# Custom GPT Action Safety Boundary

The Custom GPT Action is a context retrieval interface only.

## The Action May

- retrieve graph context;
- summarize sandbox context;
- expose gates, risks, evidence profiles and output modes;
- support internal review.

## The Action Must Not

- make final decisions;
- execute implementation;
- call Codex;
- mutate Git or files;
- connect to production;
- handle credentials;
- approve client-facing claims;
- bypass human review;
- claim that sandbox context is real-world validated.

## Human Gate

Any movement from internal context to external demonstration, client-facing claim, implementation, or production activation requires explicit human approval.

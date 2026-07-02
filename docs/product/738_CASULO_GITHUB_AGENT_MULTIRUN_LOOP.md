# 738 - CASULO GitHub Agent Multi-Run Loop

This document records the controlled multi-run loop created in PROD-7381..7420.

## Purpose

Run the same real case through multiple prompt variants:

1. graph-backed prompt;
2. strict-boundary prompt;
3. adversarial client/production claim probe;
4. evidence-gap stress prompt.

## Execution model

The workflow is manual:

```bash
env -u GITHUB_TOKEN -u GH_TOKEN gh workflow run casulo_agent_multirun_calibration.yml \
  -f allow_llm=true \
  -f model=gpt-4o-mini \
  -f prompt_variant=real_case_001_graph_backed_prompt_v0_1.md \
  -f run_key=graph_backed_prompt_candidate
```

Each run produces an artifact under:

```text
product/agent_runs/real_case_001/<run_key>
```

## Safety boundary

All outputs remain internal calibration material.

No client claim.
No production activation.
No issue/PR comment.
No external write.
No automatic merge.

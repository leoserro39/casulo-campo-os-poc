# GitHub Issues Live Discovery Dry-Run Plan v0.3

This plan selects public GitHub Issues as the first live-discovery source.

The patcher does not call the network. It creates the discovery plan, query set,
runner scaffold, source trust gate, citation gate and expected metrics.

The generated runner defaults to dry-run mode. A future explicit call may use:

```bash
python product/scripts/discover_github_issues_public_cases.py --dry-run
python product/scripts/discover_github_issues_public_cases.py --allow-network --limit 10
```

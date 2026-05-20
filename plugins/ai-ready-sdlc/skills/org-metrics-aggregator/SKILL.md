---
name: org-metrics-aggregator
description: Aggregate collected ADLC standards reports into organization-level metrics.
---

Use this skill when a collection repo contains ADLC `org-standards.json` snapshots.

Run:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/aggregate-org-metrics.py --collection-repo <collection-repo> --output metrics/org-metrics.json --markdown-output metrics/org-metrics.md
```

The aggregator computes coverage policy adoption, missing coverage artifacts, high security findings, too many security findings, large gaps, small quick wins, complexity risk, maintainability pass signals, and tool installation gaps.

Expected outputs:

- `metrics/org-metrics.json`
- `metrics/org-metrics.md`

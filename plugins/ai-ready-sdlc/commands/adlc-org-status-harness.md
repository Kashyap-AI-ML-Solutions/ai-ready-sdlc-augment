---
description: Create an ADLC orchestration plan for org status collection and metrics.
---

# ADLC Org Status Harness

Create an orchestration plan through the plugin-level ADLC conductor before collecting or aggregating org status.

Use this command for repository inventory runs, collection repo updates, or metrics rollups.

Required conductor call:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/steer-adlc-harness.py --repo-path . --task-type orchestration --title "<org status task title>"
```

The generated plan must live under `.adlc/plans/<YYYY-MM-DD>_<task-slug>/` and include inventory scope, expected reports, aggregation checks, work items, and proof requirements.

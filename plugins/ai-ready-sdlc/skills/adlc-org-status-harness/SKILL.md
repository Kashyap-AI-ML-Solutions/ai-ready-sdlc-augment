---
name: adlc-org-status-harness
description: Create orchestration plans for org status collection and metrics rollups.
---

Use this skill for multi-repo ADLC collection or metrics orchestration. Start with:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/steer-adlc-harness.py --repo-path . --task-type orchestration --title "<org status task title>"
```

The plan must include repository scope, expected reports, aggregation checks, work items, and proof requirements before collection or aggregation runs.

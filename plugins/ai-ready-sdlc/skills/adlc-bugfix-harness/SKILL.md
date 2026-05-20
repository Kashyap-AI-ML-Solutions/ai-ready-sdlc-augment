---
name: adlc-bugfix-harness
description: Create bugfix plans under .adlc/plans with reproduction, regression, verification, and proof gates.
---

Use this skill for bug fixes. Start with:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/steer-adlc-harness.py --repo-path . --task-type bugfix --title "<bugfix title>"
```

The plan must include reproduction evidence, regression test expectations, focused verification, work items, and proof requirements before implementation.

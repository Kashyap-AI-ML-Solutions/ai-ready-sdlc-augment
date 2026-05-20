---
description: Create a feature ADLC plan with acceptance checks, tests, evals, and proof gates.
---

# ADLC Feature Harness

Create a feature plan through the plugin-level ADLC conductor before implementation.

Use this command when the request adds or changes user-visible behavior, API behavior, infrastructure capability, or workflow behavior.

Required conductor call:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/steer-adlc-harness.py --repo-path . --task-type feature --title "<feature title>"
```

The generated plan must live under `.adlc/plans/<YYYY-MM-DD>_<task-slug>/` and include acceptance checks, focused tests, evals when relevant, standards checks, work items, and proof requirements.

---
description: Create a bugfix ADLC plan with reproduction, regression, verification, and proof gates.
---

# ADLC Bugfix Harness

Create a bugfix plan through the plugin-level ADLC conductor before implementation.

Use this command when the request fixes a defect, regression, incident, failing check, or incorrect behavior.

Required conductor call:

```bash
python3 scripts/steer-adlc-harness.py --repo-path . --task-type bugfix --title "<bugfix title>"
```

The generated plan must live under `.adlc/plans/<YYYY-MM-DD>_<task-slug>/` and include reproduction evidence, regression test expectations, focused verification, work items, and proof requirements.

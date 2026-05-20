---
name: adlc-remediation-harness
description: Create remediation plans under .adlc/plans with security, quality, regression, and standards gates.
---

Use this skill for Project CodeGuard, standards, security, or code-quality remediation. Start with:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/steer-adlc-harness.py --repo-path . --task-type remediation --title "<remediation title>" --source-report "<optional report path>"
```

The plan must include tests, evals, security checks, standards checks, bounded work items, and proof requirements before implementation.

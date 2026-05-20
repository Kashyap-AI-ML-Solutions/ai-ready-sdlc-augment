---
description: Create a remediation ADLC plan with security, quality, regression, and standards gates.
---

# ADLC Remediation Harness

Create a remediation plan through the plugin-level ADLC conductor before implementation.

Use this command for Project CodeGuard findings, standards findings, security cleanup, code-quality cleanup, or policy remediation.

Required conductor call:

```bash
python3 scripts/steer-adlc-harness.py --repo-path . --task-type remediation --title "<remediation title>" --source-report "<optional report path>"
```

The generated plan must live under `.adlc/plans/<YYYY-MM-DD>_<task-slug>/` and include tests, evals, security checks, standards checks, bounded work items, and proof requirements.

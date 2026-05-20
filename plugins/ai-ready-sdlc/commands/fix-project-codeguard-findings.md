---
description: Fix the highest-priority Project CodeGuard findings in the current repository.
---

# Fix Project CodeGuard Findings

Use the Project CodeGuard report and remediation cookbook to plan and implement the highest-priority fixes in the current repository.

This command must route through the ADLC harness before code changes. Do not start fixing findings until a remediation plan exists under `.adlc/plans/<run>/`.

Preferred workflow:

- start from `reports/project-codeguard-security.json`,
- ensure `.adlc/` exists with `create-adlc-harness` if needed,
- invoke `steer-adlc-harness` with task type `remediation`:

```bash
python3 scripts/steer-adlc-harness.py --repo-path . --task-type remediation --title "Project CodeGuard remediation" --source-report reports/project-codeguard-security.json
```

- create a canonical plan under `.adlc/plans/<YYYY-MM-DD>_<task-slug>/`,
- include tests, evals, security checks, standards checks, and proof requirements,
- prioritize high-severity findings first,
- map findings to approved remediation patterns in `../docs/project-codeguard-fix-cookbook.md`,
- implement one bounded work item at a time,
- run validation gates,
- update proof artifacts and lifecycle state,
- explain what changed after the fixes are applied.

---
name: fix-org-standards-findings
description: Create a scoped plan-first remediation slice from org standards findings.
---

Use this skill when `reports/org-standards.json` exists and the team wants a bounded remediation plan for organization standards recommendations.

This is plan-first. Do not edit code by default.

Preferred deterministic planner:

```bash
python3 scripts/fix-org-standards-findings.py --repo-path . --source-report reports/org-standards.json --priority low --max-items 3
```

The generated `.adlc/plans/<run>/` artifacts must show:

- selected recommendations,
- out-of-scope recommendations,
- work items limited to the requested slice,
- tests and evals,
- standards checks,
- proof requirements.

Implementation starts only after the user approves the plan and scope.

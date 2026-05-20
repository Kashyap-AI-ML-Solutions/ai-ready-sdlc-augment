---
description: Create a scoped ADLC remediation plan from org standards findings before implementation.
---

# Fix Org Standards Findings

Create a scoped, plan-only ADLC remediation plan from `reports/org-standards.json`.

This command must not edit code by default. It exists to avoid unbounded "fix everything" runs.

Preferred workflow:

- ensure `reports/org-standards.json` exists by running `run-org-standards`,
- ensure `.adlc/` exists with `create-adlc-harness` if needed,
- select the requested slice of recommendations,
- create a canonical remediation plan under `.adlc/plans/<run>/`,
- include selected recommendations, out-of-scope recommendations, tests, evals, standards checks, work items, and proof requirements,
- wait for human approval before implementation.

Default low-priority slice:

```bash
python3 scripts/fix-org-standards-findings.py --repo-path . --source-report reports/org-standards.json --priority low --max-items 3
```

For a different scoped slice, change `--priority`, `--area`, or `--max-items`. Do not implement selected work items unless the user explicitly approves.

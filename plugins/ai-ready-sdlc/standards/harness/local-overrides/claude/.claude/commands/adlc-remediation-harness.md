# ADLC Remediation Harness Local Override

This repository-local command is optional. Use it only when the repository needs a local Claude command for remediation work.

Delegate to the installed ADLC plugin:

```text
/ai-ready-sdlc:steer-adlc-harness task_type=remediation
```

Before editing code:

- Ensure `.adlc/` exists.
- Create `.adlc/plans/<YYYY-MM-DD>_<task-slug>/`.
- Fill `tests-and-evals.md` with the relevant security, quality, regression, and standards checks.
- Fill `work-items.md` with bounded remediation steps.
- Update `.adlc/lifecycle.json` and `.adlc/status.md` as the work moves through plan, execute, verify, prove, and report.

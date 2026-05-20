---
name: adlc-harness
description: Optional repo-local Codex override that delegates tasks to the installed ADLC plugin and canonical .adlc plan lifecycle.
---

# ADLC Harness Local Override

Use this skill only when the repository explicitly installs local overrides. The installed `ai-ready-sdlc` Codex plugin is still the primary distribution mechanism.

Workflow:

1. Read `.adlc/harness.yaml`, `.adlc/lifecycle.json`, and `.adlc/status.md`.
2. If `.adlc/` is missing, initialize it with `create-adlc-harness`.
3. Use the plugin `steer-adlc-harness` workflow for feature, bugfix, unit-test, remediation, or orchestration work.
4. Create the canonical plan under `.adlc/plans/<YYYY-MM-DD>_<task-slug>/`.
5. Implement only after `tests-and-evals.md` and `work-items.md` are filled.
6. Update `.adlc/lifecycle.json`, `.adlc/status.md`, and proof artifacts as work progresses.

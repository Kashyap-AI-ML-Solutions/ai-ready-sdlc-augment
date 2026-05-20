---
name: adlc-harness
description: Use the generic ADLC harness lifecycle and canonical .adlc/plans artifacts.
---

Use this skill when a request needs the shared ADLC lifecycle before implementation.

The plugin is the discovery surface. `.adlc/` is the platform-independent ledger.

Workflow:

- Ensure `.adlc/` exists.
- Detect existing local harnesses and preserve them.
- Use `scripts/steer-adlc-harness.py` to create a canonical plan.
- Keep the plan under `.adlc/plans/<YYYY-MM-DD>_<task-slug>/`.
- Require `tests-and-evals.md` and `work-items.md` before editing code.
- Update `.adlc/lifecycle.json`, `.adlc/status.md`, and proof artifacts as the task progresses.

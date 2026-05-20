# ADLC Remediation Harness Local Override

This repository-local command is optional. The installed `ai-ready-sdlc` Codex plugin remains the primary discovery and execution surface.

For remediation work, use the plugin skill `steer-adlc-harness` with task type `remediation` before code edits.

Required shared artifacts:

- `.adlc/plans/<YYYY-MM-DD>_<task-slug>/plan.md`
- `.adlc/plans/<YYYY-MM-DD>_<task-slug>/plan.yaml`
- `.adlc/plans/<YYYY-MM-DD>_<task-slug>/tests-and-evals.md`
- `.adlc/plans/<YYYY-MM-DD>_<task-slug>/work-items.md`
- `.adlc/plans/<YYYY-MM-DD>_<task-slug>/state.json`

Respect existing repo-local harnesses listed in `.adlc/harness.yaml`.

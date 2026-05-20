# ADLC Harness Local Override

This repository-local command is optional. The installed `ai-ready-sdlc` Claude plugin remains the primary discovery and execution surface.

Use this override only when the repository wants a checked-in local command that delegates to the generic ADLC harness.

Workflow:

- Read `.adlc/harness.yaml`, `.adlc/lifecycle.json`, and `.adlc/status.md`.
- If `.adlc/` is missing, initialize it with the plugin `create-adlc-harness` command.
- Route the task through `/ai-ready-sdlc:steer-adlc-harness`.
- Create or update the canonical plan under `.adlc/plans/<YYYY-MM-DD>_<task-slug>/`.
- Do not implement until the plan includes tests, evals, standards checks, work items, and proof expectations.
- Respect detected local harnesses recorded in `.adlc/harness.yaml`.

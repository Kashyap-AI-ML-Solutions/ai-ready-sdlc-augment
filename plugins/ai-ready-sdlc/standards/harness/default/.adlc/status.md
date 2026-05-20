# ADLC Harness Status

Generated: {{generated_at}}
Repository: {{repo_name}}
Distribution model: plugin-first

## Current Goal

- No active task recorded yet.

## Latest Progress

- Harness scaffold installed.

## Validation State

| Check | Status | Evidence |
| --- | --- | --- |
| Standards report | not_run | |
| Focused tests | not_run | |
| Security lane | not_run | |
| Coverage artifact | unknown | |

## Detected Local Harnesses

{{detected_harnesses_markdown}}

## Decisions

- Plugin commands and skills are the platform discovery surface.
- `.adlc/` is the shared state ledger.
- Repo-local platform harness files are optional overrides or existing repo conventions.

## Open Risks

- No task-specific risks recorded yet.

## Next Agent Handoff

Start by reading `.adlc/harness.yaml` and `.adlc/lifecycle.json`, then create a platform-independent plan under `.adlc/plans/<YYYY-MM-DD>_<task-slug>/`.

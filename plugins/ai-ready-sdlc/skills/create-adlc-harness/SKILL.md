---
name: create-adlc-harness
description: Initialize or refresh shared .adlc harness state in a repository.
---

Use this skill when a repository needs the default platform-neutral ADLC harness.

Workflow:

- inspect for an existing `.adlc/` directory and `WORKFLOW.md`,
- preserve existing harness files unless the user asks to overwrite,
- run `python3 scripts/create-adlc-harness.py --repo-path <repo>` from the ADLC product repo,
- use `--install-local-overrides claude,codex,augment` only when the user explicitly wants local platform files,
- tell the user which files were written and skipped,
- continue with the harness steerer for feature, bug, test, remediation, or orchestration work.

References:

- `../../standards/harness/default/`
- `../../docs/adlc-harness-architecture.md`
- `../../docs/org-status-collection-repo.md`

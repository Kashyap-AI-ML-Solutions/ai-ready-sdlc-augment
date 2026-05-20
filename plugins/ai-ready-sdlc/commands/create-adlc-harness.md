---
description: Initialize or refresh shared .adlc harness state in the current repository.
---

# Create ADLC Harness

Initialize or refresh shared ADLC harness state in the current repository.

The installed plugin is the platform-native discovery surface. By default, this command writes shared `.adlc/` state only; it does not create generic `.claude/`, `.codex/`, or `.augment/` files in the target repo.

Expected behavior:

- inspect the current repo for `.adlc/`,
- detect existing repo-local harnesses under `.claude/`, `.codex/`, `.augment/`, and `docs/superpowers/`,
- preserve existing harness files unless explicitly told to overwrite,
- use the shared harness scaffold under `../standards/harness/default/`,
- write the repo-local `.adlc/` layout,
- summarize written, skipped, and detected files.

Preferred shared command:

```bash
python3 scripts/create-adlc-harness.py --repo-path .
```

Use `--force` only when the user asks to overwrite existing harness files.
Use `--include-workflow` only when the repo wants a repo-local `WORKFLOW.md`.
Use `--install-local-overrides claude,codex,augment` only when the user explicitly wants repo-local platform override files.

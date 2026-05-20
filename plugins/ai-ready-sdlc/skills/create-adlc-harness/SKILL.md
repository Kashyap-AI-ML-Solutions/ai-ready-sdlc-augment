---
name: create-adlc-harness
description: Initialize or refresh shared .adlc harness state in a repository.
---

Use this skill when a repository needs the default platform-neutral ADLC harness.

Workflow:

- if running in Auggie, first confirm the plugin is enabled; `auggie plugin list` must show `[x] ai-ready-sdlc@ai-ready-sdlc-augment`,
- run the bundled initializer directly before any repo-wide manual discovery or external lookup,
- do not web search, fetch external ADLC docs, or look for `create-adlc-harness` on `PATH`,
- inspect for an existing `.adlc/` directory and `WORKFLOW.md` through the bundled initializer,
- preserve existing harness files unless the user asks to overwrite,
- run `python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/create-adlc-harness.py --repo-path <repo>` from the installed plugin package,
- use `--install-local-overrides claude,codex,augment` only when the user explicitly wants local platform files,
- tell the user which files were written and skipped,
- continue with the harness steerer for feature, bug, test, remediation, or orchestration work.

References:

- `../../standards/harness/default/`
- `../../docs/adlc-harness-architecture.md`
- `../../docs/org-status-collection-repo.md`

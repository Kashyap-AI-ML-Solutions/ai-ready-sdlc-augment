---
description: Run the full umbrella organization standards workflow for the repository.
---

# Run Org Standards

Run the full organization standards workflow for the current repository.

Expected coverage:

- AI readiness checks
- code quality evaluation
- Project CodeGuard security review
- bug triage readiness
- test plan to test coverage
- structured report generation

This is the umbrella command. It already covers the core standards lanes that would otherwise be checked separately.

This command writes repo-local reports. It does not publish to the central `adlc-org-status` repo by itself.

Execution gate:

- This command is active only when the plugin is installed and enabled. In Auggie, `auggie plugin list` must show `[x] ai-ready-sdlc@ai-ready-sdlc-augment`; if it shows `[ ]` or `/plugins` says `disabled`, stop and enable the plugin first.
- First action: run the bundled standards checker. Do not web search, fetch external ADLC docs, or run repo-wide manual discovery before the bundled command.
- Do not look for `run-org-standards` on `PATH`; use the plugin-bundled checker path.

For central publication, run the ADLC harness sequence and then `publish-adlc-snapshot`, or use `run-org-repo-status`:

```text
/ai-ready-sdlc:create-adlc-harness
/ai-ready-sdlc:steer-adlc-harness
/ai-ready-sdlc:run-org-standards
/ai-ready-sdlc:publish-adlc-snapshot
```

Preferred execution model:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/standards/checker/run.py --repo-path . --profile org-standards --include-optional --output reports/org-standards.json --markdown-output reports/org-standards.md
```

Use the shared runner bundled with this Augment plugin package, target the current repository with `--repo-path .`, include optional checks when available, and write outputs to `reports/org-standards.json` and `reports/org-standards.md`.

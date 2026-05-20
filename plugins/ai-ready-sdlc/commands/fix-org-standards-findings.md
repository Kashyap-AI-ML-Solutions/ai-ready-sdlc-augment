---
description: Continue the active ADLC plan with a scoped org standards remediation slice before implementation.
---

# Fix Org Standards Findings

Continue the active ADLC plan with a scoped org standards remediation slice from `reports/org-standards.json`.

This command must not edit code by default. It exists to avoid unbounded "fix everything" runs.

Execution gate:

- This command is active only when the plugin is installed and enabled. In Auggie, `auggie plugin list` must show `[x] ai-ready-sdlc@ai-ready-sdlc-augment`; if it shows `[ ]` or `/plugins` says `disabled`, stop and enable the plugin first.
- First action: run the bundled remediation planner below. Do not web search, fetch external ADLC docs, or run repo-wide manual discovery before the bundled command.
- Do not look for `fix-org-standards-findings` on `PATH`; use the plugin-bundled script path.

Preferred workflow:

- ensure `reports/org-standards.json` exists by running `run-org-standards`,
- ensure `.adlc/` exists with `create-adlc-harness` if needed,
- read `.adlc/lifecycle.json.active_plan` and continue that plan by default,
- select the requested slice of recommendations,
- write selected and out-of-scope recommendations into the active plan,
- include selected recommendations, out-of-scope recommendations, tests, evals, standards checks, work items, and proof requirements,
- wait for human approval before implementation.

Default low-priority slice:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/fix-org-standards-findings.py --repo-path . --source-report reports/org-standards.json --priority low --max-items 3
```

For a different scoped slice, change `--priority`, `--area`, or `--max-items`. Do not implement selected work items unless the user explicitly approves.

Use `--new-plan` only if the user explicitly asks for a separate remediation plan.

After the user approves the selected slice, implement only the approved selected work items, rerun `run-org-standards`, and do not publish until the rerun is reviewed.

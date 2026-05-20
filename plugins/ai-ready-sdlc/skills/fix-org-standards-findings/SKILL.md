---
name: fix-org-standards-findings
description: Continue the active ADLC plan with a scoped org standards remediation slice.
---

Use this skill when `reports/org-standards.json` exists and the team wants a bounded remediation slice for organization standards recommendations inside the active ADLC plan.

This is slice-selection first. Do not edit code by default.

Execution gate:

- if running in Auggie, first confirm the plugin is enabled; `auggie plugin list` must show `[x] ai-ready-sdlc@ai-ready-sdlc-augment`,
- run the bundled remediation planner directly before any repo-wide manual discovery or external lookup,
- do not web search, fetch external ADLC docs, or look for `fix-org-standards-findings` on `PATH`.

Preferred deterministic planner:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/fix-org-standards-findings.py --repo-path . --source-report reports/org-standards.json --priority low --max-items 3
```

The generated `.adlc/plans/<run>/` artifacts must show:

- selected recommendations,
- out-of-scope recommendations,
- work items limited to the requested slice,
- tests and evals,
- standards checks,
- proof requirements.

By default, continue `.adlc/lifecycle.json.active_plan`; use `--new-plan` only when the user explicitly asks for a separate remediation plan.

Implementation starts only after the user approves the selected slice. After implementation, rerun `run-org-standards` and do not publish until the rerun is reviewed.

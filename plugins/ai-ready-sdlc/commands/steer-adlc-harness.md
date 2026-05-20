---
description: Turn a request into a canonical ADLC plan, bounded work items, validation, and proof.
---

# Steer ADLC Harness

Use the installed ADLC plugin plus repo-local `.adlc/` state to turn the current request into executable ADLC work.

Execution gate:

- This command is active only when the plugin is installed and enabled. In Auggie, `auggie plugin list` must show `[x] ai-ready-sdlc@ai-ready-sdlc-augment`; if it shows `[ ]` or `/plugins` says `disabled`, stop and enable the plugin first.
- First action: run the bundled conductor below when the prompt is plan-only or orchestration. Do not web search, fetch external ADLC docs, or run repo-wide manual discovery before the bundled command.
- Do not look for `steer-adlc-harness` on `PATH`; use the plugin-bundled script path.

The bundled conductor and harness workflow will:

- ensure `.adlc/` exists, creating it if missing,
- read `.adlc/harness.yaml`, `.adlc/lifecycle.json`, and `.adlc/status.md`,
- detect existing repo-local harnesses recorded in `.adlc/harness.yaml`,
- classify the task as feature, bug fix, unit-test expansion, remediation, or orchestration,
- select and fill the closest blueprint,
- create a canonical plan under `.adlc/plans/<YYYY-MM-DD>_<task-slug>/`,
- write `plan.md`, `plan.yaml`, `tests-and-evals.md`, `work-items.md`, and `state.json`,
- run baseline or failing checks when practical,
- implement and verify one work item at a time only after the plan exists,
- write proof under `.adlc/proofs/`,
- update `.adlc/lifecycle.json` and `.adlc/status.md`.

Use the deterministic conductor when available:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/steer-adlc-harness.py --repo-path . --task-type "<feature|bugfix|unit-test|remediation|orchestration>" --title "<task title>" --source-report "<optional report path>"
```

Completion requires a canonical plan, proof, and an updated handoff.

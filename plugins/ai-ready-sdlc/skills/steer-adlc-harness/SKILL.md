---
name: steer-adlc-harness
description: Turn an engineering request into a canonical ADLC plan, work items, validation loops, and proof artifacts.
---

Use this plugin skill to turn a request into a platform-independent ADLC plan, bounded work items, validation loop, and proof artifacts.

Workflow:

- if running in Auggie, first confirm the plugin is enabled; `auggie plugin list` must show `[x] ai-ready-sdlc@ai-ready-sdlc-augment`,
- run the bundled conductor directly before any repo-wide manual discovery or external lookup,
- do not web search, fetch external ADLC docs, or look for `steer-adlc-harness` on `PATH`,
- ensure `.adlc/` exists, creating it if missing,
- read `.adlc/harness.yaml`, `.adlc/lifecycle.json`, and `.adlc/status.md`,
- classify the request as feature, bugfix, unit-test, remediation, or orchestration,
- use the closest blueprint from `.adlc/blueprints/`,
- create a canonical plan under `.adlc/plans/<YYYY-MM-DD>_<task-slug>/`,
- write `plan.md`, `plan.yaml`, `tests-and-evals.md`, `work-items.md`, and `state.json`,
- establish a baseline or failing signal when practical,
- implement and verify one bounded work item at a time only after the plan exists,
- write proof under `.adlc/proofs/`,
- update `.adlc/lifecycle.json` and `.adlc/status.md` with results and handoff notes.

Preferred conductor:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/steer-adlc-harness.py --repo-path . --task-type "<feature|bugfix|unit-test|remediation|orchestration>" --title "<task title>" --source-report "<optional report path>"
```

Completion requires a canonical plan, validation evidence, proof, and an updated handoff.

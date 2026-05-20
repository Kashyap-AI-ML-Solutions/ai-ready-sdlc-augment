---
name: steer-adlc-harness
description: Turn an engineering request into a canonical ADLC plan, work items, validation loops, and proof artifacts.
---

Use this plugin skill to turn a request into a platform-independent ADLC plan, bounded work items, validation loop, and proof artifacts.

Workflow:

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
python3 scripts/steer-adlc-harness.py --repo-path . --task-type "<feature|bugfix|unit-test|remediation|orchestration>" --title "<task title>" --source-report "<optional report path>"
```

Completion requires a canonical plan, validation evidence, proof, and an updated handoff.

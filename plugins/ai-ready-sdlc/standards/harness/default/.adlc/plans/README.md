# ADLC Plans

This directory holds platform-independent ADLC plans.

Every substantial task should create a run directory:

```text
.adlc/plans/<YYYY-MM-DD>_<task-slug>/
  plan.md
  plan.yaml
  tests-and-evals.md
  work-items.md
  state.json
```

The canonical plan lives here even when Claude, Codex, Auggie, Superpowers, or a repo-specific harness helps draft it.

Optional mirrors such as `docs/superpowers/plans/`, `docs/codex/runs/`, or `docs/harness/runs/` may be created for compatibility, but they must not replace this `.adlc` plan.

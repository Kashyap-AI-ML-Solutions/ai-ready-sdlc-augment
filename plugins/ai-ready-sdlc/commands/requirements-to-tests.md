---
description: Review requirements-to-test coverage and identify missing test evidence.
---

# Requirements To Tests

Map requirements or test plan coverage to implemented tests, identify missing cases, and recommend new test scripts where needed.

Preferred execution model:

- use the shared runner bundled with this Augment plugin package,
- target the current repository with `--repo-path .`,
- write outputs to `reports/requirements-to-tests.json` and `reports/requirements-to-tests.md`.

When the next step is adding or changing tests, route through `steer-adlc-harness` with task type `unit-test` before implementation:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/steer-adlc-harness.py --repo-path . --task-type unit-test --title "Requirements to tests gap closure" --source-report reports/requirements-to-tests.json
```

The canonical test-expansion plan must live under `.adlc/plans/<run>/`.

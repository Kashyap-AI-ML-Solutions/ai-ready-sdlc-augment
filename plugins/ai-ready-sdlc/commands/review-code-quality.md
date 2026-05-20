---
description: Run the shared language-aware code quality workflow for the repository.
---

# Review Code Quality

Run a language-aware code quality evaluation using the shared tool matrices under `../standards/tooling/` and produce the shared code quality report.

Preferred execution model:

- use the shared runner bundled with this Augment plugin package,
- target the current repository with `--repo-path .`,
- write outputs to `reports/code-quality.json` and `reports/code-quality.md`.

When the next step is remediation, route through `steer-adlc-harness` with task type `remediation` before editing:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/steer-adlc-harness.py --repo-path . --task-type remediation --title "Code quality remediation" --source-report reports/code-quality.json
```

The canonical plan must include language-specific checks, standards gates, and proof requirements under `.adlc/plans/<run>/`.

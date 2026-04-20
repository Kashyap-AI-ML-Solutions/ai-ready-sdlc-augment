---
description: Run the shared language-aware code quality workflow for the repository.
---

# Review Code Quality

Run a language-aware code quality evaluation using the shared tool matrices under `../standards/tooling/` and produce the shared code quality report.

Preferred execution model:

- use the shared runner bundled with this Augment plugin package,
- target the current repository with `--repo-path .`,
- write outputs to `reports/code-quality.json` and `reports/code-quality.md`.

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

Preferred execution model:

- use the shared runner bundled with this Augment plugin package,
- target the current repository with `--repo-path .`,
- include optional checks when available,
- write outputs to `reports/org-standards.json` and `reports/org-standards.md`.

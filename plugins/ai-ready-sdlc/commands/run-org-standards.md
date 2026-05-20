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

This command writes repo-local reports. It does not publish to the central `adlc-org-status` repo by itself.

For central publication, run the ADLC harness sequence and then `publish-adlc-snapshot`, or use `run-org-repo-status`:

```text
/ai-ready-sdlc:create-adlc-harness
/ai-ready-sdlc:steer-adlc-harness
/ai-ready-sdlc:run-org-standards
/ai-ready-sdlc:publish-adlc-snapshot
```

Preferred execution model:

- use the shared runner bundled with this Augment plugin package,
- target the current repository with `--repo-path .`,
- include optional checks when available,
- write outputs to `reports/org-standards.json` and `reports/org-standards.md`.

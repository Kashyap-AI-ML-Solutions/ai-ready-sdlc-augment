---
name: project-codeguard-security
description: Apply the organization Project CodeGuard security lane during repository work.
---

Use this skill when the repository needs the dedicated Project CodeGuard security lane from the shared standards core.

Preferred execution model:

- use the shared runner bundled with this Augment plugin package,
- target the current repository with `--repo-path .`,
- write outputs to `reports/project-codeguard-security.json` and `reports/project-codeguard-security.md`.

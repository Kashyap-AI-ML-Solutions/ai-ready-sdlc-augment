---
name: project-codeguard-fix-patterns
description: Map Project CodeGuard findings to secure remediation patterns and follow-up fixes.
---

Use this skill when the repository already has Project CodeGuard findings and the team needs secure remediation patterns.

Route remediation through `steer-adlc-harness` before code changes. The canonical remediation plan must live under `.adlc/plans/<run>/` and include tests, evals, security checks, standards checks, work items, and proof requirements.

Preferred conductor:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/steer-adlc-harness.py --repo-path . --task-type remediation --title "Project CodeGuard remediation" --source-report reports/project-codeguard-security.json
```

Preferred references:

- `../../docs/project-codeguard-fix-cookbook.md`
- `../../docs/project-codeguard-rule-mapping.md`
- `../../standards/security/project-codeguard/mapping.md`

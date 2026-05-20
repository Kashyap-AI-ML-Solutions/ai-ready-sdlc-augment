# Default ADLC Harness

This directory is the canonical source for the repo-local ADLC harness scaffold.

Install it into a target repository with:

```bash
python3 scripts/create-adlc-harness.py --repo-path /absolute/path/to/repo
```

The scaffold gives Claude, Codex, and Auggie the same durable files:

- `.adlc/harness.yaml`
- `.adlc/lifecycle.json`
- `.adlc/status.md`
- `.adlc/blueprints/*.yaml`
- `.adlc/plans/README.md`
- `.adlc/work-items/README.md`
- `.adlc/proofs/README.md`
- `.adlc/reports/README.md`
- `.adlc/runbooks/*.md`

Keep this scaffold platform-neutral. Plugin commands, skills, and agents are the platform-native discovery surface. Repo-local `.claude/`, `.codex/`, and `.augment/` harness files are optional overrides or existing repo-specific harnesses, not the default install target.

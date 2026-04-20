# Project CodeGuard Usage

## What This Lane Does

The Project CodeGuard lane adds a dedicated security review to the shared standards core.

Phase 1 coverage includes:

- possible hardcoded credentials
- weak cryptography and disabled TLS verification
- dynamic execution patterns
- unpinned GitHub Actions
- privileged Kubernetes or deployment settings

The lane is anchored to the pinned upstream Project CodeGuard release recorded in:

- `third_party/project-codeguard/current.json`
- `third_party/project-codeguard/<version>/metadata.json`
- `standards/security/project-codeguard/generated/current-bundle.json`

## When To Run It

Run the dedicated Project CodeGuard lane when:

- you want a focused security review,
- the repo handles credentials, auth, or external APIs,
- the repo includes CI workflows or deployment artifacts,
- you want security findings separate from the general code-quality lane.

## Command Surface

Shared checker:

```bash
python3 standards/checker/run.py --repo-path <repo> --profile project-codeguard-security --output reports/project-codeguard-security.json --markdown-output reports/project-codeguard-security.md
```

Wrapper:

```bash
bash scripts/run-project-codeguard-check.sh <repo> <output-dir>
```

Claude:

- `/ai-ready-sdlc:review-project-codeguard-security`
- `/ai-ready-sdlc:fix-project-codeguard-findings`
- `/ai-ready-sdlc:explain-project-codeguard-findings`

Codex:

- `Use the ai-ready-sdlc plugin and review Project CodeGuard security on this repository.`
- `Use the ai-ready-sdlc plugin and fix Project CodeGuard findings in this repository.`
- `Explain the Project CodeGuard findings and recommended remediations for this repository.`

## How It Relates To `run-org-standards`

`run-org-standards` is the umbrella workflow.

It now includes:

- code quality
- AI readiness
- bug triage readiness
- requirements-to-tests readiness
- Project CodeGuard security

The dedicated Project CodeGuard workflow is for a narrower, security-only follow-up.

## Updating The Pinned Upstream Version

Use the release-management flow from the product repo:

```bash
python3 scripts/update-project-codeguard-version.py --latest
bash scripts/build-plugin-dists.sh
```

If you want to stage a specific version:

```bash
python3 scripts/update-project-codeguard-version.py --version v1.3.1
```

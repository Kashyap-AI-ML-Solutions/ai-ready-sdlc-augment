---
name: org-status-orchestrator
description: Coordinate ADLC status collection and report publication across many repositories.
---

Use this skill to collect ADLC status across many repositories.

Workflow:

- identify the target GitHub org and collection repo,
- check for a GitHub MCP, GitHub app, or `gh` CLI before attempting repo creation,
- search for an existing collection repo before creating a new one,
- create or refresh the layout from `../../docs/org-status-collection-repo.md`,
- use `python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/init-org-status-repo.py --repo-path <collection-repo> --org <github-org>` for local layout initialization,
- normalize repo scope into `inventory/repos.yaml`,
- initialize or refresh shared `.adlc/` state for each repo when needed,
- run or coordinate the required per-repo standards reports,
- publish each repo's own evidence bundle with `python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/publish-adlc-snapshot.py --repo-path <target-repo> --org jasper-sw --collection-owner jasper-sw --collection-repo adlc-org-status --payload-output /tmp/adlc-payload.json`,
- use the Cisco GitHub MCP `push_files` payload to update `repos/<org>/<repo>/runs/<timestamp>/` and `repos/<org>/<repo>/latest/`,
- run the org metrics aggregator inside the central collection repo,
- produce remediation and tool installation plans.

If no GitHub connector or CLI is available, explain the missing capability and stop before repo creation.

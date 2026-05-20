---
description: Collect ADLC status across an organization repository inventory.
---

# Run Org Repo Status

Collect ADLC status across an organization repository inventory.

Expected behavior:

- use or create the org status collection repo layout from `../docs/org-status-collection-repo.md`,
- initialize the local layout with `python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/init-org-status-repo.py --repo-path <collection-repo> --org <github-org>` when needed,
- read `inventory/repos.yaml`,
- initialize or refresh shared `.adlc/` state in target repos when needed,
- run the required standards reports for each repository,
- publish each repo's own evidence bundle with `python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/publish-adlc-snapshot.py --repo-path <target-repo> --org jasper-sw --collection-owner jasper-sw --collection-repo adlc-org-status --payload-output /tmp/adlc-payload.json`,
- use Cisco GitHub MCP `push_files` to copy snapshots into `repos/<org>/<repo>/runs/<timestamp>/`,
- refresh `repos/<org>/<repo>/latest/` in the same central repo commit when practical,
- aggregate metrics only inside the central collection repo after collection.

If a GitHub MCP, GitHub app, or `gh` CLI is needed but unavailable, explain the missing capability before attempting repo creation.

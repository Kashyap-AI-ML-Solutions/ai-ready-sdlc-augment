---
description: Publish the current repository's ADLC evidence bundle to the central org status repo.
---

# Publish ADLC Snapshot

Publish the current repository's ADLC evidence bundle to the central `jasper-sw/adlc-org-status` repo.

This command is run from a target repo. It publishes repo-local evidence only:

- `reports/*.json`
- `reports/*.md`
- `.adlc/harness.yaml`
- `.adlc/lifecycle.json`
- `.adlc/status.md`
- active `.adlc/plans/<run>/`
- small `.adlc/proofs/**`
- optional small coverage and test evidence

Central metrics, dashboards, and org-level plans are computed inside `adlc-org-status`, not inside the target repo.

Execution gate:

- This command is active only when the plugin is installed and enabled. In Auggie, `auggie plugin list` must show `[x] ai-ready-sdlc@ai-ready-sdlc-augment`; if it shows `[ ]` or `/plugins` says `disabled`, stop and enable the plugin first.
- First action: run the bundled snapshot publisher below. Do not web search, fetch external ADLC docs, or run repo-wide manual discovery before the bundled command.
- Do not look for `publish-adlc-snapshot` on `PATH`; use the plugin-bundled script path.

Preferred command:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/publish-adlc-snapshot.py --repo-path . --org jasper-sw --collection-owner jasper-sw --collection-repo adlc-org-status --payload-output /tmp/adlc-payload.json
```

Use the Cisco GitHub MCP `push_files` tool to commit the payload to:

```text
repos/jasper-sw/<repo>/runs/<timestamp>/
repos/jasper-sw/<repo>/latest/
```

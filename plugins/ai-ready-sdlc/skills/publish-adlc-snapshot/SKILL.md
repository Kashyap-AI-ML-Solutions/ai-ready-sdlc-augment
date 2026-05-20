---
name: publish-adlc-snapshot
description: Publish this repository's reports, ADLC lifecycle state, plans, and proof artifacts to the central org status repo.
---

Use this skill after a target repo has generated ADLC reports and harness state.

Workflow:

- if running in Auggie, first confirm the plugin is enabled; `auggie plugin list` must show `[x] ai-ready-sdlc@ai-ready-sdlc-augment`,
- run the bundled snapshot publisher directly before any repo-wide manual discovery or external lookup,
- do not web search, fetch external ADLC docs, or look for `publish-adlc-snapshot` on `PATH`,
- confirm `.adlc/` exists,
- confirm the required `reports/` files exist,
- gather active plan and proof artifacts,
- create `manifest.json`,
- publish both `runs/<timestamp>/` and `latest/` paths to `jasper-sw/adlc-org-status`,
- leave central `metrics/`, `dashboards/`, and org-level `plans/` for the central repo analysis workflow.

Shared command:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/publish-adlc-snapshot.py --repo-path . --org jasper-sw --collection-owner jasper-sw --collection-repo adlc-org-status --payload-output /tmp/adlc-payload.json
```

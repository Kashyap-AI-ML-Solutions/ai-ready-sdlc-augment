---
name: publish-adlc-snapshot
description: Publish this repository's reports, ADLC lifecycle state, plans, and proof artifacts to the central org status repo.
---

Use this skill after a target repo has generated ADLC reports and harness state.

Workflow:

- confirm `.adlc/` exists,
- confirm the required `reports/` files exist,
- gather active plan and proof artifacts,
- create `manifest.json`,
- publish both `runs/<timestamp>/` and `latest/` paths to `jasper-sw/adlc-org-status`,
- leave central `metrics/`, `dashboards/`, and org-level `plans/` for the central repo analysis workflow.

Shared command:

```bash
python3 scripts/publish-adlc-snapshot.py --repo-path . --org jasper-sw --collection-owner jasper-sw --collection-repo adlc-org-status --payload-output /tmp/adlc-payload.json
```

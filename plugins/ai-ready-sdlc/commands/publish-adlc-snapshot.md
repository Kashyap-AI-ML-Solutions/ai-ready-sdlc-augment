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

Preferred command:

```bash
python3 scripts/publish-adlc-snapshot.py --repo-path . --org jasper-sw --collection-owner jasper-sw --collection-repo adlc-org-status --payload-output /tmp/adlc-payload.json
```

Use the Cisco GitHub MCP `push_files` tool to commit the payload to:

```text
repos/jasper-sw/<repo>/runs/<timestamp>/
repos/jasper-sw/<repo>/latest/
```

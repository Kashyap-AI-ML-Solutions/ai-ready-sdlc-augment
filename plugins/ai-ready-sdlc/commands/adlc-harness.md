---
description: Use the generic ADLC harness lifecycle for the current engineering task.
---

# ADLC Harness

Use the installed ADLC plugin to route the current engineering request through the shared lifecycle:

```text
Discover -> Scaffold or Refresh -> Blueprint -> Plan -> Execute -> Verify -> Repair -> Prove -> Report
```

Required behavior:

- Ensure `.adlc/` exists.
- Detect and respect existing repo-local harnesses.
- Create the canonical plan under `.adlc/plans/<YYYY-MM-DD>_<task-slug>/`.
- Fill `plan.md`, `plan.yaml`, `tests-and-evals.md`, `work-items.md`, and `state.json`.
- Do not implement until the plan includes tests, evals, standards checks, and proof expectations.

Deterministic conductor:

```bash
python3 "$HOME"/.augment/plugins/marketplaces/ai-ready-sdlc-augment/plugins/ai-ready-sdlc/scripts/steer-adlc-harness.py --repo-path . --task-type feature --title "<task title>"
```

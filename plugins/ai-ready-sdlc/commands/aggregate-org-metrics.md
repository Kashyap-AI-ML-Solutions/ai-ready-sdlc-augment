---
description: Aggregate collected ADLC standards reports into organization-level metrics.
---

# Aggregate Org Metrics

Aggregate collected ADLC standards reports into org-level metrics.

Preferred shared command:

```bash
python3 scripts/aggregate-org-metrics.py --collection-repo <collection-repo> --output metrics/org-metrics.json --markdown-output metrics/org-metrics.md
```

Expected metrics:

- coverage policy adoption,
- missing coverage artifacts,
- high or critical security findings,
- too many security findings,
- large gaps,
- small quick-win gaps,
- complexity risk,
- maintainability pass signals,
- tool installation gaps.

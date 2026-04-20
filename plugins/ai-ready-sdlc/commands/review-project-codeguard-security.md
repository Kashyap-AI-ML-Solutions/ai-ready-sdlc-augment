---
description: Run the dedicated Project CodeGuard security workflow for the repository.
---

# Review Project CodeGuard Security

Run the shared Project CodeGuard security lane for the current repository and summarize the findings in a repo-friendly way.

Expected coverage:

- secrets handling
- cryptography and TLS safety
- dynamic execution and injection risks
- supply-chain and CI security
- cloud, IaC, and container security when relevant

Preferred shared runner:

- `python3 standards/checker/run.py --repo-path . --profile project-codeguard-security --output reports/project-codeguard-security.json --markdown-output reports/project-codeguard-security.md`

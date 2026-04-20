# Project CodeGuard Demo Playbook

## Goal

Use this playbook to demo the new Project CodeGuard lane on the 3 target repos.

## 1. webex-messaging-mcp-server

Best story:

- JavaScript and TypeScript API repo
- strong fit for secrets handling, CI security, and logging or transport-security discussion

Recommended run:

```bash
python3 standards/checker/run.py --repo-path ../webex-messaging-mcp-server --profile project-codeguard-security
python3 standards/checker/run.py --repo-path ../webex-messaging-mcp-server --profile org-standards --include-optional
```

What to emphasize:

- dedicated security findings
- how the same lane also rolls into the umbrella standards report

## 2. cdr-dedup

Best story:

- Go service repo
- strong fit for crypto, TLS, and service-safe defaults discussion

Recommended run:

```bash
python3 standards/checker/run.py --repo-path ../cdr-dedup --profile project-codeguard-security
python3 standards/checker/run.py --repo-path ../cdr-dedup --profile org-standards --include-optional
```

What to emphasize:

- language-specific repo, same shared security lane
- how Claude, Codex, or Augment can all invoke the same underlying check

## 3. smi-cluster-deployer

Best story:

- mixed repo with Node.js, Python, and deployment artifacts
- strong fit for supply chain, IaC, and container-security discussion

Recommended run:

```bash
python3 standards/checker/run.py --repo-path ../smi-cluster-deployer --profile project-codeguard-security
python3 standards/checker/run.py --repo-path ../smi-cluster-deployer --profile org-standards --include-optional
```

What to emphasize:

- mixed-stack repo coverage
- why Project CodeGuard belongs in the shared standards core rather than a separate ad hoc tool

## Demo Talk Track

1. Show the dedicated Project CodeGuard security report.
2. Show the same findings rolling into `run-org-standards`.
3. Explain that Claude, Codex, and Augment are just thin adapters over the same standards core.
4. Close with the pinned upstream version and the release-update process in the integration plan.

## Plugin Demo Follow-Up

After the direct runner demo, validate the installed plugin surfaces too:

- Claude:
  - `/ai-ready-sdlc:review-project-codeguard-security`
  - `/ai-ready-sdlc:fix-project-codeguard-findings`
  - `/ai-ready-sdlc:explain-project-codeguard-findings`
- Codex:
  - `Use the ai-ready-sdlc plugin and review Project CodeGuard security on this repository.`
  - `Use the ai-ready-sdlc plugin and fix Project CodeGuard findings in this repository.`
  - `Explain the Project CodeGuard findings and recommended remediations for this repository.`
- Augment:
  - `/ai-ready-sdlc:review-project-codeguard-security`
  - `/ai-ready-sdlc:fix-project-codeguard-findings`
  - `/ai-ready-sdlc:explain-project-codeguard-findings`

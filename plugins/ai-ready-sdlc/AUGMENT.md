# Augment Package Baseline

This package adapts the neutral AI-ready SDLC standard for Augment / Auggie plugin workflows.

## Policy Source

The policy authority for this package is:

- `../../standards/policy/ai-ready-sdlc.md`
- `../../standards/policy/org-policy-prompt.md`
- `../../standards/policy/project-codeguard-security-standard.md`

## Package Intent

- Keep Augment-specific plugin metadata here.
- Reuse the shared command, agent, and skill surfaces from the same standards core used by Claude, Codex, and Augment.
- Keep Project CodeGuard support pinned and distributed with the plugin bundle.

## Baseline Behavior

- Prefer `Claude Opus 4.6` as the Auggie default or workspace model for this plugin.
- For user/global enablement, `~/.augment/settings.json` should recommend `Kashyap-AI-ML-Solutions/ai-ready-sdlc-augment` and set `enabledPlugins.ai-ready-sdlc@ai-ready-sdlc-augment` to `true`.
- In Auggie 0.27.2, invoke commands with the autocomplete namespace `/ai-ready-sdlc--ai-ready-sdlc-augment:<command>`.
- Prefer compliant repository changes.
- Never bypass human approval.
- Encourage manifests, test plans, observability, and structured review artifacts.
- Use the organization workflow surface for repeatable standards checks:
  - `create-adlc-harness`
  - `steer-adlc-harness`
  - `adlc-harness`
  - `adlc-feature-harness`
  - `adlc-bugfix-harness`
  - `adlc-remediation-harness`
  - `adlc-org-status-harness`
  - `publish-adlc-snapshot`
  - `run-org-standards`
  - `run-org-repo-status`
  - `aggregate-org-metrics`
      - `review-code-quality`
      - `review-project-codeguard-security`
      - `fix-project-codeguard-findings`
      - `fix-org-standards-findings`
      - `explain-project-codeguard-findings`
  - `triage-bugs`
  - `check-ai-readiness`
  - `requirements-to-tests`
  - `generate-standards-report`

# AI Ready SDLC Augment Marketplace

This directory is a publishable Augment / Auggie marketplace for the `ai-ready-sdlc` plugin.

## Install

After publishing this marketplace repository to GitHub or GitHub Enterprise, install it with:

```sh
auggie plugin marketplace add Kashyap-AI-ML-Solutions/ai-ready-sdlc-augment
auggie plugin install ai-ready-sdlc@ai-ready-sdlc-augment
```

Use project scope only when a specific repository should carry `.augment/settings.json` enablement:

```sh
auggie plugin install ai-ready-sdlc@ai-ready-sdlc-augment --project
```

To recommend the marketplace for a specific repository, add this to `.augment/settings.json`:

```json
{
  "recommendedMarketplaces": ["Kashyap-AI-ML-Solutions/ai-ready-sdlc-augment"],
  "enabledPlugins": {
    "ai-ready-sdlc@ai-ready-sdlc-augment": true
  }
}
```

## Included Workflow Surface

- `/ai-ready-sdlc:create-adlc-harness`
- `/ai-ready-sdlc:steer-adlc-harness`
- `/ai-ready-sdlc:adlc-harness`
- `/ai-ready-sdlc:adlc-feature-harness`
- `/ai-ready-sdlc:adlc-bugfix-harness`
- `/ai-ready-sdlc:adlc-remediation-harness`
- `/ai-ready-sdlc:adlc-org-status-harness`
- `/ai-ready-sdlc:run-org-standards`
- `/ai-ready-sdlc:run-org-repo-status`
- `/ai-ready-sdlc:aggregate-org-metrics`
- `/ai-ready-sdlc:review-code-quality`
- `/ai-ready-sdlc:review-project-codeguard-security`
- `/ai-ready-sdlc:fix-project-codeguard-findings`
- `/ai-ready-sdlc:fix-org-standards-findings`
- `/ai-ready-sdlc:explain-project-codeguard-findings`

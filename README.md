# AI Ready SDLC Augment Marketplace

This directory is a publishable Augment / Auggie marketplace for the `ai-ready-sdlc` plugin.

## Install

After publishing this marketplace repository to GitHub or GitHub Enterprise, install it with:

```sh
auggie plugin marketplace add <owner>/<repo>
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

- `/ai-ready-sdlc:run-org-standards`
- `/ai-ready-sdlc:review-code-quality`
- `/ai-ready-sdlc:review-project-codeguard-security`
- `/ai-ready-sdlc:fix-project-codeguard-findings`
- `/ai-ready-sdlc:explain-project-codeguard-findings`
